from fastapi import APIRouter

from app.core.responses import success_response

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return success_response({
        "status": "ok",
        "service": "petposter-api"
    }, "服务正常")
