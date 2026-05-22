import time
from collections import defaultdict

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.template import Template
from app.schemas.generation_task import GenerationTaskCreate
from app.services import generation_task_service
from app.services.generation_processor import process_generation_task
from app.services.generation_task_presenter import build_template_name_map, task_to_dict

router = APIRouter(prefix="/generation-tasks", tags=["generation-tasks"])

_generation_limits: dict[str, list[float]] = defaultdict(list)
_MAX_GENERATIONS_PER_HOUR = 20
_WINDOW_SECONDS = 3600
_last_cleanup: float = 0
_CLEANUP_INTERVAL = 600


def _check_generation_rate(user_id: str) -> None:
    global _last_cleanup
    key = user_id or "anonymous"
    now = time.time()
    attempts = _generation_limits[key]
    _generation_limits[key] = [t for t in attempts if now - t < _WINDOW_SECONDS]
    if len(_generation_limits[key]) >= _MAX_GENERATIONS_PER_HOUR:
        raise AppError("RATE_LIMIT", "生成次数超出限制，请稍后再试", 429)
    _generation_limits[key].append(now)

    if now - _last_cleanup > _CLEANUP_INTERVAL:
        _last_cleanup = now
        stale_keys = [k for k, v in _generation_limits.items() if not v or v[-1] < now - _WINDOW_SECONDS]
        for k in stale_keys:
            del _generation_limits[k]


@router.post("")
async def create_generation_task(
    request: GenerationTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    """创建生成任务"""
    user_id = request.user_id or "anonymous"
    _check_generation_rate(user_id)

    # 验证模板存在
    template = db.query(Template).filter(Template.id == request.template_id).first()
    if not template:
        raise AppError("TEMPLATE_NOT_FOUND", "模板不存在", 404)

    if not template.is_active:
        raise AppError("TEMPLATE_INACTIVE", "该模板已下架", 400)

    # 验证图片 URL
    if not request.image_urls or len(request.image_urls) == 0:
        raise AppError("NO_IMAGES", "请至少上传一张照片", 400)

    # 创建任务记录并 flush 获取 ID
    task = generation_task_service.create_generation_task(
        db, request.template_id, request.user_id, request.image_urls
    )
    db.flush()

    # 配额扣减（带 reference_id，无需回填）
    from app.services import quota_service

    if not quota_service.deduct(db, user_id, amount=1, reference_id=str(task.id)):
        db.rollback()
        raise AppError("QUOTA_INSUFFICIENT", "生成次数不足，请充值后再试", 403)

    db.commit()

    # 添加后台任务
    background_tasks.add_task(process_generation_task, task.id)

    # 返回任务 ID
    return success_response(task_to_dict(task, template.name), "任务创建成功")


@router.get("/{task_id}")
async def get_generation_task(
    task_id: int,
    db: Session = Depends(get_db),
    userId: str = Query(..., min_length=1),
) -> dict:
    """查询任务状态"""
    task = generation_task_service.get_generation_task_by_id(db, task_id)
    if not task:
        raise AppError("TASK_NOT_FOUND", "任务不存在", 404)

    if task.user_id != userId:
        raise AppError("TASK_NOT_FOUND", "任务不存在", 404)

    template = db.query(Template).filter(Template.id == task.template_id).first()
    return success_response(task_to_dict(task, template.name if template else ""))


@router.get("")
async def list_generation_tasks(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    userId: str = Query(..., min_length=1),
) -> dict:
    """用户历史记录"""
    tasks, total = generation_task_service.list_generation_tasks(
        db, page=page, page_size=pageSize, status=status, user_id=userId
    )

    template_names = build_template_name_map(db, tasks)
    records = [task_to_dict(task, template_names.get(task.template_id, "")) for task in tasks]

    return success_response({"records": records, "current": page, "size": pageSize, "total": total})
