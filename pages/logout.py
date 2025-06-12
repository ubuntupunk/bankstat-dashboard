import streamlit as st
from utils.propelauth_utils import auth # Updated import

if st.user.is_logged_in:
    auth.log_out(st.user.sub)
        
st.switch_page("pages/home.py") # redirect back to your home page
