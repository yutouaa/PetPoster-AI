from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 不加 unique 约束：与软删除（deleted_at）冲突——归档后无法创建同名新模板。
    # name 唯一性由 app 层维护（duplicate_template / create / import 显式查重）。
    name: Mapped[str] = mapped_column(String(100), index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    cover_url: Mapped[str] = mapped_column(String(500), default="")
    preview_url: Mapped[str] = mapped_column(String(500), default="")
    prompt_template: Mapped[str] = mapped_column(Text, default="")
    negative_prompt: Mapped[str] = mapped_column(Text, default="")
    config: Mapped[str] = mapped_column(Text, default="{}")
    sort_order: Mapped[int] = mapped_column(default=0, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    usage_count: Mapped[int] = mapped_column(default=0)
    success_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
