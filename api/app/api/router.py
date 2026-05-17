from fastapi import APIRouter

from app.api.routes import admin, admin_generation_tasks, admin_templates, generation_tasks, health, templates, upload

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(admin.router)
api_router.include_router(admin_generation_tasks.router)
api_router.include_router(admin_templates.router)
api_router.include_router(templates.router)
api_router.include_router(generation_tasks.router)
api_router.include_router(upload.router)
