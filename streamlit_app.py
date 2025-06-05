import streamlit as st
from config import Config
from propelauth_utils import auth # Updated import

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

    if st.user.is_logged_in:
        st.switch_page("_dashboard")
    else:
        st.switch_page("_home")

if __name__ == "__main__":
    main()
