from datetime import UTC, datetime, time
from datetime import timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.generation_task import GenerationTask
from app.models.template import Template


def _today_start() -> datetime:
    return datetime.combine(datetime.now(UTC).date(), time.min).replace(tzinfo=None)


def _date_key(value: datetime) -> str:
    return value.strftime("%m-%d")


def _round_rate(part: int, total: int) -> float:
    return round((part / total) * 100, 2) if total else 0


def get_dashboard_metrics(db: Session) -> dict:
    today_start = _today_start()
    today = today_start.date()
    trend_start = today_start - timedelta(days=6)

    user_count = (
        db.query(func.count(func.distinct(GenerationTask.user_id)))
        .filter(GenerationTask.user_id.isnot(None), GenerationTask.user_id != "")
        .scalar()
        or 0
    )
    template_count = db.query(func.count(Template.id)).scalar() or 0
    generation_count = db.query(func.count(GenerationTask.id)).scalar() or 0
    success_count = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.status == "success")
        .scalar()
        or 0
    )
    failed_count = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.status == "failed")
        .scalar()
        or 0
    )
    today_generation_count = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.created_at >= today_start)
        .scalar()
        or 0
    )
    today_cost = (
        db.query(func.coalesce(func.sum(GenerationTask.cost), 0))
        .filter(GenerationTask.created_at >= today_start)
        .scalar()
        or 0
    )
    active_user_count = (
        db.query(func.count(func.distinct(GenerationTask.user_id)))
        .filter(
            GenerationTask.user_id.isnot(None),
            GenerationTask.user_id != "",
            GenerationTask.created_at >= trend_start,
        )
        .scalar()
        or 0
    )
    failure_rate = _round_rate(failed_count, generation_count)
    success_rate = _round_rate(success_count, generation_count)

    status_distribution = [
        {"name": status or "unknown", "value": count}
        for status, count in (
            db.query(GenerationTask.status, func.count(GenerationTask.id))
            .group_by(GenerationTask.status)
            .order_by(func.count(GenerationTask.id).desc())
            .all()
        )
    ]

    style_distribution = [
        {"name": name or "未命名模板", "value": count}
        for name, count in (
            db.query(Template.name, func.count(GenerationTask.id))
            .join(Template, Template.id == GenerationTask.template_id)
            .group_by(Template.id, Template.name)
            .order_by(func.count(GenerationTask.id).desc())
            .limit(8)
            .all()
        )
    ]

    rows = (
        db.query(GenerationTask.created_at, GenerationTask.status, GenerationTask.cost)
        .filter(GenerationTask.created_at >= trend_start)
        .all()
    )
    trend_map = {
        _date_key(datetime.combine(today - timedelta(days=offset), time.min)): {
            "date": _date_key(datetime.combine(today - timedelta(days=offset), time.min)),
            "count": 0,
            "success": 0,
            "failed": 0,
            "cost": 0,
        }
        for offset in range(6, -1, -1)
    }
    for created_at, status, cost in rows:
        key = _date_key(created_at)
        if key not in trend_map:
            continue
        trend_map[key]["count"] += 1
        if status == "success":
            trend_map[key]["success"] += 1
        if status == "failed":
            trend_map[key]["failed"] += 1
        trend_map[key]["cost"] += int(cost or 0)
    generation_trend = list(trend_map.values())

    user_rows = (
        db.query(GenerationTask.user_id, func.count(GenerationTask.id))
        .filter(GenerationTask.user_id.isnot(None), GenerationTask.user_id != "")
        .group_by(GenerationTask.user_id)
        .all()
    )
    repeat_user_count = sum(1 for _, count in user_rows if count > 1)
    new_user_count = sum(1 for _, count in user_rows if count == 1)
    anonymous_count = (
        db.query(func.count(GenerationTask.id))
        .filter((GenerationTask.user_id.is_(None)) | (GenerationTask.user_id == ""))
        .scalar()
        or 0
    )
    high_value_user_count = sum(1 for _, count in user_rows if count >= 5)

    top_templates = [
        {
            "templateId": template_id,
            "name": name or "未命名模板",
            "category": category or "未分类",
            "count": count,
            "successRate": _round_rate(success, count),
        }
        for template_id, name, category, count, success in (
            db.query(
                Template.id,
                Template.name,
                Template.category,
                func.count(GenerationTask.id),
                func.sum(case((GenerationTask.status == "success", 1), else_=0)),
            )
            .join(Template, Template.id == GenerationTask.template_id)
            .group_by(Template.id, Template.name, Template.category)
            .order_by(func.count(GenerationTask.id).desc())
            .limit(6)
            .all()
        )
    ]

    recent_tasks = [
        {
            "id": task_id,
            "templateName": template_name or "未命名模板",
            "status": status,
            "cost": int(cost or 0),
            "createdAt": created_at.isoformat() if created_at else "",
        }
        for task_id, template_name, status, cost, created_at in (
            db.query(
                GenerationTask.id,
                Template.name,
                GenerationTask.status,
                GenerationTask.cost,
                GenerationTask.created_at,
            )
            .join(Template, Template.id == GenerationTask.template_id)
            .order_by(GenerationTask.created_at.desc())
            .limit(8)
            .all()
        )
    ]

    return {
        "userCount": user_count,
        "templateCount": template_count,
        "generationCount": generation_count,
        "todayGenerationCount": today_generation_count,
        "todayRevenue": 0,
        "todayCost": int(today_cost),
        "failureRate": failure_rate,
        "successRate": success_rate,
        "activeUserCount": active_user_count,
        "styleDistribution": style_distribution,
        "statusDistribution": status_distribution,
        "generationTrend": generation_trend,
        "userPortrait": {
            "activeUserCount": active_user_count,
            "newUserCount": new_user_count,
            "repeatUserCount": repeat_user_count,
            "anonymousCount": anonymous_count,
            "highValueUserCount": high_value_user_count,
        },
        "topTemplates": top_templates,
        "recentTasks": recent_tasks,
    }
