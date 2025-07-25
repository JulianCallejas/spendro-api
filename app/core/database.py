from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

# Database engine
try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    database_connected = True
except Exception as e:
    logging.warning(f"Database connection failed: {e}. Using mock data.")
    engine = None
    SessionLocal = None
    database_connected = False

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    if not database_connected:
        # Return mock data when database is not available
        from app.core.mock_data import get_mock_session
        return get_mock_session()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()