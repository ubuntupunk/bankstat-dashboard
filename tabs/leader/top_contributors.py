import streamlit as st
import streamlit.components.v1 as components
import time

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
