from fastapi import APIRouter

from app.api.routes import (
    admin,
    admin_ai_providers,
    admin_audit,
    admin_failed_tasks,
    admin_generation_tasks,
    admin_quota,
    admin_templates,
    admin_xhs,
    generation_tasks,
    health,
    quota,
    templates,
    upload,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(admin.router)
api_router.include_router(admin_ai_providers.router)
api_router.include_router(admin_audit.router)
api_router.include_router(admin_failed_tasks.router)
api_router.include_router(admin_generation_tasks.router)
api_router.include_router(admin_quota.router)
api_router.include_router(admin_templates.router)
api_router.include_router(admin_xhs.router)
api_router.include_router(quota.router)
api_router.include_router(templates.router)
api_router.include_router(generation_tasks.router)
api_router.include_router(upload.router)
