"""
Database Connection & Session Management Module.

Constructs connection URLs from environment variables and initializes
SQLAlchemy Engine and Session Factory.
"""

import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# Load environment variables from .env file
load_dotenv()

Base = declarative_base()

_ENGINES = {}


def get_db_url() -> str:
    """
    Construct database connection URL from environment variables or custom override.
    Defaults to DATABASE_URL if set, or local SQLite database fallback.
    """
    load_dotenv()
    custom_url = os.getenv("DATABASE_URL")
    if custom_url and custom_url.strip():
        return custom_url.strip()

    # Check if MySQL password is explicitly provided and non-default
    password = os.getenv("DATABASE_PASSWORD")
    if password and password.strip() and password != "your_mysql_password_here":
        user = os.getenv("DATABASE_USER", "root")
        host = os.getenv("DATABASE_HOST", "localhost")
        port = os.getenv("DATABASE_PORT", "3306")
        dbname = os.getenv("DATABASE_NAME", "job_market_db")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

    # Default local standalone database
    return "sqlite:///./job_market.db"


def get_engine(db_url: str = None):
    """
    Create or retrieve cached SQLAlchemy Engine.

    Args:
        db_url: Optional explicit database URL string (defaults to get_db_url()).
    """
    url = db_url or get_db_url()

    if url in _ENGINES:
        return _ENGINES[url]

    # SQLite specific static pool for in-memory DB testing or file database
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20, echo=False)

    _ENGINES[url] = engine
    return engine


def get_session_factory(db_url: str = None) -> sessionmaker:
    """Create session factory for the engine."""
    engine = get_engine(db_url)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(engine=None):
    """Create all tables defined in ORM models."""
    if engine is None:
        engine = get_engine()
    from app.database import models  # Ensure models are loaded before metadata creation
    Base.metadata.create_all(bind=engine)


def get_session(db_url: str = None) -> Generator[Session, None, None]:
    """Context generator for DB sessions."""
    session_factory = get_session_factory(db_url)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
