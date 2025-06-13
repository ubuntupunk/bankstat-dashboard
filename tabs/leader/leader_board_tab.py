import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import os
import random
import streamlit.components.v1 as components
import time

def leader_board_tab():
    """
    Enhanced leaderboard with voting for financial services and community goals.
    """
    # Load CSS
    css_path = os.path.join(os.path.dirname(__file__), "leader_board.css")
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css_content = f.read()
    else:
        st.warning("leader_board.css not found. Cards may not render correctly.")
    
    # Initialize session state data
    initialize_leaderboard_data()
    
    # Apply global CSS
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="goals-container">
            <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">🏅 Community Leaderboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Vote for the best financial services and discover trending community goals</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏦 Financial Services", 
        "🎯 Community Goals", 
        "👥 Top Contributors", 
        "📊 Voting Analytics"
    ])
    
    with tab1:
        render_financial_services_voting(css_content)
    
    with tab2:
        render_community_goals(css_content)
    
    with tab3:
        render_top_contributors(css_content)
    
    with tab4:
        render_voting_analytics(css_content)

def initialize_leaderboard_data():
    """Initialize session state with sample data matching the database model."""
    
    if 'financial_services' not in st.session_state:
        st.session_state.financial_services = [
            {
                'id': 1,
                'name': 'Discovery Bank',
                'description': 'Digital-first banking with rewards and no monthly fees',
                'category': 'Banking',
                'upvotes': 245,
                'downvotes': 12,
                'recommends': 189,
                'user_voted': None,
                'features': ['No monthly fees', 'Cashback rewards', 'Digital banking', 'Investment platform']
            },
            {
                'id': 2,
                'name': 'Old Mutual',
                'description': 'Comprehensive life insurance and investment solutions',
                'category': 'Insurance',
                'upvotes': 198,
                'downvotes': 23,
                'recommends': 156,
                'user_voted': None,
                'features': ['Life insurance', 'Unit trusts', 'Retirement planning', 'Risk cover']
            },
            {
                'id': 3,
                'name': 'Capitec Bank',
                'description': 'Simple, affordable banking for everyone',
                'category': 'Banking',
                'upvotes': 312,
                'downvotes': 8,
                'recommends': 278,
                'user_voted': None,
                'features': ['Low fees', 'Branch accessibility', 'Simple products', 'Mobile banking']
            },
            {
                'id': 4,
                'name': 'Santam Insurance',
                'description': 'Reliable short-term insurance for your assets',
                'category': 'Insurance',
                'upvotes': 167,
                'downvotes': 19,
                'recommends': 134,
                'user_voted': None,
                'features': ['Motor insurance', 'Home insurance', 'Business cover', 'Travel insurance']
            },
            {
                'id': 5,
                'name': 'FNB',
                'description': 'Full-service banking with innovative digital solutions',
                'category': 'Banking',
                'upvotes': 203,
                'downvotes': 31,
                'recommends': 167,
                'user_voted': None,
                'features': ['eBucks rewards', 'Digital banking', 'Business banking', 'Investment products']
            },
            {
                'id': 6,
                'name': 'Momentum',
                'description': 'Wellness-focused insurance and investment products',
                'category': 'Insurance',
                'upvotes': 143,
                'downvotes': 15,
                'recommends': 112,
                'user_voted': None,
                'features': ['Wellness rewards', 'Life insurance', 'Medical aid', 'Investment solutions']
            },
            {
                'id': 7,
                'name': 'Standard Bank',
                'description': 'Africa\'s largest bank with comprehensive services',
                'category': 'Banking',
                'upvotes': 178,
                'downvotes': 27,
                'recommends': 145,
                'user_voted': None,
                'features': ['International banking', 'Business solutions', 'Investment banking', 'Digital wallet']
            },
            {
                'id': 8,
                'name': 'Sanlam',
                'description': 'Leading financial services group with diverse offerings',
                'category': 'Insurance',
                'upvotes': 134,
                'downvotes': 21,
                'recommends': 98,
                'user_voted': None,
                'features': ['Life insurance', 'Investment products', 'Employee benefits', 'Wealth management']
            }
        ]
    
    if 'community_goals' not in st.session_state:
        st.session_state.community_goals = [
            {
                'id': 1,
                'name': 'Emergency Fund Challenge',
                'description': 'Build 6 months of expenses as emergency fund',
                'category': 'Safety',
                'target_amount': 50000,
                'participants': 1247,
                'completion_rate': 68,
                'avg_progress': 72,
                'created_by': 'FinanceGuru_SA',
                'likes': 892,
                'user_participating': False,
                'tips': [
                    'Start with R100 per month and increase gradually',
                    'Use a separate high-yield savings account',
                    'Automate transfers on payday'
                ]
            },
            {
                'id': 2,
                'name': 'First Home Deposit',
                'description': 'Save for a 20% deposit on your first home',
                'category': 'Asset',
                'target_amount': 200000,
                'participants': 834,
                'completion_rate': 23,
                'avg_progress': 45,
                'created_by': 'PropertyPro_CT',
                'likes': 623,
                'user_participating': True,
                'tips': [
                    'Research different home loan options',
                    'Consider first-time buyer programs',
                    'Save on rent by house-sitting or sharing'
                ]
            },
            {
                'id': 3,
                'name': 'Debt Freedom Journey',
                'description': 'Pay off all consumer debt using snowball method',
                'category': 'Debt Reduction',
                'target_amount': 75000,
                'participants': 2156,
                'completion_rate': 41,
                'avg_progress': 58,
                'created_by': 'DebtFreeLife',
                'likes': 1456,
                'user_participating': False,
                'tips': [
                    'List all debts from smallest to largest',
                    'Pay minimums on all, extra on smallest',
                    'Celebrate small wins to stay motivated'
                ]
            },
            {
                'id': 4,
                'name': 'Retirement Kickstart',
                'description': 'Start retirement savings before age 30',
                'category': 'Investment',
                'target_amount': 100000,
                'participants': 967,
                'completion_rate': 35,
                'avg_progress': 28,
                'created_by': 'RetireEarly_ZA',
                'likes': 734,
                'user_participating': False,
                'tips': [
                    'Take advantage of compound interest',
                    'Contribute to retirement annuity',
                    'Increase contributions with salary increases'
                ]
            },
            {
                'id': 5,
                'name': 'Investment Portfolio Start',
                'description': 'Build your first diversified investment portfolio',
                'category': 'Investment',
                'target_amount': 25000,
                'participants': 1543,
                'completion_rate': 52,
                'avg_progress': 61,
                'created_by': 'InvestmentKing',
                'likes': 1089,
                'user_participating': False,
                'tips': [
                    'Start with low-cost index funds',
                    'Diversify across asset classes',
                    'Don\'t try to time the market'
                ]
            }
        ]
    
    if 'top_contributors' not in st.session_state:
        st.session_state.top_contributors = [
            {
                'username': 'FinanceGuru_SA',
                'total_votes': 1247,
                'goals_created': 8,
                'goals_completed': 12,
                'points': 15600,
                'badge': '🥇 Gold Contributor',
                'streak_days': 89,
                'avatar': '👨‍💼'
            },
            {
                'username': 'SavingsQueen_JHB',
                'total_votes': 978,
                'goals_created': 5,
                'goals_completed': 18,
                'points': 13450,
                'badge': '🥈 Silver Contributor',
                'streak_days': 67,
                'avatar': '👩‍💼'
            },
            {
                'username': 'InvestmentKing',
                'total_votes': 834,
                'goals_created': 12,
                'goals_completed': 9,
                'points': 12890,
                'badge': '🥈 Silver Contributor',
                'streak_days': 45,
                'avatar': '👨‍🎓'
            },
            {
                'username': 'BudgetMaster_CPT',
                'total_votes': 723,
                'goals_created': 3,
                'goals_completed': 15,
                'points': 11200,
                'badge': '🥉 Bronze Contributor',
                'streak_days': 123,
                'avatar': '👩‍🔬'
            },
            {
                'username': 'DebtFreeWarrior',
                'total_votes': 656,
                'goals_created': 7,
                'goals_completed': 11,
                'points': 9870,
                'badge': '🥉 Bronze Contributor',
                'streak_days': 34,
                'avatar': '👨‍🚀'
            },
            {
                'username': 'PropertyPro_CT',
                'total_votes': 589,
                'goals_created': 4,
                'goals_completed': 8,
                'points': 8950,
                'badge': '🏅 Rising Star',
                'streak_days': 28,
                'avatar': '👩‍🏗️'
            }
        ]
    
    # Initialize user voting tracking
    if 'user_service_votes' not in st.session_state:
        st.session_state.user_service_votes = {}
    
    if 'user_goal_likes' not in st.session_state:
        st.session_state.user_goal_likes = set()

