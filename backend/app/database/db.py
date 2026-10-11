"""
SQLite Database Connection and Session Management
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.models.review import Base

db_path = Path(settings.SQLITE_DB_PATH)
db_path.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in SQLite."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
