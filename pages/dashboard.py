import streamlit as st
from datetime import datetime, timedelta
import os
from propelauth_utils import auth # Import auth utility

# Import necessary components from the original files
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from processing import StreamlitAnalytics
from connection import DatabaseConnection
from financial_analyzer import FinancialAnalyzer
from pdf_processor import StreamlitBankProcessor

# Import render functions from the existing tabs directory
from tabs.upload_tab import render_upload_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.settings_tab import render_settings_tab
from tabs.tools_tab import render_tools_tab

# Configure page
st.set_page_config(
    page_title="Bankstat Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Retrieve user information
if st.user.is_logged_in:
    user = auth.get_user(st.user.sub)
    if not user:
        st.error("Failed to retrieve user information. Redirecting to home page.")
        st.switch_page("home") # Redirect to home if user info can't be fetched
else:
    st.switch_page("home") # Redirect to home if not logged in

# Ensure user is available before proceeding
if user:
    # Sidebar content (similar to original streamlit_app.py)
    with st.sidebar:
        st.image("bankstatgreen.png", use_container_width=True)
        st.header("User")
        st.text(f"Logged in as {user.email} (ID: {user.user_id})")
        st.link_button('Account', auth.get_account_url(), use_container_width=True)
        st.button('Logout', on_click=lambda: st.switch_page("logout"), key="sidebar_logout_button") # Changed to "logout"
        st.header("Navigation")

        tab_selection = st.radio(
            "Choose Action:",
            ["📊 View Dashboard", "📁 Upload & Process", "🧮 Tools", "⚙️ Settings", "Logout"],
            key="dashboard_navigation_radio"
        )
        st.header("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.now() - timedelta(days=30), key="dashboard_start_date")
        with col2:
            end_date = st.date_input("To", datetime.now(), key="dashboard_end_date")

    # Header
    st.markdown(f'<h1 class="main-header">🏦 Bankstat Dashboard - Welcome {user.email}</h1>', unsafe_allow_html=True)

    # Initialize components (these were in streamlit_app.py main function)
    processor = StreamlitAnalytics()
    db_connection = DatabaseConnection()
    pdf_processor = StreamlitBankProcessor()
    analyzer = FinancialAnalyzer(base_analyzer=processor)

    # Render selected tab content by calling the respective render functions
    if tab_selection == "📁 Upload & Process":
        render_upload_tab(pdf_processor, processor, db_connection)
    elif tab_selection == "📊 View Dashboard":
        render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date)
    elif tab_selection == "🧮 Tools":
        render_tools_tab()
    elif tab_selection == "⚙️ Settings":
        render_settings_tab(processor, pdf_processor, analyzer, db_connection)
    elif tab_selection == "Logout":
        auth.log_out(st.user.sub)
        st.switch_page("home")