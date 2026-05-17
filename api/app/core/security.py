from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.errors import AppError


ALGORITHM = "HS256"


def create_admin_token(subject: str, roles: list[str]) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.admin_jwt_expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "exp": expire
    }
    return jwt.encode(payload, settings.admin_jwt_secret, algorithm=ALGORITHM)


def decode_admin_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.admin_jwt_secret, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AppError("INVALID_TOKEN", "登录状态无效，请重新登录", 401) from exc
