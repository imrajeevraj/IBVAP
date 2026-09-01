from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings
import logging
import os
import sys

logger = logging.getLogger("Database")

# Strict Production Guard: Prevent SQLite usage in production environments
env_name = os.environ.get("ENV", "development").lower()
if env_name == "production" and "sqlite" in settings.DATABASE_URL:
    logger.critical("CRITICAL SECURITY ERROR: SQLite cannot be used in a production environment. Use PostgreSQL.")
    sys.exit(1)

engine_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_args = {"connect_args": {"check_same_thread": False}}
elif settings.DATABASE_URL.startswith("postgres"):
    engine_args = {
        "pool_size": 20,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }

engine = create_engine(settings.DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
