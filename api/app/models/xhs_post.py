from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class XhsPost(Base):
    __tablename__ = "xhs_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    image_urls: Mapped[str] = mapped_column(Text, default="[]")
    tags: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    scheduled_at: Mapped[datetime | None] = mapped_column(nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    platform_post_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    llm_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
