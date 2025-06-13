import streamlit as st
import logging
from st_supabase_connection import SupabaseConnection
from config import Config

config = Config()
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Logout - Bankstat",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def perform_logout():
    """Perform logout operations"""
    try:
        # Initialize Supabase connection
        conn = st.connection(
            "supabase",
            type=SupabaseConnection,
            url=config.supabase_project_url,
            key=config.supabase_client_key
        )
        
        # Sign out from Supabase
        result = conn.auth.sign_out()
        
        # Handle different return formats
        if isinstance(result, tuple):
            data, error = result
            if error:
                st.error(f"Logout failed: {error.message if hasattr(error, 'message') else str(error)}")
                logger.error(f"Supabase logout error: {error}")
                return False
        
        # Clear session state
        st.session_state.authenticated = False
        if 'user' in st.session_state:
            del st.session_state.user
        
        # Clear any other auth-related session state
        auth_keys = [key for key in st.session_state.keys() if 'auth' in key.lower() or 'user' in key.lower()]
        for key in auth_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        return True
        
    except Exception as e:
        st.error(f"An unexpected error occurred during logout: {str(e)}")
        logger.error(f"Unexpected logout error: {e}")
        
        # Still clear session state even if Supabase logout fails
        st.session_state.authenticated = False
        if 'user' in st.session_state:
            del st.session_state.user
        
        return False

# Main logout logic
if perform_logout():
    st.success("Logged out successfully!")
    st.info("Redirecting to home page...")
    # Small delay to show the success message
    import time
    time.sleep(1)

# Redirect to home page
st.switch_page("streamlit_app.py")