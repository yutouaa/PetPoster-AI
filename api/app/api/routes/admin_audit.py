from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.responses import success_response
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit"], dependencies=[Depends(get_current_admin)])


@router.get("")
def list_audit_logs(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    action: str = Query("", alias="action"),
    resource_type: str = Query("", alias="resourceType"),
    admin_id: str = Query("", alias="adminId"),
    db: Session = Depends(get_db),
):
    base = select(AuditLog)
    if action:
        base = base.where(AuditLog.action == action)
    if resource_type:
        base = base.where(AuditLog.resource_type == resource_type)
    if admin_id:
        base = base.where(AuditLog.admin_id == admin_id)
    total = db.scalar(select(func.count()).select_from(base.subquery()))
    items = db.scalars(
        base.order_by(AuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    records = [
        {
            "id": log.id,
            "adminId": log.admin_id,
            "action": log.action,
            "resourceType": log.resource_type,
            "resourceId": log.resource_id,
            "detail": log.detail,
            "ipAddress": log.ip_address,
            "createdAt": log.created_at.isoformat() if log.created_at else None,
        }
        for log in items
    ]
    return success_response({"records": records, "total": total, "current": page, "size": page_size})
