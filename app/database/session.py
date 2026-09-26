"""
Application Database Session and Initialization.
Manages multi-tenant application state storage (users, orgs, connections, query logs).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.database.models import Base

# Engine for the application management database
app_engine = create_engine(
    settings.APP_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.APP_DATABASE_URL else {},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=app_engine)

def init_app_database():
    """Initializes tables for the multi-tenant application database."""
    Base.metadata.create_all(bind=app_engine)

def get_db():
    """FastAPI dependency yielding an isolated application database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
