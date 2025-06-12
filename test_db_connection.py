#!/usr/bin/env python3
"""
Test script to verify database connection.
"""
import sys
import os
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connection():
    """Test database connection and basic query."""
    try:
        # Import inside function to avoid circular imports
        from db.db import engine
        
        logger.info("Attempting to connect to the database...")
        
        # Test the connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"Database connection successful!\nPostgreSQL version: {version}")
            return True
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
