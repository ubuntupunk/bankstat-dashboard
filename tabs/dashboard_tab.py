import streamlit as st
import pandas as pd
import os
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from utils import debug_write


def render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date):
    # Load CSS from dashboard.css
    css_path = os.path.join(os.path.dirname(__file__), "dashboard.css")
    try:
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("ai_expert.css file not found. Please ensure it exists in the same directory as tools_tab.py.")
        return
    
    st.markdown("""
    <div class="dashboard-container">
        <h1 style="margin: 0; font-size: 2rem; font-weight: bold;">📊 Financial Dashboard</h1>
        </div>
     """, unsafe_allow_html=True)

    debug_write("Entered render_dashboard_tab")
     
    # Check data availability
    local_available = processor.get_statement_info() is not None
    debug_write(f"Local data available: {local_available}")
    db_available = False
    try:
        doc_count = db_connection.count_documents()
        db_available = doc_count > 0
        debug_write(f"Database documents count: {doc_count}")
    except Exception as e:
        debug_write(f"ERROR: Database check failed: {str(e)}") # Changed from st.error for debug purposes
    
    # Data source selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📈 Key Metrics")
    with col2:
        data_source_options = ["Database Query"] if db_available else []
        if local_available:
            data_source_options.append("Local File")
        if not data_source_options:
            data_source_options = ["No Data"]
        
        data_source = st.selectbox(
            "Data Source:",
            data_source_options,
            help="Choose whether to query database by date range or use local file",
            key="data_source_select"
        )
    
    # Handle no data case
    if data_source == "No Data":
        st.warning("⚠️ No data available. Please upload a bank statement in the 'Upload & Process' tab.")
        # Fallback to dummy data for testing
        st.info("Using dummy data for dashboard preview")
        transactions_df = pd.DataFrame({
            'date': [pd.to_datetime('2025-06-01'), pd.to_datetime('2025-06-02')],
            'description': ['Test Income', 'Test Expense'],
            'debits': [0.0, 100.0],
            'credits': [500.0, 0.0],
            'balance': [500.0, 400.0],
            'category': ['Income', 'Expense']
        })
        data_info = {
            'source': 'Dummy Data',
            'transactions_loaded': len(transactions_df),
            'selected_range': f"{start_date} to {end_date}",
            'columns': transactions_df.columns.tolist()
        }
    else:
        transactions_df = pd.DataFrame()
        data_info = {}
        
        if data_source == "Database Query":
            try:
                st.info(f"🔍 Querying database for transactions between {start_date} and {end_date}")
                with st.spinner("Loading data from database..."):
                    query = {
                        "$or": [
                            {
                                "period.start": {"$lte": end_date.strftime("%Y-%m-%d")},
                                "period.end": {"$gte": start_date.strftime("%Y-%m-%d")}
                            },
                            {
                                "period.start": {"$exists": False}
                            }
                        ]
                    }
                    documents = db_connection.find_documents(query=query, sort_by=[("uploaded_at", -1)])
                    debug_write(f"Found {len(documents)} document(s) in database")
                    
                    if documents:
                        for doc in documents:
                            debug_write(f"Processing document with keys: {list(doc.keys())}")
                            df = processor.process_latest_json()
                            if not df.empty:
                                # Standardize column names
                                column_mapping = {
                                    'Date': 'date',
                                    'Transaction Date': 'date',
                                    'Trans Date': 'date',
                                    'Description': 'description',
                                    'Details': 'description',
                                    'Trans Details': 'description',
                                    'Debit': 'debits',
                                    'Debits': 'debits',
                                    'Credit': 'credits',
                                    'Credits': 'credits',
                                    'Balance': 'balance',
                                    'Running Balance': 'balance',
                                    'Saldo': 'balance'
                                }
                                df = df.rename(columns=column_mapping)
                                
                                # Ensure required columns
                                required_columns = ['date', 'description', 'debits', 'credits', 'balance']
                                for col in required_columns:
                                    if col not in df.columns:
                                        df[col] = 'Unknown' if col == 'description' else 0.0
                                
                                # Filter by date
                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                    df = df[
                                        (df['date'] >= pd.to_datetime(start_date)) &
                                        (df['date'] <= pd.to_datetime(end_date))
                                    ]
                                
                                if not df.empty:
                                    transactions_df = pd.concat([transactions_df, df], ignore_index=True)
                    
                    if not transactions_df.empty:
                        transactions_df = transactions_df.drop_duplicates().sort_values('date' if 'date' in transactions_df.columns else transactions_df.columns[0])
                        data_info = {
                            'source': 'Database',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date} to {end_date}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    else:
                        st.warning(f"No transactions found in database for date range {start_date} to {end_date}")
                        st.info("Try uploading a bank statement in the 'Upload & Process' tab.")
            except Exception as e:
                st.error(f"Error querying database: {str(e)}")
                st.info("Falling back to local file if available...")
                data_source = "Local File"
        
        if data_source == "Local File" or (data_source == "Database Query" and transactions_df.empty):
            try:
                with st.spinner("Loading data from local file..."):
                    transactions_df = processor.load_latest_bank_statement()
                    statement_info = processor.get_statement_info()
                    debug_write(f"Statement info: {statement_info}")
                    
                    if not transactions_df.empty and statement_info:
                        # Standardize column names
                        column_mapping = {
                            'Date': 'date',
                            'Transaction Date': 'date',
                            'Trans Date': 'date',
                            'Description': 'description',
                            'Details': 'description',
                            'Trans Details': 'description',
                            'Debit': 'debits',
                            'Debits': 'debits',
                            'Credit': 'credits',
                            'Credits': 'credits',
                            'Balance': 'balance',
                            'Running Balance': 'balance',
                            'Saldo': 'balance'
                        }
                        transactions_df = transactions_df.rename(columns=column_mapping)
                        
                        # Ensure required columns
                        required_columns = ['date', 'description', 'debits', 'credits', 'balance']
                        for col in required_columns:
                            if col not in transactions_df.columns:
                                transactions_df[col] = 'Unknown' if col == 'description' else 0.0
                        
                        # Check date range overlap
                        period = statement_info.get('period', {})
                        if period.get('start') and period.get('end'):
                            file_start = pd.to_datetime(period['start'])
                            file_end = pd.to_datetime(period['end'])
                            selected_start = pd.to_datetime(start_date)
                            selected_end = pd.to_datetime(end_date)
                            
                            if file_end < selected_start or file_start > selected_end:
                                st.warning(f"⚠️ Local file covers {period['start']} to {period['end']}, but you selected {start_date} to {end_date}. There may be no overlapping data.")
                            
                            # Filter to selected date range
                            if 'date' in transactions_df.columns:
                                transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')
                                original_count = len(transactions_df)
                                transactions_df = transactions_df[
                                    (transactions_df['date'] >= selected_start) &
                                    (transactions_df['date'] <= selected_end)
                                ]
                                filtered_count = len(transactions_df)
                                
                                if filtered_count == 0:
                                    st.warning(f"No transactions found in local file for your selected date range ({start_date} to {end_date})")
                                elif filtered_count < original_count:
                                    st.info(f"Filtered to {filtered_count} transactions (from {original_count} total) matching your date range")
                        
                        data_info = {
                            'source': 'Local File',
                            'filename': statement_info.get('filename', 'Unknown'),
                            'file_period': f"{period.get('start', 'Unknown')} to {period.get('end', 'Unknown')}",
                            'transactions_loaded': len(transactions_df),
                            'selected_range': f"{start_date} to {end_date}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    
            except Exception as e:
                st.error(f"Error loading local file: {str(e)}")
    
    # Display data info
    if data_info:
        with st.expander("📋 Data Source Information", expanded=True):
            for key, value in data_info.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    # Create metrics and charts
    if not transactions_df.empty:
        debug_write("Rendering metrics and charts")
        create_dashboard_metrics(analyzer, start_date, end_date, transactions_df)

        # Charts section
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💰 Expense Breakdown")
            try:
                summary_data = analyzer.get_transaction_summary(transactions_df)
                debug_write(f"Summary data: {summary_data}")
                create_expense_breakdown_chart(summary_data)
            except Exception as e:
                st.error(f"Error loading expense data: {str(e)}")

        with col2:
            st.subheader("📊 Cash Flow Trend")
            try:
                summary_data = analyzer.get_transaction_summary(transactions_df)
                create_cash_flow_chart(summary_data)
            except Exception as e:
                st.error(f"Error loading cash flow data: {str(e)}")

        # Transaction details
        st.subheader("💳 Recent Transactions")
        try:
            display_columns = ['date', 'description', 'debits', 'credits', 'balance']
            if 'category' in transactions_df.columns:
                display_columns.append('category')
            
            display_columns = [col for col in display_columns if col in transactions_df.columns]
            if display_columns:
                display_df = transactions_df.head(20)[display_columns]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No valid columns available for transaction display")

            if 'category' in transactions_df.columns:
                uncategorized = transactions_df[transactions_df['category'] == 'Uncategorized']
                if not uncategorized.empty:
                    st.warning(f"⚠️ {len(uncategorized)} uncategorized transactions found")
                    with st.expander("View Uncategorized Transactions"):
                        uncategorized_columns = [col for col in display_columns if col != 'category']
                        st.dataframe(uncategorized[uncategorized_columns])
        except Exception as e:
            st.error(f"Error displaying transactions: {str(e)}")
    else:
        st.info("No transaction data available for the selected criteria. Please upload a bank statement.")
