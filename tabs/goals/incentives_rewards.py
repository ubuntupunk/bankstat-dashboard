import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

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
