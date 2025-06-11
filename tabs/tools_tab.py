import streamlit as st
import os
from tabs.tools.financial_calc import render_financial_flow_calculator
from tabs.tools.invest_calc import render_investment_calculator
from tabs.tools.energy_calc import render_energy_calculator
from tabs.tools.bond_calc import render_bond_calculator

def render_tools_tab():
    """Render the Tools tab with a Financial Flow Calculator."""
    # Load CSS from tools.css
    css_path = os.path.join(os.path.dirname(__file__), "tools.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("tools.css file not found. Please ensure it exists in the same directory as tools_tab.py.")
        return

    # Main container
    with st.container():
        # Header
        st.markdown("""
        <div class="tools-container">
            <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🧮 Tools Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Your tools to plan, budget, and earn rewards</p>
        </div>
    """, unsafe_allow_html=True)

     # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Financial Flow Calculator", "Bond Calculator", "Investment Calculator", "Energy Calculator"])
    
    with tab1:
        render_financial_flow_calculator()
    
    with tab2:
        render_bond_calculator()
    
    with tab3:
        render_investment_calculator()
    
    with tab4:
        render_energy_calculator()
