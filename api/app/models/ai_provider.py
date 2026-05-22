from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AiProvider(Base):
    __tablename__ = "ai_providers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    base_url: Mapped[str] = mapped_column(String(500))
    api_key: Mapped[str] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(200))
    timeout: Mapped[int] = mapped_column(default=120)
    is_active: Mapped[bool] = mapped_column(default=True)
    priority: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