def render_financial_services_voting(css_content):
    """Render financial services voting section."""
    st.markdown("### 🏦 Best Financial Services")
    st.markdown("Help the community by voting for the financial services you trust and recommend!")
    
    # Add new service option
    with st.expander("➕ Suggest a New Financial Service"):
        # Use a unique key for the form to prevent duplication issues on reruns.
        # time.time() provides a highly granular unique identifier for each render.
        with st.form(key=f"add_service_userfi_services_{time.time()}"):
            new_name = st.text_input("Service Name")
            new_description = st.text_area("Description")
            new_category = st.selectbox("Category", ["Banking", "Insurance", "Investment", "Other"])
            new_features = st.text_input("Key Features (comma-separated)")
            
            if st.form_submit_button("Add Service"):
                if new_name and new_description:
                    new_service = {
                        'id': len(st.session_state.financial_services) + 1,
                        'name': new_name,
                        'description': new_description,
                        'category': new_category,
                        'upvotes': 0,
                        'downvotes': 0,
                        'recommends': 0,
                        'user_voted': None,
                        'features': [f.strip() for f in new_features.split(',') if f.strip()]
                    }
                    st.session_state.financial_services.append(new_service)
                    st.success(f"Added {new_name} to the leaderboard!")
                    st.rerun()
                else:
                    st.error("Please fill in the required fields")
    
    # Filter options
    col1, col2 = st.columns([1, 2])
    with col1:
        category_filter = st.selectbox(
            "Filter by category:",
            ["All", "Banking", "Insurance", "Investment", "Other"],
            key=f"service_filter_{time.time()}"
        )
    
    with col2:
        sort_option = st.selectbox(
            "Sort by:",
            ["Overall Score", "Most Upvotes", "Most Recommended", "Newest"],
            key=f"service_sort_{time.time()}"
        )
    
    # Filter services
    services = st.session_state.financial_services
    if category_filter != "All":
        services = [s for s in services if s['category'] == category_filter]
    
    # Sort services
    if sort_option == "Overall Score":
        services = sorted(services, key=lambda x: x['upvotes'] + x['recommends'] - x['downvotes'], reverse=True)
    elif sort_option == "Most Upvotes":
        services = sorted(services, key=lambda x: x['upvotes'], reverse=True)
    elif sort_option == "Most Recommended":
        services = sorted(services, key=lambda x: x['recommends'], reverse=True)
    else:  # Newest
        services = sorted(services, key=lambda x: x['id'], reverse=True)
    
    for i, service in enumerate(services):
        score = service['upvotes'] + service['recommends'] - service['downvotes']
        
        # Determine ranking emoji
        if i == 0:
            rank_emoji = "🥇"
            rank_color = "#ffd700"
        elif i == 1:
            rank_emoji = "🥈"
            rank_color = "#c0c0c0"
        elif i == 2:
            rank_emoji = "🥉"
            rank_color = "#cd7f32"
        else:
            rank_emoji = f"#{i+1}"
            rank_color = "#6b7280"
        
        # Service card
        service_card_html = f"""
        <style>{css_content}</style>
        <div class="goal-card" style="border-left-color: {rank_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="font-size: 2rem;">{rank_emoji}</span>
                    <div>
                        <h3 style="margin: 0; color: #1f2937;">{service['name']}</h3>
                        <span style="background: {rank_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.875rem;">
                            {service['category']}
                        </span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: {rank_color};">
                        Score: {score}
                    </div>
                </div>
            </div>
            
            <p style="color: #6b7280; margin-bottom: 1rem;">{service['description']}</p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                {' '.join([f'<span style="background: #e5e7eb; padding: 0.25rem 0.5rem; border-radius: 0.5rem; font-size: 0.875rem;">{feature}</span>' for feature in service['features']])}
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; gap: 1rem;">
                    <span style="color: #10b981;">👍 {service['upvotes']}</span>
                    <span style="color: #ef4444;">👎 {service['downvotes']}</span>
                    <span style="color: #3b82f6;">⭐ {service['recommends']}</span>
                </div>
            </div>
        </div>
        """
        components.html(service_card_html, height=250)
        
        # Voting buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        user_vote = st.session_state.user_service_votes.get(service['id'])
        
        with col1:
            button_style = "✅ Upvoted" if user_vote == 'upvote' else "👍 Upvote"
            disabled = user_vote == 'upvote'
            if st.button(button_style, key=f"up_{service['id']}_{time.time()}", disabled=disabled):
                if user_vote == 'downvote':
                    service['downvotes'] -= 1
                elif user_vote == 'recommend':
                    service['recommends'] -= 1
                elif user_vote != 'upvote':
                    service['upvotes'] += 1
                
                st.session_state.user_service_votes[service['id']] = 'upvote'
                st.success("Upvote recorded!")
                st.rerun()
        
        with col2:
            button_style = "✅ Downvoted" if user_vote == 'downvote' else "👎 Downvote"
            disabled = user_vote == 'downvote'
            if st.button(button_style, key=f"down_{service['id']}_{time.time()}", disabled=disabled):
                if user_vote == 'upvote':
                    service['upvotes'] -= 1
                elif user_vote == 'recommend':
                    service['recommends'] -= 1
                elif user_vote != 'downvote':
                    service['downvotes'] += 1
                
                st.session_state.user_service_votes[service['id']] = 'downvote'
                st.success("Downvote recorded!")
                st.rerun()
        
        with col3:
            button_style = "✅ Recommended" if user_vote == 'recommend' else "⭐ Recommend"
            disabled = user_vote == 'recommend'
            if st.button(button_style, key=f"rec_{service['id']}_{time.time()}", disabled=disabled):
                if user_vote == 'upvote':
                    service['upvotes'] -= 1
                elif user_vote == 'downvote':
                    service['downvotes'] -= 1
                elif user_vote != 'recommend':
                    service['recommends'] += 1
                
                st.session_state.user_service_votes[service['id']] = 'recommend'
                st.success("Recommendation recorded!")
                st.rerun()
        
        with col4:
            if user_vote:
                st.markdown(f"<span style='color: #10b981; font-weight: bold;'>✓ You voted: {user_vote}</span>", unsafe_allow_html=True)

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

