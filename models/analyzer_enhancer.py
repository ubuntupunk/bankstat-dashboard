import pandas as pd
import logging
from supabase import create_client, Client
from models.transaction_categorizer import TransactionCategorizer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

def enhance_analyzer_with_ml(analyzer_class):
    """Enhance the existing analyzer with ML capabilities."""
    
    class EnhancedAnalyzer(analyzer_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                self.ml_categorizer = TransactionCategorizer(use_tensorflow=False)
                self.supabase = create_client(
                    os.getenv("SUPABASE_URL"),
                    os.getenv("SUPABASE_KEY")
                )
                logger.info("ML categorizer and Supabase client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ML categorizer or Supabase: {e}", exc_info=True)
                self.ml_categorizer = None
                self.supabase = None
        
        def categorize_transactions(self, df: pd.DataFrame, use_ml: bool = True, confidence_threshold: float = 0.7) -> pd.DataFrame:
            """Enhanced categorization using both rules and ML."""
            try:
                if 'category_name' not in df.columns:
                    df['category_name'] = 'Uncategorized'
                df['category_name'] = df['category_name'].fillna('Uncategorized')
                
                if hasattr(super(), 'categorize_transactions'):
                    df = super().categorize_transactions(df)
                
                if use_ml and self.ml_categorizer and self.ml_categorizer.is_trained:
                    df = self.ml_categorizer.auto_categorize_dataframe(df, confidence_threshold)
                
                logger.debug(f"Categorized dataframe with {len(df)} rows")
                return df
            except Exception as e:
                logger.error(f"Error in categorize_transactions: {e}", exc_info=True)
                return df
        
        def add_category_mapping(self, term: str, category_name: str, category_type: str = None) -> bool:
            """Enhanced category mapping with Supabase integration."""
            try:
                result = True
                if hasattr(super(), 'add_category_mapping'):
                    result = super().add_category_mapping(term, category_name, category_type)
                
                if not self.supabase:
                    logger.error("Supabase client not initialized")
                    return False
                
                existing_category = self.supabase.table("categories").select("*").eq("name", category_name).execute().data
                if not existing_category:
                    new_category = {"name": category_name, "type": category_type or "Expense"}
                    self.supabase.table("categories").insert(new_category).execute()
                    logger.info(f"Added category to Supabase: {category_name}")
                
                return result
            except Exception as e:
                logger.error(f"Error adding category to Supabase: {e}", exc_info=True)
                return False
    
    return EnhancedAnalyzer