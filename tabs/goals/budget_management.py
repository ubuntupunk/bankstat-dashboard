import streamlit as st
import plotly.graph_objects as go


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
