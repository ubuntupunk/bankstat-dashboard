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

# Define pages
pages = [
    st.Page("pages/_home.py", title="Home"),
    st.Page("pages/dashboard.py", title="Dashboard")
]
pg = st.navigation(pages)

# Navigation logic
if missing_secrets:
    st.error(f"⚠️ Missing secrets: {', '.join(missing_secrets)}")
    pg.run()
elif not st.user.is_logged_in:
    st.switch_page("pages/_home.py")
else:
    user = auth.get_user(st.user.sub)
    if not user:
        st.error("Failed to retrieve user information.")
        st.switch_page("pages/_home.py")
    else:
        st.switch_page("pages/dashboard.py")
