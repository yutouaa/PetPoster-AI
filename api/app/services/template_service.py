from datetime import datetime, timedelta, timezone

from pydantic import ValidationError
from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session

from app.models.generation_task import GenerationTask
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
    include_archived: bool = False,
) -> tuple[list[Template], int]:
    query = db.query(Template)

    if not include_archived:
        query = query.filter(Template.deleted_at.is_(None))

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


def get_template_by_id(db: Session, template_id: int, include_archived: bool = True) -> Template | None:
    query = db.query(Template).filter(Template.id == template_id)
    if not include_archived:
        query = query.filter(Template.deleted_at.is_(None))
    return query.first()


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
    """软删除：保留记录但从默认列表中隐藏，维持历史 generation_task 关联。"""
    template.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
    template.is_active = False
    db.commit()


def batch_archive_templates(db: Session, ids: list[int]) -> dict:
    """批量软删除模板。已归档的进 skipped；不存在的 id 自动忽略。"""
    archived = 0
    skipped = 0
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    templates = db.query(Template).filter(Template.id.in_(ids)).all()
    for t in templates:
        if t.deleted_at is not None:
            skipped += 1
            continue
        t.deleted_at = now
        t.is_active = False
        archived += 1
    db.commit()
    return {"archived": archived, "skipped": skipped}


def restore_template(db: Session, template: Template) -> Template:
    template.deleted_at = None
    db.commit()
    db.refresh(template)
    return template


def purge_template(db: Session, template: Template) -> None:
    """物理删除（仅用于清理脏数据，不通过 API 暴露）。"""
    db.delete(template)
    db.commit()


def _next_duplicate_name(db: Session, base_name: str) -> str:
    """生成不冲突的副本名：'X (副本)'，已存在则 'X (副本 2)'、'X (副本 3)' ..."""
    candidate = f"{base_name} (副本)"
    counter = 2
    while db.query(Template.id).filter(Template.name == candidate).first():
        candidate = f"{base_name} (副本 {counter})"
        counter += 1
        if counter > 999:
            # 极端兜底，避免死循环
            candidate = f"{base_name} (副本 {datetime.now(timezone.utc).strftime('%H%M%S')})"
            break
    return candidate


def duplicate_template(db: Session, template: Template) -> Template:
    """复制模板为 inactive 副本，自动递增编号避免重名。"""
    clone = Template(
        name=_next_duplicate_name(db, template.name),
        category=template.category,
        description=template.description,
        cover_url=template.cover_url,
        preview_url=template.preview_url,
        prompt_template=template.prompt_template,
        negative_prompt=template.negative_prompt,
        config=template.config,
        sort_order=template.sort_order,
        is_active=False,
        usage_count=0,
        success_count=0,
    )
    db.add(clone)
    db.commit()
    db.refresh(clone)
    return clone


def toggle_template_status(db: Session, template: Template, is_active: bool) -> Template:
    template.is_active = is_active
    db.commit()
    db.refresh(template)
    return template


def batch_sort_templates(db: Session, items: list[TemplateSortItem]) -> None:
    for item in items:
        db.query(Template).filter(Template.id == item.id).update({"sort_order": item.sort_order})
    db.commit()


EXPORT_FIELDS = (
    "name", "category", "description", "cover_url", "preview_url",
    "prompt_template", "negative_prompt", "config", "sort_order", "is_active",
)


def export_templates(db: Session, ids: list[int] | None = None, limit: int = 500) -> list[dict]:
    query = db.query(Template).filter(Template.deleted_at.is_(None))
    if ids:
        query = query.filter(Template.id.in_(ids))
    items = query.order_by(Template.sort_order.asc(), Template.id.asc()).limit(limit).all()
    return [{field: getattr(t, field) for field in EXPORT_FIELDS} for t in items]


def import_templates(db: Session, payload: list[dict]) -> dict:
    """按 name 字段 upsert 模板。每条用 TemplateCreate schema 校验，非法的进 skipped。"""
    created = 0
    updated = 0
    skipped = 0
    for item in payload:
        if not isinstance(item, dict):
            skipped += 1
            continue
        # 用 TemplateCreate 校验字段（含 config JSON、长度、ge=0 等）
        try:
            validated = TemplateCreate(**{k: v for k, v in item.items() if k in EXPORT_FIELDS}).model_dump()
        except (ValidationError, TypeError, ValueError):
            skipped += 1
            continue
        name = validated["name"]
        existing = db.query(Template).filter(Template.name == name, Template.deleted_at.is_(None)).first()
        if existing:
            for field in EXPORT_FIELDS:
                if field == "name":
                    continue
                setattr(existing, field, validated[field])
            updated += 1
        else:
            db.add(Template(**validated))
            created += 1
    db.commit()
    return {"created": created, "updated": updated, "skipped": skipped}


def get_template_stats(db: Session, template: Template) -> dict:
    """计算单个模板的统计：用量、成功率、平均耗时、最近 30 天每日用量。"""
    failed = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.template_id == template.id, GenerationTask.status == "failed")
        .scalar()
        or 0
    )

    duration_rows = (
        db.query(GenerationTask.started_at, GenerationTask.completed_at)
        .filter(
            GenerationTask.template_id == template.id,
            GenerationTask.status == "success",
            GenerationTask.started_at.isnot(None),
            GenerationTask.completed_at.isnot(None),
        )
        .all()
    )
    durations = [
        int((c - s).total_seconds() * 1000)
        for s, c in duration_rows
        if s and c and (c - s).total_seconds() >= 0
    ]
    avg_duration_ms = int(sum(durations) / len(durations)) if durations else 0

    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
    daily_rows = (
        db.query(
            func.strftime("%Y-%m-%d", GenerationTask.created_at).label("day"),
            func.count(GenerationTask.id),
            func.sum(case((GenerationTask.status == "success", 1), else_=0)),
        )
        .filter(GenerationTask.template_id == template.id, GenerationTask.created_at >= cutoff)
        .group_by("day")
        .order_by("day")
        .all()
    )
    recent_30d = [
        {"date": day, "count": int(count or 0), "success": int(succ or 0)}
        for day, count, succ in daily_rows
    ]

    return {
        "usageCount": template.usage_count,
        "successCount": template.success_count,
        "failedCount": failed,
        "successRate": round(template.success_count / template.usage_count * 100, 2) if template.usage_count else 0,
        "avgDurationMs": avg_duration_ms,
        "recent30d": recent_30d,
    }
