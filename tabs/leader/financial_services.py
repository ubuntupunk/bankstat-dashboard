import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time

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
