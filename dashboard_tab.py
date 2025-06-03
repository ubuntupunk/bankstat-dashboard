import streamlit as st
import pandas as pd
from dashboard_viz import create_dashboard_metrics, create_expense_breakdown_chart, create_cash_flow_chart

def render_dashboard_tab(analyzer, processor, db_connection, start_date, end_date):
    st.header("📊 Financial Dashboard")
    
    # Data source selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📈 Key Metrics")
    with col2:
        # Check what data is available
        local_available = processor.get_statement_info() is not None
        db_available = False
        try:
            doc_count = db_connection.count_documents()
            db_available = doc_count > 0
        except:
            db_available = False
        
        data_source = st.selectbox(
            "Data Source:",
            ["Database Query", "Local File"] if db_available else (["Local File"] if local_available else ["No Data"]),
            help="Choose whether to query database by date range or use local file"
        )
    
    if data_source == "No Data":
        st.warning("⚠️ No data available. Please upload and process a bank statement first.")
        return
        
    # Load data based on source
    transactions_df = pd.DataFrame()
    data_info = {}
    
    if data_source == "Database Query":
        try:
            st.info(f"🔍 Querying database for transactions between {start_date} and {end_date}")
            with st.spinner("Loading data from database..."):
                # Query database for date range
                query = {
                    "$or": [
                        {
                            "period.start": {"$lte": end_date.strftime("%Y-%m-%d")},
                            "period.end": {"$gte": start_date.strftime("%Y-%m-%d")}
                        },
                        {
                            "period.start": {"$exists": False}  # Fallback for documents without period
                        }
                    ]
                }
                
                documents = db_connection.find_documents(query=query, sort_by=[("uploaded_at", -1)])
                st.write(f"📊 Found {len(documents)} relevant document(s) in database")
                
                if documents:
                    # Process all documents that match the date range
                    for doc in documents:
                        df = processor.extract_tables_to_dataframe(doc)
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
                            
                            # Ensure required columns exist
                            required_columns = ['date', 'description', 'debits', 'credits', 'balance']
                            for col in required_columns:
                                if col not in df.columns:
                                    df[col] = 'Unknown' if col == 'description' else 0.0
                            
                            # Filter by actual transaction dates
                            if 'date' in df.columns:
                                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                df = df[
                                    (df['date'] >= pd.to_datetime(start_date)) &
                                    (df['date'] <= pd.to_datetime(end_date))
                                ]
                            
                            if not df.empty:
                                transactions_df = pd.concat([transactions_df, df], ignore_index=True)
                
                    if not transactions_df.empty:
                        # Remove duplicates and sort
                        transactions_df = transactions_df.drop_duplicates().sort_values('date' if 'date' in transactions_df.columns else transactions_df.columns[0])
                        data_info = {
                            'source': 'Database',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date} to {end_date}",
                            'columns': transactions_df.columns.tolist()
                        }
                    else:
                        st.warning(f"No transactions found in database for date range {start_date} to {end_date}")
                else:
                    st.warning(f"No documents found in database covering the date range {start_date} to {end_date}")
                    
        except Exception as e:
            st.error(f"Error querying database: {str(e)}")
            st.info("Falling back to local file if available...")
            data_source = "Local File"
    
    if data_source == "Local File" or (data_source == "Database Query" and transactions_df.empty):
        try:
            with st.spinner("Loading data from local file..."):
                transactions_df = processor.load_latest_bank_statement()
                statement_info = processor.get_statement_info()
                
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
                    
                    # Ensure required columns exist
                    required_columns = ['date', 'description', 'debits', 'credits', 'balance']
                    for col in required_columns:
                        if col not in transactions_df.columns:
                            transactions_df[col] = 'Unknown' if col == 'description' else 0.0
                    
                    # Check if local file date range overlaps with selected range
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
                        'filename': statement_info['filename'],
                        'file_period': f"{period.get('start', 'Unknown')} to {period.get('end', 'Unknown')}",
                        'transactions_loaded': len(transactions_df),
                        'selected_range': f"{start_date} to {end_date}",
                        'columns': transactions_df.columns.tolist()
                    }
                
        except Exception as e:
            st.error(f"Error loading local file: {str(e)}")
    
    # Display data info
    if data_info:
        with st.expander("📋 Data Source Information", expanded=True):
            for key, value in data_info.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    # Create metrics and charts if we have data
    if not transactions_df.empty:
        create_dashboard_metrics(analyzer, start_date, end_date, transactions_df)

        # Charts section
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Expense Breakdown")
            try:
                summary_data = analyzer.get_transaction_summary(transactions_df)
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
            # Display top 20 transactions with available columns
            display_columns = ['date', 'description', 'debits', 'credits', 'balance']
            if 'category' in transactions_df.columns:
                display_columns.append('category')
            
            # Filter to only available columns
            display_columns = [col for col in display_columns if col in transactions_df.columns]
            if display_columns:
                display_df = transactions_df.head(20)[display_columns]
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("No valid columns available for transaction display")

            # Show uncategorized transactions
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
        st.info("No transaction data available for the selected criteria.")