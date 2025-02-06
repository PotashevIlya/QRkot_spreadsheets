from sqlalchemy import Column, String, Text

from .base_model import InvestmentBaseModel


class CharityProject(InvestmentBaseModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f'название проекта - {self.name}, '
            f'описание проекта - {self.description}, '
            f'{super().__repr__()}'
        )
