import asyncio
import base64
import json
import logging
import uuid
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.models.ai_provider import AiProvider

logger = logging.getLogger(__name__)


def _get_active_provider(db: Session | None) -> dict | None:
    """从数据库获取优先级最高的活跃 provider 配置。"""
    if db is None:
        return None
    try:
        provider = db.scalars(
            select(AiProvider).where(AiProvider.is_active == True).order_by(AiProvider.priority.desc()).limit(1)
        ).first()
        if provider:
            return {
                "base_url": provider.base_url,
                "api_key": provider.api_key,
                "model": provider.model_name,
                "timeout": provider.timeout,
            }
    except Exception:
        pass
    return None


class AIService:
    def __init__(self, settings=None, client=None, db: Session | None = None):
        self.settings = settings or get_settings()
        self._owns_client = client is None

        provider = _get_active_provider(db)
        base_url = (provider["base_url"] if provider else self.settings.rightcode_base_url).rstrip("/")
        api_key = provider["api_key"] if provider else self.settings.rightcode_api_key
        self._model = provider["model"] if provider else self.settings.rightcode_model
        timeout = provider["timeout"] if provider else self.settings.rightcode_timeout

        if base_url.endswith("/v1"):
            base_url = base_url[:-3]
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._api_key = api_key
        self.client = client or httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    async def generate_image(
        self, prompt: str, negative_prompt: str = "", image_urls: list[str] | None = None
    ) -> dict:
        """生成图片，返回 {image_url, cost}"""
        if not self._api_key:
            raise AppError("AI_MISSING_API_KEY", "缺少 RIGHTCODE_API_KEY", 500)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await self._call_api(prompt, negative_prompt, image_urls or [])
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2**attempt
                logger.warning("AI 服务调用失败，%s秒后重试: %s", wait_time, e)
                await asyncio.sleep(wait_time)

        raise AppError("AI_SERVICE_ERROR", "AI 服务调用失败", 500)

    async def _call_api(self, prompt: str, negative_prompt: str, image_urls: list[str]) -> dict:
        """调用 Right Code 图像生成 API。"""
        payload = {
            "model": self._model,
            "prompt": self._build_content(prompt, negative_prompt, image_urls),
            "size": "1024x1024",
            "n": 1,
        }

        response = await self.client.post("/v1/images/generations", json=payload)
        if response.status_code >= 400:
            raise AppError("AI_API_ERROR", f"AI 服务返回错误: {response.status_code} {response.text}", 500)

        data = response.json()
        items = data.get("data")
        if not isinstance(items, list) or not items:
            raise AppError("AI_NO_IMAGE", "AI 服务未返回图片数据", 500)

        image_url = self._extract_image_url(items[0])
        cost = self._extract_cost(data)
        return {"image_url": image_url, "cost": cost}

    def _build_content(self, prompt: str, negative_prompt: str, image_urls: list[str]) -> str:
        """构建请求内容"""
        content = f"请根据以下描述生成一张图片：\n\n{prompt}"
        if negative_prompt:
            content += f"\n\n不要包含：{negative_prompt}"
        if image_urls:
            content += f"\n\n参考图片：{', '.join(image_urls)}"
        return content

    def _extract_image_url(self, item: dict[str, Any]) -> str:
        image_url = item.get("url")
        if isinstance(image_url, str) and image_url.strip():
            return image_url

        b64_json = item.get("b64_json") or item.get("b64")
        if isinstance(b64_json, str) and b64_json.strip():
            return self._save_base64_image(b64_json)

        raise AppError("AI_NO_IMAGE", f"图片响应缺少 url 或 b64_json: {json.dumps(item, ensure_ascii=False)}", 500)

    def _save_base64_image(self, b64_json: str) -> str:
        output_dir = Path(
            getattr(self.settings, "generated_image_dir", None) or self.settings.upload_dir
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"generated-{uuid.uuid4()}.png"
        output_path = output_dir / filename
        output_path.write_bytes(base64.b64decode(b64_json))

        public_base_url = getattr(self.settings, "public_base_url", "").rstrip("/")
        if public_base_url:
            return f"{public_base_url}/uploads/{filename}"
        return f"/uploads/{filename}"

    def _extract_cost(self, data: dict[str, Any]) -> int:
        usage = data.get("usage")
        if isinstance(usage, dict):
            value = usage.get("total_cost") or usage.get("cost") or usage.get("total_tokens")
            if isinstance(value, (int, float)):
                return int(value)
        return 0

    async def close(self):
        if self._owns_client:
            await self.client.aclose()


# 全局实例
_ai_service: AIService | None = None


def get_ai_service(db: Session | None = None) -> AIService:
    global _ai_service
    if db is not None:
        return AIService(db=db)
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
