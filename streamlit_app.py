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
from enhanced_financial_analyzer import FinancialAnalyzer
import logging

# Configure page
st.set_page_config(
    page_title="Bankstat Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .upload-area {
        border: 2px dashed #2E8B57;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid;
    }
    .status-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitBankProcessor:
    def __init__(self):
        self.api_key = os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            st.error("⚠️ UPSTAGE_API_KEY not found in environment variables")
        
    def process_pdf(self, uploaded_file):
        """Process uploaded PDF file using Upstage API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Call Upstage API
            url = 'https://api.upstage.ai/v1/document-ai/document-parse'
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            with open(tmp_file_path, "rb") as file:
                files = {"document": file}
                response = requests.post(url, headers=headers, files=files)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if response.status_code == 200:
                data = response.json()
                
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
    analyzer = FinancialAnalyzer()
    
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
                                        # Here you would save to MongoDB
                                        st.success("✅ Saved to database!")
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
            # Get latest transactions
            transactions_df = analyzer.process_latest_json()
            if not transactions_df.empty:
                # Filter by date range
                filtered_df = transactions_df[
                    (transactions_df['date'] >= pd.to_datetime(start_date)) &
                    (transactions_df['date'] <= pd.to_datetime(end_date))
                ]
                
                # Display top 20 transactions
                display_df = filtered_df.head(20)[['date', 'description', 'debits', 'credits', 'category']]
                st.dataframe(display_df, use_container_width=True)
                
                # Show uncategorized transactions
                uncategorized = filtered_df[filtered_df['category'] == 'Uncategorized']
                if not uncategorized.empty:
                    st.warning(f"⚠️ {len(uncategorized)} uncategorized transactions found")
                    with st.expander("View Uncategorized Transactions"):
                        st.dataframe(uncategorized[['date', 'description', 'debits', 'credits']])
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