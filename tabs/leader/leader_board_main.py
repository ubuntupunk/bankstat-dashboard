import streamlit as st
import os
from tabs.leader.data_initializer import initialize_leaderboard_data
from tabs.leader.financial_services import render_financial_services_voting
from tabs.leader.community_goals import render_community_goals
from tabs.leader.top_contributors import render_top_contributors
from tabs.leader.voting_analytics import render_voting_analytics

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
