import time
import logging
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.password import verify_password
from app.core.responses import success_response
from app.core.security import create_admin_token, decode_admin_token
from app.models.admin_user import AdminUser
from app.services.dashboard_service import get_dashboard_metrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# 简易速率限制：每个 IP 60 秒内最多 5 次登录尝试
_login_attempts: dict[str, list[float]] = defaultdict(list)
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 60
_last_login_cleanup: float = 0


def _check_rate_limit(client_ip: str) -> None:
    global _last_login_cleanup
    now = time.time()
    attempts = _login_attempts[client_ip]
    _login_attempts[client_ip] = [t for t in attempts if now - t < _WINDOW_SECONDS]
    if len(_login_attempts[client_ip]) >= _MAX_ATTEMPTS:
        raise AppError("TOO_MANY_ATTEMPTS", "登录尝试过于频繁，请稍后再试", 429)
    _login_attempts[client_ip].append(now)

    if now - _last_login_cleanup > _WINDOW_SECONDS * 2:
        _last_login_cleanup = now
        stale = [k for k, v in _login_attempts.items() if not v or v[-1] < now - _WINDOW_SECONDS]
        for k in stale:
            del _login_attempts[k]


class AdminLoginRequest(BaseModel):
    userName: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=72)


class RefreshTokenRequest(BaseModel):
    refreshToken: str


@router.post("/auth/login")
def admin_login(payload: AdminLoginRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    user = db.query(AdminUser).filter_by(username=payload.userName).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        logger.warning("admin.auth.login_failed username=%s ip=%s", payload.userName, client_ip)
        raise AppError("INVALID_CREDENTIALS", "账号或密码不正确", 401)

    if not user.is_active:
        logger.warning("admin.auth.disabled username=%s ip=%s", payload.userName, client_ip)
        raise AppError("ACCOUNT_DISABLED", "账号已被禁用，请联系管理员", 403)

    roles = [r.strip() for r in user.roles.split(",") if r.strip()]
    token = create_admin_token(user.username, roles)
    logger.info("admin.auth.login_success username=%s ip=%s", user.username, client_ip)
    return success_response({
        "token": token,
        "refreshToken": token
    }, "登录成功")


@router.post("/auth/refresh")
def admin_refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> dict:
    claims = decode_admin_token(payload.refreshToken)
    username = claims.get("sub")
    if not username:
        raise AppError("INVALID_TOKEN", "无效的刷新令牌", 401)

    user = db.query(AdminUser).filter_by(username=username).first()
    if not user or not user.is_active:
        raise AppError("INVALID_TOKEN", "用户不存在或已被禁用", 401)

    roles = [r.strip() for r in user.roles.split(",") if r.strip()]
    token = create_admin_token(user.username, roles)
    return success_response({
        "token": token,
        "refreshToken": token
    })


@router.get("/me")
def admin_me(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    user = db.query(AdminUser).filter_by(username=current_admin.get("sub")).first()
    if not user:
        raise AppError("USER_NOT_FOUND", "用户不存在", 404)

    roles = [r.strip() for r in user.roles.split(",") if r.strip()]
    return success_response({
        "userId": str(user.id),
        "userName": user.username,
        "nickName": user.nickname,
        "roles": roles,
        "buttons": ["*"]
    })


@router.get("/dashboard")
def admin_dashboard(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    logger.info("admin.dashboard admin=%s", current_admin.get("sub"))
    return success_response(get_dashboard_metrics(db))
