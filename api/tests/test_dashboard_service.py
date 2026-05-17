from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.password import hash_password
from app.db.base import Base
from app.models.admin_user import AdminUser
from app.models.generation_task import GenerationTask
from app.models.template import Template
from app.services.dashboard_service import get_dashboard_metrics


def make_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_get_dashboard_metrics_counts_real_database_records():
    db = make_db()
    now = datetime.now(UTC).replace(tzinfo=None)
    yesterday = now - timedelta(days=1)
    try:
        db.add(
            AdminUser(
                username="admin",
                nickname="Admin",
                hashed_password=hash_password("admin123"),
                roles="R_ADMIN",
            )
        )
        db.add_all(
            [
                Template(name="油画", category="classic", is_active=True),
                Template(name="杂志", category="editorial", is_active=False),
            ]
        )
        db.flush()
        db.add_all(
            [
                GenerationTask(template_id=1, status="success", cost=12, created_at=now),
                GenerationTask(template_id=1, status="failed", cost=0, created_at=now, user_id="u1"),
                GenerationTask(template_id=2, status="success", cost=5, created_at=yesterday, user_id="u2"),
            ]
        )
        db.commit()

        metrics = get_dashboard_metrics(db)

        assert metrics["userCount"] == 2
        assert metrics["templateCount"] == 2
        assert metrics["generationCount"] == 3
        assert metrics["todayGenerationCount"] == 2
        assert metrics["todayCost"] == 12
        assert metrics["todayRevenue"] == 0
        assert metrics["failureRate"] == 33.33
        assert metrics["successRate"] == 66.67
        assert metrics["activeUserCount"] == 2
        assert metrics["styleDistribution"][0] == {"name": "油画", "value": 2}
        assert {"name": "failed", "value": 1} in metrics["statusDistribution"]
        assert len(metrics["generationTrend"]) == 7
        assert metrics["generationTrend"][-1]["count"] == 2
        assert metrics["userPortrait"]["repeatUserCount"] == 0
        assert metrics["userPortrait"]["newUserCount"] == 2
        assert metrics["topTemplates"][0]["name"] == "油画"
        assert len(metrics["recentTasks"]) == 3
    finally:
        db.close()
