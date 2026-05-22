from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.responses import success_response
from app.models.generation_task import GenerationTask
from app.services import audit_service

router = APIRouter(prefix="/admin/failed-tasks", tags=["admin-failed-tasks"])


class BatchRetryRequest(BaseModel):
    task_ids: list[int] = Field(min_length=1, max_length=500)


@router.get("/summary")
def failed_tasks_summary(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    _=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    subq = (
        select(
            GenerationTask.user_id,
            func.count().label("failed_count"),
            func.max(GenerationTask.created_at).label("last_failed_at"),
        )
        .where(GenerationTask.status == "failed")
        .group_by(GenerationTask.user_id)
        .subquery()
    )

    total = db.scalar(select(func.count()).select_from(subq))

    rows = (
        db.execute(
            select(subq).order_by(subq.c.failed_count.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        .all()
    )

    records = []
    user_ids = [row.user_id for row in rows]

    # Batch: total tasks per user
    total_tasks_rows = db.execute(
        select(GenerationTask.user_id, func.count().label("cnt"))
        .where(GenerationTask.user_id.in_(user_ids))
        .group_by(GenerationTask.user_id)
    ).all()
    total_tasks_map = {r.user_id: r.cnt for r in total_tasks_rows}

    # Batch: recent failed tasks per user (top 10 each)
    failed_tasks_all = db.scalars(
        select(GenerationTask)
        .where(GenerationTask.user_id.in_(user_ids), GenerationTask.status == "failed")
        .order_by(GenerationTask.user_id, GenerationTask.created_at.desc())
    ).all()
    from collections import defaultdict
    failed_tasks_map: dict[str | None, list] = defaultdict(list)
    for t in failed_tasks_all:
        if len(failed_tasks_map[t.user_id]) < 10:
            failed_tasks_map[t.user_id].append(t)

    for row in rows:
        user_id = row.user_id
        records.append({
            "userId": user_id or "anonymous",
            "failedCount": row.failed_count,
            "lastFailedAt": row.last_failed_at.isoformat() if row.last_failed_at else None,
            "totalTasks": total_tasks_map.get(user_id, 0),
            "tasks": [
                {
                    "id": t.id,
                    "templateId": t.template_id,
                    "status": t.status,
                    "errorMessage": t.error_message,
                    "retryCount": t.retry_count,
                    "createdAt": t.created_at.isoformat() if t.created_at else None,
                }
                for t in failed_tasks_map.get(user_id, [])
            ],
        })

    return success_response({"records": records, "total": total, "current": page, "size": page_size})


@router.post("/batch-retry")
def batch_retry(body: BatchRetryRequest, request: Request, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    tasks = db.scalars(
        select(GenerationTask).where(
            GenerationTask.id.in_(body.task_ids),
            GenerationTask.status == "failed",
        )
    ).all()

    retried = 0
    for task in tasks:
        task.status = "pending"
        task.retry_count += 1
        task.error_message = None
        task.failure_type = None
        retried += 1

    audit_service.log_action(
        db, current_admin.get("sub", ""), "batch_retry", "generation_task",
        None, f"count={retried}, ids={body.task_ids[:10]}", request.client.host if request.client else None,
    )
    db.commit()
    return success_response({"retried": retried})
