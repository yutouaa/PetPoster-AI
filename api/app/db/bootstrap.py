import logging

from sqlalchemy import inspect, text
from sqlalchemy.sql import functions as sa_functions

from app.core.config import get_settings
from app.db.base import Base
from app.db.seed import seed_admin, seed_templates
from app.db.session import engine
from app.models import AdminUser, AiProvider, AuditLog, GenerationTask, QuotaTransaction, Template, UserQuota, XhsPost  # noqa: F401

logger = logging.getLogger(__name__)


def _sqlite_default_clause(col) -> str | None:
    """提取列的 SQLite 兼容 DEFAULT 子句；不支持的返回 None。"""
    # Python-side default (scalar)
    if col.default is not None and getattr(col.default, "is_scalar", False):
        v = col.default.arg
        if isinstance(v, bool):
            return f"DEFAULT {int(v)}"
        if isinstance(v, (int, float)):
            return f"DEFAULT {v}"
        if isinstance(v, str):
            escaped = v.replace("'", "''")
            return f"DEFAULT '{escaped}'"
        return None
    # Server-side default (func.now() etc.)
    if col.server_default is not None:
        arg = getattr(col.server_default, "arg", None)
        if isinstance(arg, sa_functions.now) or (arg is not None and str(arg).lower() in ("now()", "current_timestamp")):
            return "DEFAULT CURRENT_TIMESTAMP"
    return None


def _sqlite_column_sql(col) -> str:
    """根据 SQLAlchemy Column 对象生成 SQLite ALTER ADD COLUMN 子句。"""
    col_type = col.type.compile(dialect=engine.dialect)
    parts = [f'"{col.name}"', col_type]
    if not col.nullable:
        parts.append("NOT NULL")
    default_clause = _sqlite_default_clause(col)
    if default_clause:
        parts.append(default_clause)
    return " ".join(parts)


def _sync_missing_columns() -> None:
    """开发环境 SQLite 自动补缺失列。
    限制：仅处理简单列定义；不支持加 unique/index（由 _sync_unique_indexes 单独处理）。"""
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                try:
                    sql = f'ALTER TABLE "{table.name}" ADD COLUMN {_sqlite_column_sql(column)}'
                    conn.execute(text(sql))
                    logger.info("[bootstrap] 自动补列: %s.%s", table.name, column.name)
                except Exception:
                    logger.exception("[bootstrap] 补列失败 %s.%s", table.name, column.name)


def _sync_unique_indexes() -> None:
    """为 model 中声明了 unique=True 但表里缺索引的列补建 UNIQUE INDEX。
    若列存在重复值则跳过并 warning，避免阻塞启动。"""
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing_indexes = inspector.get_indexes(table.name)
            existing_unique_cols = {
                tuple(idx["column_names"])
                for idx in existing_indexes
                if idx.get("unique")
            }
            # primary key 也算 unique，但 SQLAlchemy 列上 unique=True 通常指业务字段
            for column in table.columns:
                if not column.unique or column.primary_key:
                    continue
                col_tuple = (column.name,)
                if col_tuple in existing_unique_cols:
                    continue
                # 检查是否有重复值
                duplicate_count = conn.execute(
                    text(
                        f'SELECT COUNT(*) FROM (SELECT "{column.name}" FROM "{table.name}" '
                        f'GROUP BY "{column.name}" HAVING COUNT(*) > 1) sub'
                    )
                ).scalar()
                if duplicate_count and duplicate_count > 0:
                    logger.warning(
                        "[bootstrap] 跳过唯一索引 %s.%s：发现 %s 组重复值",
                        table.name, column.name, duplicate_count,
                    )
                    continue
                idx_name = f"ux_{table.name}_{column.name}"
                try:
                    conn.execute(text(f'CREATE UNIQUE INDEX IF NOT EXISTS "{idx_name}" ON "{table.name}" ("{column.name}")'))
                    logger.info("[bootstrap] 自动建唯一索引: %s", idx_name)
                except Exception:
                    logger.exception("[bootstrap] 建唯一索引失败 %s", idx_name)


def bootstrap_dev_database() -> None:
    """Create and seed the local SQLite database for development only."""
    settings = get_settings()
    if settings.app_env == "production" or not settings.database_url.startswith("sqlite"):
        return

    Base.metadata.create_all(bind=engine)
    _sync_missing_columns()
    _sync_unique_indexes()
    seed_admin()
    seed_templates()
