import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.responses import error_response

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400) -> None:
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.error_code, exc.message)
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("未处理异常")
    return JSONResponse(
        status_code=500,
        content=error_response("INTERNAL_SERVER_ERROR", "服务器内部错误")
    )
