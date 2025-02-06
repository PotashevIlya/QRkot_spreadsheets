from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_charity_project_by_name(
            self,
            project_name: str,
            session: AsyncSession
    ) -> Optional[int]:
        charity_project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_name)
        )
        return charity_project.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> list[CharityProject]:
        """Возвращает закрытые проекты, отсортрованные по скорости закрытия"""
        charity_projects = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested))
        return sorted(
            charity_projects.scalars().all(),
            key=lambda project: project.close_date - project.create_date
        )


charity_project_crud = CRUDCharityProject(CharityProject)
