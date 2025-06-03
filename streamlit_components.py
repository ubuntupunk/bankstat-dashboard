# streamlit_components.py
import streamlit as st
import financial_analyzer
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_metric_cards(metrics_data):
    """Create styled metric cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Total Income</h3>
            <h2 style="color: #28a745;">R {:.2f}</h2>
        </div>
        """.format(metrics_data.get('total_income', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💸 Total Expenses</h3>
            <h2 style="color: #dc3545;">R {:.2f}</h2>
        </div>
        """.format(metrics_data.get('total_expenses', 0)), unsafe_allow_html=True)
    
    with col3:
        net_flow = metrics_data.get('net_flow', 0)
        color = "#28a745" if net_flow >= 0 else "#dc3545"
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Net Flow</h3>
            <h2 style="color: {};">R {:.2f}</h2>
        </div>
        """.format(color, net_flow), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🏦 Avg Balance</h3>
            <h2 style="color: #17a2b8;">R {:.2f}</h2>
        </div>
        """.format(metrics_data.get('avg_balance', 0)), unsafe_allow_html=True)

def create_advanced_charts(analyzer):
    """Create advanced visualization charts"""
    
    # Monthly trend chart
    enhanced_analyzer = financial_analyzer(analyzer)
    monthly_trends = enhanced_analyzer.get_monthly_trends()
    
    if monthly_trends:
        months = list(monthly_trends.keys())
        debits = [data['debits'] for data in monthly_trends.values()]
        credits = [data['credits'] for data in monthly_trends.values()]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Income', x=months, y=credits, marker_color='green'))
        fig.add_trace(go.Bar(name='Expenses', x=months, y=debits, marker_color='red'))
        
        fig.update_layout(
            title="Monthly Income vs Expenses Trend",
            xaxis_title="Month",
            yaxis_title="Amount (R)",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Category breakdown with better styling
    insights = enhanced_analyzer.get_category_insights()
    if insights and insights['top_categories']:
        categories = [cat[0] for cat in insights['top_categories']]
        amounts = [cat[1] for cat in insights['top_categories']]
        
        fig = px.treemap(
            names=categories,
            values=amounts,
            title="Expense Categories (Top 5)"
        )
        
        st.plotly_chart(fig, use_container_width=True)