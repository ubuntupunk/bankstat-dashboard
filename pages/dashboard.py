import streamlit as st
from datetime import datetime, timedelta
from propelauth_utils import auth
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from processing import StreamlitAnalytics
from connection import DatabaseConnection
from financial_analyzer import FinancialAnalyzer
from pdf_processor import StreamlitBankProcessor
from utils import debug_write
from tabs.upload_tab import render_upload_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.settings_tab import render_settings_tab
from tabs.tools_tab import render_tools_tab
from tabs.goals_tab import render_goals_tab
from tabs.ai_expert_tab import render_ai_advisor_tab

# CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Get user info from PropelAuth
user = auth.get_user(st.user.sub) if hasattr(st, 'user') and hasattr(st.user, 'sub') else None
user_email = user.email if user and hasattr(user, 'email') else "User"
user_id = user.sub if user and hasattr(user, 'sub') else "Unknown"

# Initialize session state
if "dashboard_navigation_radio" not in st.session_state:
    st.session_state.dashboard_navigation_radio = "📊 View Dashboard"
if "dashboard_start_date" not in st.session_state:
    st.session_state.dashboard_start_date = datetime.now() - timedelta(days=30)
if "dashboard_end_date" not in st.session_state:
    st.session_state.dashboard_end_date = datetime.now()

# Sidebar
with st.sidebar:
    st.image("bankstatgreen.png", use_container_width=True)
    st.header("User")
    st.text(f"Logged in as {user_email} (ID: {user_id})")
    st.link_button('Account', auth.get_account_url(), use_container_width=True)
    st.header("Navigation")

    tab_selection = st.radio(
        "Choose Action:",
        ["Ask Bankstat", "📊 View Dashboard", "📁 Upload & Process", "🎯 Goals", "🧮 Tools", "⚙️ Settings", "🔒 Logout"],
        index=0,
        key="dashboard_navigation_radio"
    )
    st.header("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", st.session_state.dashboard_start_date, key="dashboard_start_date")
    with col2:
        end_date = st.date_input("To", st.session_state.dashboard_end_date, key="dashboard_end_date")

# Header
st.markdown(f'<h1 class="main-header">🏦 Bankstat Dashboard - Welcome {user_email}</h1>', unsafe_allow_html=True)

# Initialize components
processor = StreamlitAnalytics()
db_connection = DatabaseConnection()
pdf_processor = StreamlitBankProcessor()
analyzer = FinancialAnalyzer(base_analyzer=processor)

# Render tab content
if tab_selection == "📁 Upload & Process":
    render_upload_tab(pdf_processor, processor, db_connection)
elif tab_selection == "Ask Bankstat":
    render_ai_advisor_tab()
elif tab_selection == "📊 View Dashboard":
    debug_write("Debug: Calling render_dashboard_tab")
    render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date)
elif tab_selection == "🎯 Goals":
    render_goals_tab()
elif tab_selection == "🧮 Tools":
    render_tools_tab()
elif tab_selection == "⚙️ Settings":
    render_settings_tab(processor, pdf_processor, analyzer, db_connection)
elif tab_selection == "🔒 Logout":
    auth.log_out(user_id)
    st.switch_page("logout")
