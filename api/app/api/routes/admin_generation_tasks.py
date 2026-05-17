import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.template import Template
from app.services import generation_task_service
from app.services.generation_processor import process_generation_task
from app.services.generation_task_presenter import build_template_name_map, task_to_dict

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/generation-tasks", tags=["admin-generation-tasks"])


@router.get("")
def list_admin_generation_tasks(
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    userId: str | None = Query(default=None),
) -> dict:
    tasks, total = generation_task_service.list_generation_tasks(
        db, page=page, page_size=pageSize, status=status, user_id=userId
    )
    template_names = build_template_name_map(db, tasks)
    logger.info(
        "admin_generation_tasks.list admin=%s page=%s page_size=%s status=%s user_id=%s total=%s",
        current_admin.get("sub"),
        page,
        pageSize,
        status,
        userId,
        total,
    )
    return success_response({
        "records": [task_to_dict(task, template_names.get(task.template_id, "")) for task in tasks],
        "current": page,
        "size": pageSize,
        "total": total,
    })


@router.get("/{task_id}")
def get_admin_generation_task(
    task_id: int,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    task = generation_task_service.get_generation_task_by_id(db, task_id)
    if not task:
        raise AppError("TASK_NOT_FOUND", "任务不存在", 404)

    template = db.query(Template).filter(Template.id == task.template_id).first()
    logger.info("admin_generation_tasks.detail admin=%s task_id=%s", current_admin.get("sub"), task_id)
    return success_response(task_to_dict(task, template.name if template else ""))


@router.post("/{task_id}/retry")
def retry_admin_generation_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    current_admin: Annotated[dict, Depends(get_current_admin)],
    db: Session = Depends(get_db),
) -> dict:
    task = generation_task_service.get_generation_task_by_id(db, task_id)
    if not task:
        raise AppError("TASK_NOT_FOUND", "任务不存在", 404)
    if task.status not in {"failed", "success"}:
        raise AppError("TASK_NOT_RETRYABLE", "只有已完成或失败任务可以重新生成", 400)

    task.status = "pending"
    task.result_image_url = None
    task.error_message = None
    task.failure_type = None
    task.completed_at = None
    task.retry_count += 1
    db.commit()
    db.refresh(task)

    background_tasks.add_task(process_generation_task, task.id)
    template = db.query(Template).filter(Template.id == task.template_id).first()
    logger.info("admin_generation_tasks.retry admin=%s task_id=%s", current_admin.get("sub"), task_id)
    return success_response(task_to_dict(task, template.name if template else ""), "已重新提交生成任务")
