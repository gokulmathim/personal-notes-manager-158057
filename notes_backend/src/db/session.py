from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy declarative models."""
    pass


settings = get_settings()

# SQLite needs check_same_thread=False for single-threaded applications
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)

# Factory for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
