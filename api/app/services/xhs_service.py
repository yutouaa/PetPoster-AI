import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def generate_xhs_content(prompt: str) -> str:
    """调用 AI 生成小红书推广文案。"""
    settings = get_settings()
    if not settings.rightcode_api_key:
        return "（未配置 API Key，无法生成文案）"

    base_url = settings.rightcode_base_url.rstrip("/")
    if base_url.endswith("/v1"):
        base_url = base_url[:-3]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.rightcode_api_key}",
    }

    payload = {
        "model": settings.rightcode_model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的小红书文案撰写助手。请根据用户提供的信息，生成吸引人的小红书推广帖子文案，包含标题、正文和推荐标签。格式要求：第一行为标题，空一行后为正文，最后一行为标签（以#开头用空格分隔）。",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=60) as client:
            response = await client.post("/v1/chat/completions", json=payload)
            if response.status_code >= 400:
                logger.error("XHS content generation failed: %s", response.text)
                return f"（生成失败: HTTP {response.status_code}）"
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return "（AI 未返回内容）"
    except Exception as e:
        logger.exception("XHS content generation error")
        return f"（生成异常: {e}）"
