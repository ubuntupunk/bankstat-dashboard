import streamlit as st
from st_supabase_connection import SupabaseConnection # New import

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

# Perform logout
try:
    data, error = conn.auth.sign_out()
    if error:
        st.error(f"Logout failed: {error.message}")
    else:
        st.session_state.authenticated = False
        if 'user' in st.session_state:
            del st.session_state.user
        st.success("Logged out successfully!")
except Exception as e:
    st.error(f"An unexpected error occurred during logout: {str(e)}")

st.switch_page("pages/home.py") # redirect back to your home page
