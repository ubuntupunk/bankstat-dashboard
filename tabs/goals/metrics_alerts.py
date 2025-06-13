import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go

def render_metrics_alerts():
    """Render metrics with line chart and alerts."""
    st.markdown("### Financial Metrics & Alerts")
    
    # Savings rate chart
    fig = px.line(
        st.session_state.savings_history,
        x='Date',
        y='Savings_Rate',
        title='Savings Rate Trend (%)',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Savings Rate (%)",
        hovermode='x unified'
    )
    
    fig.add_hline(y=20, line_dash="dash", line_color="orange", 
                  annotation_text="Target: 20%")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Current metrics
    current_savings_rate = st.session_state.savings_history['Savings_Rate'].iloc[-1]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metrics-card">
            <h3 style="margin: 0; color: #3b82f6;">{current_savings_rate}%</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280;">Current Savings Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_savings = st.session_state.savings_history['Savings_Rate'].mean()
        st.markdown(f"""
        <div class="metrics-card">
            <h3 style="margin: 0; color: #10b981;">{avg_savings:.1f}%</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280;">Average Savings Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_budget = sum([cat['budget'] for cat in st.session_state.budget_data.values()])
        total_spent = sum([cat['spent'] for cat in st.session_state.budget_data.values()])
        budget_utilization = (total_spent / total_budget) * 100
        
        st.markdown(f"""
        <div class="metrics-card">
            <h3 style="margin: 0; color: #f59e0b;">{budget_utilization:.1f}%</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280;">Budget Utilization</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed_goals = len([g for g in st.session_state.financial_goals if (g['current'] / g['target']) >= 1.0])
        
        st.markdown(f"""
        <div class="metrics-card">
            <h3 style="margin: 0; color: #8b5cf6;">{completed_goals}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280;">Goals Completed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Alerts section
    st.markdown("#### 🚨 Smart Alerts")
    
    alerts = []
    
    # Check for overspending
    for category, data in st.session_state.budget_data.items():
        if data['spent'] > data['budget']:
            overspend = data['spent'] - data['budget']
            alerts.append({
                'type': 'overspend',
                'message': f"You've exceeded your {category} budget by R{overspend:,.2f}"
            })
    
    # Check for low savings rate
    if current_savings_rate < 20:
        alerts.append({
            'type': 'savings',
            'message': f"Your current savings rate ({current_savings_rate}%) is below the recommended 20%"
        })
    
    # Check for approaching goal deadlines
    for goal in st.session_state.financial_goals:
        days_left = (datetime.strptime(goal['deadline'], '%Y-%m-%d') - datetime.now()).days
        progress = (goal['current'] / goal['target']) * 100
        if days_left < 30 and progress < 90:
            alerts.append({
                'type': 'goal',
                'message': f"Goal '{goal['name']}' has only {days_left} days left and is {progress:.1f}% complete"
            })
    
    if alerts:
        for alert in alerts:
            if alert['type'] == 'overspend':
                st.markdown(f"""
                <div class="alert-overspend">
                    <strong>⚠️ Overspending Alert:</strong> {alert['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-overspend">
                    <strong>📊 Financial Alert:</strong> {alert['message']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <strong>✅ All Good:</strong> No alerts at this time. Keep up the great work!
        </div>
        """, unsafe_allow_html=True)
