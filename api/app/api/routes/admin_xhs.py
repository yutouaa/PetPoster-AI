import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.errors import AppError
from app.core.responses import success_response
from app.models.xhs_post import XhsPost
from app.services.xhs_service import generate_xhs_content

router = APIRouter(prefix="/admin/xhs-posts", tags=["admin-xhs-posts"], dependencies=[Depends(get_current_admin)])

XhsStatus = Literal["draft", "scheduled", "published", "failed"]


class XhsPostCreate(BaseModel):
    title: str = Field(max_length=200)
    content: str = Field(default="", max_length=10000)
    image_urls: list[str] = []
    tags: list[str] = Field(default=[], max_length=20)
    status: XhsStatus = "draft"
    scheduled_at: str | None = None
    llm_prompt: str | None = Field(default=None, max_length=2000)


class XhsPostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, max_length=10000)
    image_urls: list[str] | None = None
    tags: list[str] | None = Field(default=None, max_length=20)
    status: XhsStatus | None = None
    scheduled_at: str | None = None
    llm_prompt: str | None = Field(default=None, max_length=2000)


class GenerateContentRequest(BaseModel):
    prompt: str = Field(max_length=2000)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """按状态聚合帖子数量，一次返回全部统计。"""
    rows = db.execute(
        select(XhsPost.status, func.count(XhsPost.id)).group_by(XhsPost.status)
    ).all()
    counts: dict[str, int] = {"draft": 0, "scheduled": 0, "published": 0, "failed": 0}
    total = 0
    for status_value, count in rows:
        counts[status_value] = count
        total += count
    return success_response({**counts, "total": total})


@router.get("")
def list_posts(
    page: int = 1,
    page_size: int = Query(20, alias="pageSize"),
    status: XhsStatus | None = None,
    db: Session = Depends(get_db),
):
    query = select(XhsPost).order_by(XhsPost.id.desc())
    if status:
        query = query.where(XhsPost.status == status)

    count_query = select(func.count()).select_from(XhsPost)
    if status:
        count_query = count_query.where(XhsPost.status == status)

    total = db.scalar(count_query)
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    records = [_serialize(p) for p in items]
    return success_response({"records": records, "total": total, "current": page, "size": page_size})


@router.post("")
def create_post(body: XhsPostCreate, db: Session = Depends(get_db)):
    post = XhsPost(
        title=body.title,
        content=body.content,
        image_urls=json.dumps(body.image_urls),
        tags=json.dumps(body.tags),
        status=body.status,
        scheduled_at=datetime.fromisoformat(body.scheduled_at) if body.scheduled_at else None,
        llm_prompt=body.llm_prompt,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return success_response(_serialize(post))


@router.put("/{post_id}")
def update_post(post_id: int, body: XhsPostUpdate, db: Session = Depends(get_db)):
    post = db.get(XhsPost, post_id)
    if not post:
        raise AppError("NOT_FOUND", "帖子不存在", 404)

    updates = body.model_dump(exclude_unset=True)
    if "image_urls" in updates and updates["image_urls"] is not None:
        updates["image_urls"] = json.dumps(updates["image_urls"])
    if "tags" in updates and updates["tags"] is not None:
        updates["tags"] = json.dumps(updates["tags"])
    if "scheduled_at" in updates:
        updates["scheduled_at"] = datetime.fromisoformat(updates["scheduled_at"]) if updates["scheduled_at"] else None

    for key, value in updates.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return success_response(_serialize(post))


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(XhsPost, post_id)
    if not post:
        raise AppError("NOT_FOUND", "帖子不存在", 404)
    db.delete(post)
    db.commit()
    return success_response(None)


@router.post("/{post_id}/generate-content")
async def generate_content(post_id: int, body: GenerateContentRequest, db: Session = Depends(get_db)):
    post = db.get(XhsPost, post_id)
    if not post:
        raise AppError("NOT_FOUND", "帖子不存在", 404)

    content = await generate_xhs_content(body.prompt)
    if content.startswith("（") and content.endswith("）"):
        raise AppError("AI_ERROR", content, 502)
    post.content = content
    post.llm_prompt = body.prompt
    db.commit()
    db.refresh(post)
    return success_response({"content": content})


@router.post("/{post_id}/publish")
def publish_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(XhsPost, post_id)
    if not post:
        raise AppError("NOT_FOUND", "帖子不存在", 404)

    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(post)
    return success_response(_serialize(post))


def _serialize(p: XhsPost) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "content": p.content,
        "imageUrls": json.loads(p.image_urls) if p.image_urls else [],
        "tags": json.loads(p.tags) if p.tags else [],
        "status": p.status,
        "scheduledAt": p.scheduled_at.isoformat() if p.scheduled_at else None,
        "publishedAt": p.published_at.isoformat() if p.published_at else None,
        "platformPostId": p.platform_post_id,
        "llmPrompt": p.llm_prompt,
        "createdAt": p.created_at.isoformat() if p.created_at else None,
        "updatedAt": p.updated_at.isoformat() if p.updated_at else None,
    }
