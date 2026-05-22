import statistics
import time
from datetime import UTC, datetime, time as dt_time, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.generation_task import GenerationTask
from app.models.quota_transaction import QuotaTransaction
from app.models.template import Template


def _today_start() -> datetime:
    return datetime.combine(datetime.now(UTC).date(), dt_time.min).replace(tzinfo=None)


def _date_key(value: datetime) -> str:
    return value.strftime("%m-%d")


def _round_rate(part: int, total: int) -> float:
    return round((part / total) * 100, 2) if total else 0


def _calc_duration_percentiles(durations: list[int]) -> dict:
    if not durations:
        return {"avg": 0, "p50": 0, "p95": 0, "sampleSize": 0}
    avg = int(sum(durations) / len(durations))
    if len(durations) == 1:
        return {"avg": avg, "p50": durations[0], "p95": durations[0], "sampleSize": 1}
    sorted_d = sorted(durations)
    # statistics.quantiles 用线性插值，n=100 返回 99 个边界，索引 49=P50, 94=P95
    try:
        quantiles = statistics.quantiles(sorted_d, n=100)
        p50 = int(quantiles[49])
        p95 = int(quantiles[94])
    except statistics.StatisticsError:
        # 极端情况兜底
        p50 = sorted_d[len(sorted_d) // 2]
        p95 = sorted_d[-1]
    return {"avg": avg, "p50": p50, "p95": p95, "sampleSize": len(durations)}


def _build_zero_trend_map(today, days: int) -> dict[str, dict]:
    """构造连续日期的零值占位映射，便于后续按日期填充。"""
    return {
        _date_key(datetime.combine(today - timedelta(days=offset), dt_time.min)): {
            "date": _date_key(datetime.combine(today - timedelta(days=offset), dt_time.min)),
            "count": 0,
            "success": 0,
            "failed": 0,
            "cost": 0,
        }
        for offset in range(days - 1, -1, -1)
    }


def _build_zero_revenue_map(today, days: int) -> dict[str, dict]:
    return {
        _date_key(datetime.combine(today - timedelta(days=offset), dt_time.min)): {
            "date": _date_key(datetime.combine(today - timedelta(days=offset), dt_time.min)),
            "amount": 0,
        }
        for offset in range(days - 1, -1, -1)
    }


def _period_stats_query(db: Session, start: datetime, end: datetime) -> dict:
    """用单条 query 计算窗口内 generations/cost/failureRate。仅用于上期对比。"""
    rows = (
        db.query(GenerationTask.status, GenerationTask.cost)
        .filter(GenerationTask.created_at >= start, GenerationTask.created_at < end)
        .all()
    )
    total = len(rows)
    failed = sum(1 for s, _ in rows if s == "failed")
    cost = sum(int(c or 0) for _, c in rows)
    return {"generations": total, "cost": cost, "failureRate": _round_rate(failed, total)}


def _pct_delta(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


# ===== TTL 缓存 =====
_CACHE: dict[tuple, tuple[float, dict]] = {}
_CACHE_TTL = 5.0  # 秒


def _cache_get(key: tuple) -> dict | None:
    cached = _CACHE.get(key)
    if cached and (time.time() - cached[0]) < _CACHE_TTL:
        return cached[1]
    return None


def _cache_set(key: tuple, value: dict) -> None:
    _CACHE[key] = (time.time(), value)
    # 简单清理：保持 cache 体积可控
    if len(_CACHE) > 32:
        # 删除最早的一半条目
        sorted_keys = sorted(_CACHE.items(), key=lambda kv: kv[1][0])
        for k, _ in sorted_keys[: len(_CACHE) // 2]:
            _CACHE.pop(k, None)


def clear_dashboard_cache() -> None:
    """供测试或管理操作显式清缓存。"""
    _CACHE.clear()


def get_dashboard_metrics(db: Session, days: int = 7, compare: bool = False) -> dict:
    key = (days, compare)
    cached = _cache_get(key)
    if cached is not None:
        return cached
    result = _compute_dashboard(db, days=days, compare=compare)
    _cache_set(key, result)
    return result


def _compute_dashboard(db: Session, days: int, compare: bool) -> dict:
    today_start = _today_start()
    today = today_start.date()
    window_start = today_start - timedelta(days=days - 1)
    now = datetime.now(UTC).replace(tzinfo=None)

    # === 全局聚合（不受 days 影响）===
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
            GenerationTask.created_at >= window_start,
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

    # === 时间序列：窗口内每日生成数 ===
    rows = (
        db.query(GenerationTask.created_at, GenerationTask.status, GenerationTask.cost)
        .filter(GenerationTask.created_at >= window_start)
        .all()
    )
    trend_map = _build_zero_trend_map(today, days)
    for created_at, status, cost in rows:
        date_key = _date_key(created_at)
        if date_key not in trend_map:
            continue
        trend_map[date_key]["count"] += 1
        if status == "success":
            trend_map[date_key]["success"] += 1
        if status == "failed":
            trend_map[date_key]["failed"] += 1
        trend_map[date_key]["cost"] += int(cost or 0)
    generation_trend = list(trend_map.values())

    # === 用户画像 ===
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

    # === Top 模板（增强）：加 avgDurationMs / failureRate ===
    template_agg_rows = (
        db.query(
            Template.id,
            Template.name,
            Template.category,
            func.count(GenerationTask.id),
            func.sum(case((GenerationTask.status == "success", 1), else_=0)),
            func.sum(case((GenerationTask.status == "failed", 1), else_=0)),
        )
        .join(Template, Template.id == GenerationTask.template_id)
        .group_by(Template.id, Template.name, Template.category)
        .order_by(func.count(GenerationTask.id).desc())
        .limit(6)
        .all()
    )

    top_template_ids = [row[0] for row in template_agg_rows]
    duration_by_template: dict[int, list[int]] = {tid: [] for tid in top_template_ids}
    if top_template_ids:
        dur_rows = (
            db.query(
                GenerationTask.template_id,
                GenerationTask.started_at,
                GenerationTask.completed_at,
            )
            .filter(
                GenerationTask.template_id.in_(top_template_ids),
                GenerationTask.status == "success",
                GenerationTask.started_at.isnot(None),
                GenerationTask.completed_at.isnot(None),
            )
            .all()
        )
        for tid, started, completed in dur_rows:
            if started and completed:
                ms = int((completed - started).total_seconds() * 1000)
                if ms >= 0:
                    duration_by_template.setdefault(tid, []).append(ms)

    top_templates = [
        {
            "templateId": template_id,
            "name": name or "未命名模板",
            "category": category or "未分类",
            "count": count,
            "successRate": _round_rate(success, count),
            "failureRate": _round_rate(failed, count),
            "avgDurationMs": (
                int(sum(duration_by_template[template_id]) / len(duration_by_template[template_id]))
                if duration_by_template.get(template_id)
                else 0
            ),
        }
        for template_id, name, category, count, success, failed in template_agg_rows
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

    # === 任务耗时 avg / P50 / P95（成功任务，窗口内）===
    duration_rows = (
        db.query(GenerationTask.started_at, GenerationTask.completed_at)
        .filter(
            GenerationTask.status == "success",
            GenerationTask.started_at.isnot(None),
            GenerationTask.completed_at.isnot(None),
            GenerationTask.created_at >= window_start,
        )
        .all()
    )
    durations_ms = [
        int((completed - started).total_seconds() * 1000)
        for started, completed in duration_rows
        if started and completed and (completed - started).total_seconds() >= 0
    ]
    task_duration = _calc_duration_percentiles(durations_ms)

    # === 失败类型分布（窗口内）===
    failure_type_distribution = [
        {"type": ftype or "unknown", "count": count}
        for ftype, count in (
            db.query(GenerationTask.failure_type, func.count(GenerationTask.id))
            .filter(
                GenerationTask.status == "failed",
                GenerationTask.created_at >= window_start,
            )
            .group_by(GenerationTask.failure_type)
            .order_by(func.count(GenerationTask.id).desc())
            .all()
        )
    ]

    # === 重试效果（全量）===
    retry_total = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.retry_count > 0)
        .scalar()
        or 0
    )
    retry_succeeded = (
        db.query(func.count(GenerationTask.id))
        .filter(GenerationTask.retry_count > 0, GenerationTask.status == "success")
        .scalar()
        or 0
    )
    retry_effectiveness = {
        "attempted": retry_total,
        "succeeded": retry_succeeded,
        "rate": _round_rate(retry_succeeded, retry_total),
    }

    # === 收入趋势：窗口内按天 ===
    revenue_rows = (
        db.query(QuotaTransaction.created_at, QuotaTransaction.amount)
        .filter(
            QuotaTransaction.type == "recharge",
            QuotaTransaction.created_at >= window_start,
        )
        .all()
    )
    revenue_map = _build_zero_revenue_map(today, days)
    for created_at, amount in revenue_rows:
        date_key = _date_key(created_at)
        if date_key in revenue_map:
            revenue_map[date_key]["amount"] += int(amount or 0)
    revenue_trend = list(revenue_map.values())

    # === 配额消费率 ===
    consume_count = (
        db.query(func.count(QuotaTransaction.id))
        .filter(
            QuotaTransaction.type == "consume",
            QuotaTransaction.created_at >= window_start,
        )
        .scalar()
        or 0
    )
    consumption_per_user = (
        round(consume_count / active_user_count, 2) if active_user_count else 0
    )

    # === 24 小时内 timeout 任务数 ===
    yesterday = now - timedelta(hours=24)
    recent_timeouts_24h = (
        db.query(func.count(GenerationTask.id))
        .filter(
            GenerationTask.failure_type == "timeout",
            GenerationTask.created_at >= yesterday,
        )
        .scalar()
        or 0
    )

    # === 周同比：本期数据从已计算的 trend 复用，仅上期单独 query ===
    period_comparison = None
    if compare:
        current_period = {
            "generations": sum(t["count"] for t in generation_trend),
            "cost": sum(t["cost"] for t in generation_trend),
            "failureRate": _round_rate(
                sum(t["failed"] for t in generation_trend),
                sum(t["count"] for t in generation_trend),
            ),
        }
        prev_start = window_start - timedelta(days=days)
        prev_period = _period_stats_query(db, prev_start, window_start)
        period_comparison = {
            "current": current_period,
            "previous": prev_period,
            "generationsPct": _pct_delta(current_period["generations"], prev_period["generations"]),
            "costPct": _pct_delta(current_period["cost"], prev_period["cost"]),
            "failureRateDelta": round(
                current_period["failureRate"] - prev_period["failureRate"], 2
            ),
        }

    return {
        # 全局
        "userCount": user_count,
        "templateCount": template_count,
        "generationCount": generation_count,
        "todayGenerationCount": today_generation_count,
        "todayRevenue": 0,
        "todayCost": int(today_cost),
        "failureRate": failure_rate,
        "successRate": success_rate,
        "activeUserCount": active_user_count,
        # 分布
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
        # Track A 指标
        "taskDuration": task_duration,
        "failureTypeDistribution": failure_type_distribution,
        "retryEffectiveness": retry_effectiveness,
        "revenueTrend": revenue_trend,
        "consumptionPerUser": consumption_per_user,
        "recentTimeouts24h": recent_timeouts_24h,
        "periodComparison": period_comparison,
        "days": days,
    }
