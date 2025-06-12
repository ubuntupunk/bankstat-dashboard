import streamlit as st
import logging
from st_supabase_connection import SupabaseConnection # New import
from urllib.parse import urlparse, parse_qs, urlencode
from config import Config

config = Config()

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

# Initialize Supabase connection
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=config.supabase_project_url, # Pass project URL from config
    key=config.supabase_client_key # Pass client key from config
)

# Check if user is already authenticated via Supabase session
# Supabase client stores session in local storage, so we can check it directly
# For Streamlit, we might need to explicitly get the user from the session
user_session = conn.auth.get_session()
if user_session:
    st.session_state.authenticated = True
    st.session_state.user = {
        'email': user_session.user.email,
        'user_id': user_session.user.id
    }
    st.switch_page("pages/dashboard.py")

# Main login page
st.title("Welcome to Bankstat")

# If already authenticated (from previous session check), redirect to dashboard
if st.session_state.get('authenticated'):
    st.switch_page("pages/dashboard.py")
else:
    st.subheader("Sign In")
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        login_button = st.form_submit_button("Login")

        if login_button:
            try:
                user_data, error = conn.auth.sign_in_with_password({"email": email, "password": password})
                if error:
                    st.error(f"Login failed: {error.message}")
                    logger.error(f"Supabase login error: {error.message}")
                elif user_data and user_data.user:
                    st.session_state.authenticated = True
                    st.session_state.user = {
                        'email': user_data.user.email,
                        'user_id': user_data.user.id
                    }
                    st.success("Logged in successfully!")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Login failed: Unknown error.")
            except Exception as e:
                st.error(f"An unexpected error occurred during login: {str(e)}")
                logger.error(f"Unexpected login error: {str(e)}")

    st.markdown("---")

    st.subheader("Create an Account")
    with st.form("signup_form"):
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_button = st.form_submit_button("Sign Up")

        if signup_button:
            try:
                user_data, error = conn.auth.sign_up({"email": signup_email, "password": signup_password})
                if error:
                    st.error(f"Sign up failed: {error.message}")
                    logger.error(f"Supabase signup error: {error.message}")
                elif user_data and user_data.user:
                    st.success("Account created! Please check your email to confirm your account.")
                    # Optionally, log in the user immediately if auto-login after signup is desired
                    # st.session_state.authenticated = True
                    # st.session_state.user = {'email': user_data.user.email, 'user_id': user_data.user.id}
                    # st.switch_page("pages/dashboard.py")
                else:
                    st.error("Sign up failed: Unknown error.")
            except Exception as e:
                st.error(f"An unexpected error occurred during sign up: {str(e)}")
                logger.error(f"Unexpected signup error: {str(e)}")

    st.markdown("---")

    st.subheader("Forgot Password?")
    with st.form("forgot_password_form"):
        forgot_email = st.text_input("Enter your email", key="forgot_email")
        forgot_password_button = st.form_submit_button("Reset Password")

        if forgot_password_button:
            try:
                # Supabase sends a password reset email
                data, error = conn.auth.reset_password_for_email(forgot_email)
                if error:
                    st.error(f"Password reset failed: {error.message}")
                    logger.error(f"Supabase password reset error: {error.message}")
                else:
                    st.success("If an account with that email exists, a password reset link has been sent.")
            except Exception as e:
                st.error(f"An unexpected error occurred during password reset: {str(e)}")
                logger.error(f"Unexpected password reset error: {str(e)}")

    # The development login form is removed as Supabase Auth will handle all flows.
