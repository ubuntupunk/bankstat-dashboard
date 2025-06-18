import streamlit as st
from datetime import datetime, timedelta
from propelauth_utils import auth
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from processing import StreamlitAnalytics
from db.connection import DatabaseConnection    
from financial_analyzer import FinancialAnalyzer
from pdf_processor import StreamlitBankProcessor
from utils.utils import debug_write
from tabs.upload_tab import render_upload_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.settings_tab import render_settings_tab
from tabs.tools.tools_tab import render_tools_tab
from tabs.goals.goals_tab import render_goals_tab
from tabs.expert.ai_expert_tab import render_ai_advisor_tab
from components.footer import display_footer
# CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Get user info from PropelAuth
user = auth.get_user(st.user.sub) if hasattr(st, 'user') and hasattr(st.user, 'sub') else None
user_email = user.email if user and hasattr(user, 'email') else "User"
user_id = user.sub if user and hasattr(user, 'sub') else "Unknown"

# Initialize session state
options = ["🧠 Ask Bankstat", "📊 My Dashboard", "🎯 Goals", "🧮 Tools", "📁 Upload & Process","⚙️ Settings", "🔒 Logout"]

if "dashboard_navigation_radio" not in st.session_state:
    st.session_state.dashboard_navigation_radio = options[0] # Default to the first option string

if "dashboard_start_date" not in st.session_state:
    st.session_state.dashboard_start_date = datetime.now() - timedelta(days=30)
if "dashboard_end_date" not in st.session_state:
    st.session_state.dashboard_end_date = datetime.now()

# Initialize start_date and end_date with default values
# These will be updated by st.date_input widgets in the sidebar
# and then re-read from session_state before rendering tabs.
if "dashboard_start_date" not in st.session_state:
    st.session_state.dashboard_start_date = datetime.now() - timedelta(days=30)
if "dashboard_end_date" not in st.session_state:
    st.session_state.dashboard_end_date = datetime.now()

# Sidebar
with st.sidebar:
    st.image("static/bankstatgreen.png", use_container_width=True)
    st.header("User")
    st.text(f"Logged in as {user_email} (ID: {user_id})")
    st.link_button('Account', auth.get_account_url(), use_container_width=True)
    st.header("Navigation")

    tab_selection = st.radio(
        "Choose Action:",
        options, # Use the defined options list
        index=options.index(st.session_state.dashboard_navigation_radio), # Set index based on session state value
        key="dashboard_navigation_radio"
    )
    st.header("Date Range")
    if tab_selection in ["📊 My Dashboard", "🎯 Goals"]:
        col1, col2 = st.columns(2)
        with col1:
            st.date_input("From", st.session_state.dashboard_start_date, key="dashboard_start_date")
        with col2:
            st.date_input("To", st.session_state.dashboard_end_date, key="dashboard_end_date")
        # The values in session_state are updated automatically by st.date_input
        debug_write(f"Dashboard UI selected date range: {st.session_state.dashboard_start_date.strftime('%Y-%m-%d')} to {st.session_state.dashboard_end_date.strftime('%Y-%m-%d')}")
    else:
        st.info("Date range not applicable for this section.")

# Header
st.markdown(f'<h1 class="main-header">🏦 Bankstat - Welcome {user_email}</h1>', unsafe_allow_html=True)

# Re-assign start_date and end_date from session_state to ensure they reflect the latest UI selection
start_date = st.session_state.dashboard_start_date
end_date = st.session_state.dashboard_end_date

# Initialize components
processor = StreamlitAnalytics()
db_connection = DatabaseConnection()
pdf_processor = StreamlitBankProcessor()
analyzer = FinancialAnalyzer(base_analyzer=processor)

# Render tab content
if tab_selection == "📁 Upload & Process":
    render_upload_tab(pdf_processor, processor, db_connection)
elif tab_selection == "🧠 Ask Bankstat":
    render_ai_advisor_tab()
elif tab_selection == "📊 My Dashboard":
    debug_write(f"Calling render_dashboard_tab with dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date)
elif tab_selection == "🎯 Goals":
    debug_write(f"Calling render_goals_tab with dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    render_goals_tab()
elif tab_selection == "🧮 Tools":
    render_tools_tab()
elif tab_selection == "⚙️ Settings":
    render_settings_tab(processor, pdf_processor, analyzer, db_connection)
elif tab_selection == "🔒 Logout":
    auth.log_out(user_id)
    st.switch_page("logout")

display_footer()
