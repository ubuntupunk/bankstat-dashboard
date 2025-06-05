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
from propelauth import auth # Import the auth object from propelauth.py

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

    # Handle OAuth2 callback
    query_params = st.query_params
    auth_code = query_params.get("code")
    returned_state = query_params.get("state")
    
    if auth_code and returned_state:
        expected_state = st.session_state.get("oauth_state")
        if not expected_state or returned_state[0] != expected_state:
            st.error("CSRF attack detected or invalid state parameter. Please try logging in again.")
            st.session_state.clear()
            st.experimental_set_query_params()
            st.experimental_rerun()
            return

        user_id = auth.exchange_code_for_user_id(auth_code[0])
        if user_id:
            st.session_state["user_id"] = user_id
            # Clear query parameters and state from session to prevent re-processing
            del st.session_state["oauth_state"]
            st.experimental_set_query_params() # Clears all query params
            st.experimental_rerun() # Rerun to update the UI
            return # Stop execution until rerun completes
        else:
            st.error("Failed to exchange authorization code for user ID.")
            st.session_state.clear() # Clear session state on failure
            st.experimental_set_query_params() # Clear query params
            st.experimental_rerun() # Rerun to clear error
            return
    elif auth_code or returned_state: # If only one of them is present, it's an incomplete or malformed callback
        st.error("Incomplete authentication callback. Please try logging in again.")
        st.session_state.clear()
        st.experimental_set_query_params()
        st.experimental_rerun()
        return

    # Authentication with PropelAuth
    user_id = st.session_state.get("user_id")
    if user_id is None:
        st.warning("Please log in to access the dashboard.")
        st.link_button("Login with PropelAuth", auth.get_login_url())
        st.stop()

    user = auth.get_user(user_id)
    if user is None:
        st.error('Unauthorized. Please log in again.')
        st.session_state.clear() # Clear session state if user is unauthorized
        st.experimental_rerun() # Rerun to reflect logout
        return # Stop execution until rerun completes

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
