import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time

def render_community_goals(css_content):
    """Render community goals section."""
    st.markdown("### 🎯 Trending Community Goals")
    st.markdown("Join popular financial goals and share your journey with the community!")
    
    # Add goal creation option
    with st.expander("🎯 Create Your Own Goal"):
        with st.form(key=f"create_goal_form_community_goals_{time.time()}"):
            col1, col2 = st.columns(2)
            with col1:
                goal_name = st.text_input("Goal Name")
                goal_category = st.selectbox("Category", ["Safety", "Asset", "Debt Reduction", "Investment", "Other"])
                target_amount = st.number_input("Target Amount (R)", min_value=0, value=10000)
            
            with col2:
                goal_description = st.text_area("Description")
                tips_input = st.text_area("Tips (one per line)")
            
            if st.form_submit_button("Create Goal"):
                if goal_name and goal_description:
                    tips_list = [tip.strip() for tip in tips_input.split('\n') if tip.strip()]
                    new_goal = {
                        'id': len(st.session_state.community_goals) + 1,
                        'name': goal_name,
                        'description': goal_description,
                        'category': goal_category,
                        'target_amount': target_amount,
                        'participants': 1,
                        'completion_rate': 0,
                        'avg_progress': 0,
                        'created_by': 'You',
                        'likes': 0,
                        'user_participating': True,
                        'tips': tips_list if tips_list else ['Stay consistent and track your progress!']
                    }
                    st.session_state.community_goals.append(new_goal)
                    st.success(f"Created goal: {goal_name}!")
                    st.rerun()
                else:
                    st.error("Please fill in the required fields")
    
    # Filter and sort options
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Filter by category:",
            ["All", "Safety", "Asset", "Debt Reduction", "Investment", "Other"],
            key=f"goal_category_filter_{time.time()}"
        )
    
    with col2:
        goal_sort = st.selectbox(
            "Sort by:",
            ["Most Popular", "Highest Success Rate", "Most Liked", "Newest"],
            key=f"goal_sort_{time.time()}"
        )
    
    # Filter goals
    goals = st.session_state.community_goals
    if category_filter != "All":
        goals = [g for g in goals if g['category'] == category_filter]
    
    # Sort goals
    if goal_sort == "Most Popular":
        goals = sorted(goals, key=lambda x: x['participants'], reverse=True)
    elif goal_sort == "Highest Success Rate":
        goals = sorted(goals, key=lambda x: x['completion_rate'], reverse=True)
    elif goal_sort == "Most Liked":
        goals = sorted(goals, key=lambda x: x['likes'], reverse=True)
    else:  # Newest
        goals = sorted(goals, key=lambda x: x['id'], reverse=True)
    
    for i, goal in enumerate(goals):
        # Determine trending status
        if i == 0:
            trend_emoji = "🔥"
            trend_text = "Most Popular"
            border_color = "#ef4444"
        elif goal['completion_rate'] > 50:
            trend_emoji = "⭐"
            trend_text = "High Success Rate"
            border_color = "#10b981"
        else:
            trend_emoji = "📈"
            trend_text = "Growing"
            border_color = "#3b82f6"
        
        goal_card_html = f"""
        <style>{css_content}</style>
        <div class="goal-card" style="border-left-color: {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <h3 style="margin: 0; color: #1f2937;">{trend_emoji} {goal['name']}</h3>
                    <span style="background: {border_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem;">
                        {trend_text}
                    </span>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: bold; color: #1f2937;">{goal['participants']:,} participants</div>
                    <div style="color: #6b7280; font-size: 0.875rem;">❤️ {goal['likes']} likes</div>
                </div>
            </div>
            
            <p style="color: #6b7280; margin-bottom: 1rem;">{goal['description']}</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #3b82f6;">R{goal['target_amount']:,}</div>
                    <div style="color: #6b7280; font-size: 0.875rem;">Target Amount</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #10b981;">{goal['completion_rate']}%</div>
                    <div style="color: #6b7280; font-size: 0.875rem;">Success Rate</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: #f59e0b;">{goal['avg_progress']}%</div>
                    <div style="color: #6b7280; font-size: 0.875rem;">Avg Progress</div>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <div style="font-weight: bold; color: #1f2937; margin-bottom: 0.5rem;">💡 Community Tips:</div>
                <ul style="margin: 0; padding-left: 1.5rem; color: #6b7280;">
                    {' '.join([f'<li style="margin-bottom: 0.25rem;">{tip}</li>' for tip in goal['tips']])}
                </ul>
            </div>
            
            <div style="color: #6b7280; font-size: 0.875rem; margin-bottom: 1rem;">
                Created by: <strong>{goal['created_by']}</strong>
            </div>
        </div>
        """
        components.html(goal_card_html, height=400)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if not goal['user_participating']:
                if st.button(f"🚀 Join Goal", key=f"join_{goal['id']}_{time.time()}"):
                    goal['user_participating'] = True
                    goal['participants'] += 1
                    st.success(f"You've joined '{goal['name']}'!")
                    st.rerun()
            else:
                st.markdown("<span style='color: #10b981; font-weight: bold;'>✓ Joined</span>", unsafe_allow_html=True)
        
        with col2:
            liked = goal['id'] in st.session_state.user_goal_likes
            button_text = "❤️ Liked" if liked else "❤️ Like"
            if st.button(button_text, key=f"like_{goal['id']}_{time.time()}", disabled=liked):
                goal['likes'] += 1
                st.session_state.user_goal_likes.add(goal['id'])
                st.success("Goal liked!")
                st.rerun()
        
        with col3:
            if st.button(f"📤 Share", key=f"share_{goal['id']}_{time.time()}"):
                st.info("Share link copied to clipboard!")
        
        # Progress bar for community average
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: #6b7280;">Community Progress</span>
                <span style="color: #6b7280; font-weight: bold;">{goal['avg_progress']}%</span>
            </div>
            <div style="background: #e5e7eb; border-radius: 0.5rem; height: 0.75rem;">
                <div style="background: {border_color}; height: 100%; border-radius: 0.5rem; width: {goal['avg_progress']}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
