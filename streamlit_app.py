import streamlit as st
import logging
from config import Config
from utils.utils import DEBUG_MODE, debug_write
from components.footer import display_footer

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.debug("Initializing Streamlit app")

# Configure page - This must be the first Streamlit command
st.set_page_config(
    page_title="Bankstat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import CSS
try:
    with open("styles.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("styles.css not found. Some styling may be missing.")

# Initialize configuration
config = Config()

# Validate configuration and handle missing secrets
try:
    config.validate_config()
    secrets_ok = True
except ValueError as e:
    st.error(f"⚠️ Configuration Error: {e}")
    secrets_ok = False

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'

def check_authentication():
    """Check if user is authenticated, redirect to auth if not"""
    if not st.session_state.get('authenticated') or not st.session_state.get('user'):
        # Redirect to authentication page
        st.switch_page("pages/login.py")
        return False
    return True

def render_authenticated_layout():
    """Render the layout for authenticated users"""
    # Sidebar navigation
    with st.sidebar:
        st.title("Bankstat")
        st.markdown("---")
        
        # User info
        if st.session_state.user:
            st.write(f"👤 {st.session_state.user.get('email', 'User')}")
        
        st.markdown("---")
        
        # Navigation buttons
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("pages/dashboard.py")
        
        if st.button("📊 Analytics", use_container_width=True):
            # st.switch_page("pages/analytics.py")  # When you create this page
            st.info("Analytics page coming soon!")
        
        if st.button("⚙️ Settings", use_container_width=True):
            # st.switch_page("pages/settings.py")  # When you create this page
            st.info("Settings page coming soon!")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.switch_page("pages/logout.py")

def render_welcome_page():
    """Render welcome page for unauthenticated users"""
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.image("static/bankstatgreen.png", width=350)
        st.title("Welcome to Bankstat")
        
        st.markdown("""
        ### Your Personal Banking Analytics Platform
        
        Bankstat helps you understand your financial patterns, track spending, 
        and make informed decisions about your money.
        
        **Features:**
        - 📊 Interactive spending analytics
        - 💳 Transaction categorization
        - 📈 Financial trend analysis
        - 🎯 Budget tracking
        - 📱 Mobile-friendly interface
        """)
        
        st.markdown("---")
        
        # Auth buttons
        col_login, col_register = st.columns(2)
        
        with col_login:
            if st.button("Sign In", use_container_width=True, type="primary"):
                st.session_state.auth_mode = 'login'
                st.switch_page("pages/login.py")
        
        with col_register:
            if st.button("Create Account", use_container_width=True):
                st.session_state.auth_mode = 'register'
                st.switch_page("pages/login.py")

# Main app logic
def main():
    if DEBUG_MODE:
        st.sidebar.info("Debug mode is ON.")
    
    if not secrets_ok:
        st.error("⚠️ Configuration issues detected. Please check your environment variables.")
        st.stop()

    # Check for password reset callback tokens in URL
    query_params = st.query_params
    access_token = query_params.get("access_token")
    refresh_token = query_params.get("refresh_token")

    if access_token and refresh_token:
        # If reset tokens are present, redirect to login page to handle the reset form
        st.session_state.auth_mode = 'reset_form'
        st.session_state.reset_tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        # Clear URL params here to prevent re-processing on subsequent loads
        st.query_params.clear() 
        st.switch_page("pages/login.py")
        return
    
    # Check authentication status
    if st.session_state.authenticated and st.session_state.user:
        # User is authenticated - show main app
        render_authenticated_layout()
        
        # Default to dashboard if no specific page requested
        st.switch_page("pages/dashboard.py")
        
    else:
        # User is not authenticated - show welcome page
        render_welcome_page()

if __name__ == "__main__":
    main()
    
    # Always show footer
    display_footer()
