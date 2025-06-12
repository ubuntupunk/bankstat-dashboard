from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import sys
import os
import logging

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
except Exception as e:
    logger.error(f"Error creating database engine: {e}")
    raise

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for ORM models
Base = declarative_base()

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()