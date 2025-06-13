import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from tabs.goals.goals_overview import render_goals_overview
from tabs.goals.budget_management import render_budget_management
from tabs.goals.metrics_alerts import render_metrics_alerts
from tabs.goals.incentives_rewards import render_incentives
import plotly.graph_objects as go
import plotly.express as px

def render_goals_tab():
    """Render the Goals tab with financial goals management."""
    # Load CSS (assuming similar structure to tools tab)
    css_path = os.path.join(os.path.dirname(__file__), "goals.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("tools.css file not found. Please ensure it exists in the same directory as tools_tab.py.")
        return
        
    # Initialize session state for goals and data
    if 'financial_goals' not in st.session_state:
        st.session_state.financial_goals = [
            {
                'id': 1,
                'name': 'Emergency Fund',
                'target': 50000,
                'current': 32000,
                'deadline': '2025-12-31',
                'category': 'Safety',
                'priority': 'High'
            },
            {
                'id': 2,
                'name': 'Vacation Fund',
                'target': 25000,
                'current': 8500,
                'deadline': '2025-08-15',
                'category': 'Lifestyle',
                'priority': 'Medium'
            },
            {
                'id': 3,
                'name': 'Car Down Payment',
                'target': 80000,
                'current': 45000,
                'deadline': '2026-03-01',
                'category': 'Asset',
                'priority': 'High'
            }
        ]
    
    if 'budget_data' not in st.session_state:
        st.session_state.budget_data = {
            'Housing': {'budget': 12000, 'spent': 11800},
            'Food': {'budget': 4000, 'spent': 4200},
            'Transportation': {'budget': 3000, 'spent': 2800},
            'Utilities': {'budget': 1500, 'spent': 1350},
            'Entertainment': {'budget': 2000, 'spent': 2400},
            'Healthcare': {'budget': 1000, 'spent': 850},
            'Other': {'budget': 1500, 'spent': 1200}
        }
    
    if 'user_points' not in st.session_state:
        st.session_state.user_points = 2850
    
    if 'savings_history' not in st.session_state:
        # Generate sample savings rate data
        dates = pd.date_range(start='2024-01-01', end='2025-05-31', freq='M')
        savings_rates = [15, 18, 22, 19, 25, 28, 24, 26, 30, 27, 32, 29, 31, 28, 35, 33, 30]
        st.session_state.savings_history = pd.DataFrame({
            'Date': dates,
            'Savings_Rate': savings_rates[:len(dates)]
        })

    # Header
    st.markdown("""
        <div class="goals-container">
            <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🎯 Financial Goals Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Track your progress, manage your budget, and earn rewards</p>
        </div>
    """, unsafe_allow_html=True)

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Goals Overview", "💰 Budget Management", "📈 Metrics & Alerts", "🏆 Incentives & Rewards" ])
    
    with tab1:
        render_goals_overview()
    
    with tab2:
        render_budget_management()
    
    with tab3:
        render_metrics_alerts()
    
    with tab4:
        render_incentives()
 

def render_goals_overview():
    """Render the goals overview with progress cards."""
    st.markdown("### Active Financial Goals")
    
    # Add new goal section
    with st.expander("➕ Add New Goal"):
        col1, col2 = st.columns(2)
        with col1:
            new_goal_name = st.text_input("Goal Name")
            new_goal_target = st.number_input("Target Amount (R)", min_value=0.0, step=100.0)
        with col2:
            new_goal_deadline = st.date_input("Target Date")
            new_goal_category = st.selectbox("Category", ["Safety", "Lifestyle", "Asset", "Investment", "Other"])
        
        if st.button("Add Goal") and new_goal_name and new_goal_target > 0:
            new_id = max([goal['id'] for goal in st.session_state.financial_goals]) + 1
            st.session_state.financial_goals.append({
                'id': new_id,
                'name': new_goal_name,
                'target': new_goal_target,
                'current': 0,
                'deadline': str(new_goal_deadline),
                'category': new_goal_category,
                'priority': 'Medium'
            })
            st.success(f"Goal '{new_goal_name}' added successfully!")
            st.rerun()
    
    # Display goal cards
    for i, goal in enumerate(st.session_state.financial_goals):
        progress = (goal['current'] / goal['target']) * 100
        days_left = (datetime.strptime(goal['deadline'], '%Y-%m-%d') - datetime.now()).days
        
        # Color coding based on progress and urgency
        if progress >= 100:
            border_color = "#10b981"  # Green
            status_emoji = "✅"
        elif progress >= 75:
            border_color = "#3b82f6"  # Blue
            status_emoji = "🔥"
        elif days_left < 30:
            border_color = "#ef4444"  # Red
            status_emoji = "⚠️"
        else:
            border_color = "#f59e0b"  # Orange
            status_emoji = "📈"
        
        st.markdown(f"""
        <div class="goal-card" style="border-left-color: {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #1f2937;">{status_emoji} {goal['name']}</h3>
                <span style="background: {border_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem;">
                    {goal['category']}
                </span>
            </div>
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: #6b7280;">Progress: R{goal['current']:,.2f} / R{goal['target']:,.2f}</span>
                    <span style="color: #6b7280; font-weight: bold;">{progress:.1f}%</span>
                </div>
                <div style="background: #e5e7eb; border-radius: 0.5rem; height: 0.75rem;">
                    <div style="background: {border_color}; height: 100%; border-radius: 0.5rem; width: {min(progress, 100)}%;"></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; color: #6b7280; font-size: 0.875rem;">
                <span>🗓️ Due: {goal['deadline']}</span>
                <span>⏰ {days_left} days left</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Update progress section
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            update_amount = st.number_input(f"Add to {goal['name']}", min_value=0.0, step=50.0, key=f"update_{goal['id']}")
        with col2:
            if st.button("Update", key=f"btn_{goal['id']}") and update_amount > 0:
                st.session_state.financial_goals[i]['current'] += update_amount
                # Award points for progress
                points_earned = int(update_amount / 100)
                st.session_state.user_points += points_earned
                st.success(f"Updated! Earned {points_earned} points!")
                st.rerun()
        with col3:
            if st.button("Delete", key=f"del_{goal['id']}", type="secondary"):
                st.session_state.financial_goals.pop(i)
                st.rerun()

def render_budget_management():
    """Render budget management with pie chart and input forms."""
    st.markdown("### Budget Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Calculate totals
        total_budget = sum([cat['budget'] for cat in st.session_state.budget_data.values()])
        total_spent = sum([cat['spent'] for cat in st.session_state.budget_data.values()])
        
        # Create pie chart
        categories = list(st.session_state.budget_data.keys())
        spent_amounts = [st.session_state.budget_data[cat]['spent'] for cat in categories]
        budget_amounts = [st.session_state.budget_data[cat]['budget'] for cat in categories]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=categories,
                values=spent_amounts,
                hole=0.4,
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Spent: R%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Budget Allocation (Current Spending)",
            font=dict(size=12),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Budget Summary")
        
        budget_status = "Over Budget" if total_spent > total_budget else "Under Budget"
        status_color = "#ef4444" if total_spent > total_budget else "#10b981"
        
        st.markdown(f"""
        <div style="background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="margin: 0 0 1rem 0; color: #374151;">Monthly Overview</h4>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #6b7280;">Total Budget:</span>
                <span style="float: right; font-weight: bold;">R{total_budget:,.2f}</span>
            </div>
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #6b7280;">Total Spent:</span>
                <span style="float: right; font-weight: bold;">R{total_spent:,.2f}</span>
            </div>
            <hr style="margin: 1rem 0;">
            <div style="margin-bottom: 0.5rem;">
                <span style="color: #6b7280;">Remaining:</span>
                <span style="float: right; font-weight: bold; color: {status_color};">R{total_budget - total_spent:,.2f}</span>
            </div>
            <div style="text-align: center; margin-top: 1rem;">
                <span style="background: {status_color}; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem;">
                    {budget_status}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Budget input form
    st.markdown("#### Update Budget Categories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Budget Amounts**")
        for category in categories[:4]:
            new_budget = st.number_input(
                f"{category} Budget",
                value=float(st.session_state.budget_data[category]['budget']),
                min_value=0.0,
                step=100.0,
                key=f"budget_{category}"
            )
            st.session_state.budget_data[category]['budget'] = new_budget
    
    with col2:
        st.markdown("**Spent Amounts**")
        for category in categories[4:]:
            new_budget = st.number_input(
                f"{category} Budget",
                value=float(st.session_state.budget_data[category]['budget']),
                min_value=0.0,
                step=100.0,
                key=f"budget_{category}"
            )
            st.session_state.budget_data[category]['budget'] = new_budget
    
    # Expense input
    st.markdown("#### Add New Expense")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        expense_category = st.selectbox("Category", categories)
    with col2:
        expense_amount = st.number_input("Amount", min_value=0.0, step=10.0)
    with col3:
        if st.button("Add Expense") and expense_amount > 0:
            st.session_state.budget_data[expense_category]['spent'] += expense_amount
            st.success(f"Added R{expense_amount:,.2f} to {expense_category}")
            st.rerun()

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

def render_incentives():
    """Render incentives and rewards system."""
    st.markdown("### 🏆 Incentives & Rewards")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="incentive-card">
            <h2 style="margin: 0 0 1rem 0; text-align: center;">🎉 Your Points</h2>
            <h1 style="margin: 0; text-align: center; font-size: 3rem;">{st.session_state.user_points:,}</h1>
            <p style="margin: 0.5rem 0 0 0; text-align: center;">Keep saving to earn more!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### How to Earn Points")
        st.markdown("""
        - **Goal Progress**: 1 point per R1 added to goals
        - **Budget Compliance**: 100 points for staying under budget
        - **Savings Target**: 200 points for meeting monthly savings rate
        - **Goal Completion**: 500 points per completed goal
        """)
    
    with col2:
        st.markdown("#### 🎁 Available Rewards")
        
        rewards = [
            {'name': '☕ Coffee Voucher', 'points': 500, 'description': 'R50 coffee shop voucher'},
            {'name': '🎬 Movie Tickets', 'points': 800, 'description': '2x cinema tickets'},
            {'name': '🍕 Dinner Voucher', 'points': 1200, 'description': 'R200 restaurant voucher'},
            {'name': '📱 Tech Gadget', 'points': 2000, 'description': 'Wireless earbuds or power bank'},
            {'name': '✈️ Weekend Getaway', 'points': 5000, 'description': 'R1000 travel voucher'},
            {'name': '💎 Premium Investment Advice', 'points': 10000, 'description': '1-hour consultation with financial advisor'}
        ]
        
        for reward in rewards:
            can_claim = st.session_state.user_points >= reward['points']
            
            card_style = "background: white; border: 2px solid #10b981;" if can_claim else "background: #f9fafb; border: 2px solid #d1d5db;"
            text_color = "#059669" if can_claim else "#6b7280"
            
            st.markdown(f"""
            <div style="{card_style} border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: {text_color};">{reward['name']}</h4>
                        <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 0.875rem;">{reward['description']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-weight: bold; color: {text_color};">{reward['points']:,} pts</div>
                        <div style="margin-top: 0.5rem;">
                            {'🔓 Available' if can_claim else '🔒 Locked'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if can_claim:
                col_a, col_b, col_c = st.columns([2, 1, 2])
                with col_b:
                    if st.button(f"Claim", key=f"claim_{reward['name']}"):
                        st.session_state.user_points -= reward['points']
                        st.success(f"🎉 Claimed {reward['name']}! Check your email for details.")
                        st.rerun()
        
        # Bonus challenges
        st.markdown("#### 🎯 This Month's Challenges")
        
        challenges = [
            {'name': 'Save 25% this month', 'reward': 300, 'progress': 80},
            {'name': 'Stay under budget in all categories', 'reward': 500, 'progress': 60},
            {'name': 'Add R2000 to any goal', 'reward': 200, 'progress': 45}
        ]
        
        for challenge in challenges:
            st.markdown(f"""
            <div style="background: #fffbeb; border: 1px solid #fbbf24; border-radius: 0.5rem; padding: 1rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: between; margin-bottom: 0.5rem;">
                    <span style="font-weight: bold;">{challenge['name']}</span>
                    <span style="color: #f59e0b;">+{challenge['reward']} points</span>
                </div>
                <div style="background: #e5e7eb; border-radius: 0.25rem; height: 0.5rem;">
                    <div style="background: #f59e0b; height: 100%; border-radius: 0.25rem; width: {challenge['progress']}%;"></div>
                </div>
                <div style="text-align: right; font-size: 0.875rem; color: #6b7280; margin-top: 0.25rem;">
                    {challenge['progress']}% complete
                </div>
            </div>
            """, unsafe_allow_html=True)
