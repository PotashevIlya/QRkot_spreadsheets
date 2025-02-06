from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.api.validators import (
    check_charity_project_exists, check_charity_project_is_open,
    check_charity_project_investments, check_full_amount_update,
    check_charity_project_name_duplicate
)
from app.services.investment_logic import distribute_investments


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров."""
    await check_charity_project_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(
        charity_project, session, need_for_commit=False
    )
    changed_donations = distribute_investments(
        new_project, await donation_crud.get_all_open(session)
    )
    session.add_all(changed_donations)
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Для любого пользователя."""
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров"""
    charity_project = await check_charity_project_exists(project_id, session)
    await check_charity_project_is_open(project_id, session)
    if obj_in.full_amount:
        check_full_amount_update(
            charity_project.invested_amount, obj_in.full_amount
        )
    if obj_in.name:
        await check_charity_project_name_duplicate(obj_in.name, session)
    return await charity_project_crud.update(charity_project, obj_in, session)


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    await check_charity_project_is_open(project_id, session)
    await check_charity_project_investments(
        project_id, session
    )
    return await charity_project_crud.remove(
        charity_project, session
    )
