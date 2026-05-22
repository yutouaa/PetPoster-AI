from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.quota_transaction import QuotaTransaction
from app.models.user_quota import UserQuota
from app.core.responses import success_response

router = APIRouter(prefix="/quota", tags=["quota"])


@router.get("/balance")
def get_balance(user_id: str = Query(...), db: Session = Depends(get_db)):
    quota = db.scalar(select(UserQuota).where(UserQuota.user_id == user_id))
    return success_response({
        "userId": user_id,
        "balance": quota.balance if quota else 0,
        "totalPurchased": quota.total_purchased if quota else 0,
        "totalConsumed": quota.total_consumed if quota else 0,
    })


@router.get("/transactions")
def get_transactions(
    user_id: str = Query(...),
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    base = select(QuotaTransaction).where(QuotaTransaction.user_id == user_id)
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    items = db.scalars(
        base.order_by(QuotaTransaction.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    records = [
        {
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "balanceAfter": t.balance_after,
            "referenceId": t.reference_id,
            "remark": t.remark,
            "createdAt": t.created_at.isoformat() if t.created_at else None,
        }
        for t in items
    ]
    return success_response({"records": records, "total": total, "current": page, "size": page_size})
