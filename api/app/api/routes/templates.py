import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.template import Template

router = APIRouter(prefix="/templates", tags=["templates"])


def _public_template_to_dict(t: Template) -> dict:
    config = {}
    try:
        config = json.loads(t.config) if t.config else {}
    except (json.JSONDecodeError, TypeError):
        pass

    return {
        "id": t.id,
        "name": t.name,
        "category": t.category,
        "description": t.description,
        "coverUrl": t.cover_url,
        "previewUrl": t.preview_url,
        "config": config,
        "sortOrder": t.sort_order,
    }


@router.get("")
def list_public_templates(db: Session = Depends(get_db)) -> dict:
    templates = (
        db.query(Template)
        .filter(Template.is_active == True)  # noqa: E712
        .order_by(Template.sort_order.asc(), Template.created_at.desc())
        .all()
    )
    return success_response([_public_template_to_dict(t) for t in templates])


@router.get("/{template_id}")
def get_public_template(template_id: int, db: Session = Depends(get_db)) -> dict:
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.is_active == True)  # noqa: E712
        .first()
    )
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)
    return success_response(_public_template_to_dict(template))
