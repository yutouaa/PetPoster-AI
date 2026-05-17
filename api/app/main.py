import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.db.bootstrap import bootstrap_dev_database
from app.services.ai_service import get_ai_service
from app.services.image_service import get_image_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    bootstrap_dev_database()
    image_service = get_image_service()
    deleted = await image_service.cleanup_old_images(max_age_hours=72)
    if deleted:
        logger.info("startup cleanup: removed %s old uploaded files", deleted)
    yield
    ai_service = get_ai_service()
    await ai_service.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.api_title, lifespan=lifespan)
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
