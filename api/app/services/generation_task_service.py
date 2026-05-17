import json
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.generation_task import GenerationTask


def create_generation_task(
    db: Session, template_id: int, user_id: str | None, image_urls: list[str]
) -> GenerationTask:
    task = GenerationTask(
        template_id=template_id,
        user_id=user_id,
        status="pending",
        original_image_urls=json.dumps(image_urls),
        cost=0,
        retry_count=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_generation_task_by_id(db: Session, task_id: int) -> GenerationTask | None:
    return db.query(GenerationTask).filter(GenerationTask.id == task_id).first()


def list_generation_tasks(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 10,
    status: str | None = None,
    user_id: str | None = None,
) -> tuple[list[GenerationTask], int]:
    query = db.query(GenerationTask)

    if status:
        query = query.filter(GenerationTask.status == status)
    if user_id:
        query = query.filter(GenerationTask.user_id == user_id)

    total = query.count()
    items = (
        query.order_by(GenerationTask.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def update_task_status(
    db: Session,
    task: GenerationTask,
    status: str,
    result_url: str | None = None,
    error: str | None = None,
    cost: int = 0,
) -> GenerationTask:
    task.status = status
    if result_url:
        task.result_image_url = result_url
    if error:
        task.error_message = error
    if cost:
        task.cost = cost
    if status in ("success", "failed"):
        task.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(task)
    return task


