import streamlit as st
import logging
from propelauth_utils import auth
from urllib.parse import urlparse, parse_qs, urlencode

# Configure logging
logger = logging.getLogger(__name__)

# Set page config - must be first Streamlit command
st.set_page_config(
    page_title="Login - Bankstat",
    layout="centered",
    initial_sidebar_state="collapsed"
)

try:
    # Import CSS
    with open("styles.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("styles.css not found. Some styling may be missing.")

# Check for authentication callback
if 'code' in st.query_params and 'state' in st.query_params:
    # This is a callback from PropelAuth after successful login
    try:
        # Exchange the authorization code for an access token
        code = st.query_params['code']
        state = st.query_params['state']
        
        # This is where you would normally exchange the code for tokens
        # For PropelAuth, you might use their SDK here
        # user_info = auth.handle_redirect(code, state)
        
        # For now, we'll just set a flag to indicate successful login
        st.session_state.authenticated = True
        st.session_state.user = {
            'email': 'user@example.com',  # Replace with actual user info
            'user_id': '123'             # Replace with actual user ID
        }
        
        # Redirect to dashboard
        st.switch_page("pages/dashboard.py")
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        st.error("Authentication failed. Please try again.")

# Main login page
st.title("Welcome to Bankstat")

# If already authenticated, redirect to dashboard
if st.session_state.get('authenticated'):
    st.switch_page("pages/dashboard.py")

# Show login options
else:
    # Get current query params and create redirect URI
    query_params = dict(st.query_params)
    query_params.pop('code', None)
    query_params.pop('state', None)
    redirect_uri = "/" + "?" + urlencode(query_params) if query_params else "/"
    
    # Create login URL with redirect
    login_url = f"{auth.auth_url}/login?redirect_uri={redirect_uri}"
    
    st.markdown(
        f"""
        <div style='text-align: center; margin: 2rem 0;'>
            <a href="{login_url}" style='display: inline-block; padding: 0.75rem 2rem; 
                background-color: #4CAF50; color: white; text-decoration: none; 
                border-radius: 4px; font-weight: bold;'>
                Continue with PropelAuth
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"[Create an account]({auth.auth_url}/signup)",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"[Forgot password?]({auth.auth_url}/forgot_password)",
            unsafe_allow_html=True
        )

    # For local development/testing, you might want to keep a simple form
    if st.secrets.get("ENVIRONMENT", {}).get("ENVIRONMENT") == "development":
        with st.expander("Development Login"):
            with st.form("dev_login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    # This is just for development - in production, use PropelAuth's hosted login
                    st.session_state.authenticated = True
                    st.session_state.user = {'email': email, 'user_id': 'dev-user'}
                    st.rerun()
