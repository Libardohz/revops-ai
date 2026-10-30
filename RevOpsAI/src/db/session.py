"""Database session and engine management for RevOpsAI."""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from RevOpsAI.src.db.models import Base


def get_engine(db_url: str | None = None):
    """Create and return a SQLAlchemy engine, prioritizing DATABASE_URL environment variable.

    Supports both Supabase PostgreSQL (with connection pooling and keep-alives)
    and SQLite fallback for local offline development.
    """
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "sqlite:///RevOpsAI/data/revops.db")

    # Normalize Supabase/Heroku postgres:// URI to standard postgresql+psycopg2://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    engine_kwargs = {"echo": False}

    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    else:
        # Supabase / PostgreSQL Production Connection Pooling
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_recycle"] = 300
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    return create_engine(db_url, **engine_kwargs)


def init_db(engine) -> None:
    """Initialize database schema from ORM models."""
    Base.metadata.create_all(engine)


def get_session_factory(engine) -> sessionmaker[Session]:
    """Return a configured sessionmaker instance."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
