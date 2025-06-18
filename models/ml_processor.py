import streamlit as st
import pandas as pd
import psutil
import logging
from typing import Dict, Any, Tuple
from models.transaction_categorizer import TransactionCategorizer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

class MLProcessor:
    """Handles ML model interactions with memory management and logging."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        self.categorizer = categorizer
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information with error handling."""
        try:
            return self.categorizer.get_model_info()
        except Exception as e:
            logger.error(f"Error getting model info: {e}", exc_info=True)
            return {"status": "Error", "error": str(e)}
    
    def is_trained(self) -> bool:
        """Check if the model is trained."""
        return self.categorizer.is_trained
    
    def train_model(self, transactions_df: pd.DataFrame):
        """Train the ML model with memory monitoring."""
        try:
            categorized_df = transactions_df[
                (transactions_df['category_name'] != 'Uncategorized') & 
                (transactions_df['category_name'].notna())
            ]
            
            if len(categorized_df) < 10:
                logger.warning("Insufficient categorized data for training")
                st.error("Need at least 10 categorized transactions to train the model.")
                return
            
            process = psutil.Process()
            with st.spinner("Training AI model..."):
                progress_bar = st.progress(0)
                training_results = self.categorizer.train(categorized_df)
                progress_bar.progress(100)
                
                st.success("✅ Model trained successfully!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Training Samples", training_results.get('training_samples', 0))
                with col2:
                    st.metric("Validation Samples", training_results.get('validation_samples', 0))
                with col3:
                    accuracy = training_results.get('classification_report', {}).get('accuracy', 0)
                    st.metric("Accuracy", f"{accuracy:.1%}")
                
                logger.info(f"Model trained. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                
                if st.checkbox("Show Detailed Metrics"):
                    report = training_results.get('classification_report', {})
                    if report:
                        metrics_df = pd.DataFrame(report).transpose()
                        metrics_df = metrics_df.drop(['accuracy', 'macro avg', 'weighted avg'], errors='ignore')
                        st.dataframe(metrics_df.round(3))
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            st.error(f"Training failed: {e}")
    
    def auto_categorize_transactions(self, processor, transactions_df: pd.DataFrame, confidence_threshold: float):
        """Auto-categorize transactions with memory monitoring."""
        try:
            if not self.categorizer.is_trained:
                logger.warning("Model not trained")
                st.error("Model is not trained. Please train the model first.")
                return
            
            uncategorized_mask = (
                (transactions_df['category_name'] == 'Uncategorized') | 
                (transactions_df['category_name'].isna())
            )
            uncategorized_count = uncategorized_mask.sum()
            
            if uncategorized_count == 0:
                logger.info("All transactions already categorized")
                st.info("All transactions are already categorized!")
                return
            
            process = psutil.Process()
            with st.spinner(f"Auto-categorizing {uncategorized_count} transactions..."):
                updated_df = self.categorizer.auto_categorize_dataframe(
                    transactions_df, 
                    confidence_threshold=confidence_threshold
                )
                
                newly_categorized_mask = uncategorized_mask & (updated_df['category_name'] != 'Uncategorized')
                newly_categorized = newly_categorized_mask.sum()
                
                if newly_categorized > 0:
                    processor.save_categorized_data(updated_df)
                    st.success(f"✅ Successfully categorized {newly_categorized} transactions!")
                    logger.info(f"Categorized {newly_categorized} transactions. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    
                    if st.checkbox("Show Newly Categorized Transactions"):
                        new_cats = updated_df[newly_categorized_mask][['description', 'category_name', 'confidence']].copy()
                        st.dataframe(new_cats)
                else:
                    logger.info("No transactions met confidence threshold")
                    st.warning("No transactions met the confidence threshold for auto-categorization.")
        except Exception as e:
            logger.error(f"Auto-categorization failed: {e}", exc_info=True)
            st.error(f"Auto-categorization failed: {e}")
    
    def predict_single(self, description: str) -> Tuple[str, float]:
        """Predict category for a single description."""
        try:
            result = self.categorizer.predict_single(description, return_confidence=True)
            return result if isinstance(result, tuple) else (result, 0.0)
        except Exception as e:
            logger.error(f"Prediction failed for '{description}': {e}", exc_info=True)
            return 'Uncategorized', 0.0