import json
import logging

from app.db.session import SessionLocal
from app.models.generation_task import GenerationTask
from app.models.template import Template
from app.services.ai_service import get_ai_service
from app.services.generation_task_service import update_task_status

logger = logging.getLogger(__name__)


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
            update_task_status(db, task, "failed", error="模板不存在")
            return

        update_task_status(db, task, "processing")

        prompt = template.prompt_template or f"生成一张 {template.name} 风格的宠物海报"
        negative_prompt = template.negative_prompt or ""
        image_urls = json.loads(task.original_image_urls) if task.original_image_urls else []
        task.prompt = prompt
        db.commit()

        ai_service = get_ai_service()
        result = await ai_service.generate_image(prompt, negative_prompt, image_urls)

        update_task_status(
            db, task, "success", result_url=result["image_url"], cost=result.get("cost", 0)
        )
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
        except Exception:
            pass
    finally:
        db.close()
