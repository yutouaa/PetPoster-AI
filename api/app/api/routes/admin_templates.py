import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
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
from app.services import audit_service, template_service


class TemplateImportRequest(BaseModel):
    templates: list[dict]


class TemplateBatchArchiveRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=200)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/templates", tags=["admin-templates"])


def _template_to_dict(t) -> dict:
    usage = t.usage_count or 0
    success = t.success_count or 0
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
        "deletedAt": t.deleted_at.isoformat() if t.deleted_at else None,
        "usageCount": usage,
        "successCount": success,
        "successRate": round(success / usage * 100, 2) if usage else 0,
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
    includeArchived: bool = Query(default=False),
) -> dict:
    items, total = template_service.get_templates(
        db,
        page=page,
        page_size=pageSize,
        keyword=keyword,
        category=category,
        is_active=isActive,
        include_archived=includeArchived,
    )
    return success_response({
        "records": [_template_to_dict(t) for t in items],
        "current": page,
        "size": pageSize,
        "total": total,
    })


@router.get("/export")
def export_templates(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    ids: str | None = Query(default=None, description="逗号分隔 id 列表，不传则全量导出"),
    limit: int = Query(default=500, ge=1, le=5000),
) -> dict:
    id_list: list[int] | None = None
    if ids:
        try:
            id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
        except ValueError as exc:
            raise AppError("INVALID_PARAM", "ids 必须为逗号分隔的整数", 400) from exc
    items = template_service.export_templates(db, id_list, limit=limit)
    logger.info("admin_templates.export admin=%s count=%s limit=%s", current_admin.get("sub"), len(items), limit)
    return success_response({"templates": items, "count": len(items)})


@router.post("/import")
def import_templates(
    body: TemplateImportRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    if not body.templates:
        raise AppError("INVALID_PARAM", "导入数据不能为空", 400)
    result = template_service.import_templates(db, body.templates)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "import_templates", "template",
        None,
        f"created={result['created']}, updated={result['updated']}, skipped={result['skipped']}",
        request.client.host if request.client else None,
    )
    db.commit()
    logger.info("admin_templates.import admin=%s result=%s", current_admin.get("sub"), result)
    return success_response(result, "导入完成")


@router.post("/batch-archive")
def batch_archive(
    body: TemplateBatchArchiveRequest,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    result = template_service.batch_archive_templates(db, body.ids)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "batch_archive_templates", "template",
        None,
        f"ids={body.ids[:20]}, result={result}",
        request.client.host if request.client else None,
    )
    db.commit()
    logger.info(
        "admin_templates.batch_archive admin=%s count=%s result=%s",
        current_admin.get("sub"), len(body.ids), result,
    )
    return success_response(result, "批量归档完成")


@router.post("")
def create_template(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    data: TemplateCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.create_template(db, data)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "create_template", "template",
        str(template.id), f"name={template.name}", request.client.host if request.client else None,
    )
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
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    template = template_service.update_template(db, template, data)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "update_template", "template",
        str(template_id), None, request.client.host if request.client else None,
    )
    logger.info("admin_templates.update admin=%s template_id=%s", current_admin.get("sub"), template_id)
    return success_response(_template_to_dict(template), "更新成功")


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    template_service.delete_template(db, template)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "delete_template", "template",
        str(template_id), None, request.client.host if request.client else None,
    )
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


@router.post("/{template_id}/duplicate")
def duplicate_template(
    template_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    clone = template_service.duplicate_template(db, template)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "duplicate_template", "template",
        str(clone.id), f"source={template_id}", request.client.host if request.client else None,
    )
    db.commit()
    logger.info("admin_templates.duplicate admin=%s source=%s new=%s", current_admin.get("sub"), template_id, clone.id)
    return success_response(_template_to_dict(clone), "复制成功")


@router.post("/{template_id}/archive")
def archive_template(
    template_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    if template.deleted_at is not None:
        raise AppError("ALREADY_ARCHIVED", "模板已归档", 400)
    template_service.delete_template(db, template)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "archive_template", "template",
        str(template_id), None, request.client.host if request.client else None,
    )
    db.commit()
    logger.info("admin_templates.archive admin=%s template_id=%s", current_admin.get("sub"), template_id)
    return success_response(message="归档成功")


@router.post("/{template_id}/restore")
def restore_template(
    template_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    if template.deleted_at is None:
        raise AppError("NOT_ARCHIVED", "模板未归档", 400)
    template = template_service.restore_template(db, template)
    audit_service.log_action(
        db, current_admin.get("sub", ""), "restore_template", "template",
        str(template_id), None, request.client.host if request.client else None,
    )
    db.commit()
    logger.info("admin_templates.restore admin=%s template_id=%s", current_admin.get("sub"), template_id)
    return success_response(_template_to_dict(template), "恢复成功")


@router.get("/{template_id}/stats")
def template_stats(
    template_id: int,
    _: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    template = template_service.get_template_by_id(db, template_id)
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    return success_response(template_service.get_template_stats(db, template))
