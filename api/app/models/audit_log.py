from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_id: Mapped[str] = mapped_column(String(100), index=True)
    action: Mapped[str] = mapped_column(String(50))  # e.g. create_template, delete_provider
    resource_type: Mapped[str] = mapped_column(String(50))  # e.g. template, ai_provider
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
