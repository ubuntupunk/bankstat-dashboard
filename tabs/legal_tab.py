import streamlit as st

def render_legal_tab():
    st.markdown("""
    <div class="legal-container">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: bold;">🏋️ Gym Memberships</h2>
        </div>
     """, unsafe_allow_html=True)
    st.write("Find and compare legal plans.")
    st.info("Gym membership comparison features coming soon!")
