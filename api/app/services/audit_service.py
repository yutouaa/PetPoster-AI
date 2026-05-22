import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    admin_id: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
):
    """记录管理员操作审计。失败时记录 warning，不阻塞业务事务。"""
    try:
        entry = AuditLog(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail[:5000] if detail else None,
            ip_address=ip_address,
        )
        db.add(entry)
        db.flush()
    except Exception:
        logger.exception(
            "[审计] 写入失败 admin=%s action=%s resource=%s/%s",
            admin_id, action, resource_type, resource_id,
        )
