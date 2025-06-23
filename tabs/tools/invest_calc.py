import streamlit as st

def render_investment_calculator():
    """Placeholder for Investment Calculator."""
    st.write("Investment Calculator content will go here.")
import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

def render_investment_calculator():
    """Renders the Investment Calculator section."""
    with st.container():
        st.markdown('<div class="calculator-container">', unsafe_allow_html=True)
        st.markdown("""
        <div class="header">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-up"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
            <h1>Investment Calculator</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Input and Results sections
        col1, col2 = st.columns([1, 1])

        # Input Section
        with col1:
            st.markdown('<div class="input-section"><h2>Input Parameters</h2></div>', unsafe_allow_html=True)
            current_age = st.number_input(
                "Current Age",
                min_value=18,
                max_value=100,
                value=30,
                step=1,
                key="current_age",
                help="Enter your current age."
            )
            retirement_age = st.number_input(
                "Retirement Age",
                min_value=18,
                max_value=100,
                value=65,
                step=1,
                key="retirement_age",
                help="Enter the age at which you plan to retire."
            )
            life_expectancy = st.number_input(
                "Life Expectancy",
                min_value=18,
                max_value=120,
                value=85,
                step=1,
                key="life_expectancy",
                help="Enter your expected life expectancy."
            )
            current_savings = st.number_input(
                "Current Savings (R)",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
                format="%.2f",
                key="current_savings",
                help="Enter your current savings amount in Rand."
            )
            annual_contribution = st.number_input(
                "Annual Contribution (R)",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
                format="%.2f",
                key="annual_contribution",
                help="Enter the amount you plan to contribute annually until retirement."
            )
            expected_return = st.number_input(
                "Expected Annual Return (%)",
                min_value=0.0,
                max_value=100.0,
                value=7.0,
                step=0.1,
                format="%.1f",
                key="expected_return",
                help="Enter the expected annual return on investments as a percentage."
            )
            withdrawal_rate = st.number_input(
                "Annual Withdrawal Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=4.0,
                step=0.1,
                format="%.1f",
                key="withdrawal_rate",
                help="Enter the annual withdrawal rate during retirement as a percentage."
            )

        # Calculations
        years_to_retirement = retirement_age - current_age
        years_in_retirement = life_expectancy - retirement_age

        if years_to_retirement <= 0 or years_in_retirement <= 0:
            st.error("Please ensure that retirement age is greater than current age and life expectancy is greater than retirement age.")
            return

        # Calculate future value at retirement
        future_value = current_savings * (1 + expected_return / 100) ** years_to_retirement
        for year in range(1, years_to_retirement + 1):
            future_value += annual_contribution * (1 + expected_return / 100) ** (years_to_retirement - year)

        # Calculate annual withdrawal amount
        annual_withdrawal = future_value * (withdrawal_rate / 100)

        # Simulate retirement years
        retirement_balance = future_value
        retirement_data = []
        for year in range(1, years_in_retirement + 1):
            retirement_balance *= (1 + expected_return / 100)
            retirement_balance -= annual_withdrawal
            if retirement_balance < 0:
                retirement_balance = 0
            retirement_data.append(retirement_balance)

        # Results Section
        with col2:
            st.markdown('<div class="results-section"><h2>Calculated Results</h2></div>', unsafe_allow_html=True)
            
            # Retirement Savings Projection
            st.markdown('<div class="result-card investment-card">', unsafe_allow_html=True)
            st.markdown("""
                <div class="title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-up"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
                    <span>Retirement Savings Projection</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="color: #15803d; font-size: 0.875rem;">
                    <div>Years to Retirement: {years_to_retirement}</div>
                    <div>Projected Savings at Retirement: R{future_value:.2f}</div>
                    <div>Annual Withdrawal: R{annual_withdrawal:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Living Annuity Projection
            st.markdown('<div class="result-card consumption-card">', unsafe_allow_html=True)
            st.markdown("""
                <div class="title">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-down"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>
                    <span>Living Annuity Projection</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style="color: #b91c1c; font-size: 0.875rem;">
                    <div>Years in Retirement: {years_in_retirement}</div>
                    <div>Final Balance: R{retirement_data[-1]:.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Chart
        df = pd.DataFrame({
            'Year': list(range(1, years_in_retirement + 1)),
            'Balance': retirement_data
        })
        fig = px.line(df, x='Year', y='Balance', title='Retirement Balance Over Time')
        st.plotly_chart(fig)

    st.markdown('</div>', unsafe_allow_html=True)

# # Example usage in a Streamlit app
# if __name__ == "__main__":
#     st.set_page_config(page_title="Financial Calculators", layout="wide")
#     st.title("Financial Calculators")
#     tab1, tab2 = st.tabs(["Financial Flow Calculator", "Investment Calculator"])
#     with tab1:
#         from financial_calc import render_financial_flow_calculator
#         render_financial_flow_calculator()
#     with tab2:
#         render_investment_calculator()