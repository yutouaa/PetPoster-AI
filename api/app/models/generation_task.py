from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    original_image_urls: Mapped[str] = mapped_column(Text, default="[]")
    result_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, default="")
    cost: Mapped[int] = mapped_column(default=0)
    failure_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
