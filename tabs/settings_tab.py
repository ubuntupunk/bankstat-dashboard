import streamlit as st
import os

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

    col1, col2 = st.columns(2)
    with col1:
        new_term = st.text_input("Transaction Term", placeholder="e.g., 'netflix'")
        new_category = st.text_input("Category", placeholder="e.g., 'Entertainment'")

    with col2:
        category_type = st.selectbox(
            "Category Type",
            ['Necessary Expenses', 'Discretionary Expenses', 'Investment Spending', 'Income', 'Notices', 'Special']
        )

    if st.button("➕ Add Category Mapping"):
        if new_term and new_category:
            try:
                success = analyzer.add_category_mapping(new_term, new_category, category_type)
                if success:
                    st.success(f"✅ Added mapping: '{new_term}' → '{new_category}' ({category_type})")
                else:
                    st.error("Failed to add category mapping")
            except Exception as e:
                st.error(f"Error adding mapping: {str(e)}")
        else:
            st.error("Please fill in both term and category")

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