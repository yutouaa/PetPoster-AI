import json
import logging
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.models.generation_task import GenerationTask
from app.models.template import Template
from app.services.ai_service import get_ai_service
from app.services.generation_task_service import update_task_status

logger = logging.getLogger(__name__)

# 服务端原因导致的失败才退款；用户原因（违规内容、图片解码等）不退款
REFUNDABLE_FAILURE_TYPES = {"api_error", "timeout", "rate_limit", "template_missing"}


async def process_generation_task(task_id: int):
    """后台处理生成任务（ai_service 内部已有重试逻辑）"""
    logger.info("[后台任务] 开始处理任务 %s", task_id)

    db = SessionLocal()

    try:
        task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
        if not task:
            logger.error("[后台任务] 任务 %s 不存在", task_id)
            return

        template = db.query(Template).filter(Template.id == task.template_id).first()
        if not template:
            task.failure_type = "template_missing"
            update_task_status(db, task, "failed", error="模板不存在")
            _refund_quota(db, task)
            return

        task.started_at = datetime.now(timezone.utc)
        update_task_status(db, task, "processing")

        prompt = template.prompt_template or f"生成一张 {template.name} 风格的宠物海报"
        negative_prompt = template.negative_prompt or ""
        image_urls = json.loads(task.original_image_urls) if task.original_image_urls else []
        task.prompt = prompt
        db.commit()

        ai_service = get_ai_service(db)
        result = await ai_service.generate_image(prompt, negative_prompt, image_urls)

        update_task_status(
            db, task, "success", result_url=result["image_url"], cost=result.get("cost", 0)
        )
        _increment_template_usage(db, template, succeeded=True)
        logger.info("[后台任务] 任务 %s 生成成功", task_id)

    except Exception as e:
        logger.exception("[后台任务] 任务 %s 失败: %s", task_id, e)
        try:
            task = db.query(GenerationTask).filter(GenerationTask.id == task_id).first()
            if task:
                error_msg = str(e)
                failure_type = "api_error"
                if "timeout" in error_msg.lower():
                    failure_type = "timeout"
                elif "rate" in error_msg.lower():
                    failure_type = "rate_limit"
                task.failure_type = failure_type
                update_task_status(db, task, "failed", error=error_msg)
                template = db.query(Template).filter(Template.id == task.template_id).first()
                if template:
                    _increment_template_usage(db, template, succeeded=False)
                _refund_quota(db, task)
        except Exception:
            logger.exception("[后台任务] 任务 %s 终态处理失败", task_id)
    finally:
        db.close()


def _increment_template_usage(db, template: Template, succeeded: bool) -> None:
    """任务进入终态时累加模板使用计数。容忍少量丢失（并发冲突不致命）。"""
    try:
        template.usage_count = (template.usage_count or 0) + 1
        if succeeded:
            template.success_count = (template.success_count or 0) + 1
        db.commit()
    except Exception:
        logger.exception("[模板统计] 模板 %s 累加失败", template.id)
        db.rollback()


def _refund_quota(db, task: GenerationTask):
    """仅对服务端原因失败退还配额；用户原因（违规、图片错误等）不退款"""
    if not task.user_id:
        return
    if task.failure_type not in REFUNDABLE_FAILURE_TYPES:
        logger.info(
            "[配额退还] 任务 %s failure_type=%s 非服务端原因，不退款",
            task.id, task.failure_type,
        )
        return
    try:
        from app.services import quota_service

        quota_service.refund(
            db, task.user_id, amount=1,
            reference_id=str(task.id),
            remark=f"任务失败自动退还: {task.failure_type}",
        )
        db.commit()
    except Exception:
        logger.exception("[配额退还] 任务 %s 退还失败", task.id)
