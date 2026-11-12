from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..core.config import get_settings


class Base(DeclarativeBase):
    pass


_engine = None
_Session = None


def get_engine():
    global _engine, _Session
    if _engine is None:
        url = get_settings().database_url
        kw = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
        _engine = create_engine(url, **kw)
        _Session = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine(url: str | None = None):
    """Used by tests to point at a throwaway database."""
    global _engine, _Session
    if url:
        import os
        os.environ["DATABASE_URL"] = url
        get_settings.cache_clear()
    _engine = _Session = None


def get_session():
    get_engine()
    return _Session()


def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(get_engine())
