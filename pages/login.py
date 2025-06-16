import streamlit as st
from supabase import create_client, Client
import logging
from config import Config
from utils.utils import DEBUG_MODE, debug_write

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

# Initialize Supabase client
@st.cache_resource
def init_supabase_client():
    url = config.supabase_url
    key = config.supabase_api_key
    return create_client(url, key)

supabase: Client = init_supabase_client()

# Initialize session state
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'  # 'login', 'register', 'reset', 'reset_form'
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

def check_auth_callback():
    """Handle authentication callbacks (OAuth, password reset, etc.)"""
    debug_write("check_auth_callback called")
    query_params = st.query_params
    debug_write(f"Query Params in callback: {dict(query_params)}")
    
    # Check for authentication callbacks (password reset, magic link, email confirmation)
    access_token = query_params.get("access_token")
    refresh_token = query_params.get("refresh_token")
    callback_type = query_params.get("type")

    if access_token and refresh_token:
        debug_write(f"Access Token found. Type: {callback_type}")
        if callback_type == "recovery":
            # This is a password reset callback
            st.session_state.auth_mode = 'reset_form'
            st.session_state.reset_tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            debug_write("Auth Mode set to 'reset_form'")
            st.query_params.clear() # Clear URL params after processing
            st.rerun() # Rerun to apply session state and clear URL
            return True
        elif callback_type == "magiclink":
            # This is a magic link login
            debug_write("Attempting magic link login...")
            try:
                with st.spinner("Logging in with magic link..."):
                    supabase.auth.set_session(
                        access_token=access_token,
                        refresh_token=refresh_token
                    )
                    user_session = supabase.auth.get_session()
                    if user_session and user_session.user:
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            'email': user_session.user.email,
                            'user_id': user_session.user.id
                        }
                        st.success("Logged in successfully via magic link!")
                        debug_write("Magic link login successful. Redirecting to dashboard.")
                        st.query_params.clear() # Clear URL params after successful login
                        st.switch_page("pages/dashboard.py") # Redirect to dashboard
                        return True
                    else:
                        st.error("Magic link login failed. Please try again.")
                        debug_write("Magic link login failed. Rerunning.")
                        st.session_state.auth_mode = 'login'
                        st.query_params.clear() # Clear URL params on failure
                        st.rerun()
                        return False
            except Exception as e:
                st.error(f"An error occurred during magic link login: {str(e)}")
                logger.error(f"Magic link login error: {e}")
                debug_write(f"Magic link login error: {e}. Rerunning.")
                st.session_state.auth_mode = 'login'
                st.query_params.clear() # Clear URL params on error
                st.rerun()
                return False
    
    # Check for email confirmation callback
    if callback_type == "signup":
        debug_write("Signup callback detected.")
        st.success("Email confirmed successfully! You can now log in.")
        st.session_state.auth_mode = 'login'
        st.query_params.clear()
        st.rerun()
        return True
    
    debug_write("No auth callback handled.")
    return False

def check_existing_session():
    """Check if user already has a valid session"""
    try:
        user_session = supabase.auth.get_session()
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
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })
                    
                    if response.user:
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            'email': response.user.email,
                            'user_id': response.user.id
                        }
                        st.success("Signed in successfully!")
                        st.switch_page("pages/dashboard.py")
                    elif response.error:
                        st.error(f"Sign in failed: {response.error.message}")
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
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    
                    if response.user:
                        if response.user.email_confirmed_at:
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'email': response.user.email,
                                'user_id': response.user.id
                            }
                            st.success("Account created and signed in successfully!")
                            st.switch_page("pages/dashboard.py")
                        else:
                            st.success("Account created! Please check your email and click the confirmation link before signing in.")
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                    elif response.error:
                        st.error(f"Registration failed: {response.error.message}")
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
                    response = supabase.auth.reset_password_for_email(email)
                    
                    if response.error:
                        st.error(f"Reset failed: {response.error.message}")
                    else:
                        st.success("If an account with that email exists, a password reset link has been sent. Please check your email.")
                        st.info("The reset link will redirect you back here to set your new password.")
                            
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
                    tokens = st.session_state.reset_tokens
                    supabase.auth.set_session(
                        access_token=tokens['access_token'],
                        refresh_token=tokens['refresh_token']
                    )
                    
                    response = supabase.auth.update_user({"password": new_password})
                    
                    if response.user:
                        del st.session_state.reset_tokens
                        
                        # Set authenticated state
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            'email': response.user.email,
                            'user_id': response.user.id
                        }
                        st.success("Password updated successfully! You are now signed in.")
                        st.switch_page("pages/dashboard.py")
                    elif response.error:
                        st.error(f"Password update failed: {response.error.message}")
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
        # If a callback was handled (e.g., password reset link or magic link),
        # and it set auth_mode to 'reset_form' or redirected to dashboard,
        # we should return immediately.
        if st.session_state.auth_mode == 'reset_form':
            st.image("static/bankstatgreen.png", width=300)
            st.title("Bankstat")
            render_reset_password_form()
            # Debug info (remove in production)
            if DEBUG_MODE:
                st.write("Auth Mode:", st.session_state.auth_mode)
                st.write("Authenticated:", st.session_state.authenticated)
                st.write("User:", st.session_state.user)
                st.write("Reset Tokens:", st.session_state.get('reset_tokens'))
                st.write("Query Params:", dict(st.query_params))
            return
        # If magic link successfully logged in and redirected, check_auth_callback would have returned True
        # and switched page, so we don't need to do anything further here.
        return # Important: return here if check_auth_callback handled something and reran/switched page.
    
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
    if DEBUG_MODE:
        st.write("Auth Mode:", st.session_state.auth_mode)
        st.write("Authenticated:", st.session_state.authenticated)
        st.write("User:", st.session_state.user)
        st.write("Reset Tokens:", st.session_state.get('reset_tokens'))
        st.write("Query Params:", dict(st.query_params))

if __name__ == "__main__":
    main()
