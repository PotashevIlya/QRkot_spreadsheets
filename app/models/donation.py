from sqlalchemy import Column, ForeignKey, Integer, Text

from .base_model import InvestmentBaseModel


class Donation(InvestmentBaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return (
            f'id пользователя - {self.user_id}, '
            f'комментарий - {self.comment}, '
            f'{super().__repr__()}'
        )
