import streamlit as st
import pandas as pd
from models.transaction_categorizer import TransactionCategorizer
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
            return []

    def _get_category_by_name(self, category_name: str) -> Optional[Category]:
        """Fetches a category by name from the database with proper error handling."""
        if not category_name:
            return None
        
        try:
            with get_db_session() as db:
                category = db.query(Category).filter(Category.name == category_name).first()
                return category
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching category '{category_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching category '{category_name}': {e}")
            return None

    def _add_category_to_db(self, category_name: str, category_type: str = None) -> Optional[Category]:
        """Adds a new category to the database if it doesn't exist with proper error handling."""
        if not category_name:
            return None
        
        try:
            with get_db_session() as db:
                # Check if category already exists
                existing_category = db.query(Category).filter(Category.name == category_name).first()
                if existing_category:
                    logger.info(f"Category '{category_name}' already exists")
                    return existing_category
                
                # Create new category
                new_category = Category(name=category_name, type=category_type or 'Expense')
                db.add(new_category)
                db.commit()
                db.refresh(new_category)
                logger.info(f"Created new category: '{category_name}'")
                return new_category
                
        except SQLAlchemyError as e:
            logger.error(f"Database error creating category '{category_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating category '{category_name}': {e}")
            return None

    def render_ml_tab(self, processor):
        """Render the ML categorization tab with comprehensive error handling"""
        st.header("🤖 Transaction Categorization with Local Machine Learning")
        
        # Check if categorizer is available
        if self.categorizer is None:
            st.error("❌ ML Categorizer failed to initialize. Please check the logs.")
            return
        
        try:
            # Model status
            model_info = self.categorizer.get_model_info()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                status_color = "green" if model_info.get("status") == "Trained" else "red"
                st.markdown(f"**Model Status:** :{status_color}[{model_info.get('status', 'Unknown')}]")
            
            with col2:
                if model_info.get("categories"):
                    st.markdown(f"**Categories:** {len(model_info['categories'])}")
                else:
                    st.markdown("**Categories:** 0")
            
            with col3:
                if model_info.get("last_modified"):
                    st.markdown(f"**Last Trained:** {model_info['last_modified']}")
            
            # Load current data with error handling
            try:
                transactions_df = processor.load_latest_bank_statement()
                if transactions_df is None or transactions_df.empty:
                    st.warning("No transaction data available. Please upload a bank statement first.")
                    return
            except Exception as e:
                st.error(f"Error loading transaction data: {e}")
                logger.error(f"Error loading transactions: {traceback.format_exc()}")
                return
            
            # Ensure 'category_name' column exists for ML model
            if 'category_name' not in transactions_df.columns:
                transactions_df['category_name'] = 'Uncategorized'
            
            # Fill any NaN values in category_name
            transactions_df['category_name'] = transactions_df['category_name'].fillna('Uncategorized')
            
            # Training section
            st.subheader("🎯 Model Training")
            
            # Show categorization statistics
            self._render_categorization_stats(transactions_df)
            
            # Training controls
            col1, col2 = st.columns([2, 1])
            with col1:
                confidence_threshold = st.slider(
                    "Confidence Threshold",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Minimum confidence required for auto-categorization"
                )
            
            with col2:
                st.write("")  # Spacing
                st.write("")
                
                # Training button
                if st.button("🔄 Retrain Model", type="primary"):
                    self._train_model(transactions_df)
                
                # Auto-categorize button
                if st.button("✨ Auto-Categorize"):
                    self._auto_categorize_transactions(processor, confidence_threshold)
            
            # Manual categorization section
            st.subheader("✏️ Manual Categorization")
            self._render_manual_categorization(transactions_df, processor)
            
            # Prediction testing
            st.subheader("🔍 Test Predictions")
            self._render_prediction_testing()
            
        except Exception as e:
            st.error(f"Error in ML tab: {e}")
            logger.error(f"Error in render_ml_tab: {traceback.format_exc()}")
    
    def _render_categorization_stats(self, transactions_df: pd.DataFrame):
        """Render categorization statistics with error handling"""
        try:
            if 'category_name' in transactions_df.columns:
                category_counts = transactions_df['category_name'].value_counts()
                uncategorized_count = category_counts.get('Uncategorized', 0)
                categorized_count = len(transactions_df) - uncategorized_count
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Transactions", len(transactions_df))
                with col2:
                    st.metric("Categorized", categorized_count)
                with col3:
                    st.metric("Uncategorized", uncategorized_count)
                
                # Category distribution chart
                if len(category_counts) > 1:
                    try:
                        fig = px.pie(
                            values=category_counts.values,
                            names=category_counts.index,
                            title="Transaction Category Distribution"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        logger.error(f"Error creating pie chart: {e}")
                        st.error("Could not display category distribution chart")
        except Exception as e:
            logger.error(f"Error rendering categorization stats: {e}")
            st.error("Could not display categorization statistics")
    
    def _train_model(self, transactions_df: pd.DataFrame):
        """Train the ML model with comprehensive error handling"""
        try:
            # Check if we have enough categorized data
            categorized_df = transactions_df[
                (transactions_df['category_name'] != 'Uncategorized') & 
                (transactions_df['category_name'].notna())
            ]
            
            if len(categorized_df) < 10:
                st.error("Need at least 10 categorized transactions to train the model.")
                st.info("Please categorize some transactions manually first.")
                return
            
            with st.spinner("Training AI model... This may take a few minutes."):
                progress_bar = st.progress(0)
                progress_bar.progress(25)
                
                # Ensure categorizer is available
                if self.categorizer is None:
                    st.error("Categorizer not available")
                    return
                
                # Train the model
                training_results = self.categorizer.train(transactions_df)
                progress_bar.progress(100)
                
                # Show results
                st.success("✅ Model trained successfully!")
                
                # Display training metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Training Samples", training_results.get('training_samples', 0))
                with col2:
                    st.metric("Validation Samples", training_results.get('validation_samples', 0))
                with col3:
                    accuracy = training_results.get('classification_report', {}).get('accuracy', 0)
                    st.metric("Accuracy", f"{accuracy:.1%}")
                
                # Show category performance
                if st.checkbox("Show Detailed Metrics"):
                    report = training_results.get('classification_report', {})
                    if report:
                        try:
                            metrics_df = pd.DataFrame(report).transpose()
                            metrics_df = metrics_df.drop(['accuracy', 'macro avg', 'weighted avg'], errors='ignore')
                            st.dataframe(metrics_df.round(3))
                        except Exception as e:
                            logger.error(f"Error displaying metrics: {e}")
                            st.error("Could not display detailed metrics")
        
        except Exception as e:
            st.error(f"Training failed: {str(e)}")
            logger.error(f"Training error: {traceback.format_exc()}")
    
    def _auto_categorize_transactions(self, processor, confidence_threshold: float):
        """Auto-categorize uncategorized transactions with proper error handling"""
        try:
            transactions_df = processor.load_latest_bank_statement()
            
            if self.categorizer is None or not self.categorizer.is_trained:
                st.error("Model is not trained. Please train the model first.")
                return
            
            # Count uncategorized transactions
            uncategorized_mask = (
                (transactions_df['category_name'] == 'Uncategorized') | 
                (transactions_df['category_name'].isna())
            )
            uncategorized_count = uncategorized_mask.sum()
            
            if uncategorized_count == 0:
                st.info("All transactions are already categorized!")
                return
            
            with st.spinner(f"Auto-categorizing {uncategorized_count} transactions..."):
                # Auto-categorize
                updated_df = self.categorizer.auto_categorize_dataframe(
                    transactions_df, 
                    confidence_threshold=confidence_threshold
                )
                
                # Count successful categorizations
                newly_categorized_mask = uncategorized_mask & (updated_df['category_name'] != 'Uncategorized')
                newly_categorized = newly_categorized_mask.sum()
                
                if newly_categorized > 0:
                    st.success(f"✅ Successfully categorized {newly_categorized} transactions!")
                    
                    # Save updated data with error handling
                    try:
                        if hasattr(processor, 'save_categorized_data'):
                            processor.save_categorized_data(updated_df)
                        else:
                            st.warning("Unable to save categorized data - method not available")
                    except Exception as e:
                        st.error(f"Error saving categorized data: {e}")
                        logger.error(f"Save error: {traceback.format_exc()}")
                    
                    # Show newly categorized transactions
                    if st.checkbox("Show Newly Categorized Transactions"):
                        try:
                            new_cats = updated_df[newly_categorized_mask][
                                ['description', 'category_name', 'confidence']
                            ].copy()
                            st.dataframe(new_cats)
                        except Exception as e:
                            logger.error(f"Error displaying newly categorized: {e}")
                            st.error("Could not display newly categorized transactions")
                else:
                    st.warning("No transactions met the confidence threshold for auto-categorization.")
                    st.info("Try lowering the confidence threshold or manually categorize more examples.")
        
        except Exception as e:
            st.error(f"Auto-categorization failed: {str(e)}")
            logger.error(f"Auto-categorization error: {traceback.format_exc()}")
    
    def _render_manual_categorization(self, transactions_df: pd.DataFrame, processor):
        """Render manual categorization interface with error handling"""
        try:
            # Filter uncategorized transactions
            uncategorized_mask = (
                (transactions_df['category_name'] == 'Uncategorized') | 
                (transactions_df['category_name'].isna())
            )
            uncategorized_df = transactions_df[uncategorized_mask]
            
            if uncategorized_df.empty:
                st.info("🎉 All transactions are categorized!")
                return
            
            st.write(f"**{len(uncategorized_df)} uncategorized transactions found**")
            
            # Pagination for large datasets
            items_per_page = 10
            total_pages = max(1, (len(uncategorized_df) - 1) // items_per_page + 1)
            
            if total_pages > 1:
                page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
                start_idx = page * items_per_page
                end_idx = min(start_idx + items_per_page, len(uncategorized_df))
                display_df = uncategorized_df.iloc[start_idx:end_idx]
            else:
                display_df = uncategorized_df
            
            # Get existing categories from DB with error handling
            existing_categories_objs = self._get_all_categories()
            existing_category_names = [cat.name for cat in existing_categories_objs if cat and cat.name]
            
            # Add default categories if none exist
            if not existing_category_names:
                existing_category_names = ['Food', 'Transport', 'Shopping', 'Bills', 'Income', 'Other']
            
            # Manual categorization form
            with st.form("manual_categorization"):
                st.write("**Categorize Transactions:**")
                
                categorizations = {}  # Stores {idx: category_name}
                
                for idx, row in display_df.iterrows():
                    try:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            # Safely get amount
                            amount = abs(row.get('debits', 0) - row.get('credits', 0))
                            if amount == 0:
                                amount = abs(row.get('amount', 0))
                            
                            description = str(row.get('description', 'Unknown'))[:50]
                            st.write(f"**{description}** - R{amount:.2f}")
                        
                        with col2:
                            category_name = st.selectbox(
                                "Category",
                                [""] + existing_category_names,
                                key=f"cat_{idx}",
                                label_visibility="collapsed"
                            )
                            if category_name:
                                categorizations[idx] = category_name
                    
                    except Exception as e:
                        logger.error(f"Error rendering transaction {idx}: {e}")
                        continue
                
                # Bulk categorization
                st.write("**Bulk Actions:**")
                col1, col2 = st.columns(2)
                with col1:
                    bulk_category_name = st.selectbox(
                        "Apply category to all displayed", 
                        [""] + existing_category_names
                    )
                with col2:
                    new_category_name = st.text_input("Or create new category")
                
                if st.form_submit_button("💾 Save Categorizations"):
                    try:
                        # Handle bulk categorization
                        if bulk_category_name or new_category_name:
                            category_to_use = new_category_name if new_category_name else bulk_category_name
                            if category_to_use:
                                # Ensure new category is added to DB if it doesn't exist
                                self._add_category_to_db(category_to_use)
                                for idx in display_df.index:
                                    categorizations[idx] = category_to_use
                        
                        if categorizations:
                            # Update the dataframe with category names
                            for idx, category_name in categorizations.items():
                                transactions_df.loc[idx, 'category_name'] = category_name
                            
                            # Save updated data with error handling
                            try:
                                if hasattr(processor, 'save_categorized_data'):
                                    processor.save_categorized_data(transactions_df)
                                    st.success(f"✅ Categorized {len(categorizations)} transactions!")
                                    st.rerun()
                                else:
                                    st.error("Save method not available")
                            except Exception as e:
                                st.error(f"Error saving categorizations: {e}")
                                logger.error(f"Save categorizations error: {traceback.format_exc()}")
                        else:
                            st.warning("No categorizations to save")
                    
                    except Exception as e:
                        st.error(f"Error processing categorizations: {e}")
                        logger.error(f"Categorization processing error: {traceback.format_exc()}")
        
        except Exception as e:
            st.error(f"Error in manual categorization: {e}")
            logger.error(f"Manual categorization error: {traceback.format_exc()}")
    
    def _render_prediction_testing(self):
        """Render prediction testing interface with error handling"""
        try:
            if self.categorizer is None or not self.categorizer.is_trained:
                st.info("Train the model first to test predictions.")
                return
            
            # Test single prediction
            test_description = st.text_input(
                "Test Description",
                placeholder="e.g., 'WALMART SUPERCENTER #1234'"
            )
            
            if test_description:
                try:
                    result = self.categorizer.predict_single(
                        test_description, 
                        return_confidence=True
                    )
                    
                    if isinstance(result, tuple):
                        category, confidence = result
                    else:
                        category, confidence = result, 0.0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Predicted Category:** {category}")
                    with col2:
                        confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.5 else "red"
                        st.write(f"**Confidence:** :{confidence_color}[{confidence:.1%}]")
                
                except Exception as e:
                    st.error(f"Prediction failed: {e}")
                    logger.error(f"Prediction error: {traceback.format_exc()}")
        
        except Exception as e:
            st.error(f"Error in prediction testing: {e}")
            logger.error(f"Prediction testing error: {traceback.format_exc()}")


# Enhanced analyzer integration with proper error handling
def enhance_analyzer_with_ml(analyzer_class):
    """Enhance the existing analyzer with ML capabilities"""
    
    class EnhancedAnalyzer(analyzer_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                self.ml_categorizer = TransactionCategorizer()
                logger.info("ML categorizer initialized in enhanced analyzer")
            except Exception as e:
                logger.error(f"Failed to initialize ML categorizer in enhanced analyzer: {e}")
                self.ml_categorizer = None
        
        def categorize_transactions(self, df: pd.DataFrame, use_ml: bool = True, confidence_threshold: float = 0.7) -> pd.DataFrame:
            """Enhanced categorization using both rules and ML with error handling."""
            try:
                # Ensure 'category_name' column exists
                if 'category_name' not in df.columns:
                    df['category_name'] = 'Uncategorized'
                
                # Fill any NaN values
                df['category_name'] = df['category_name'].fillna('Uncategorized')
                
                # First apply rule-based categorization (if method exists)
                if hasattr(super(), 'categorize_transactions'):
                    try:
                        df = super().categorize_transactions(df)
                    except Exception as e:
                        logger.error(f"Error in rule-based categorization: {e}")
                
                # Then apply ML categorization for uncategorized transactions
                if use_ml and self.ml_categorizer and self.ml_categorizer.is_trained:
                    try:
                        df = self.ml_categorizer.auto_categorize_dataframe(df, confidence_threshold)
                    except Exception as e:
                        logger.error(f"Error in ML categorization: {e}")
                
                return df
            
            except Exception as e:
                logger.error(f"Error in categorize_transactions: {e}")
                return df
        
        def add_category_mapping(self, term: str, category_name: str, category_type: str = None) -> bool:
            """Enhanced category mapping with proper error handling."""
            try:
                # Add to rule-based mapping (if method exists)
                result = True
                if hasattr(super(), 'add_category_mapping'):
                    try:
                        result = super().add_category_mapping(term, category_name, category_type)
                    except Exception as e:
                        logger.error(f"Error in rule-based category mapping: {e}")
                        result = False
                
                # Ensure category exists in the database
                try:
                    with get_db_session() as db:
                        existing_category = db.query(Category).filter(Category.name == category_name).first()
                        if not existing_category:
                            new_category = Category(name=category_name, type=category_type or 'Expense')
                            db.add(new_category)
                            db.commit()
                            db.refresh(new_category)
                            logger.info(f"Added category to database: {category_name}")
                except SQLAlchemyError as e:
                    logger.error(f"Database error adding category: {e}")
                    result = False
                except Exception as e:
                    logger.error(f"Unexpected error adding category: {e}")
                    result = False
                
                return result
            
            except Exception as e:
                logger.error(f"Error in add_category_mapping: {e}")
                return False
    
    return EnhancedAnalyzer