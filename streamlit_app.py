import streamlit as st
import logging
from config import Config
from propelauth_utils import auth

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
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize configuration
config = Config()
missing_secrets = config.validate_config()

# Get current page
current_page = st.query_params.get("page", ["home"])[0]

# Navigation
pages = {
    "home": "Home",
    "dashboard": "Dashboard"
}

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    for page_id, page_name in pages.items():
        if st.button(page_name, key=f"nav_{page_id}"):
            st.query_params["page"] = page_id
            st.rerun()

# Authentication check
def check_auth():
    if not hasattr(st, 'user') or not st.user.is_logged_in:
        if current_page != "home":  # Only redirect if not already on home
            st.query_params["page"] = "home"
            st.rerun()
        return False
    return True

# Main app logic
if missing_secrets:
    st.error(f"⚠️ Missing secrets: {', '.join(missing_secrets)}")
else:
    # Handle authentication and routing
    if current_page == "home":
        if check_auth():
            st.rerun()
        else:
            st.rerun()
    elif current_page == "dashboard":
        if check_auth():
            st.rerun()
        else:
            st.rerun()
    else:
        st.warning("Page not found")
        st.rerun()
