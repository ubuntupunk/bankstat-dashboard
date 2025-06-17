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
            logger.debug("Initializing TransactionCategorizer")
            self.categorizer = TransactionCategorizer(use_tensorflow=False)  # Disable TensorFlow for stability
            self.ml_processor = MLProcessor(self.categorizer)
            logger.info(f"Components initialized. Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            self.categorizer = None
            self.ml_processor = None
    
    def render_ml_tab(self, processor, start_date: datetime, end_date: datetime, data_source: str = "Auto"):
        """Render the ML categorization tab with uniform data loading."""
        logger.debug("Starting render_ml_tab")
        try:
            if self.categorizer is None or self.ml_processor is None:
                logger.error("Categorizer or processor not initialized")
                st.error("❌ ML Categorizer failed to initialize. Please check the logs.")
                return
            
            # Load transactions with chunking and fallback
            transactions_df, data_info = self._load_transactions(processor, start_date, end_date, data_source)
            if transactions_df is None or transactions_df.empty:
                logger.warning(f"No transaction data available. Source: {data_source}, Info: {data_info}")
                if data_info.get('source') == 'Database' and data_info.get('documents_found', 0) == 0:
                    st.error(f"❌ No transactions found in MongoDB for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}. Please upload a bank statement or adjust the date range.")
                elif data_info.get('source') == 'Local File' and data_info.get('filename'):
                    st.error(f"❌ No valid transactions in local file '{data_info.get('filename')}' for the selected date range. Please upload a new bank statement.")
                else:
                    st.error("❌ No transaction data available. Please upload a bank statement in the 'Upload & Process' tab.")
                return
            
            # Display data info
            with st.expander("📋 Data Source Information", expanded=False):
                for key, value in data_info.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            # Render UI components
            render_ml_tab_ui(self.ml_processor, processor, transactions_df, self.db, self.db_connection)
            
        except Exception as e:
            logger.error(f"Error in render_ml_tab: {e}", exc_info=True)
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
            logger.debug(f"Local available: {local_available}, MongoDB documents: {doc_count}")
        except Exception as e:
            logger.error(f"MongoDB check failed: {e}", exc_info=True)
        
        # Auto-select data source
        if data_source == "Auto":
            data_source = "Database Query" if db_available else "Local File" if local_available else "No Data"
        
        # Load from MongoDB
        if data_source == "Database Query" and db_available:
            try:
                logger.debug(f"Querying MongoDB for {start_date} to {end_date}")
                with st.spinner("Loading data from MongoDB..."):
                    query = {
                        "$or": [
                            {
                                "period.start": {"$lte": end_date.strftime("%Y-%m-%d")},
                                "period.end": {"$gte": start_date.strftime("%Y-%m-%d")}
                            },
                            {"period.start": {"$exists": False}}
                        ]
                    }
                    documents = self.db_connection.find_documents(query=query, sort_by=[("uploaded_at", -1)])
                    logger.debug(f"Found {len(documents)} MongoDB documents")
                    
                    if documents:
                        for doc in documents:
                            logger.debug(f"Processing MongoDB document: {list(doc.keys())}")
                            df = processor.process_latest_json()  # Assumes this processes the document
                            if not df.empty:
                                df = self._standardize_columns(df)
                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                    df = df[
                                        (df['date'] >= pd.to_datetime(start_date)) &
                                        (df['date'] <= pd.to_datetime(end_date))
                                    ]
                                if not df.empty:
                                    transactions_df = pd.concat([transactions_df, df], ignore_index=True)
                    
                    if not transactions_df.empty:
                        transactions_df = transactions_df.drop_duplicates().sort_values('date')
                        data_info = {
                            'source': 'MongoDB',
                            'documents_found': len(documents),
                            'transactions_loaded': len(transactions_df),
                            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        logger.info(f"Loaded {len(transactions_df)} transactions from MongoDB. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    else:
                        logger.warning(f"No MongoDB transactions for {start_date} to {end_date}")
                        if local_available:
                            data_source = "Local File"
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}", exc_info=True)
                if local_available:
                    logger.info("Falling back to local file")
                    data_source = "Local File"
        
        # Load from Local File
        if (data_source == "Local File" and local_available) or (data_source == "Database Query" and transactions_df.empty and local_available):
            try:
                with st.spinner("Loading data from local file..."):
                    chunk_size = 1000
                    chunks = []
                    for chunk in processor.load_latest_bank_statement(chunk_size=chunk_size):
                        if chunk is not None and not chunk.empty:
                            chunk = self._standardize_columns(chunk)
                            if 'date' in chunk.columns:
                                chunk['date'] = pd.to_datetime(chunk['date'], errors='coerce')
                                chunk = chunk[
                                    (chunk['date'] >= pd.to_datetime(start_date)) &
                                    (chunk['date'] <= pd.to_datetime(end_date))
                                ]
                            chunks.append(chunk)
                            logger.debug(f"Processed chunk of {len(chunk)} rows. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    
                    if chunks:
                        transactions_df = pd.concat(chunks, ignore_index=True).drop_duplicates().sort_values('date')
                        statement_info = processor.get_statement_info()
                        data_info = {
                            'source': 'Local File',
                            'filename': statement_info.get('filename', 'Unknown'),
                            'file_period': f"{statement_info.get('period', {}).get('start', 'Unknown')} to {statement_info.get('period', {}).get('end', 'Unknown')}",
                            'transactions_loaded': len(transactions_df),
                            'selected_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            'columns': transactions_df.columns.tolist()
                        }
                        logger.info(f"Loaded {len(transactions_df)} transactions from local file. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
            except Exception as e:
                logger.error(f"Local file loading failed: {e}", exc_info=True)
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
        
        return df
