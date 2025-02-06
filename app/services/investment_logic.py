from datetime import datetime

from app.models import InvestmentBaseModel


def distribute_investments(
    target: InvestmentBaseModel,
    sources: list[InvestmentBaseModel]
) -> list[InvestmentBaseModel]:
    changed = []
    for source in sources:
        trans_amount = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        for obj in (target, source):
            obj.invested_amount += trans_amount
            if obj.invested_amount == obj.full_amount:
                obj.fully_invested = True
                obj.close_date = datetime.utcnow()
        changed.append(source)
        if target.fully_invested:
            break
    return changed
