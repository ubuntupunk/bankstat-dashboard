import streamlit as st
from propelauth import auth

if st.user.is_logged_in:
    auth.log_out(st.user.sub)
        
st.switch_page("home.py") # redirect back to your home page
