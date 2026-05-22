from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.quota_transaction import QuotaTransaction
from app.models.user_quota import UserQuota
from app.services import audit_service, quota_service

router = APIRouter(prefix="/admin/quota", tags=["admin-quota"])


class QuotaAdjustRequest(BaseModel):
    user_id: str
    amount: int
    remark: str = ""

    @field_validator("user_id")
    @classmethod
    def user_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id must not be empty")
        return v


@router.get("/users")
def list_quota_users(
    _=Depends(get_current_admin),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    search: str = "",
    db: Session = Depends(get_db),
):
    base = select(UserQuota)
    if search:
        base = base.where(UserQuota.user_id.contains(search))
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    items = db.scalars(
        base.order_by(UserQuota.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    records = [
        {
            "id": q.id,
            "userId": q.user_id,
            "balance": q.balance,
            "totalPurchased": q.total_purchased,
            "totalConsumed": q.total_consumed,
            "createdAt": q.created_at.isoformat() if q.created_at else None,
            "updatedAt": q.updated_at.isoformat() if q.updated_at else None,
        }
        for q in items
    ]
    return success_response({"records": records, "total": total, "current": page, "size": page_size})


@router.post("/adjust")
def adjust_quota(
    body: QuotaAdjustRequest,
    request: Request,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if body.amount == 0:
        raise AppError("INVALID_PARAM", "调整数量不能为 0", 400)
    admin_id = current_admin.get("sub", "")
    quota_service.adjust(db, body.user_id, body.amount, body.remark, admin_id=admin_id)
    audit_service.log_action(
        db, admin_id, "adjust_quota", "user_quota",
        body.user_id, f"amount={body.amount}, remark={body.remark}",
        request.client.host if request.client else None,
    )
    db.commit()
    quota = db.scalar(select(UserQuota).where(UserQuota.user_id == body.user_id))
    return success_response({
        "userId": body.user_id,
        "balance": quota.balance if quota else 0,
        "totalPurchased": quota.total_purchased if quota else 0,
    })


@router.get("/transactions")
def list_all_transactions(
    _=Depends(get_current_admin),
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    user_id: str = Query("", alias="userId"),
    tx_type: str = Query("", alias="type"),
    db: Session = Depends(get_db),
):
    base = select(QuotaTransaction)
    if user_id:
        base = base.where(QuotaTransaction.user_id == user_id)
    if tx_type:
        base = base.where(QuotaTransaction.type == tx_type)
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    items = db.scalars(
        base.order_by(QuotaTransaction.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    records = [
        {
            "id": t.id,
            "userId": t.user_id,
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
