from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.crud.charity_project import charity_project_crud
from app.schemas.donation import (
    DonationCreate, DonationBriefDB, DonationFullDB
)
from app.models import User

from app.services.investment_logic import distribute_investments


router = APIRouter()


@router.post(
    '/',
    response_model=DonationBriefDB,
    response_model_exclude_none=True
)
async def create_new_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Для всех зарегистрированных пользователей."""
    new_donation = await donation_crud.create(
        donation, session, user, need_for_commit=False
    )
    changed_projects = distribute_investments(
        new_donation, await charity_project_crud.get_all_open(session)
    )
    session.add_all(changed_projects)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationFullDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationBriefDB],
    response_model_exclude_none=True,
    response_model_exclude={'user_id'}
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Получить список пожертвований текущего пользователя."""
    return await donation_crud.get_user_donations(
        session=session,
        user=user
    )
