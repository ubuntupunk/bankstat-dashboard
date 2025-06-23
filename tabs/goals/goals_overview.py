import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

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
