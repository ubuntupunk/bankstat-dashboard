import streamlit as st

def render_services_tab():
    st.markdown("""
    <div class="services-container">
        <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🛒 Services</h1>
        </div>
     """, unsafe_allow_html=True)
    st.write("This tab will allow users to purchase services such as banking and insurance, by comparing the best rates available in the market.")
    st.info("Service comparison features coming soon!")
