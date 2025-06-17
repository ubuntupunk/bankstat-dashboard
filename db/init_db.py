from db import Base, engine
from db.model import Category, User, Role, Goal, Transaction, Budget, AIChatMessage, UserFinancialMetric, GoalProgress, Incentive, UserReward, FinancialService, ServiceVote, Appliance, EnergyConsumption # Explicitly import all models
from db.connection import SessionLocal # Import SessionLocal to get a DB session
import logging
from config import Config
from sqlalchemy.exc import IntegrityError

config = Config()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initializes the Supabase database by creating all tables defined in db/model.py
    and populating default categories if they don't exist.
    """
    logger.info("Attempting to create all database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Populate default categories
        populate_default_categories()

    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def populate_default_categories():
    """
    Populates the categories table with a default set of categories.
    """
    default_categories = [
        {'name': 'Food & Dining', 'type': 'Discretionary Expenses'},
        {'name': 'Rent & Housing', 'type': 'Necessary Expenses'},
        {'name': 'Transportation', 'type': 'Necessary Expenses'},
        {'name': 'Shopping', 'type': 'Discretionary Expenses'},
        {'name': 'Groceries', 'type': 'Necessary Expenses'},
        {'name': 'Hardware', 'type': 'Discretionary Expenses'},
        {'name': 'Entertainment', 'type': 'Discretionary Expenses'},
        {'name': 'Bills & Utilities', 'type': 'Necessary Expenses'},
        {'name': 'Income', 'type': 'Income'},
        {'name': 'Insurance', 'type': 'Necessary Expenses'},
        {'name': 'Healthcare', 'type': 'Necessary Expenses'},
        {'name': 'Donation', 'type': 'Discretionary Expenses'},
        {'name': 'Other', 'type': 'Special'},
        {'name': 'Uncategorized', 'type': 'Special'} # Ensure 'Uncategorized' exists
    ]

    db = SessionLocal()
    try:
        for cat_data in default_categories:
            existing_category = db.query(Category).filter(Category.name == cat_data['name']).first()
            if not existing_category:
                new_category = Category(name=cat_data['name'], type=cat_data.get('type'))
                db.add(new_category)
                logger.info(f"Added default category: {cat_data['name']}")
        db.commit()
        logger.info("Default categories populated successfully!")
    except IntegrityError:
        db.rollback()
        logger.warning("Some default categories already exist, skipping insertion.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error populating default categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
