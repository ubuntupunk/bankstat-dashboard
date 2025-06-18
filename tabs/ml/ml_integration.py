import streamlit as st
import pandas as pd
import psutil
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from db.category_db import CategoryDB
from models.ui_components import render_ml_tab_ui
from models.ml_processor import MLProcessor
from models.transaction_categorizer import TransactionCategorizer
from utils.utils import debug_write # Import custom debug_write

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

class MLCategoryIntegration:
    """Integration layer for ML-based transaction categorization with uniform data handling."""
    
    def __init__(self, analyzer, db_connection):
        self.analyzer = analyzer
        self.db_connection = db_connection  # MongoDB connection for transactions
        self.categorizer = None
        self.db = CategoryDB()  # Supabase connection for categories
        self.ml_processor = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize categorizer and processor with memory monitoring."""
        process = psutil.Process()
        try:
            debug_write("Initializing TransactionCategorizer")
            self.categorizer = TransactionCategorizer(use_tensorflow=False)  # Disable TensorFlow for stability
            self.ml_processor = MLProcessor(self.categorizer)
            debug_write(f"Components initialized. Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        except Exception as e:
            debug_write(f"Initialization failed: {e}")
            self.categorizer = None
            self.ml_processor = None
    
    def render_ml_tab(self, processor, start_date: datetime, end_date: datetime, data_source: str = "Auto"):
        """Render the ML categorization tab with uniform data loading."""
        debug_write("Starting render_ml_tab")
        try:
            if self.categorizer is None or self.ml_processor is None:
                debug_write("Categorizer or processor not initialized")
                st.error("❌ ML Categorizer failed to initialize. Please check the logs.")
                return
            
            # Load transactions with chunking and fallback
            transactions_df, data_info = self._load_transactions(processor, start_date, end_date, data_source)
            
            # Render UI components, passing potentially empty transactions_df and data_info
            render_ml_tab_ui(self.ml_processor, processor, transactions_df, self.db, self.db_connection, data_info, start_date, end_date)
            
        except Exception as e:
            debug_write(f"Error in render_ml_tab: {e}")
            st.error(f"Error in ML tab: {e}")
    
    def _load_transactions(self, processor, start_date: datetime, end_date: datetime, data_source: str = "Auto") -> tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """Load transactions from MongoDB or local file with chunking."""
        transactions_df = pd.DataFrame()
        data_info = {}
        process = psutil.Process()
        
        # Check data source availability
        local_available = processor.get_statement_info() is not None
        db_available = False
        try:
            doc_count = self.db_connection.count_documents()
            db_available = doc_count > 0
            debug_write(f"Local available: {local_available}, MongoDB documents: {doc_count}")
        except Exception as e:
            debug_write(f"MongoDB check failed: {e}")
        
        # Auto-select data source
        if data_source == "Auto":
            data_source = "Database Query" if db_available else "Local File" if local_available else "No Data"
        debug_write(f"Selected data source: {data_source}")
        
        # Load from MongoDB
        if data_source == "Database Query" and db_available:
            try:
                debug_write(f"Querying MongoDB for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                with st.spinner("Loading data from MongoDB..."):
                    # MongoDB query for documents within the date range
                    # Documents store 'period.start' and 'period.end' as strings in 'YYYY-MM-DD' format
                    query = {
                        "$or": [
                            {
                                "period.start": {"$lte": end_date.strftime("%Y-%m-%d")},
                                "period.end": {"$gte": start_date.strftime("%Y-%m-%d")}
                            },
                            # Include documents without a defined period (e.g., single transactions)
                            {"period.start": {"$exists": False}} 
                        ]
                    }
                    documents = self.db_connection.find_documents(query=query, sort_by=[("uploaded_at", -1)])
                    debug_write(f"Found {len(documents)} MongoDB documents matching date range query.")
                    
                    if documents:
                        for doc in documents:
                            debug_write(f"Processing MongoDB document: {doc.get('filename', 'N/A')}. Document keys: {list(doc.keys())}")
                            df = processor.process_latest_json(json_data=doc)
                            debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' processed by processor. Initial rows: {len(df)}")
                            
                            if not df.empty:
                                df = self._standardize_columns(df)
                                if 'date' in df.columns:
                                    debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' date column dtype: {df['date'].dtype}")
                                    if pd.api.types.is_datetime64_any_dtype(df['date']):
                                        debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' date range: {df['date'].min()} to {df['date'].max()}")
                                        df_filtered = df[
                                            (df['date'] >= pd.to_datetime(start_date)) &
                                            (df['date'] <= pd.to_datetime(end_date))
                                        ]
                                        debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' rows after date filter: {len(df_filtered)}")
                                    else:
                                        df_filtered = df # Cannot filter if date is not datetime, use as is
                                        debug_write(f"MongoDB doc '{doc.get('filename', 'N/A')}' 'date' column is not datetime. Skipping date filter for this doc.")
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
                    # This is crucial to ensure all transactions fall within the selected range,
                    # especially if documents without 'period' were included.
                    if not transactions_df.empty:
                        transactions_df['date'] = pd.to_datetime(transactions_df['date'], errors='coerce') # Ensure date is datetime before final filter
                        transactions_df = transactions_df[
                            (transactions_df['date'] >= pd.to_datetime(start_date)) &
                            (transactions_df['date'] <= pd.to_datetime(end_date))
                        ]
                        debug_write(f"Final filter applied to combined MongoDB transactions. Transactions after final filter: {len(transactions_df)}")
                    
                    if not transactions_df.empty:
                        transactions_df = transactions_df.drop_duplicates().sort_values('date')
                        data_info = {
                            'source': 'MongoDB',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"Loaded {len(transactions_df)} transactions from MongoDB. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    else:
                        debug_write(f"No MongoDB transactions for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                        if local_available:
                            data_source = "Local File"
            except Exception as e:
                debug_write(f"MongoDB query failed: {e}")
                data_info['error'] = str(e)
                if local_available:
                    debug_write("Falling back to local file")
                    data_source = "Local File"
        
        # Load from Local File
        if (data_source == "Local File" and local_available) or (data_source == "Database Query" and transactions_df.empty and local_available):
            try:
                debug_write(f"Loading data from local file for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                with st.spinner("Loading data from local file..."):
                    temp_df = processor.load_latest_bank_statement() 
                    debug_write(f"Local file loaded. Initial rows: {len(temp_df)}")
                    
                    if not temp_df.empty:
                        temp_df = self._standardize_columns(temp_df)
                        if 'date' in temp_df.columns:
                            temp_df['date'] = pd.to_datetime(temp_df['date'], errors='coerce') # Ensure date is datetime
                            debug_write(f"Local file date column min/max: {temp_df['date'].min()} / {temp_df['date'].max()}")
                            debug_write(f"Filtering local file for range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                            temp_df = temp_df[
                                (temp_df['date'] >= pd.to_datetime(start_date)) &
                                (temp_df['date'] <= pd.to_datetime(end_date))
                            ]
                            debug_write(f"Local file data has {len(temp_df)} rows after date filtering.")
                        else:
                            debug_write("Local file data has no 'date' column. Using all rows.")

                        transactions_df = pd.concat([transactions_df, temp_df], ignore_index=True)
                        debug_write(f"Added {len(temp_df)} rows from local file to total. Current total: {len(transactions_df)}")
                    else:
                        debug_write("Processor returned empty DataFrame for local file.")
                    
                    if not transactions_df.empty: # Check if transactions_df has data after processing temp_df
                        transactions_df = transactions_df.drop_duplicates().sort_values('date')
                        statement_info = processor.get_statement_info()
                        data_info = {
                            'source': 'Local File',
                            'filename': statement_info.get('filename', 'Unknown'),
                            'file_period': f"{statement_info.get('period', {}).get('start', 'Unknown')} to {statement_info.get('period', {}).get('end', 'Unknown')}",
                            'transactions_loaded': len(transactions_df),
                            'selected_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        debug_write(f"Loaded {len(transactions_df)} transactions from local file. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    else:
                        debug_write(f"No local file transactions for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            except Exception as e:
                debug_write(f"Local file loading failed: {e}")
                data_info['error'] = str(e)
            except Exception as e:
                debug_write(f"Local file loading failed: {e}")
                data_info['error'] = str(e)
        
        # Ensure category_name column
        if not transactions_df.empty:
            if 'category_name' not in transactions_df.columns:
                transactions_df['category_name'] = 'Uncategorized'
            transactions_df['category_name'] = transactions_df['category_name'].fillna('Uncategorized')
        
        return transactions_df, data_info
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format."""
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
            'Saldo': 'balance',
            'Category': 'category_name',
            'category': 'category_name'
        }
        df = df.rename(columns=column_mapping)
        
        required_columns = ['date', 'description', 'debits', 'credits', 'balance', 'category_name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = 'Unknown' if col in ['description', 'category_name'] else 0.0
        
        # Ensure 'date' column is datetime after standardization
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Drop rows where date conversion failed
            df.dropna(subset=['date'], inplace=True)
        
        return df
