import streamlit as st
from tabs.insurance_tab import render_insurance_tab
from tabs.banking_tab import render_banking_tab
from tabs.gym_tab import render_gym_tab
from tabs.leader_board_tab import leader_board_tab
def render_services_tab():
    st.markdown("""
    <div class="services-container">
        <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🛒 Services</h1>
        </div>
     """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Insurance", "Banking", "Gym Memberships", "Leader Board"])

    with tab1:
        render_insurance_tab()
    with tab2:
        render_banking_tab()
    with tab3:
        render_gym_tab()
    with tab4:
        leader_board_tab()    
