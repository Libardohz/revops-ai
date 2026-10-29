"""Database session and engine management for RevOpsAI."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from RevOpsAI.src.db.models import Base


def get_engine(db_url: str = "sqlite:///RevOpsAI/data/revops.db"):
    """Create and return a SQLAlchemy engine, ensuring local directories exist for SQLite."""
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(db_url, echo=False)


def init_db(engine) -> None:
    """Initialize database schema from ORM models."""
    Base.metadata.create_all(engine)


def get_session_factory(engine) -> sessionmaker[Session]:
    """Return a configured sessionmaker instance."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