def render_top_contributors(css_content):
    """Render top contributors leaderboard."""
    st.markdown("### 👥 Top Contributors")
    st.markdown("Recognize our most active community members who help make our financial community thrive!")
    
    contributors = st.session_state.top_contributors
    
    # Create podium for top 3
    if len(contributors) >= 3:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        # Second place
        with col1:
            contrib = contributors[1]
            contributor_card_html_2nd = f"""
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #c0c0c0, #e8e8e8); border-radius: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">{contrib['avatar']}</div>
                <div style="font-size: 2rem;">🥈</div>
                <h3 style="margin: 0.5rem 0; color: #1f2937;">{contrib['username']}</h3>
                <div style="font-weight: bold; color: #6b7280;">{contrib['points']:,} points</div>
                <div style="color: #6b7280; font-size: 0.875rem;">{contrib['badge']}</div>
            </div>
            """
            components.html(contributor_card_html_2nd, height=200)
        
        # First place (winner)
        with col2:
            contrib = contributors[0]
            contributor_card_html_1st = f"""
            <style>{css_content}</style>
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #ffd700, #ffed4e); border-radius: 1rem; margin-bottom: 1rem; transform: scale(1.05);">
                <div style="font-size: 3rem;">{contrib['avatar']}</div>
                <div style="font-size: 2rem;">🥇</div>
                <h3 style="margin: 0.5rem 0; color: #1f2937;">{contrib['username']}</h3>
                <div style="font-weight: bold; color: #1f2937;">{contrib['points']:,} points</div>
                <div style="color: #1f2937; font-size: 0.875rem; font-weight: bold;">{contrib['badge']}</div>
            </div>
            """
            components.html(contributor_card_html_1st, height=200)
        
        # Third place
        with col3:
            contrib = contributors[2]
            contributor_card_html_3rd = f"""
            <style>{css_content}</style>
            <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #cd7f32, #daa520); border-radius: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">{contrib['avatar']}</div>
                <div style="font-size: 2rem;">🥉</div>
                <h3 style="margin: 0.5rem 0; color: #1f2937;">{contrib['username']}</h3>
                <div style="font-weight: bold; color: #1f2937;">{contrib['points']:,} points</div>
                <div style="color: #1f2937; font-size: 0.875rem;">{contrib['badge']}</div>
            </div>
            """
            components.html(contributor_card_html_3rd, height=200)
    
    st.markdown("---")
    
    # Full leaderboard with detailed stats
    for i, contributor in enumerate(contributors):
        rank_color = "#ffd700" if i == 0 else "#c0c0c0" if i == 1 else "#cd7f32" if i == 2 else "#6b7280"
        
        contributor_detail_card_html = f"""
        <style>{css_content}</style>
        <div class="goal-card" style="border-left-color: {rank_color};">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="text-align: center; min-width: 60px;">
                    <div style="font-size: 2rem;">{contributor['avatar']}</div>
                    <div style="font-weight: bold; color: {rank_color};">#{i+1}</div>
                </div>
                
                <div style="flex: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h3 style="margin: 0; color: #1f2937;">{contributor['username']}</h3>
                        <div style="font-size: 1.25rem; font-weight: bold; color: {rank_color};">
                            {contributor['points']:,} pts
                        </div>
                    </div>
                    
                    <div style="color: #6b7280; margin-bottom: 1rem;">
                        {contributor['badge']}
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem;">
                        <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 0.5rem;">
                            <div style="font-weight: bold; color: #3b82f6;">{contributor['total_votes']:,}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Total Votes</div>
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 0.5rem;">
                            <div style="font-weight: bold; color: #10b981;">{contributor['goals_created']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Goals Created</div>
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 0.5rem;">
                            <div style="font-weight: bold; color: #f59e0b;">{contributor['goals_completed']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Goals Done</div>
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: #f3f4f6; border-radius: 0.5rem;">
                            <div style="font-weight: bold; color: #ef4444;">{contributor['streak_days']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Day Streak</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        components.html(contributor_detail_card_html, height=250)
        
        # Follow/Message buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button(f"👤 Follow", key=f"follow_{contributor['username']}_{time.time()}"):
                st.success(f"Now following {contributor['username']}!")
        
        with col2:
            if st.button(f"💬 Message", key=f"message_{contributor['username']}_{time.time()}"):
                st.info(f"Message feature coming soon!")

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

if __name__ == "__main__":
    # This allows the script to be run directly for testing
    leader_board_tab()
