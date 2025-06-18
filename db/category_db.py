from typing import List, Optional
import logging
import os
from supabase import create_client, Client
from config import Config
from utils.utils import debug_write

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

class CategoryDB:
    """Database operations for categories using Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        debug_write("Initializing CategoryDB Supabase client.")
        try:
            config = Config()
            supabase_url = config.supabase_url
            supabase_key = config.supabase_api_key
            
            if not supabase_url or not supabase_key:
                debug_write("Supabase URL or Key not found in config.")
                logger.error("Supabase URL or Key not found in config.")
                self.supabase = None
                return

            self.supabase: Client = create_client(
                supabase_url,
                supabase_key
            )
            logger.debug("Supabase client initialized")
            debug_write("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            debug_write(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
    
    def get_all_categories(self) -> List[dict]:
        """Fetch all categories from Supabase."""
        debug_write("Attempting to fetch all categories from Supabase.")
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                return []
            response = self.supabase.table("categories").select("*").order("name").execute()
            categories = response.data
            logger.info(f"Retrieved {len(categories)} categories from Supabase")
            debug_write(f"Retrieved {len(categories)} categories from Supabase.")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories from Supabase: {e}", exc_info=True)
            debug_write(f"Error fetching categories from Supabase: {e}")
            return []
    
    def get_category_by_name(self, category_name: str) -> Optional[dict]:
        """Fetch a category by name from Supabase."""
        debug_write(f"Attempting to fetch category by name: {category_name}")
        if not category_name:
            logger.warning("Empty category name provided")
            debug_write("Empty category name provided for get_category_by_name.")
            return None
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                debug_write("Supabase client not initialized for get_category_by_name.")
                return None
            response = self.supabase.table("categories").select("*").eq("name", category_name).execute()
            category = response.data[0] if response.data else None
            logger.debug(f"Fetched category: {category_name}")
            debug_write(f"Fetched category by name '{category_name}': {category}")
            return category
        except Exception as e:
            logger.error(f"Error fetching category '{category_name}' from Supabase: {e}", exc_info=True)
            debug_write(f"Error fetching category '{category_name}' from Supabase: {e}")
            return None
    
    def add_category(self, category_name: str, category_type: str = None) -> Optional[dict]:
        """Add a new category to Supabase if it doesn't exist."""
        debug_write(f"Attempting to add category: {category_name} (Type: {category_type})")
        if not category_name:
            logger.warning("Empty category name provided")
            debug_write("Empty category name provided for add_category.")
            return None
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                debug_write("Supabase client not initialized for add_category.")
                return None
            existing_category = self.get_category_by_name(category_name)
            if existing_category:
                logger.info(f"Category '{category_name}' already exists")
                debug_write(f"Category '{category_name}' already exists.")
                return existing_category
            new_category = {"name": category_name, "type": category_type or "Expense"}
            response = self.supabase.table("categories").insert(new_category).execute()
            logger.info(f"Created new category: '{category_name}'")
            debug_write(f"Created new category: '{category_name}'. Response: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating category '{category_name}' in Supabase: {e}", exc_info=True)
            debug_write(f"Error creating category '{category_name}' in Supabase: {e}")
            return None
