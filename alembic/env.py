"""Alembic environment: uses the same DATABASE_URL and models as the backend."""
from sqlalchemy import create_engine

import backend  # noqa: F401  (puts src/ on sys.path)
from alembic import context
from backend.app.core.config import get_settings
from backend.app.db import models  # noqa: F401
from backend.app.db.session import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=get_settings().database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_settings().database_url)
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
