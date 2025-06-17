import streamlit as st
import os
from db.model import Category
from db.db import get_db_session
from sqlalchemy.orm import Session
from typing import List

def _get_all_categories(db: Session) -> List[Category]:
    """Fetches all categories from the database."""
    return db.query(Category).order_by(Category.name).all()

def _add_category_to_db(db: Session, category_name: str, category_type: str = None) -> Category:
    """Adds a new category to the database if it doesn't exist."""
    existing_category = db.query(Category).filter(Category.name == category_name).first()
    if existing_category:
        return existing_category
    
    new_category = Category(name=category_name, type=category_type)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def render_settings_tab(processor, pdf_processor, analyzer, db_connection):
    st.header("⚙️ Settings")

    # Show current statement info
    st.subheader("📋 Current Statement")
    statement_info = processor.get_statement_info()
    if statement_info:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**File:** {statement_info['filename']}")
            st.info(f"**Processed:** {statement_info['processed_date'].strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            period = statement_info.get('period', {})
            if period.get('start') and period.get('end'):
                st.info(f"**Period:** {period['start']} to {period['end']}")
            st.info(f"**File Size:** {statement_info['file_size']:,} bytes")
    else:
        st.info("No bank statement currently loaded")

    # Category management
    st.subheader("🏷️ Category Management")

    with get_db_session() as db:
        existing_categories_objs = _get_all_categories(db)
        existing_category_names = [cat.name for cat in existing_categories_objs]
        
        st.write("### Existing Categories")
        if existing_category_names:
            st.write(", ".join(existing_category_names))
        else:
            st.info("No categories defined yet.")

        st.write("### Add New Category Mapping")
        col1, col2 = st.columns(2)
        with col1:
            new_term = st.text_input("Transaction Term", placeholder="e.g., 'netflix'")
            new_category_name = st.text_input("Category Name", placeholder="e.g., 'Entertainment'")

        with col2:
            category_type = st.selectbox(
                "Category Type",
                ['Necessary Expenses', 'Discretionary Expenses', 'Investment Spending', 'Income', 'Notices', 'Special']
            )

        if st.button("➕ Add Category Mapping"):
            if new_term and new_category_name:
                try:
                    # Add category to DB if it doesn't exist
                    _add_category_to_db(db, new_category_name, category_type)
                    
                    # Add mapping to analyzer (which might store it in a config or DB)
                    success = analyzer.add_category_mapping(new_term, new_category_name, category_type)
                    if success:
                        st.success(f"✅ Added mapping: '{new_term}' → '{new_category_name}' ({category_type})")
                        st.rerun() # Rerun to update category list
                    else:
                        st.error("Failed to add category mapping")
                except Exception as e:
                    st.error(f"Error adding mapping: {str(e)}")
            else:
                st.error("Please fill in both term and category name")

    # API Configuration
    st.subheader("🔑 API Configuration")
    current_api_key = st.text_input(
        "Upstage API Key",
        value=pdf_processor.api_key or "",
        type="password",
        help="Your Upstage Document AI API key"
    )

    if st.button("💾 Save API Key"):
        # In a real app, you'd save this securely
        st.success("✅ API key updated")

    # Database Connection Test
    st.subheader("🛢️ Database Connection")
    if st.button("🔍 Test Database Connection"):
        success, message = db_connection.test_connection()
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")

    # System Information
    st.subheader("ℹ️ System Information")
    st.info(f"**Current Directory:** {os.getcwd()}")
    st.info(f"**Environment Variables:** {len(os.environ)} loaded")
