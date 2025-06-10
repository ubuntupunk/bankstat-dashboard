import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import debug_write

def create_dashboard_metrics(analyzer, start_date, end_date, transactions_df=None):
    """Create key financial metrics display"""
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Use provided transactions_df or load from processor
        if transactions_df is None or transactions_df.empty:
            transactions_df = analyzer.process_latest_json()
        
        if transactions_df is not None and not transactions_df.empty:
            # Filter by date range if not already filtered
            if 'date' in transactions_df.columns:
                transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')
                if len(transactions_df) > 0:
                    date_range_filtered = transactions_df[
                        (transactions_df['date'] >= pd.to_datetime(start_date)) &
                        (transactions_df['date'] <= pd.to_datetime(end_date))
                    ]
                    if len(date_range_filtered) > 0:
                        transactions_df = date_range_filtered
            
            # Debug: Show data summary
            debug_write("**Debug: Transaction Data Summary**")
            st.write(transactions_df[['debits', 'credits', 'balance']].describe())
            debug_write("**Debug: Sample Transactions**")
            st.write(transactions_df[['date', 'description', 'debits', 'credits', 'balance']].head())
            
            # Get transaction summary with the filtered data
            summary = analyzer.get_transaction_summary(transactions_df)
            
            # Calculate metrics from the data we have
            total_income = transactions_df['credits'].sum() if 'credits' in transactions_df.columns else 0
            total_expenses = transactions_df['debits'].sum() if 'debits' in transactions_df.columns else 0
            
            # Try to get balance data from analyzer, fallback to simple calculation
            try:
                balance_data = analyzer.calculate_monthly_average_balance(
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                avg_balance = balance_data.get('average_balance', 0)
            except:
                avg_balance = transactions_df['balance'].mean() if 'balance' in transactions_df.columns else 0

            with col1:
                # Total Income (no delta)
                st.write(f"""
                <div class="custom-metric-container">
                    <div class="custom-metric-label">💰 Total Income</div>
                    <div class="custom-metric-value">R {total_income:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                # Total Expenses (no delta)
                st.write(f"""
                <div class="custom-metric-container">
                    <div class="custom-metric-label">💸 Total Expenses</div>
                    <div class="custom-metric-value">R {total_expenses:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                # Net Flow (with delta)
                net_flow = total_income - total_expenses
                if net_flow < 0:
                    st.write(f"""
                    <div class="custom-metric-container">
                        <div class="custom-metric-label">📊 Net Flow</div>
                        <div class="custom-metric-value">R {net_flow:,.2f}</div>
                        <div class="custom-metric-delta negative">
                            <span class="arrow">↓</span> Negative (R {abs(net_flow):,.2f})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.write(f"""
                    <div class="custom-metric-container">
                        <div class="custom-metric-label">📊 Net Flow</div>
                        <div class="custom-metric-value">R {net_flow:,.2f}</div>
                        <div class="custom-metric-delta positive">
                            <span class="arrow">↑</span> Positive (R {net_flow:,.2f})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with col4:
                # Avg Balance (no delta)
                st.write(f"""
                <div class="custom-metric-container">
                    <div class="custom-metric-label">🏦 Avg Balance</div>
                    <div class="custom-metric-value">R {avg_balance:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with col1:
                st.metric("💰 Total Income", "R 0.00")
            with col2:
                st.metric("💸 Total Expenses", "R 0.00")
            with col3:
                st.metric("📊 Net Flow", "R 0.00")
            with col4:
                st.metric("🏦 Avg Balance", "R 0.00")
            
            st.warning("No transactions available to analyze")
        
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")

def create_expense_breakdown_chart(summary_data):
    """Create expense breakdown visualization"""
    try:
        expense_types = summary_data.get('expense_types', {})
        if not expense_types:
            st.warning("No expense data available")
            return

        categories = []
        amounts = []

        for category, data in expense_types.items():
            if isinstance(data, dict) and 'debits' in data:
                debits = data['debits']
                if debits > 0:
                    categories.append(category)
                    amounts.append(debits)

        if categories and amounts:
            df_expenses = pd.DataFrame({
                'Category': categories,
                'Amount': amounts
            })

            fig = px.pie(df_expenses, values='Amount', names='Category',
                        title="Expense Breakdown by Category",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data to display")

    except Exception as e:
        st.error(f"Error creating expense chart: {str(e)}")

def create_cash_flow_chart(summary_data):
    """Create cash flow over time visualization"""
    try:
        daily_flow = summary_data.get('daily_flow', {})
        if not daily_flow:
            st.warning("No daily flow data available")
            return

        dates = []
        debits = []
        credits = []

        for date_str, data in daily_flow.items():
            if isinstance(data, dict):
                dates.append(pd.to_datetime(date_str))
                debits.append(data.get('debits', 0))
                credits.append(data.get('credits', 0))

        if dates:
            df_flow = pd.DataFrame({
                'Date': dates,
                'Expenses': debits,
                'Income': credits
            })
            df_flow = df_flow.sort_values('Date')

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_flow['Date'], y=df_flow['Income'],
                                   mode='lines+markers', name='Income',
                                   line=dict(color='green')))
            fig.add_trace(go.Scatter(x=df_flow['Date'], y=df_flow['Expenses'],
                                   mode='lines+markers', name='Expenses',
                                   line=dict(color='red')))

            fig.update_layout(title="Daily Cash Flow",
                              xaxis_title="Date",
                              yaxis_title="Amount (R)",
                              hovermode='x unified')

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cash flow data to display")

    except Exception as e:
        st.error(f"Error creating cash flow chart: {str(e)}")
