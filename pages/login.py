import streamlit as st
import logging
from st_supabase_connection import SupabaseConnection
from config import Config

config = Config()
logger = logging.getLogger(__name__)

# Set page config - must be first Streamlit command
st.set_page_config(
    page_title="Bankstat - Authentication",
    layout="centered",
    initial_sidebar_state="collapsed"
)

try:
    with open("styles.css") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("styles.css not found. Some styling may be missing.")

# Initialize Supabase connection
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=config.supabase_project_url,
    key=config.supabase_client_key
)

# Initialize session state
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'  # 'login', 'register', 'reset', 'reset_form'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def check_auth_callback():
    """Handle authentication callbacks (OAuth, password reset, etc.)"""
    query_params = st.query_params
    
    # Check for password reset callback
    access_token = query_params.get("access_token")
    refresh_token = query_params.get("refresh_token")
    
    if access_token and refresh_token:
        # This is a password reset callback
        st.session_state.auth_mode = 'reset_form'
        st.session_state.reset_tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        # Clear URL params to prevent re-processing
        # st.query_params.clear() # Do not clear here, let streamlit_app.py handle it
        # st.rerun() # Do not rerun here, let streamlit_app.py handle the redirect
        return True
    
    # Check for email confirmation callback
    if query_params.get("type") == "signup":
        st.success("Email confirmed successfully! You can now log in.")
        st.session_state.auth_mode = 'login'
        st.query_params.clear()
        st.rerun()
        return True
    
    return False

def check_existing_session():
    """Check if user already has a valid session"""
    try:
        user_session = conn.auth.get_session()
        if user_session and user_session.user:
            st.session_state.authenticated = True
            st.session_state.user = {
                'email': user_session.user.email,
                'user_id': user_session.user.id
            }
            return True
    except Exception as e:
        logger.debug(f"No existing session: {e}")
    return False

def render_login_form():
    """Render the login form"""
    st.subheader("Sign In to Bankstat")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("Sign In", use_container_width=True)
        with col2:
            forgot_btn = st.form_submit_button("Forgot Password?", use_container_width=True)
        
        if login_btn:
            if not email or not password:
                st.error("Please enter both email and password")
                return
            
            try:
                with st.spinner("Signing in..."):
                    result = conn.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if isinstance(result, tuple):
                        user_data, error = result
                    else:
                        user_data = result
                        error = None
                    
                    if error:
                        error_msg = error.message if hasattr(error, 'message') else str(error)
                        if "invalid_credentials" in error_msg.lower():
                            st.error("Invalid email or password")
                        elif "email_not_confirmed" in error_msg.lower():
                            st.error("Please confirm your email address before signing in")
                        else:
                            st.error(f"Sign in failed: {error_msg}")
                    elif user_data and hasattr(user_data, 'user') and user_data.user:
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            'email': user_data.user.email,
                            'user_id': user_data.user.id
                        }
                        st.success("Signed in successfully!")
                        st.rerun()
                    else:
                        st.error("Sign in failed. Please try again.")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Login error: {e}")
        
        elif forgot_btn:
            if not email:
                st.error("Please enter your email address")
                return
            
            st.session_state.reset_email = email
            st.session_state.auth_mode = 'reset'
            st.rerun()
    
    st.markdown("---")
    
    # Switch to register mode
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("Don't have an account?")
    with col2:
        if st.button("Create Account", use_container_width=True):
            st.session_state.auth_mode = 'register'
            st.rerun()

def render_register_form():
    """Render the registration form"""
    st.subheader("Create Your Account")
    
    with st.form("register_form", clear_on_submit=False):
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        register_btn = st.form_submit_button("Create Account", use_container_width=True)
        
        if register_btn:
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return
            
            try:
                with st.spinner("Creating account..."):
                    result = conn.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    
                    if isinstance(result, tuple):
                        user_data, error = result
                    else:
                        user_data = result
                        error = None
                    
                    if error:
                        error_msg = error.message if hasattr(error, 'message') else str(error)
                        if "already_registered" in error_msg.lower():
                            st.error("An account with this email already exists")
                        else:
                            st.error(f"Registration failed: {error_msg}")
                    elif user_data and hasattr(user_data, 'user') and user_data.user:
                        if user_data.user.email_confirmed_at:
                            # Auto-login if email is already confirmed
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'email': user_data.user.email,
                                'user_id': user_data.user.id
                            }
                            st.success("Account created and signed in successfully!")
                            st.rerun()
                        else:
                            st.success("Account created! Please check your email and click the confirmation link before signing in.")
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    else:
                        st.error("Registration failed. Please try again.")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Registration error: {e}")
    
    st.markdown("---")
    
    # Switch to login mode
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("Already have an account?")
    with col2:
        if st.button("Sign In", use_container_width=True):
            st.session_state.auth_mode = 'login'
            st.rerun()

