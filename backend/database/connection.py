"""
PostgreSQL database connection and session management
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config_manager import get_config

logger = logging.getLogger(__name__)

# Database Configuration using secure config manager
DATABASE_URL = get_config("DATABASE_URL")

# Create engine with connection pooling for production
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,  # Validates connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False,          # Set to True for SQL query logging
)

# Create sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    from database.models import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def check_db_connection():
    """
    Test database connection
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Database utilities
class DatabaseManager:
    """
    Database management utilities
    """
    
    @staticmethod
    def create_all_tables():
        """Create all database tables"""
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("All database tables created")
    
    @staticmethod
    def drop_all_tables():
        """Drop all database tables (use with caution!)"""
        from database.models import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    
    @staticmethod
    def get_table_info():
        """Get information about existing tables"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {tables}")
        return tables