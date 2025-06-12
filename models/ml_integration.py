import streamlit as st
import pandas as pd
from models.transaction_categorizer import TransactionCategorizer
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class MLCategoryIntegration:
    """Integration layer for ML-based transaction categorization"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.categorizer = TransactionCategorizer()
    
    def render_ml_tab(self, processor):
        """Render the ML categorization tab"""
        st.header("🤖 Transaction Categorization with Local Machine Learning")
        
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
        
        # Load current data
        transactions_df = processor.load_latest_bank_statement()
        
        if transactions_df.empty:
            st.warning("No transaction data available. Please upload a bank statement first.")
            return
        
        # Training section
        st.subheader("🎯 Model Training")
        
        # Show categorization statistics
        if 'category' in transactions_df.columns:
            category_counts = transactions_df['category'].value_counts()
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
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Transaction Category Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
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
    
    def _train_model(self, transactions_df):
        """Train the ML model"""
        try:
            # Check if we have enough categorized data
            categorized_df = transactions_df[transactions_df['category'] != 'Uncategorized']
            
            if len(categorized_df) < 10:
                st.error("Need at least 10 categorized transactions to train the model.")
                st.info("Please categorize some transactions manually first.")
                return
            
            with st.spinner("Training AI model... This may take a few minutes."):
                progress_bar = st.progress(0)
                progress_bar.progress(25)
                
                # Train the model
                training_results = self.categorizer.train(transactions_df)
                progress_bar.progress(100)
                
                # Show results
                st.success("✅ Model trained successfully!")
                
                # Display training metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Training Samples", training_results['training_samples'])
                with col2:
                    st.metric("Validation Samples", training_results['validation_samples'])
                with col3:
                    accuracy = training_results['classification_report']['accuracy']
                    st.metric("Accuracy", f"{accuracy:.1%}")
                
                # Show category performance
                if st.checkbox("Show Detailed Metrics"):
                    report = training_results['classification_report']
                    metrics_df = pd.DataFrame(report).transpose()
                    metrics_df = metrics_df.drop(['accuracy', 'macro avg', 'weighted avg'])
                    st.dataframe(metrics_df.round(3))
        
        except Exception as e:
            st.error(f"Training failed: {str(e)}")
    
    def _auto_categorize_transactions(self, processor, confidence_threshold):
        """Auto-categorize uncategorized transactions"""
        try:
            transactions_df = processor.load_latest_bank_statement()
            
            if not self.categorizer.is_trained:
                st.error("Model is not trained. Please train the model first.")
                return
            
            # Count uncategorized transactions
            uncategorized_count = len(transactions_df[transactions_df['category'] == 'Uncategorized'])
            
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
                newly_categorized = len(updated_df[
                    (transactions_df['category'] == 'Uncategorized') & 
                    (updated_df['category'] != 'Uncategorized')
                ])
                
                if newly_categorized > 0:
                    st.success(f"✅ Successfully categorized {newly_categorized} transactions!")
                    
                    # Save updated data (you'll need to implement this in your processor)
                    # processor.save_categorized_data(updated_df)
                    
                    # Show newly categorized transactions
                    if st.checkbox("Show Newly Categorized Transactions"):
                        mask = (transactions_df['category'] == 'Uncategorized') & (updated_df['category'] != 'Uncategorized')
                        new_cats = updated_df[mask][['description', 'category', 'confidence']].copy()
                        st.dataframe(new_cats)
                else:
                    st.warning("No transactions met the confidence threshold for auto-categorization.")
                    st.info("Try lowering the confidence threshold or manually categorize more examples.")
        
        except Exception as e:
            st.error(f"Auto-categorization failed: {str(e)}")
    
    def _render_manual_categorization(self, transactions_df, processor):
        """Render manual categorization interface"""
        # Filter uncategorized transactions
        uncategorized_df = transactions_df[transactions_df['category'] == 'Uncategorized']
        
        if uncategorized_df.empty:
            st.info("🎉 All transactions are categorized!")
            return
        
        st.write(f"**{len(uncategorized_df)} uncategorized transactions found**")
        
        # Pagination for large datasets
        items_per_page = 10
        total_pages = (len(uncategorized_df) - 1) // items_per_page + 1
        
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
            start_idx = page * items_per_page
            end_idx = min(start_idx + items_per_page, len(uncategorized_df))
            display_df = uncategorized_df.iloc[start_idx:end_idx]
        else:
            display_df = uncategorized_df
        
        # Get existing categories
        existing_categories = list(self.analyzer.category_mappings.keys()) if hasattr(self.analyzer, 'category_mappings') else [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment', 
            'Bills & Utilities', 'Income', 'Healthcare', 'Other'
        ]
        
        # Manual categorization form
        with st.form("manual_categorization"):
            st.write("**Categorize Transactions:**")
            
            categorizations = {}
            for idx, row in display_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{row['description']}** - R{abs(row.get('debits', 0) - row.get('credits', 0)):.2f}")
                with col2:
                    category = st.selectbox(
                        "Category",
                        [""] + existing_categories,
                        key=f"cat_{idx}",
                        label_visibility="collapsed"
                    )
                    if category:
                        categorizations[idx] = category
            
            # Bulk categorization
            st.write("**Bulk Actions:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                bulk_category = st.selectbox("Apply category to all displayed", [""] + existing_categories)
            with col2:
                new_category = st.text_input("Or create new category")
            
            if st.form_submit_button("💾 Save Categorizations"):
                if bulk_category or new_category:
                    category_to_use = new_category if new_category else bulk_category
                    for idx in display_df.index:
                        categorizations[idx] = category_to_use
                
                if categorizations:
                    # Update the dataframe
                    for idx, category in categorizations.items():
                        transactions_df.loc[idx, 'category'] = category
                    
                    # Save updated data (implement this in your processor)
                    # processor.save_categorized_data(transactions_df)
                    
                    st.success(f"✅ Categorized {len(categorizations)} transactions!")
                    st.rerun()
    
    def _render_prediction_testing(self):
        """Render prediction testing interface"""
        if not self.categorizer.is_trained:
            st.info("Train the model first to test predictions.")
            return
        
        # Test single prediction
        test_description = st.text_input(
            "Test Description",
            placeholder="e.g., 'WALMART SUPERCENTER #1234'"
        )
        
        if test_description:
            category, confidence = self.categorizer.predict_single(
                test_description, 
                return_confidence=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Predicted Category:** {category}")
            with col2:
                confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.5 else "red"
                st.write(f"**Confidence:** :{confidence_color}[{confidence:.1%}]")

# Enhanced analyzer integration
def enhance_analyzer_with_ml(analyzer_class):
    """Enhance the existing analyzer with ML capabilities"""
    
    class EnhancedAnalyzer(analyzer_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ml_categorizer = TransactionCategorizer()
        
        def categorize_transactions(self, df, use_ml=True, confidence_threshold=0.7):
            """Enhanced categorization using both rules and ML"""
            # First apply rule-based categorization
            df = super().categorize_transactions(df) if hasattr(super(), 'categorize_transactions') else df
            
            # Then apply ML categorization for uncategorized transactions
            if use_ml and self.ml_categorizer.is_trained:
                df = self.ml_categorizer.auto_categorize_dataframe(df, confidence_threshold)
            
            return df
        
        def add_category_mapping(self, term, category, category_type=None):
            """Enhanced category mapping that updates ML model"""
            # Add to rule-based mapping
            result = super().add_category_mapping(term, category, category_type) if hasattr(super(), 'add_category_mapping') else True
            
            # Note: In a production system, you might want to trigger retraining
            # when enough new mappings are added
            
            return result
    
    return EnhancedAnalyzer