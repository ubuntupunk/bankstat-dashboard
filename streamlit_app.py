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
    """Check if user is authenticated. If not, redirect to login page."""
    if not st.session_state.get('authenticated') or not st.session_state.get('user'):
        st.switch_page("pages/login.py")
        return False
    return True

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
                st.switch_page("pages/logout.py") # Direct switch to logout page
    
    # Page routing
    if current_page == "home":
        if not st.session_state.authenticated:
            st.image("static/bankstatgreen.png", width=350, use_container_width=False)
            st.title("Welcome to Bankstat")
            st.markdown(
                """
                <style>
                    .stApp {
                        background-color: #f0f2f6; /* Light grey background */
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }
                    .stApp > header {
                        display: none; /* Hide Streamlit header */
                    }
                    .stApp > footer {
                        display: none; /* Hide Streamlit footer */
                    }
                    .stButton > button {
                        background-color: #2E8B57;
                        color: white;
                        padding: 0.75rem 2rem;
                        border-radius: 0.5rem;
                        border: none;
                        font-size: 1.2rem;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                    }
                    .stButton > button:hover {
                        background-color: #3CB371; /* Lighter green on hover */
                    }
                    h1 {
                        color: #2E8B57;
                        font-size: 2.5rem;
                        margin-bottom: 1rem;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )
            if st.button("Login"):
                st.switch_page("pages/login.py")
        else:
            st.switch_page("pages/dashboard.py")
    
    elif current_page == "dashboard":
        check_auth() # Just call check_auth, it handles redirection if needed
    
    else:
        st.warning("Page not found")
        st.switch_page("pages/home.py") # Redirect to home page

display_footer()
