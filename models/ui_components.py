import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.ml_processor import MLProcessor
from db.category_db import CategoryDB

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

def render_ml_tab_ui(ml_processor: MLProcessor, processor, transactions_df: pd.DataFrame, db: CategoryDB, db_connection, data_info: Dict[str, Any], start_date: datetime, end_date: datetime):
    """Render the ML categorization tab UI components."""
    try:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>🤖 Transaction Categorization</h2>
            <p>AI-powered transaction categorization</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col2:
            st.markdown("### ⚙️ Settings")
            
            # Data source selection
            local_available = processor.get_statement_info() is not None
            db_available = db_connection.count_documents() > 0 if db_connection else False
            data_source_options = ["Auto"]
            if db_available:
                data_source_options.append("MongoDB Query")
            if local_available:
                data_source_options.append("Local File")
            
            data_source = st.selectbox(
                "Data Source:",
                data_source_options,
                index=data_source_options.index(data_info.get('source', 'Auto')) if data_info.get('source') in data_source_options else 0,
                help="Choose data source for transactions"
            )
            
            # Date range selection
            st.date_input("Start Date", start_date, key="ml_start_date")
            st.date_input("End Date", end_date, key="ml_end_date")
        
        with col1:
            if transactions_df is None or transactions_df.empty:
                st.error("❌ No transaction data available for the selected date range. Please upload a bank statement or adjust the date range.")
                if data_info:
                    with st.expander("📋 Data Source Information", expanded=False):
                        for key, value in data_info.items():
                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                return
            
            # Display data info
            if data_info:
                with st.expander("📋 Data Source Information", expanded=False):
                    for key, value in data_info.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Model status
            model_info = ml_processor.get_model_info()
            col1a, col1b, col1c = st.columns(3)
            with col1a:
                status_color = "green" if model_info.get("status") == "Trained" else "red"
                st.markdown(f"**Model Status:** :{status_color}[{model_info.get('status', 'Unknown')}]")
            with col1b:
                st.markdown(f"**Categories:** {len(model_info.get('categories', []))}")
            with col1c:
                if model_info.get("last_modified"):
                    st.markdown(f"**Last Trained:** {model_info['last_modified']}")
            
            # Categorization stats
            render_categorization_stats(transactions_df)
            
            # Training controls
            st.subheader("🎯 Model Training")
            col1a, col1b = st.columns([2, 1])
            with col1a:
                confidence_threshold = st.slider(
                    "Confidence Threshold",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Minimum confidence required for auto-categorization"
                )
            with col1b:
                st.write("")  # Spacing
                st.write("")
                if st.button("🔄 Retrain Model", type="primary"):
                    ml_processor.train_model(transactions_df)
                if st.button("✨ Auto-Categorize"):
                    ml_processor.auto_categorize_transactions(processor, transactions_df, confidence_threshold)
            
            # Manual categorization
            st.subheader("✏️ Manual Categorization")
            render_manual_categorization(transactions_df, processor, db)
            
            # Prediction testing
            st.subheader("🔍 Test Predictions")
            render_prediction_testing(ml_processor)
        
    except Exception as e:
        logger.error(f"Error rendering UI: {e}", exc_info=True)
        st.error(f"Error rendering ML tab: {e}")

def render_categorization_stats(transactions_df: pd.DataFrame):
    """Render categorization statistics."""
    try:
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
        
        if len(category_counts) > 1:
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Transaction Category Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error rendering stats: {e}", exc_info=True)
        st.error("Could not display categorization statistics")

def render_manual_categorization(transactions_df: pd.DataFrame, processor, db: CategoryDB):
    """Render manual categorization interface."""
    try:
        uncategorized_mask = (
            (transactions_df['category_name'] == 'Uncategorized') | 
            (transactions_df['category_name'].isna())
        )
        uncategorized_df = transactions_df[uncategorized_mask]
        
        if uncategorized_df.empty:
            st.info("🎉 All transactions are categorized!")
            return
        
        st.write(f"**{len(uncategorized_df)} uncategorized transactions found**")
        
        items_per_page = 10
        total_pages = max(1, (len(uncategorized_df) - 1) // items_per_page + 1)
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1) - 1
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(uncategorized_df))
        display_df = uncategorized_df.iloc[start_idx:end_idx]
        
        existing_categories = [cat['name'] for cat in db.get_all_categories() if cat and cat.get('name')]
        if not existing_categories:
            existing_categories = ['Food', 'Transport', 'Shopping', 'Bills', 'Income', 'Other']
        
        with st.form("manual_categorization"):
            categorizations = {}
            for idx, row in display_df.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    amount = abs(row.get('debits', 0) - row.get('credits', 0)) or abs(row.get('amount', 0))
                    description = str(row.get('description', 'Unknown'))[:50]
                    st.write(f"**{description}** - R{amount:.2f}")
                with col2:
                    category_name = st.selectbox(
                        "Category",
                        [""] + existing_categories,
                        key=f"cat_{idx}",
                        label_visibility="collapsed"
                    )
                    if category_name:
                        categorizations[idx] = category_name
            
            st.write("**Bulk Actions:**")
            col1, col2 = st.columns(2)
            with col1:
                bulk_category_name = st.selectbox(
                    "Apply category to all displayed", 
                    [""] + existing_categories
                )
            with col2:
                new_category_name = st.text_input("Or create new category")
            
            if st.form_submit_button("💾 Save Categorizations"):
                try:
                    if bulk_category_name or new_category_name:
                        category_to_use = new_category_name if new_category_name else bulk_category_name
                        if category_to_use:
                            db.add_category(category_to_use)
                            for idx in display_df.index:
                                categorizations[idx] = category_to_use
                    
                    if categorizations:
                        for idx, category_name in categorizations.items():
                            transactions_df.loc[idx, 'category_name'] = category_name
                        processor.save_categorized_data(transactions_df)
                        st.success(f"✅ Categorized {len(categorizations)} transactions!")
                        st.rerun()
                    else:
                        st.warning("No categorizations to save")
                except Exception as e:
                    logger.error(f"Error saving categorizations: {e}", exc_info=True)
                    st.error(f"Error saving categorizations: {e}")
    except Exception as e:
        logger.error(f"Error in manual categorization: {e}", exc_info=True)
        st.error(f"Error in manual categorization: {e}")

def render_prediction_testing(ml_processor: MLProcessor):
    """Render prediction testing interface."""
    try:
        if not ml_processor.is_trained():
            st.info("Train the model first to test predictions.")
            return
        
        test_description = st.text_input(
            "Test Description",
            placeholder="e.g., 'WALMART SUPERCENTER #1234'"
        )
        
        if test_description:
            category, confidence = ml_processor.predict_single(test_description)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Predicted Category:** {category}")
            with col2:
                confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.5 else "red"
                st.write(f"**Confidence:** :{confidence_color}[{confidence:.1%}]")
    except Exception as e:
        logger.error(f"Error in prediction testing: {e}", exc_info=True)
        st.error(f"Prediction failed: {e}")
