import streamlit as st
import pandas as pd
import os
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart
from utils.utils import debug_write

def render_key_metrics_tab(analyzer, processor, db_connection, start_date, end_date):
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
        debug_write("Using dummy data for dashboard preview as no data source is available.")
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
                debug_write(f"Attempting to query database for transactions between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
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
                    debug_write(f"Found {len(documents)} document(s) in database matching query.")
                    
                    if documents:
                        for doc in documents:
                            debug_write(f"Processing MongoDB document: {doc.get('filename', 'N/A')}. Document keys: {list(doc.keys())}")
                            df = processor.process_latest_json(json_data=doc) # Pass the document data
                            debug_write(f"DataFrame from doc '{doc.get('filename', 'N/A')}' has {len(df)} rows before filtering.")

                            if not df.empty:
                                # Standardize column names (replicate _standardize_columns logic from ml_integration)
                                column_mapping = {
                                    'Date': 'date', 'Transaction Date': 'date', 'Trans Date': 'date',
                                    'Description': 'description', 'Details': 'description', 'Trans Details': 'description',
                                    'Narrative Description': 'description',
                                    'Debit': 'debits', 'Debits': 'debits', 'Debits (R)': 'debits', 'Fees (R) Debits (R)': 'debits',
                                    'Credit': 'credits', 'Credits': 'credits', 'Credits (R)': 'credits',
                                    'Balance': 'balance', 'Balance (R)': 'balance', 'Running Balance': 'balance', 'Saldo': 'balance',
                                    'Category': 'category', 'category': 'category' # Ensure category is mapped
                                }
                                df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
                                
                                required_columns = ['date', 'description', 'debits', 'credits', 'balance', 'category']
                                for col in required_columns:
                                    if col not in df.columns:
                                        df[col] = 'Unknown' if col in ['description', 'category'] else 0.0
                                
                                # Ensure 'date' column is datetime and drop NaT
                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                    df.dropna(subset=['date'], inplace=True)
                                    debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' date column min/max: {df['date'].min()} / {df['date'].max()}")
                                    debug_write(f"Filtering MongoDB doc '{doc.get('filename', 'N/A')}' for range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                                    df_filtered = df[
                                        (df['date'] >= pd.to_datetime(start_date)) &
                                        (df['date'] <= pd.to_datetime(end_date))
                                    ]
                                    debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' rows after date filter: {len(df_filtered)}")
                                else:
                                    df_filtered = df # No date column to filter, use as is
                                    debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' has no 'date' column. Using all {len(df_filtered)} rows.")

                                if not df_filtered.empty:
                                    transactions_df = pd.concat([transactions_df, df_filtered], ignore_index=True)
                                    debug_write(f"Added {len(df_filtered)} transactions from MongoDB doc to total. Current total: {len(transactions_df)}")
                                else:
                                    debug_write(f"No transactions from MongoDB doc '{doc.get('filename', 'N/A')}' after date filtering or date column issues.")
                            else:
                                debug_write(f"Processor returned empty DataFrame for MongoDB document '{doc.get('filename', 'N/A')}'.")
                    
                    # After processing all documents, apply the overall date range filter one last time
                    if not transactions_df.empty:
                        transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce') # Ensure date is datetime before final filter
                        transactions_df.dropna(subset=['date'], inplace=True) # Drop rows where date conversion failed
                        transactions_df = transactions_df[
                            (transactions_df['date'] >= pd.to_datetime(start_date)) &
                            (transactions_df['date'] <= pd.to_datetime(end_date))
                        ]
                        debug_write(f"Final filter applied to combined MongoDB transactions. Transactions after final filter: {len(transactions_df)}")

                    if not transactions_df.empty:
                        transactions_df = transactions_df.drop_duplicates().sort_values('date' if 'date' in transactions_df.columns else transactions_df.columns[0])
                        data_info = {
                            'source': 'Database',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    else:
                        st.warning(f"No transactions found in database for date range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                        st.info("Try uploading a bank statement in the 'Upload & Process' tab.")
            except Exception as e:
                st.error(f"Error querying database: {str(e)}")
                debug_write(f"Error querying database: {str(e)}")
                st.info("Falling back to local file if available...")
                data_source = "Local File"
        
        if data_source == "Local File" or (data_source == "Database Query" and transactions_df.empty):
            try:
                debug_write(f"Attempting to load data from local file for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                with st.spinner("Loading data from local file..."):
                    transactions_df = processor.load_latest_bank_statement()
                    statement_info = processor.get_statement_info()
                    debug_write(f"Statement info: {statement_info}")
                    
                    if not transactions_df.empty and statement_info:
                        # Standardize column names (replicate _standardize_columns logic from ml_integration)
                        column_mapping = {
                            'Date': 'date', 'Transaction Date': 'date', 'Trans Date': 'date',
                            'Description': 'description', 'Details': 'description', 'Trans Details': 'description',
                            'Narrative Description': 'description',
                            'Debit': 'debits', 'Debits': 'debits', 'Debits (R)': 'debits', 'Fees (R) Debits (R)': 'debits',
                            'Credit': 'credits', 'Credits': 'credits', 'Credits (R)': 'credits',
                            'Balance': 'balance', 'Balance (R)': 'balance', 'Running Balance': 'balance', 'Saldo': 'balance',
                            'Category': 'category', 'category': 'category' # Ensure category is mapped
                        }
                        transactions_df = transactions_df.rename(columns={k: v for k, v in column_mapping.items() if k in transactions_df.columns})
                        
                        required_columns = ['date', 'description', 'debits', 'credits', 'balance', 'category']
                        for col in required_columns:
                            if col not in transactions_df.columns:
                                transactions_df[col] = 'Unknown' if col in ['description', 'category'] else 0.0
                        
                        # Ensure 'date' column is datetime and drop NaT
                        if 'date' in transactions_df.columns:
                            transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce')
                            transactions_df.dropna(subset=['date'], inplace=True)
                            debug_write(f"Local file date column min/max: {transactions_df['date'].min()} / {transactions_df['date'].max()}")
                            debug_write(f"Filtering local file for range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                            
                            original_count = len(transactions_df)
                            transactions_df = transactions_df[
                                (transactions_df['date'] >= pd.to_datetime(start_date)) &
                                (transactions_df['date'] <= pd.to_datetime(end_date))
                            ]
                            filtered_count = len(transactions_df)
                            debug_write(f"Local file data has {filtered_count} rows after date filtering (from {original_count} total).")
                            
                            if filtered_count == 0:
                                st.warning(f"No transactions found in local file for your selected date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
                            elif filtered_count < original_count:
                                st.info(f"Filtered to {filtered_count} transactions (from {original_count} total) matching your date range")
                        else:
                            debug_write("Local file data has no 'date' column. Using all rows.")
                            st.warning("Local file data has no 'date' column. Cannot filter by date range.")
                        
                        data_info = {
                            'source': 'Local File',
                            'filename': statement_info.get('filename', 'Unknown'),
                            'file_period': f"{statement_info.get('period', {}).get('start', 'Unknown')} to {statement_info.get('period', {}).get('end', 'Unknown')}",
                            'transactions_loaded': len(transactions_df),
                            'selected_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"transactions_df shape: {transactions_df.shape}")
                    else:
                        debug_write("Local file is empty or statement info is missing.")
                        st.warning("No local file transactions found or statement info is missing.")
            except Exception as e:
                st.error(f"Error loading local file: {str(e)}")
                debug_write(f"Error loading local file: {str(e)}")
    
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
