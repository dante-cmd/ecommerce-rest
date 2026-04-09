from __future__ import annotations

from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool, text
from sqlalchemy.engine import make_url

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import get_settings  # noqa: E402
from app.models import Base  # noqa: E402

config = context.config
fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def _ensure_database_exists() -> None:
    url = make_url(config.get_main_option("sqlalchemy.url"))
    if not url.database or url.database.lower() == "master":
        return
    master_url = url.set(database="master")
    engine = engine_from_config(
        {"sqlalchemy.url": master_url.render_as_string(hide_password=False)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    db_name = url.database
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(
            text("IF DB_ID(:db_name) IS NULL BEGIN CREATE DATABASE [" + db_name + "] END"),
            {"db_name": db_name},
        )


def run_migrations_online() -> None:
    _ensure_database_exists()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
