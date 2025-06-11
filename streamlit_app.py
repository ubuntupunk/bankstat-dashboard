import streamlit as st
import logging
from config import Config
from propelauth_utils import auth
from utils import DEBUG_MODE, debug_write

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.debug("Initializing Streamlit app")

# Configure page - This must be the first Streamlit command
st.set_page_config(
    page_title="Bankstat Dashboard",
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
missing_secrets = config.validate_config()

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Get current page from query params
query_params = st.query_params
current_page = query_params.get("page", ["home"])[0]

# Navigation
pages = {
    "home": "Home",
    "dashboard": "Dashboard"
}

# Authentication check
def check_auth():
    """Check if user is authenticated"""
    if not st.session_state.authenticated or not st.session_state.user:
        if current_page != "home":
            st.query_params["page"] = "home"
            st.rerun()
        return False
    return True

# Handle logout
if query_params.get("logout"):
    if st.session_state.authenticated and st.session_state.user:
        auth.log_out(st.session_state.user.get('user_id'))
    st.session_state.authenticated = False
    st.session_state.user = None
    st.query_params["page"] = "home"
    st.query_params.pop("logout", None)
    st.rerun()

# Main app logic
if DEBUG_MODE:
    st.info("Debug mode is ON.")
else:
    st.caption("Debug mode is OFF.")

if missing_secrets:
    st.error(f"⚠️ Missing secrets: {', '.join(missing_secrets)}")
else:
    # Sidebar navigation (only show when authenticated)
    if st.session_state.authenticated:
        with st.sidebar:
            st.title("Navigation")
            for page_id, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_id}"):
                    st.query_params["page"] = page_id
                    st.rerun()
            
            if st.button("Logout"):
                st.query_params["logout"] = "true"
                st.rerun()
    
    # Page routing
    if current_page == "home":
        if not st.session_state.authenticated:
            # Show login form or redirect to PropelAuth
            st.title("Welcome to Bankstat Dashboard")
            if st.button("Login"):
                # This should redirect to PropelAuth login
                st.switch_page("pages/login.py")
        else:
            st.switch_page("pages/dashboard.py")
    
    elif current_page == "dashboard":
        if check_auth():
            st.switch_page("pages/dashboard.py")
    
    else:
        st.warning("Page not found")
        st.query_params["page"] = "home"
        st.rerun()
