import json

from sqlalchemy.orm import Session

from app.models.generation_task import GenerationTask
from app.models.template import Template


def build_template_name_map(db: Session, tasks: list[GenerationTask]) -> dict[int, str]:
    template_ids = {task.template_id for task in tasks}
    if not template_ids:
        return {}

    return {
        item.id: item.name
        for item in db.query(Template).filter(Template.id.in_(template_ids)).all()
    }


def task_to_dict(task: GenerationTask, template_name: str = "") -> dict:
    try:
        original_image_urls = json.loads(task.original_image_urls) if task.original_image_urls else []
    except (TypeError, json.JSONDecodeError):
        original_image_urls = []

    return {
        "id": task.id,
        "templateId": task.template_id,
        "templateName": template_name,
        "status": task.status,
        "originalImageUrls": original_image_urls,
        "resultImageUrl": task.result_image_url,
        "prompt": task.prompt,
        "cost": task.cost,
        "failureType": task.failure_type,
        "errorMessage": task.error_message,
        "retryCount": task.retry_count,
        "requestId": task.request_id,
        "createdAt": task.created_at.isoformat() if task.created_at else "",
        "updatedAt": task.updated_at.isoformat() if task.updated_at else "",
        "completedAt": task.completed_at.isoformat() if task.completed_at else None,
    }
