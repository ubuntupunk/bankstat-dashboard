import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import os
import re
import json
from datetime import datetime, timedelta
from io import StringIO
import tempfile
from financial_analyzer import FinancialAnalyzer
import logging

# Configure page
st.set_page_config(
    page_title="Bankstat Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import CSS from external file
with open("styles.css") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

class StreamlitBankProcessor:
    def __init__(self):
        st.write("Secrets keys:", list(st.secrets.keys()))
        self.api_key = st.secrets["upstage"]["api_key"]
        if not self.api_key:
            st.error("⚠️ UPSTAGE_API_KEY not found in environment variables")
        
        # Define the path for the latest bank statement JSON file
        self.json_file_path = os.path.join(os.path.dirname(__file__), "latest_bank_statement.json")

    def process_latest_json(self):
        """Load the latest processed bank statement JSON from storage and convert to DataFrame."""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r") as f:
                    json_data = json.load(f)

                df = self.extract_tables_to_dataframe(json_data)
                if not df.empty:
                    # Ensure 'date' column is datetime and handle missing 'debits'/'credits'
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')

                    # Fill NaN in 'debits' and 'credits' with 0
                    if 'debits' not in df.columns:
                        df['debits'] = 0.0
                    else:
                        df['debits'] = pd.to_numeric(df['debits'], errors='coerce').fillna(0.0)

                    if 'credits' not in df.columns:
                        df['credits'] = 0.0
                    else:
                        df['credits'] = pd.to_numeric(df['credits'], errors='coerce').fillna(0.0)

                    # Add 'category' column if not exists
                    if 'category' not in df.columns:
                        df['category'] = 'Uncategorized'

                    return df
                else:
                    st.info("No tables found in the latest JSON data.")
                    return pd.DataFrame()
            else:
                st.info(f"No bank statement JSON found at {self.json_file_path}. Please upload and process a bank statement first.")
                return pd.DataFrame()
        except json.JSONDecodeError:
            st.error(f"Error decoding {self.json_file_path}. File might be corrupted.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading latest JSON data from {self.json_file_path}: {str(e)}")
            return pd.DataFrame()

    def process_pdf(self, uploaded_file):
        """Process uploaded PDF file using Upstage API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Call Upstage API
            st.write("📄 Starting PDF processing...")
            st.write(f"📂 Temporary file created at: {tmp_file_path}")
            url = 'https://api.upstage.ai/v1/document-ai/document-parse'
            headers = {"Authorization": f"Bearer {self.api_key}"}
            st.write("🔗 API endpoint:", url)
            st.write("🔑 Using API key (truncated):", self.api_key[:4] + "..." + self.api_key[-4:])

            with open(tmp_file_path, "rb") as file:
                files = {"document": file}
                response = requests.post(url, headers=headers, files=files)

            # Clean up temp file
            os.unlink(tmp_file_path)

            if response.status_code == 200:
                st.write("✅ API request successful")
                st.write(f"⏱️ Response time: {response.elapsed.total_seconds():.2f}s")
                data = response.json()
                st.write("📊 Extracted data keys:", list(data.keys()))

                # Parse filename for date range
                filename = uploaded_file.name
                start_date, end_date = self.parse_pdf_name(filename)

                data["filename"] = filename
                data["period"] = {
                    "start": start_date.strftime('%Y-%m-%d') if start_date else None,
                    "end": end_date.strftime('%Y-%m-%d') if end_date else None
                }

                return data
            else:
                st.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return None

    def parse_pdf_name(self, pdf_name):
        """Parse date range from PDF filename"""
        pattern = r'(\d{2}\s\w{3}\s\d{4})\s-\s(\d{2}\s\w{3}\s\d{4})\.pdf'
        match = re.match(pattern, pdf_name)
        if match:
            start_date = datetime.strptime(match.group(1), '%d %b %Y')
            end_date = datetime.strptime(match.group(2), '%d %b %Y')
            return start_date, end_date
        return None, None

    def extract_tables_to_dataframe(self, json_data):
        """Extract tables from JSON data and convert to DataFrame"""
        try:
            all_tables = []
            for page in json_data.get('elements', []):
                if page.get('category') == 'table':
                    html_table = page.get('content', {}).get('html', "")
                    if html_table:
                        df = pd.read_html(StringIO(html_table))[0]
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.map('_'.join)
                        all_tables.append(df)

            if all_tables:
                combined_df = pd.concat(all_tables, ignore_index=True)
                combined_df.columns = combined_df.columns.astype(str) # Ensure all column names are strings
                
                # --- Start: Logic to find and process Balance/Running Total ---
                # Find the balance column (case-insensitive, flexible matching)
                balance_col = None
                for col in combined_df.columns:
                    if isinstance(col, str) and ('balance' in col.lower() or 'saldo' in col.lower()):
                        balance_col = col
                        break

                if balance_col:
                    # Clean and convert balance column to numeric
                    try:
                        combined_df['balance'] = combined_df[balance_col].astype(str).str.replace(r'[^\d.,-]', '', regex=True).str.replace(',', '', regex=True)
                        # Handle potential multiple decimal points if comma was used as decimal separator
                        if combined_df['balance'].str.count(r'\.').max() > 1:
                             combined_df['balance'] = combined_df['balance'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False) # Assuming comma was decimal
                        combined_df['balance'] = pd.to_numeric(combined_df['balance'], errors='coerce').fillna(0.0)
                        
                        # Ensure date column is datetime and sort for running total
                        if 'date' in combined_df.columns:
                             combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
                             combined_df = combined_df.sort_values('date')
                             
                             # Calculate running total if needed (optional, based on typical bank statements)
                             # This assumes the first balance is the starting point.
                             # If the balance column is already a running balance, this might be redundant.
                             # Keeping it simple for now by just ensuring the 'balance' column is present and numeric.
                             # If a separate 'running_total' is required, more complex logic is needed.
                             
                    except Exception as e:
                        st.warning(f"Could not process balance column '{balance_col}': {str(e)}")
                        combined_df['balance'] = 0.0 # Add a default balance column

                else:
                    st.warning("Balance column not found in extracted tables.")
                    combined_df['balance'] = 0.0 # Add a default balance column if not found
                # --- End: Logic to find and process Balance/Running Total ---

                # Ensure debits and credits are numeric after potential concatenation issues
                if 'debits' in combined_df.columns:
                    combined_df['debits'] = pd.to_numeric(combined_df['debits'], errors='coerce').fillna(0.0)
                else:
                    combined_df['debits'] = 0.0

                if 'credits' in combined_df.columns:
                    combined_df['credits'] = pd.to_numeric(combined_df['credits'], errors='coerce').fillna(0.0)
                else:
                    combined_df['credits'] = 0.0

                # Add 'category' column if not exists (already present, but good to ensure)
                if 'category' not in combined_df.columns:
                    combined_df['category'] = 'Uncategorized'

                return combined_df
            return pd.DataFrame()
            
        except Exception as e:
            st.error(f"Error extracting tables: {str(e)}")
            return pd.DataFrame()

def create_dashboard_metrics(analyzer, start_date, end_date):
    """Create key financial metrics display"""
    col1, col2, col3, col4 = st.columns(4)

    try:
        # Get transaction summary
        summary = analyzer.get_transaction_summary()
        balance_data = analyzer.calculate_monthly_average_balance(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        fees_data = analyzer.analyze_bank_fees(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        with col1:
            total_income = summary.get('total_credits', 0)
            st.metric("💰 Total Income", f"R {total_income:,.2f}")

        with col2:
            total_expenses = summary.get('total_debits', 0)
            st.metric("💸 Total Expenses", f"R {total_expenses:,.2f}")

        with col3:
            net_flow = total_income - total_expenses
            st.metric("📊 Net Flow", f"R {net_flow:,.2f}",
                     delta=f"{'Positive' if net_flow > 0 else 'Negative'}")

        with col4:
            avg_balance = balance_data.get('average_balance', 0)
            st.metric("🏦 Avg Balance", f"R {avg_balance:,.2f}")

    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")

def create_expense_breakdown_chart(summary_data):
    """Create expense breakdown visualization"""
    try:
        expense_types = summary_data.get('expense_types', {})
        if not expense_types:
            st.warning("No expense data available")
            return

        # Convert to DataFrame for plotting
        categories = []
        amounts = []

        for category, data in expense_types.items():
            if isinstance(data, dict) and 'debits' in data:
                debits = data['debits']
                if debits > 0:  # Only show expenses (debits)
                    categories.append(category)
                    amounts.append(debits)

        if categories and amounts:
            df_expenses = pd.DataFrame({
                'Category': categories,
                'Amount': amounts
            })

            # Create pie chart
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

        # Convert to DataFrame
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

            # Create line chart
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

def main():
    # Header
    st.markdown('<h1 class="main-header">🏦 Bankstat Dashboard</h1>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("bankstatgreen.png", use_container_width=True)
        st.header("Navigation")

        # Tab selection
        tab_selection = st.radio(
            "Choose Action:",
            ["📊 View Dashboard", "📁 Upload & Process", "⚙️ Settings"]
        )

        # Date range selection
        st.header("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("To", datetime.now())

    # Initialize components
    processor = StreamlitBankProcessor()
    analyzer = FinancialAnalyzer(base_analyzer=processor) # Initialize with base_analyzer

    if tab_selection == "📁 Upload & Process":
        st.header("📁 Upload Bank Statement")

        # File upload section
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drop your PDF bank statement here",
            type=['pdf'],
            help="Upload a PDF bank statement to process and analyze"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is not None:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.info(f"📄 File: {uploaded_file.name}")
                st.info(f"📏 Size: {uploaded_file.size:,} bytes")

            with col2:
                if st.button("🚀 Process PDF", type="primary"):
                    with st.spinner("Processing PDF... This may take a moment..."):
                        # Process the PDF
                        json_data = processor.process_pdf(uploaded_file)

                        if json_data:
                            st.success("✅ PDF processed successfully!")

                            # Display extracted data
                            st.subheader("📊 Extracted Data Preview")

                            # Extract tables
                            df = processor.extract_tables_to_dataframe(json_data)
                            if not df.empty:
                                st.dataframe(df.head(10), use_container_width=True)

                                # Download options
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    csv_data = df.to_csv(index=False)
                                    st.download_button(
                                        "📥 Download CSV",
                                        csv_data,
                                        f"{uploaded_file.name.replace('.pdf', '.csv')}",
                                        "text/csv"
                                    )

                                with col2:
                                    json_str = json.dumps(json_data, indent=2)
                                    st.download_button(
                                        "📥 Download JSON",
                                        json_str,
                                        f"{uploaded_file.name.replace('.pdf', '.json')}",
                                        "application/json"
                                    )

                                with col3:
                                    if st.button("💾 Save to Database"):
                                        # Upload to MongoDB with detailed debug output
                                        debug_container = st.container()
                                        debug_container.subheader("MongoDB Upload Debug")
                                        
                                        with st.spinner("Saving data..."):
                                            # Clear previous debug messages
                                            debug_container.empty()

                                            # Save to a local JSON file for demonstration
                                            with open(self.json_file_path, "w") as f:
                                                json.dump(json_data, f, indent=2)
                                            st.success(f"✅ Saved to local file: {self.json_file_path}!")

                                            debug_container.write("🛢️ Starting MongoDB upload process...")
                                            debug_container.write(f"JSON data valid: {json.dumps(json_data, indent=2)[:1000]}...")
                                            
                                            try:
                                                debug_container.write("🔌 Attempting to connect to MongoDB via FinancialAnalyzer...")
                                                collection = analyzer.connect_to_db()
                                                debug_container.write("✅ MongoDB connection successful via FinancialAnalyzer")
                                                debug_container.write(f"📄 Connected to collection: {collection.name}")
                                                
                                                debug_container.write("📝 Preparing to insert document...")
                                                debug_container.write(f"📊 Document size: {len(json.dumps(json_data)):,} bytes")
                                                debug_container.write("⏳ Inserting document...")
                                                result = collection.insert_one(json_data)
                                                debug_container.write(f"📌 Success! Inserted document ID: {result.inserted_id}")
                                                debug_container.write(f"📊 Collection now has {collection.count_documents({})} documents")
                                                
                                                st.success("✅ Data uploaded to MongoDB successfully!")
                                                
                                                # Note: FinancialAnalyzer's connect_to_db returns the collection,
                                                # so explicit client.close() is not directly managed here.
                                                # The connection is typically managed by the MongoClient instance.
                                            except Exception as e:
                                                st.error("❌ MongoDB upload failed!")
                                                debug_container.write("🛠️ Error details:")
                                                debug_container.exception(e)
                                                debug_container.write("Please check your MongoDB connection settings and try again")
                            else:
                                st.warning("⚠️ No tables found in the PDF")
                        else:
                            st.error("❌ Failed to process PDF")

    elif tab_selection == "📊 View Dashboard":
        st.header("📊 Financial Dashboard")

        # Key Metrics
        st.subheader("📈 Key Metrics")
        create_dashboard_metrics(analyzer, start_date, end_date)

        # Charts section
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Expense Breakdown")
            try:
                summary_data = analyzer.get_transaction_summary()
                create_expense_breakdown_chart(summary_data)
            except Exception as e:
                st.error(f"Error loading expense data: {str(e)}")

        with col2:
            st.subheader("📊 Cash Flow Trend")
            try:
                summary_data = analyzer.get_transaction_summary()
                create_cash_flow_chart(summary_data)
            except Exception as e:
                st.error(f"Error loading cash flow data: {str(e)}")

        # Transaction details
        st.subheader("💳 Recent Transactions")
        try:
            # Get latest transactions using FinancialAnalyzer's method
            transactions_df = analyzer.process_latest_json()
            if not transactions_df.empty:
                # Filter by date range
                filtered_df = transactions_df[
                    (transactions_df['date'] >= pd.to_datetime(start_date)) &
                    (transactions_df['date'] <= pd.to_datetime(end_date))
                ]

                # Display top 20 transactions
                display_df = filtered_df.head(20)[['date', 'description', 'debits', 'credits', 'balance', 'category']]
                st.dataframe(display_df, use_container_width=True)

                # Show uncategorized transactions
                uncategorized = filtered_df[filtered_df['category'] == 'Uncategorized']
                if not uncategorized.empty:
                    st.warning(f"⚠️ {len(uncategorized)} uncategorized transactions found")
                    with st.expander("View Uncategorized Transactions"):
                        st.dataframe(uncategorized[['date', 'description', 'debits', 'credits', 'balance']])
            else:
                st.info("No transaction data available. Please upload and process a bank statement first.")

        except Exception as e:
            st.error(f"Error loading transactions: {str(e)}")

    elif tab_selection == "⚙️ Settings":
        st.header("⚙️ Settings")

        # Category management
        st.subheader("🏷️ Category Management")

        col1, col2 = st.columns(2)
        with col1:
            new_term = st.text_input("Transaction Term", placeholder="e.g., 'netflix'")
            new_category = st.text_input("Category", placeholder="e.g., 'Entertainment'")

        with col2:
            category_type = st.selectbox(
                "Category Type",
                ['Necessary Expenses', 'Discretionary Expenses', 'Investment Spending', 'Income', 'Notices', 'Special']
            )

        if st.button("➕ Add Category Mapping"):
            if new_term and new_category:
                try:
                    analyzer.add_category_mapping(new_term, new_category, category_type)
                    st.success(f"✅ Added mapping: '{new_term}' → '{new_category}' ({category_type})")
                except Exception as e:
                    st.error(f"Error adding mapping: {str(e)}")
            else:
                st.error("Please fill in both term and category")

        # API Configuration
        st.subheader("🔑 API Configuration")
        current_api_key = st.text_input(
            "Upstage API Key",
            value=processor.api_key or "",
            type="password",
            help="Your Upstage Document AI API key"
        )

        if st.button("💾 Save API Key"):
            # In a real app, you'd save this securely
            st.success("✅ API key updated")

        # System Information
        st.subheader("ℹ️ System Information")
        st.info(f"**Current Directory:** {os.getcwd()}")
        st.info(f"**Environment Variables:** {len(os.environ)} loaded")

if __name__ == "__main__":
    main()
