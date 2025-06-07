import streamlit as st
from propelauth_utils import auth

# Import CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Main content
st.image("bankstatgreen.png", use_container_width=True)
st.title("Welcome to Bankstat Dashboard")
st.subheader("Your personal financial insights at a glance.")

# Check if user is logged in
if not st.user.is_logged_in:
    st.write("Please log in or sign up to access your dashboard.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.experimental_set_query_params(page="login")
            st.rerun()
    with col2:
        st.link_button("Sign Up", f"{auth.auth_url}/signup")
        
    st.markdown("---")
    if st.button("Terms of Service", key="home_tos_button"):
        st.experimental_set_query_params(page="tos")
        st.rerun()
else:
    st.experimental_set_query_params(page="dashboard")
    st.rerun()
