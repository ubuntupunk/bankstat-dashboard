import streamlit as st
from datetime import datetime, timedelta
# from utils.propelauth_utils import auth # Removed PropelAuth import
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from processing import StreamlitAnalytics
from db.connection import DatabaseConnection
from financial_analyzer import FinancialAnalyzer
from utils.pdf_processor import StreamlitBankProcessor
from utils.utils import debug_write
from tabs.upload_tab import render_upload_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.settings_tab import render_settings_tab
from tabs.tools_tab import render_tools_tab
from tabs.goals_tab import render_goals_tab
from tabs.ai_expert_tab import render_ai_advisor_tab
from components.footer import display_footer

# CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# --- Authentication Check ---
# Ensure the user is authenticated before rendering the dashboard content
if not st.session_state.get('authenticated') or not st.session_state.get('user'):
    st.warning("You must be logged in to access the dashboard.")
    st.switch_page("pages/login.py")
    st.stop() # Stop execution if not authenticated

# Get user info from session state (now from Supabase Auth)
user_email = st.session_state.user.get('email', 'User')
user_id = st.session_state.user.get('user_id', 'Unknown')

# Initialize session state
options = ["🧠 Ask Bankstat", "📊 My Dashboard", "🎯 Goals", "🧮 Tools", "📁 Upload & Process","⚙️ Settings", "🔒 Logout"]

if "dashboard_navigation_radio" not in st.session_state:
    st.session_state.dashboard_navigation_radio = options[0] # Default to the first option string

if "dashboard_start_date" not in st.session_state:
    st.session_state.dashboard_start_date = datetime.now() - timedelta(days=30)
if "dashboard_end_date" not in st.session_state:
    st.session_state.dashboard_end_date = datetime.now()

# Sidebar
with st.sidebar:
    st.image("static/bankstatgreen.png", use_container_width=True)
    st.header("User")
    st.text(f"Logged in as {user_email} (ID: {user_id})")
    # Removed PropelAuth account link: st.link_button('Account', auth.get_account_url(), use_container_width=True)
    st.header("Navigation")

    tab_selection = st.radio(
        "Choose Action:",
        options, # Use the defined options list
        index=options.index(st.session_state.dashboard_navigation_radio), # Set index based on session state value
        key="dashboard_navigation_radio"
    )
    st.header("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", st.session_state.dashboard_start_date, key="dashboard_start_date")
    with col2:
        end_date = st.date_input("To", st.session_state.dashboard_end_date, key="dashboard_end_date")

# Header
st.markdown(f'<h1 class="main-header">🏦 Bankstat - Welcome {user_email}</h1>', unsafe_allow_html=True)

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
    debug_write("Debug: Calling render_dashboard_tab")
    render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date)
elif tab_selection == "🎯 Goals":
    render_goals_tab()
elif tab_selection == "🧮 Tools":
    render_tools_tab()
elif tab_selection == "⚙️ Settings":
    render_settings_tab(processor, pdf_processor, analyzer, db_connection)
elif tab_selection == "🔒 Logout":
    st.switch_page("pages/logout.py") # Direct switch to logout page

display_footer()
