from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.quota_transaction import QuotaTransaction
from app.models.user_quota import UserQuota


def get_or_create_quota(db: Session, user_id: str, for_update: bool = False) -> UserQuota:
    stmt = select(UserQuota).where(UserQuota.user_id == user_id)
    if for_update:
        stmt = stmt.with_for_update()
    quota = db.scalar(stmt)
    if not quota:
        quota = UserQuota(user_id=user_id, balance=0, total_purchased=0, total_consumed=0)
        db.add(quota)
        db.flush()
    return quota


def check_balance(db: Session, user_id: str) -> int:
    quota = db.scalar(select(UserQuota).where(UserQuota.user_id == user_id))
    return quota.balance if quota else 0


def deduct(db: Session, user_id: str, amount: int = 1, reference_id: str | None = None) -> bool:
    quota = get_or_create_quota(db, user_id, for_update=True)
    if quota.balance < amount:
        return False
    quota.balance -= amount
    quota.total_consumed += amount
    tx = QuotaTransaction(
        user_id=user_id,
        type="consume",
        amount=-amount,
        balance_after=quota.balance,
        reference_id=reference_id,
    )
    db.add(tx)
    db.flush()
    return True


def refund(db: Session, user_id: str, amount: int = 1, reference_id: str | None = None, remark: str | None = None):
    quota = get_or_create_quota(db, user_id, for_update=True)
    quota.balance += amount
    quota.total_consumed = max(0, quota.total_consumed - amount)
    tx = QuotaTransaction(
        user_id=user_id,
        type="refund",
        amount=amount,
        balance_after=quota.balance,
        reference_id=reference_id,
        remark=remark,
    )
    db.add(tx)
    db.flush()


def adjust(db: Session, user_id: str, amount: int, remark: str | None = None, admin_id: str | None = None):
    quota = get_or_create_quota(db, user_id, for_update=True)
    quota.balance += amount
    if amount > 0:
        quota.total_purchased += amount
    else:
        quota.total_consumed += abs(amount)
    tx = QuotaTransaction(
        user_id=user_id,
        type="admin_adjust",
        amount=amount,
        balance_after=quota.balance,
        reference_id=None,
        remark=remark or f"admin:{admin_id}",
    )
    db.add(tx)
    db.flush()
