import uuid
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from app.core.config import get_settings
from app.core.errors import AppError


class ImageService:
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_uploaded_image(self, file: UploadFile) -> str:
        """保存上传的图片，返回 URL"""
        # 验证图片
        self.validate_image(file)

        # 生成唯一文件名
        ext = Path(file.filename or "image.jpg").suffix.lower()
        if not ext:
            ext = ".jpg"
        filename = f"{uuid.uuid4()}{ext}"
        filepath = self.upload_dir / filename

        # 流式写入，边读边检查大小
        max_size = self.settings.max_upload_size
        total_read = 0
        chunk_size = 64 * 1024  # 64KB chunks
        try:
            with open(filepath, "wb") as f:
                while chunk := await file.read(chunk_size):
                    total_read += len(chunk)
                    if total_read > max_size:
                        filepath.unlink(missing_ok=True)
                        raise AppError(
                            "FILE_TOO_LARGE",
                            f"图片大小不能超过 {max_size // 1024 // 1024}MB",
                            400,
                        )
                    f.write(chunk)
        except AppError:
            raise
        except Exception as e:
            filepath.unlink(missing_ok=True)
            raise AppError("UPLOAD_FAILED", f"写入文件失败: {str(e)}", 500)

        await self.validate_image_content(filepath)

        # 返回 URL（本地开发用相对路径）
        public_base_url = self.settings.public_base_url.rstrip("/")
        if public_base_url:
            return f"{public_base_url}/uploads/{filename}"
        return f"/uploads/{filename}"

    def validate_image(self, file: UploadFile) -> None:
        """验证图片格式和大小"""
        # 检查文件名
        if not file.filename:
            raise AppError("INVALID_IMAGE", "文件名不能为空", 400)

        # 检查扩展名
        ext = Path(file.filename).suffix.lower()
        allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
        if ext not in allowed_exts:
            raise AppError("INVALID_FORMAT", f"不支持的图片格式，仅支持: {', '.join(allowed_exts)}", 400)

        # 检查 MIME 类型
        if file.content_type and not file.content_type.startswith("image/"):
            raise AppError("INVALID_MIME", "文件类型必须是图片", 400)

    async def validate_image_content(self, filepath: Path) -> None:
        """验证图片内容（尺寸、大小）"""
        try:
            # 检查文件大小
            file_size = filepath.stat().st_size
            if file_size > self.settings.max_upload_size:
                filepath.unlink()
                raise AppError(
                    "FILE_TOO_LARGE",
                    f"图片大小不能超过 {self.settings.max_upload_size // 1024 // 1024}MB",
                    400,
                )

            # 检查图片尺寸
            with Image.open(filepath) as img:
                width, height = img.size
                if width < 512 or height < 512:
                    filepath.unlink()
                    raise AppError("IMAGE_TOO_SMALL", "图片尺寸不能小于 512x512", 400)
                if width > 4096 or height > 4096:
                    filepath.unlink()
                    raise AppError("IMAGE_TOO_LARGE", "图片尺寸不能超过 4096x4096", 400)

        except AppError:
            raise
        except Exception as e:
            if filepath.exists():
                filepath.unlink()
            raise AppError("INVALID_IMAGE_FILE", f"无法读取图片文件: {str(e)}", 400)

    async def cleanup_old_images(self, max_age_hours: int = 24) -> int:
        """清理旧图片，返回删除数量"""
        if not self.upload_dir.exists():
            return 0

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        deleted_count = 0

        for filepath in self.upload_dir.iterdir():
            if filepath.is_file():
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if file_mtime < cutoff_time:
                    try:
                        filepath.unlink()
                        deleted_count += 1
                    except Exception:
                        pass

        return deleted_count


# 全局实例
_image_service: ImageService | None = None


def get_image_service() -> ImageService:
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service
