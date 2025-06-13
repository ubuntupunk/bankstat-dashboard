import streamlit as st

def render_gym_tab():
    st.markdown("""
    <div class="gym-container">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: bold;">🏋️ Gym Memberships</h2>
        </div>
     """, unsafe_allow_html=True)
    st.write("Find and compare gym memberships and fitness programs.")
    st.info("Gym membership comparison features coming soon!")
