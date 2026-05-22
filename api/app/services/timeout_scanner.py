import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.generation_task import GenerationTask

logger = logging.getLogger(__name__)


def scan_timeout_tasks() -> int:
    settings = get_settings()
    threshold = datetime.now(timezone.utc) - timedelta(minutes=settings.task_timeout_minutes)

    db: Session = SessionLocal()
    try:
        tasks = db.scalars(
            select(GenerationTask).where(
                GenerationTask.status == "processing",
                GenerationTask.started_at < threshold,
            )
        ).all()

        if not tasks:
            return 0

        count = 0
        for task in tasks:
            try:
                task.status = "failed"
                task.failure_type = "timeout"
                task.error_message = f"任务超时（超过 {settings.task_timeout_minutes} 分钟未完成）"
                task.completed_at = datetime.now(timezone.utc)

                if task.user_id:
                    from app.services import quota_service
                    quota_service.refund(
                        db, task.user_id, amount=1,
                        reference_id=str(task.id),
                        remark="任务超时自动退还",
                    )

                db.commit()
                count += 1
            except Exception:
                logger.exception("[超时扫描] 任务 %s 处理失败", task.id)
                db.rollback()

        if count:
            logger.info("[超时扫描] 标记 %d 个超时任务", count)
        return count
    except Exception:
        logger.exception("[超时扫描] 扫描失败")
        db.rollback()
        return 0
    finally:
        db.close()
