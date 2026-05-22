from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserQuota(Base):
    __tablename__ = "user_quotas"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    balance: Mapped[int] = mapped_column(default=0)
    total_purchased: Mapped[int] = mapped_column(default=0)
    total_consumed: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
