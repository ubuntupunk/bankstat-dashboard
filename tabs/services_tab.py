import streamlit as st
from tabs.insurance_tab import render_insurance_tab
from tabs.banking_tab import render_banking_tab
from tabs.gym_tab import render_gym_tab
from tabs.legal_tab import render_legal_tab

def render_services_tab():
    st.markdown("""
    <div class="services-container">
        <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🛒 Services</h1>
        </div>
     """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Banking", "Insurance", "Legal",  "Gym Memberships" ])

    with tab1:
        render_banking_tab()
    with tab2:
        render_insurance_tab()
    with tab3:
        render_legal_tab()
    with tab4:    
        render_gym_tab()
        
