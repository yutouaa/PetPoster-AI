from collections.abc import Generator

from fastapi import Header
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_admin_token
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise AppError("UNAUTHORIZED", "请先登录", 401)

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AppError("INVALID_AUTH_HEADER", "登录凭证格式不正确", 401)

    return decode_admin_token(token)
