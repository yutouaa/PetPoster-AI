from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.template import Template
from app.schemas.template import TemplateCreate, TemplateSortItem, TemplateUpdate


def _escape_like(value: str) -> str:
    value = value.replace("\\", "\\\\")
    value = value.replace("%", "\\%")
    value = value.replace("_", "\\_")
    return value


def get_templates(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[Template], int]:
    query = db.query(Template)

    if keyword:
        escaped = _escape_like(keyword)
        query = query.filter(
            or_(
                Template.name.ilike(f"%{escaped}%"),
                Template.description.ilike(f"%{escaped}%"),
            )
        )
    if category:
        query = query.filter(Template.category == category)
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)

    total = query.count()
    items = (
        query.order_by(Template.sort_order.asc(), Template.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_template_by_id(db: Session, template_id: int) -> Template | None:
    return db.query(Template).filter(Template.id == template_id).first()


def create_template(db: Session, data: TemplateCreate) -> Template:
    template = Template(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def update_template(db: Session, template: Template, data: TemplateUpdate) -> Template:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template: Template) -> None:
    db.delete(template)
    db.commit()


def toggle_template_status(db: Session, template: Template, is_active: bool) -> Template:
    template.is_active = is_active
    db.commit()
    db.refresh(template)
    return template


def batch_sort_templates(db: Session, items: list[TemplateSortItem]) -> None:
    for item in items:
        db.query(Template).filter(Template.id == item.id).update({"sort_order": item.sort_order})
    db.commit()
