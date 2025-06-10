import streamlit as st
import pandas as pd

def calculate_monthly_payment(P, r_annual, t):
    """Calculate the monthly payment for a bond."""
    r = r_annual / 12 / 100  # Monthly interest rate
    n = t * 12  # Number of monthly payments
    if r == 0:
        M = P / n
    else:
        M = P * (r * (1 + r)**n) / ((1 + r)**n - 1)
    return M

def calculate_total_interest(M, n, P):
    """Calculate the total interest paid over the term of the bond."""
    return M * n - P

def generate_amortization_schedule(P, r_annual, t):
    """Generate the amortization schedule for the bond."""
    r = r_annual / 12 / 100  # Monthly interest rate
    n = t * 12  # Number of monthly payments
    M = calculate_monthly_payment(P, r_annual, t)
    balance = P
    schedule = []
    for i in range(1, n + 1):
        interest = round(balance * r, 2)
        principal = round(M - interest, 2)
        balance = round(balance - principal, 2)
        schedule.append({
            'Payment': i,
            'Principal': principal,
            'Interest': interest,
            'Balance': balance
        })
    return schedule

def render_bond_calculator():
    """Renders the Bond Calculator section."""
    st.title("Bond Calculator")
    st.markdown("Calculate your bond repayments by entering the bond amount, annual interest rate, and term.")

    # Inputs
    st.markdown("### Bond Parameters")
    P = st.number_input(
        "Bond Amount (R)", 
        min_value=0.0, 
        value=100000.0, 
        step=1000.0, 
        help="The total amount of the bond."
    )
    r_annual = st.number_input(
        "Annual Interest Rate (%)", 
        min_value=0.0, 
        value=5.0, 
        step=0.1, 
        help="The annual interest rate for the bond."
    )
    t = st.number_input(
        "Term (years)", 
        min_value=1, 
        value=20, 
        step=1, 
        help="The term of the bond in years."
    )
    calculate = st.button("Calculate")

    # Display results when calculate button is clicked
    if calculate:
        M = calculate_monthly_payment(P, r_annual, t)
        n = t * 12
        total_interest = calculate_total_interest(M, n, P)
        
        st.markdown("### Results")
        st.write(f"**Monthly Payment:** R {M:.2f}")
        st.write("The amount you need to pay each month to repay the bond over the term.")
        st.write(f"**Total Interest Paid:** R {total_interest:.2f}")
        st.write("The total amount of interest you will pay over the term of the bond.")
    else:
        st.write("Enter values and click 'Calculate' to see your bond repayment details.")

    # Option to view amortization schedule
    if st.checkbox("View Amortization Schedule"):
        # Ensure calculations are performed if checkbox is ticked without recalculating main results
        if 'M' not in locals(): # Check if M is defined from a previous 'calculate' click
            M = calculate_monthly_payment(P, r_annual, t)
            n = t * 12
        
        st.markdown("### Amortization Schedule")
        st.markdown("This table shows the breakdown of each payment into principal and interest, and the remaining balance after each payment.")
        schedule = generate_amortization_schedule(P, r_annual, t)
        df = pd.DataFrame(schedule)
        st.dataframe(df)
