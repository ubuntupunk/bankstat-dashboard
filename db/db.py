from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from config import Config

# This file is used to connect to the Supabase database
# Load environment variables
config = Config()
DATABASE_URL = config.supabase_database_url

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, poolclass=NullPool)  # Use NullPool for Supabase transaction mode

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for ORM models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()