import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.schemas.template import (
    TemplateCreate,
    TemplateSortUpdate,
    TemplateStatusUpdate,
    TemplateUpdate,
)
from app.services import template_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/templates", tags=["admin-templates"])


def _template_to_dict(t) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "category": t.category,
        "description": t.description,
        "coverUrl": t.cover_url,
        "previewUrl": t.preview_url,
        "promptTemplate": t.prompt_template,
        "negativePrompt": t.negative_prompt,
        "config": t.config,
        "sortOrder": t.sort_order,
        "isActive": t.is_active,
        "createdAt": t.created_at.isoformat() if t.created_at else None,
        "updatedAt": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.get("")
def list_templates(
    _: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    keyword: str | None = Query(default=None),
    category: str | None = Query(default=None),
    isActive: bool | None = Query(default=None),
) -> dict:
    items, total = template_service.get_templates(
        db, page=page, page_size=pageSize, keyword=keyword, category=category, is_active=isActive
    )
    return success_response({
        "records": [_template_to_dict(t) for t in items],
        "current": page,
        "size": pageSize,
        "total": total,
    })


@router.post("")
def create_template(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    data: TemplateCreate,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.create_template(db, data)
    logger.info("admin_templates.create admin=%s template_id=%s name=%s", current_admin.get("sub"), template.id, template.name)
    return success_response(_template_to_dict(template), "创建成功")


@router.get("/{template_id}")
def get_template(
    template_id: int,
    _: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    return success_response(_template_to_dict(template))


@router.put("/{template_id}")
def update_template(
    template_id: int,
    data: TemplateUpdate,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    template = template_service.update_template(db, template, data)
    logger.info("admin_templates.update admin=%s template_id=%s", current_admin.get("sub"), template_id)
    return success_response(_template_to_dict(template), "更新成功")


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    template_service.delete_template(db, template)
    logger.info("admin_templates.delete admin=%s template_id=%s", current_admin.get("sub"), template_id)
    return success_response(message="删除成功")


@router.patch("/{template_id}/status")
def toggle_status(
    template_id: int,
    data: TemplateStatusUpdate,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    template = template_service.toggle_template_status(db, template, data.is_active)
    logger.info(
        "admin_templates.status admin=%s template_id=%s is_active=%s",
        current_admin.get("sub"),
        template_id,
        data.is_active,
    )
    return success_response(_template_to_dict(template), "状态更新成功")


@router.patch("/sort")
def batch_sort(
    data: TemplateSortUpdate,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template_service.batch_sort_templates(db, data.items)
    logger.info("admin_templates.sort admin=%s count=%s", current_admin.get("sub"), len(data.items))
    return success_response(message="排序更新成功")
