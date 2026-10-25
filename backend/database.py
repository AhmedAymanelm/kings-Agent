"""
database.py — SQLAlchemy engine, session, and Base
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    db_url,
    # SQLite-specific: allow same connection across threads
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    """Called once at startup to create missing tables."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️ create_all_tables warning: {e}")
