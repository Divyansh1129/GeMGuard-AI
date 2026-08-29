"""
database.py
-----------
Sets up the SQLAlchemy engine + session. Every router uses `get_db()` as a
FastAPI dependency to get a DB session per-request.

Using SQLite for the hackathon (zero setup). To move to Postgres later,
just change DATABASE_URL in .env — no other code changes needed.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()