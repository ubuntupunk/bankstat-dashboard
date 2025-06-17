import streamlit as st
import pandas as pd
import os
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from utils.utils import debug_write
from tabs.services.services_tab import render_services_tab
from tabs.goals.goals_tab import render_goals_tab
from tabs.tools.tools_tab import render_tools_tab
from tabs.leader.leader_board_main import leader_board_tab
from models.ml_integration import MLCategoryIntegration
import plotly.express as px
from tabs.metrics.key_metrics_tab import render_key_metrics_tab
from tabs.predictions.spending_predictor import render_prediction_tab
# from tabs.goals.metrics_alerts import render_metrics_alerts

def render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date):
    # Load CSS from dashboard.css
    css_path = os.path.join(os.path.dirname(__file__), "dashboard.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("dashboard.css file not found. Please ensure it exists in the same directory as dashboard_tab.py.")
        return
    
    st.markdown("""
    <div class="dashboard-container">
        <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">📊 Financial Dashboard</h1>
        </div>
     """, unsafe_allow_html=True)

    debug_write("Entered render_dashboard_tab")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Key Metrics", 
        "🔮 Predictions",
        "🧠 My Neural Net", 
        "🎯 Goals", 
        "🏦 Services", 
        "🛠️ Tools", 
        "🏅 Leader Board"
    ])

    with tab1:
        render_key_metrics_tab(analyzer, processor, db_connection, start_date, end_date)
    
    with tab2:
        render_prediction_tab(analyzer, processor, db_connection, start_date, end_date)
    
    with tab3:
        ml_integration = MLCategoryIntegration(analyzer, db_connection)
        ml_integration.render_ml_tab(processor, start_date, end_date)
    
    with tab4:    
        render_goals_tab() 
    
    with tab5:
        render_services_tab()
    
    with tab6:
        render_tools_tab()
    
    with tab7:
        leader_board_tab()
