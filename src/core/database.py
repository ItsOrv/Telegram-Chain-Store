from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, configure_mappers
from contextlib import contextmanager
from typing import Generator, Optional, Any
import os
import logging
from pathlib import Path

from src.core.models.base import Base
from src.core.config import DatabaseConfig

logger = logging.getLogger(__name__)

# Make sure the data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Get database URL from environment variable or use SQLite by default
def get_database_url(config: Optional[DatabaseConfig] = None) -> str:
    """
    Generate database URL based on config or environment variables
    
    Args:
        config: Optional database configuration object
        
    Returns:
        Database URL string
    """
    if config:
        # Use provided config
        if config.type.lower() == "sqlite":
            return f"sqlite:///{data_dir}/chainstore.db"
        elif config.type.lower() == "mysql":
            return f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        elif config.type.lower() == "postgresql":
            return f"postgresql+psycopg2://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}"
        else:
            logger.warning(f"Unsupported database type: {config.type}, falling back to SQLite")
            return f"sqlite:///{data_dir}/chainstore.db"
    else:
        # Use environment variables or default to SQLite
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url
        return f"sqlite:///{data_dir}/chainstore.db"

# Create SQLAlchemy engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true"  # Set to True for SQL query logging
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all tables defined in the models"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def drop_tables() -> None:
    """Drop all tables defined in the models"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures that session is closed after use and handles exceptions.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session from dependency injection system.
    Used with FastAPI dependency system.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Database:
    """Compatible Database class for backward compatibility"""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize database with config"""
        self.config = config
        
        # Update engine connection if needed
        global engine, SessionLocal
        engine = create_engine(
            get_database_url(config),
            pool_pre_ping=True,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true"
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    async def connect(self) -> None:
        """Connect to database (compatibility method)"""
        try:
            logger.info(f"Initializing database with SQLAlchemy")
            # Configure all mappers before creating tables
            configure_mappers()
            logger.info("All SQLAlchemy mappers configured")
            # Create tables if they don't exist
            create_tables()
            logger.info("Database initialization completed")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from database (compatibility method)"""
        logger.info("Database connection closed")
    
    async def init_db(self) -> None:
        """Initialize database (compatibility method)"""
        try:
            # Configure all mappers before creating tables
            configure_mappers()
            logger.info("All SQLAlchemy mappers configured")
            create_tables()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
            
    def get_session(self) -> Session:
        """Get a database session"""
        return SessionLocal()
