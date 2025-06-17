from typing import List, Optional
import logging
from supabase import create_client, Client

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
        try:
            self.supabase: Client = create_client(
                os.getenv("SUPABASE_URL"),
                os.getenv("SUPABASE_KEY")
            )
            logger.debug("Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            self.supabase = None
    
    def get_all_categories(self) -> List[dict]:
        """Fetch all categories from Supabase."""
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                return []
            response = self.supabase.table("categories").select("*").order("name").execute()
            categories = response.data
            logger.info(f"Retrieved {len(categories)} categories from Supabase")
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories from Supabase: {e}", exc_info=True)
            return []
    
    def get_category_by_name(self, category_name: str) -> Optional[dict]:
        """Fetch a category by name from Supabase."""
        if not category_name:
            logger.warning("Empty category name provided")
            return None
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                return None
            response = self.supabase.table("categories").select("*").eq("name", category_name).execute()
            category = response.data[0] if response.data else None
            logger.debug(f"Fetched category: {category_name}")
            return category
        except Exception as e:
            logger.error(f"Error fetching category '{category_name}' from Supabase: {e}", exc_info=True)
            return None
    
    def add_category(self, category_name: str, category_type: str = None) -> Optional[dict]:
        """Add a new category to Supabase if it doesn't exist."""
        if not category_name:
            logger.warning("Empty category name provided")
            return None
        try:
            if not self.supabase:
                logger.error("Supabase client not initialized")
                return None
            existing_category = self.get_category_by_name(category_name)
            if existing_category:
                logger.info(f"Category '{category_name}' already exists")
                return existing_category
            new_category = {"name": category_name, "type": category_type or "Expense"}
            response = self.supabase.table("categories").insert(new_category).execute()
            logger.info(f"Created new category: '{category_name}'")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating category '{category_name}' in Supabase: {e}", exc_info=True)
            return None