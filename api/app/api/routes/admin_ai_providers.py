from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.ai_provider import AiProvider
from app.services import audit_service

router = APIRouter(prefix="/admin/ai-providers", tags=["admin-ai-providers"])


class AiProviderCreate(BaseModel):
    name: str
    base_url: str
    api_key: str
    model_name: str
    timeout: int = 120
    is_active: bool = True
    priority: int = 0


class AiProviderUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None
    timeout: int | None = None
    is_active: bool | None = None
    priority: int | None = None


@router.get("")
def list_providers(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    _=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    query = select(AiProvider).order_by(AiProvider.priority.desc(), AiProvider.id.desc())
    total = db.scalar(select(func.count(AiProvider.id)))
    items = db.scalars(query.offset(offset).limit(page_size)).all()
    records = [_serialize(p) for p in items]
    return success_response({"records": records, "total": total, "current": page, "size": page_size})


@router.post("")
def create_provider(
    body: AiProviderCreate,
    request: Request,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    provider = AiProvider(**body.model_dump())
    db.add(provider)
    db.flush()
    audit_service.log_action(
        db, current_admin.get("sub", ""), "create_provider", "ai_provider",
        str(provider.id), f"name={provider.name}", request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(provider)
    return success_response(_serialize(provider))


@router.put("/{provider_id}")
def update_provider(
    provider_id: int,
    body: AiProviderUpdate,
    request: Request,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    provider = db.get(AiProvider, provider_id)
    if not provider:
        raise AppError("NOT_FOUND", "供应商不存在", 404)
    updates = body.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(provider, key, value)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "update_provider", "ai_provider",
        str(provider_id), f"fields={list(updates.keys())}", request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(provider)
    return success_response(_serialize(provider))


@router.delete("/{provider_id}")
def delete_provider(
    provider_id: int,
    request: Request,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    provider = db.get(AiProvider, provider_id)
    if not provider:
        raise AppError("NOT_FOUND", "供应商不存在", 404)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "delete_provider", "ai_provider",
        str(provider_id), f"name={provider.name}", request.client.host if request.client else None,
    )
    db.delete(provider)
    db.commit()
    return success_response(None)


@router.patch("/{provider_id}/active")
def toggle_active(
    provider_id: int,
    request: Request,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    provider = db.get(AiProvider, provider_id)
    if not provider:
        raise AppError("NOT_FOUND", "供应商不存在", 404)
    provider.is_active = not provider.is_active
    audit_service.log_action(
        db, current_admin.get("sub", ""), "toggle_provider", "ai_provider",
        str(provider_id), f"is_active={provider.is_active}", request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(provider)
    return success_response(_serialize(provider))


def _serialize(p: AiProvider) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "baseUrl": p.base_url,
        "apiKey": "****" + p.api_key[-4:] if p.api_key and len(p.api_key) > 4 else "****",
        "modelName": p.model_name,
        "timeout": p.timeout,
        "isActive": p.is_active,
        "priority": p.priority,
        "createdAt": p.created_at.isoformat() if p.created_at else None,
        "updatedAt": p.updated_at.isoformat() if p.updated_at else None,
    }