def render_reset_request_form():
    """Render password reset request form"""
    st.subheader("Reset Your Password")
    
    email = st.session_state.get('reset_email', '')
    
    with st.form("reset_form"):
        email = st.text_input("Email", value=email, key="reset_email_input")
        
        col1, col2 = st.columns(2)
        with col1:
            reset_btn = st.form_submit_button("Send Reset Link", use_container_width=True)
        with col2:
            back_btn = st.form_submit_button("Back to Sign In", use_container_width=True)
        
        if reset_btn:
            if not email:
                st.error("Please enter your email address")
                return
            
            try:
                with st.spinner("Sending reset email..."):
                    result = conn.auth.reset_password_for_email(email)
                    
                    # Handle different return formats
                    if result is None or (isinstance(result, tuple) and len(result) == 2 and result[1] is None):
                        st.success("If an account with that email exists, a password reset link has been sent. Please check your email.")
                        st.info("The reset link will redirect you back here to set your new password.")
                    else:
                        if isinstance(result, tuple) and len(result) == 2:
                            _, error = result
                            if error:
                                error_msg = error.message if hasattr(error, 'message') else str(error)
                                st.error(f"Reset failed: {error_msg}")
                        else:
                            st.error("Reset failed. Please try again.")
                            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Password reset error: {e}")
        
        elif back_btn:
            st.session_state.auth_mode = 'login'
            st.rerun()

def render_reset_password_form():
    """Render new password form after reset link clicked"""
    st.subheader("Set New Password")
    
    if 'reset_tokens' not in st.session_state:
        st.error("Invalid reset session. Please request a new password reset.")
        st.session_state.auth_mode = 'reset'
        st.rerun()
        return
    
    with st.form("new_password_form"):
        new_password = st.text_input("New Password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_new_password")
        
        col1, col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button("Update Password", use_container_width=True)
        with col2:
            cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
        
        if update_btn:
            if not new_password or not confirm_password:
                st.error("Please fill in both password fields")
                return
            
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
                return
            
            try:
                with st.spinner("Updating password..."):
                    # Set session with reset tokens
                    tokens = st.session_state.reset_tokens
                    conn.auth.set_session(
                        access_token=tokens['access_token'],
                        refresh_token=tokens['refresh_token']
                    )
                    
                    # Update password
                    result = conn.auth.update_user({"password": new_password})
                    
                    if isinstance(result, tuple):
                        user_data, error = result
                    else:
                        user_data = result
                        error = None
                    
                    if error:
                        error_msg = error.message if hasattr(error, 'message') else str(error)
                        st.error(f"Password update failed: {error_msg}")
                    elif user_data and hasattr(user_data, 'user') and user_data.user:
                        # Clean up reset tokens
                        del st.session_state.reset_tokens
                        
                        # Set authenticated state
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            'email': user_data.user.email,
                            'user_id': user_data.user.id
                        }
                        
                        st.success("Password updated successfully! You are now signed in.")
                        st.rerun()
                    else:
                        st.error("Password update failed. Please try again.")
                        
            except Exception as e:
                error_msg = str(e).lower()
                if "invalid_grant" in error_msg or "expired" in error_msg:
                    st.error("Reset link has expired. Please request a new password reset.")
                    st.session_state.auth_mode = 'reset'
                    if 'reset_tokens' in st.session_state:
                        del st.session_state.reset_tokens
                    st.rerun()
                else:
                    st.error(f"An error occurred: {str(e)}")
                    logger.error(f"Password update error: {e}")
        
        elif cancel_btn:
            st.session_state.auth_mode = 'login'
            if 'reset_tokens' in st.session_state:
                del st.session_state.reset_tokens
            st.rerun()

def main():
    """Main authentication flow"""
    
    # Handle callbacks first
    if check_auth_callback():
        # If a callback was handled (e.g., password reset link),
        # and it set auth_mode to 'reset_form', we should render that form immediately.
        # No need to check existing session or redirect to dashboard yet.
        if st.session_state.auth_mode == 'reset_form':
            st.image("static/bankstatgreen.png", width=300)
            st.title("Bankstat")
            render_reset_password_form()
            # Debug info (remove in production)
            if st.checkbox("Show Debug Info"):
                st.write("Auth Mode:", st.session_state.auth_mode)
                st.write("Authenticated:", st.session_state.authenticated)
                st.write("Query Params:", dict(st.query_params))
            return
    
    # Check existing session
    if check_existing_session() and st.session_state.authenticated:
        st.switch_page("pages/dashboard.py")
        return
    
    # Show logo and title
    st.image("static/bankstatgreen.png", width=300)
    st.title("Bankstat")
    
    # Render appropriate form based on auth_mode
    if st.session_state.auth_mode == 'login':
        render_login_form()
    elif st.session_state.auth_mode == 'register':
        render_register_form()
    elif st.session_state.auth_mode == 'reset':
        render_reset_request_form()
    elif st.session_state.auth_mode == 'reset_form':
        render_reset_password_form()
    
    # Debug info (remove in production)
    if st.checkbox("Show Debug Info"):
        st.write("Auth Mode:", st.session_state.auth_mode)
        st.write("Authenticated:", st.session_state.authenticated)
        st.write("Query Params:", dict(st.query_params))

if __name__ == "__main__":
    main()
