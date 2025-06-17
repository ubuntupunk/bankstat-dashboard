import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from db.model import Category
from db.db import get_db_session
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Tuple, Dict, Any, Union, Optional
import uuid
import logging
import traceback
import sys
import os

# Add the models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLCategoryIntegration:
    """Integration layer for ML-based transaction categorization with stability fixes"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.categorizer = None  # Initialize as None
        self._initialize_categorizer()
    
    def _initialize_categorizer(self):
        """Initialize categorizer with proper error handling and fallbacks"""
        try:
            # Try to import the robust categorizer
            from models.transaction_categorizer import TransactionCategorizer
            
            # Initialize with fallback options
            self.categorizer = TransactionCategorizer(use_tensorflow=True)
            logger.info("TransactionCategorizer initialized successfully")
            
            # Test basic functionality
            model_info = self.categorizer.get_model_info()
            logger.info(f"Model status: {model_info.get('status', 'Unknown')}")
            
        except ImportError as e:
            logger.error(f"Failed to import TransactionCategorizer: {e}")
            self.categorizer = None
        except Exception as e:
            logger.error(f"Failed to initialize TransactionCategorizer: {e}")
            # Try fallback initialization
            try:
                from models.transaction_categorizer import TransactionCategorizer
                self.categorizer = TransactionCategorizer(use_tensorflow=False)
                logger.info("TransactionCategorizer initialized with sklearn fallback")
            except Exception as fallback_error:
                logger.error(f"Fallback initialization also failed: {fallback_error}")
                self.categorizer = None
    
    def _get_all_categories(self) -> List[Category]:
        """Fetches all categories from the database with proper error handling."""
        try:
            with get_db_session() as db:
                categories = db.query(Category).order_by(Category.name).all()
                logger.info(f"Retrieved {len(categories)} categories from database")
                return categories
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching categories: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching categories: {e}")