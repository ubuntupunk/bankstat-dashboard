from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import sys
import os
import logging

#supabase connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# Initialize config
config = Config()

# Use direct URL for database connections
DATABASE_URL = config.supabase_direct_url

# Create SQLAlchemy engine with connection pooling disabled for Supabase
from utils.utils import debug_write
debug_write("Attempting to create SQLAlchemy engine.")
try:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Use NullPool for Supabase transaction mode
        pool_pre_ping=True,  # Enable connection health checks
        connect_args={
            'connect_timeout': 10,  # 10 second timeout for connection
            'keepalives': 1,  # Enable keepalive
            'keepalives_idle': 30,  # Idle time before sending keepalive
            'keepalives_interval': 10,  # Interval between keepalives
            'keepalives_count': 5,  # Number of keepalives before dropping connection
        }
    )
    logger.info("Successfully connected to the database")
    debug_write("Successfully created SQLAlchemy engine.")
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    debug_write(f"Error creating database engine: {e}")
    raise

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for ORM models
Base = declarative_base()

from contextlib import contextmanager

def get_db():
    """Dependency to get DB session"""
    debug_write("Attempting to get DB session (get_db).")
    db = SessionLocal()
    try:
        debug_write("DB session obtained (get_db).")
        yield db
    finally:
        db.close()
        debug_write("DB session closed (get_db).")

@contextmanager
def get_db_session():
    """Context manager to get DB session"""
    debug_write("Attempting to get DB session (get_db_session context manager).")
    db = SessionLocal()
    try:
        debug_write("DB session obtained (get_db_session context manager).")
        yield db
    finally:
        db.close()
        debug_write("DB session closed (get_db_session context manager).")
