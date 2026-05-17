from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.api.router import api_router
from app.core.errors import AppError, app_error_handler
from app.core.security import create_admin_token
from app.db.base import Base
from app.models.generation_task import GenerationTask
from app.models.template import Template


def make_client_with_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    template = Template(name="古典油画", category="classic", is_active=True)
    db.add(template)
    db.flush()
    db.add(
        GenerationTask(
            template_id=template.id,
            user_id="user-1",
            status="success",
            original_image_urls='["http://example.com/pet.png"]',
            result_image_url="http://example.com/result.png",
            prompt="生成宠物海报",
            cost=7,
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
    )
    db.commit()

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(api_router, prefix="/api")

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), db


def test_admin_generation_tasks_require_auth_and_return_template_name():
    client, db = make_client_with_db()
    try:
        unauth = client.get("/api/admin/generation-tasks")
        assert unauth.status_code == 401

        token = create_admin_token("admin", ["R_ADMIN"])
        response = client.get(
            "/api/admin/generation-tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["total"] == 1
        assert body["data"]["records"][0]["templateName"] == "古典油画"
        assert body["data"]["records"][0]["resultImageUrl"] == "http://example.com/result.png"
    finally:
        db.close()
