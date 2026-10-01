"""Saakshi Database Base & Session Management.

Purpose: Configures SQLAlchemy engine, session factory, and declarative base.
Inputs: Application database settings.
Outputs: Thread-safe DB sessions and Declarative Base class.
Status: Implemented
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy entities."""


# Create engine supporting SQLite for unit tests and PostgreSQL for production
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
