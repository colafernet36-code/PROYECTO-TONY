"""Engine y session factory de SQLAlchemy a partir de config.settings."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings


def make_engine(database_url: str | None = None) -> Engine:
    url = database_url or get_settings().database_url
    return create_engine(url, pool_pre_ping=True, future=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def check_database(engine: Engine) -> None:
    """Health check minimo de arranque: falla si PostgreSQL no responde (v0.3 S4 bootstrap)."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
