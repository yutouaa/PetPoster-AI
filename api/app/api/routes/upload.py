import time
from collections import defaultdict

from fastapi import APIRouter, File, Request, UploadFile

from app.core.errors import AppError
from app.core.responses import success_response
from app.services.image_service import get_image_service

router = APIRouter(prefix="/upload", tags=["upload"])

_upload_limits: dict[str, list[float]] = defaultdict(list)
_MAX_UPLOADS_PER_MINUTE = 10
_WINDOW_SECONDS = 60
_last_cleanup: float = 0
_CLEANUP_INTERVAL = 300


def _check_upload_rate(client_ip: str) -> None:
    global _last_cleanup
    now = time.time()
    attempts = _upload_limits[client_ip]
    _upload_limits[client_ip] = [t for t in attempts if now - t < _WINDOW_SECONDS]
    if len(_upload_limits[client_ip]) >= _MAX_UPLOADS_PER_MINUTE:
        raise AppError("RATE_LIMIT", "上传过于频繁，请稍后再试", 429)
    _upload_limits[client_ip].append(now)

    if now - _last_cleanup > _CLEANUP_INTERVAL:
        _last_cleanup = now
        stale_keys = [k for k, v in _upload_limits.items() if not v or v[-1] < now - _WINDOW_SECONDS]
        for k in stale_keys:
            del _upload_limits[k]


@router.post("/images")
async def upload_images(request: Request, files: list[UploadFile] = File(...)) -> dict:
    """上传宠物照片（最多 5 张）"""
    client_ip = request.client.host if request.client else "unknown"
    _check_upload_rate(client_ip)

    if not files or len(files) == 0:
        raise AppError("NO_FILES", "请至少上传一张照片", 400)

    if len(files) > 5:
        raise AppError("TOO_MANY_FILES", "最多只能上传 5 张照片", 400)

    image_service = get_image_service()
    urls = []

    for file in files:
        try:
            url = await image_service.save_uploaded_image(file)
            urls.append(url)
        except AppError:
            raise
        except Exception as e:
            raise AppError("UPLOAD_FAILED", f"上传失败: {str(e)}", 500)

    return success_response({"urls": urls}, "上传成功")
