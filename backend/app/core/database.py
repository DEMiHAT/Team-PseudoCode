"""
SQLAlchemy database connectivity and session lifecycle management.
Architected for SQLite local development and seamless production migration to PostgreSQL.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

# Build engine parameters based on target database driver
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,  # Proactively verifies connections before handing them to requests
}

if settings.is_sqlite:
    # SQLite-specific connection arguments
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL connection pool settings
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a managed SQLAlchemy session per request.
    Ensures safe rollback on unhandled exceptions and cleans up connections.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        logger.error(f"Database transaction error: {exc}", exc_info=True)
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initializes database tables and triggers seed data population if required.
    """
    logger.info("Initializing database schema...")
    # Import all models to register them on Base metadata
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")

    # Automatically seed curriculum and benchmark problems if tables are empty
    try:
        from app.content.seed_data import seed_initial_content

        with SessionLocal() as session:
            seed_initial_content(session)
    except Exception as seed_err:
        logger.warning(f"Could not auto-seed database: {seed_err}")
