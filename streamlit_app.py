import streamlit as st
from datetime import datetime, timedelta
from config import Config
from processing import StreamlitAnalytics
from connection import DatabaseConnection
from financial_analyzer import FinancialAnalyzer
from pdf_processor import StreamlitBankProcessor
from tabs.upload_tab import render_upload_tab
from tabs.dashboard_tab import render_dashboard_tab
from tabs.settings_tab import render_settings_tab
from tabs.tools_tab import render_tools_tab
from propelauth import init_auth
import streamlit as st

auth = init_auth()

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

# Initialize configuration
config = Config()
missing_secrets = config.validate_config()

def main():
    if missing_secrets:
        st.error(f"⚠️ Missing secrets: {', '.join(missing_secrets)}")
        return

    # Authentication with PropelAuth and Streamlit OIDC
    if not st.user.is_logged_in:
        st.button("Login", on_click=st.login)
        st.stop()

    user = auth.get_user(st.user.sub)
    if user is None:
        st.error('Unauthorized')
        st.stop()

    # Sidebar
    with st.sidebar:
        st.image("bankstatgreen.png", use_container_width=True)
        st.header("User")
        st.text(f"Logged in as {user.email} (ID: {user.user_id})")
        st.link_button('Account', auth.get_account_url(), use_container_width=True)
        st.button('Logout', on_click=auth.log_out, args=(user.user_id,))
        st.header("Navigation")
        tab_selection = st.radio(
            "Choose Action:",
            ["📊 View Dashboard", "📁 Upload & Process", "🧮 Tools", "⚙️ Settings"]
        )
        st.header("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("To", datetime.now())

    # Header
    st.markdown(f'<h1 class="main-header">🏦 Bankstat Dashboard - Welcome {user.email}</h1>', unsafe_allow_html=True)

    # Initialize components
    processor = StreamlitAnalytics()
    db_connection = DatabaseConnection()
    pdf_processor = StreamlitBankProcessor()
    analyzer = FinancialAnalyzer(base_analyzer=processor)

    # Render selected tab
    if tab_selection == "📁 Upload & Process":
        render_upload_tab(pdf_processor, processor, db_connection)
    elif tab_selection == "📊 View Dashboard":
        render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date)
    elif tab_selection == "🧮 Tools":
        render_tools_tab()
    elif tab_selection == "⚙️ Settings":
        render_settings_tab(processor, pdf_processor, analyzer, db_connection)

if __name__ == "__main__":
    main()
