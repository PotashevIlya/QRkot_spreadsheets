from datetime import datetime

from sqlalchemy import Boolean, Column, CheckConstraint, DateTime, Integer

from app.core.db import Base


class InvestmentBaseModel(Base):
    __abstract__ = True
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.utcnow)
    close_date = Column(DateTime)
    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('0 <= invested_amount <= full_amount')
    )

    def __repr__(self):
        return (
            f'полная сумма - {self.full_amount}, '
            f'инвестированная сумма - {self.invested_amount}, '
            f'инвестирован полностью - {self.fully_invested}, '
            f'дата создания - {self.create_date}, '
            f'дата закрытия - {self.close_date}'
        )
