from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QuotaTransaction(Base):
    __tablename__ = "quota_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    type: Mapped[str] = mapped_column(String(20))  # recharge, consume, refund, admin_adjust
    amount: Mapped[int] = mapped_column()  # positive=add, negative=deduct
    balance_after: Mapped[int] = mapped_column()
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
