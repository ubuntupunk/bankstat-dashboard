import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import pandas as pd
import time

def render_voting_analytics(css_content):
    """Render voting analytics and insights."""
    st.markdown("### 📊 Voting Analytics & Insights")
    st.markdown("Explore community voting patterns and discover trending financial services!")
    
    # Create sample analytics data
    services = st.session_state.financial_services
    goals = st.session_state.community_goals
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_votes = sum(s['upvotes'] + s['downvotes'] + s['recommends'] for s in services)
        metrics_card_html_total_votes = f"""
        <style>{css_content}</style>
        <div class="metrics-card">
            <div style="font-size: 2rem; font-weight: bold; color: #3b82f6;">{total_votes:,}</div>
            <div style="color: #6b7280;">Total Votes Cast</div>
        </div>
        """
        components.html(metrics_card_html_total_votes, height=100)
    
    with col2:
        total_participants = sum(g['participants'] for g in goals)
        metrics_card_html_total_participants = f"""
        <style>{css_content}</style>
        <div class="metrics-card">
            <div style="font-size: 2rem; font-weight: bold; color: #10b981;">{total_participants:,}</div>
            <div style="color: #6b7280;">Goal Participants</div>
        </div>
        """
        components.html(metrics_card_html_total_participants, height=100)
    
    with col3:
        avg_completion = sum(g['completion_rate'] for g in goals) / len(goals) if goals else 0
        metrics_card_html_avg_completion = f"""
        <style>{css_content}</style>
        <div class="metrics-card">
            <div style="font-size: 2rem; font-weight: bold; color: #f59e0b;">{avg_completion:.1f}%</div>
            <div style="color: #6b7280;">Avg Success Rate</div>
        </div>
        """
        components.html(metrics_card_html_avg_completion, height=100)
    
    with col4:
        active_services = len([s for s in services if s['upvotes'] + s['recommends'] > s['downvotes']])
        metrics_card_html_active_services = f"""
        <style>{css_content}</style>
        <div class="metrics-card">
            <div style="font-size: 2rem; font-weight: bold; color: #ef4444;">{active_services}</div>
            <div style="color: #6b7280;">Top Rated Services</div>
        </div>
        """
        components.html(metrics_card_html_active_services, height=100)
    
    st.markdown("---")
    
    # Voting trends chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Service Voting Trends")
        
        # Create voting data for chart
        chart_data = []
        for service in services[:6]:  # Top 6 services
            chart_data.append({
                'Service': service['name'][:15] + ('...' if len(service['name']) > 15 else ''),
                'Upvotes': service['upvotes'],
                'Recommends': service['recommends'],
                'Downvotes': service['downvotes']
            })
        
        df = pd.DataFrame(chart_data)
        
        fig = px.bar(df, x='Service', y=['Upvotes', 'Recommends', 'Downvotes'],
                     title="Voting Distribution by Service",
                     color_discrete_map={
                         'Upvotes': '#10b981',
                         'Recommends': '#3b82f6', 
                         'Downvotes': '#ef4444'
                     })
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True, key=f"service_voting_chart_{time.time()}")
    
    with col2:
        st.markdown("#### 🎯 Goal Participation Trends")
        
        # Create goal participation data
        goal_data = []
        for goal in goals[:6]:  # Top 6 goals
            goal_data.append({
                'Goal': goal['name'][:20] + ('...' if len(goal['name']) > 20 else ''),
                'Participants': goal['participants'],
                'Success Rate': goal['completion_rate']
            })
        
        df_goals = pd.DataFrame(goal_data)
        
        fig2 = px.scatter(df_goals, x='Participants', y='Success Rate', 
                         size='Participants', hover_data=['Goal'],
                         title="Goal Success vs Participation",
                         color='Success Rate',
                         color_continuous_scale='viridis')
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True, key=f"goal_participation_chart_{time.time()}")
    
    # Category breakdown
    st.markdown("#### 🏷️ Service Categories Performance")
    
    # Calculate category stats
    category_stats = {}
    for service in services:
        cat = service['category']
        if cat not in category_stats:
            category_stats[cat] = {
                'count': 0,
                'total_upvotes': 0,
                'total_recommends': 0,
                'total_downvotes': 0
            }
        
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_upvotes'] += service['upvotes']
        category_stats[cat]['total_recommends'] += service['recommends']
        category_stats[cat]['total_downvotes'] += service['downvotes']
    
    # Display category performance
    for category, stats in category_stats.items():
        total_positive = stats['total_upvotes'] + stats['total_recommends']
        total_votes = total_positive + stats['total_downvotes']
        approval_rate = (total_positive / total_votes * 100) if total_votes > 0 else 0
        
        category_item_html = f"""
        <style>{css_content}</style>
        <div class="activity-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #1f2937;">{category}</h4>
                    <div style="color: #6b7280;">{stats['count']} services • {approval_rate:.1f}% approval rate</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #10b981; font-weight: bold;">👍 {stats['total_upvotes']} ⭐ {stats['total_recommends']}</div>
                    <div style="color: #ef4444; font-weight: bold;">👎 {stats['total_downvotes']}</div>
                </div>
            </div>
            <div style="margin-top: 0.5rem;">
                <div style="background: #e5e7eb; border-radius: 0.5rem; height: 0.5rem;">
                    <div style="background: #10b981; height: 100%; border-radius: 0.5rem; width: {approval_rate}%;"></div>
                </div>
            </div>
        </div>
        """
        components.html(category_item_html, height=120)
    
    # Recent activity feed
    st.markdown("---")
    st.markdown("#### 🔥 Recent Community Activity")
    
    # Generate some sample recent activities
    activities = [
        {"type": "vote", "user": "FinanceGuru_SA", "action": "upvoted", "target": "Discovery Bank", "time": "2 minutes ago"},
        {"type": "goal", "user": "SavingsQueen_JHB", "action": "joined", "target": "Emergency Fund Challenge", "time": "5 minutes ago"},
        {"type": "vote", "user": "InvestmentKing", "action": "recommended", "target": "Capitec Bank", "time": "8 minutes ago"},
        {"type": "goal", "user": "BudgetMaster_CPT", "action": "completed", "target": "First Home Deposit", "time": "12 minutes ago"},
        {"type": "vote", "user": "DebtFreeWarrior", "action": "upvoted", "target": "Old Mutual", "time": "15 minutes ago"},
        {"type": "goal", "user": "PropertyPro_CT", "action": "created", "target": "Investment Portfolio Start", "time": "18 minutes ago"},
    ]
    
    for activity in activities:
        icon = "🗳️" if activity["type"] == "vote" else "🎯"
        color = "#3b82f6" if activity["type"] == "vote" else "#10b981"
        
        activity_item_html = f"""
        <style>{css_content}</style>
        <div class="activity-item">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <div style="flex: 1;">
                    <span style="font-weight: bold; color: {color};">{activity['user']}</span>
                    <span style="color: #6b7280;"> {activity['action']} </span>
                    <span style="font-weight: bold; color: #1f2937;">{activity['target']}</span>
                </div>
                <div style="color: #9ca3af; font-size: 0.875rem;">
                    {activity['time']}
                </div>
            </div>
        </div>
        """
        components.html(activity_item_html, height=80)
