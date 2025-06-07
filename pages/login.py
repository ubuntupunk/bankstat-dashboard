import streamlit as st
from propelauth_utils import auth

st.set_page_config(
    page_title="Login - Bankstat Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Import CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("Login to Bankstat")

# If user is already logged in, redirect to dashboard
if st.user.is_logged_in:
    st.switch_page("pages/dashboard.py")

# Login form
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        login_button = st.form_submit_button("Login")
    with col2:
        st.markdown(f"[Forgot password?]({auth.auth_url}/forgot_password)", unsafe_allow_html=True)
    
    if login_button:
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            try:
                # This is where you would normally call your auth service
                # For PropelAuth, you'd typically use their hosted login page
                # So we'll redirect there instead
                st.switch_page("pages/home.py")
                
                # If you want to handle the login directly, you would do something like:
                # user = auth.auth.login(email, password)
                # st.session_state.user = user
                # st.switch_page("pages/dashboard.py")
                
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

st.markdown("---")
st.markdown(
    f"""
    Don't have an account? [Sign up here]({auth.auth_url}/signup)
    """,
    unsafe_allow_html=True
)
st.markdown(
    "[Back to Home](pages/home.py)",
    unsafe_allow_html=True
)
