from db import Base, engine
from model import *  # Import all models to ensure they are registered with Base.metadata
import logging
from config import Config

config = Config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initializes the Supabase database by creating all tables defined in db/model.py.
    """
    logger.info("Attempting to create all database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db()
