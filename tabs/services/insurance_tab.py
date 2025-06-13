import streamlit as st

def render_insurance_tab():
    st.markdown("""
    <div class="insurance-container">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: bold;">🛡️ Insurance Services</h2>
        </div>
     """, unsafe_allow_html=True)
    st.write("Compare and purchase insurance policies (e.g., health, auto, home).")
    st.info("Insurance comparison features coming soon!")
