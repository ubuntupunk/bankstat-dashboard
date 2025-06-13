import streamlit as st
# Import CSS
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Main content
st.image("static/bankstatgreen.png", use_container_width=True) # Use static/ for image path
st.title("Welcome to Bankstat")
st.subheader("Your personal financial insights at a glance.")

# Check if user is logged in using session state
if not st.session_state.get('authenticated'):
    st.write("Please log in or sign up to access your dashboard.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.switch_page("pages/login.py") # Use st.switch_page for navigation
    with col2:
        # Assuming Supabase signup URL is known or can be constructed
        # For now, a placeholder or direct link to login for signup
        st.button("Sign Up", on_click=lambda: st.switch_page("pages/login.py")) # Redirect to login for signup
        
    st.markdown("---")
    if st.button("Terms of Service", key="home_tos_button"):
        st.switch_page("pages/tos.py") # Use st.switch_page for navigation
    if st.button("Privacy Policy", key="home_privacy_button"):
        st.switch_page("pages/privacy.py") # Add Privacy Policy button
else:
    st.switch_page("pages/dashboard.py") # Redirect to dashboard if authenticated
