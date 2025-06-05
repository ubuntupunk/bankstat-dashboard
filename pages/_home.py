import streamlit as st

st.set_page_config(
    page_title="Bankstat Dashboard - Home",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Import CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.image("bankstatgreen.png", use_container_width=True)
st.title("Welcome to Bankstat Dashboard")
st.subheader("Your personal financial insights at a glance.")

st.write("Please log in or sign up to access your dashboard.")

col1, col2 = st.columns(2)
with col1:
    st.button("Login", on_click=st.login, key="home_login_button")
with col2:
    st.link_button("Sign Up", "https://your-propelauth-signup-url.com") # Placeholder URL

st.markdown("---")
if st.button("Terms of Service", key="home_tos_button"):
    st.switch_page("_tos")
