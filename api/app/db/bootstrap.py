from app.core.config import get_settings
from app.db.base import Base
from app.db.seed import seed_admin, seed_templates
from app.db.session import engine
from app.models import AdminUser, GenerationTask, Template  # noqa: F401


def bootstrap_dev_database() -> None:
    """Create and seed the local SQLite database for development only."""
    settings = get_settings()
    if settings.app_env == "production" or not settings.database_url.startswith("sqlite"):
        return

    Base.metadata.create_all(bind=engine)
    seed_admin()
    seed_templates()
