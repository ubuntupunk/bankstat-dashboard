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
            
            # Render UI components, passing potentially empty transactions_df and data_info
            render_ml_tab_ui(self.ml_processor, processor, transactions_df, self.db, self.db_connection, data_info, start_date, end_date)
            
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
                    logger.debug(f"Found {len(documents)} MongoDB documents matching date range query.")
                    
                    if documents:
                        for doc in documents:
                            logger.debug(f"Processing MongoDB document: {doc.get('filename', 'N/A')}")
                            # Assuming 'doc' contains the raw JSON structure of a bank statement
                            # We need to pass the actual document content to processor for extraction
                            # This might require a change in processor.process_latest_json or a new method
                            # For now, let's assume processor can take a dict or has a way to load from a specific doc
                            # If processor.process_latest_json() always reads from 'latest_bank_statement.json',
                            # then we need to save the current doc to that file temporarily or refactor processor.
                            
                            # For demonstration, let's assume processor can take the document directly
                            # This is a placeholder and might need actual implementation in processing.py
                            # For now, we'll simulate by loading the latest_bank_statement.json if it exists
                            # and then filtering it by the document's period if available.
                            
                            # A more robust solution would involve passing the 'doc' content to processor
                            # or having processor fetch specific documents by ID.
                            
                            # Pass the document content directly to processor.process_latest_json
                            # This assumes the document structure is compatible with what process_latest_json expects
                            # (i.e., it contains 'elements' with 'table' categories and 'content.html')
                            df = processor.process_latest_json(json_data=doc)
                            
                            if not df.empty:
                                df = self._standardize_columns(df)
                                if 'date' in df.columns:
                                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                                    # Filter by the overall selected range, as the MongoDB query already handled document periods
                                    df = df[
                                        (df['date'] >= pd.to_datetime(start_date)) &
                                        (df['date'] <= pd.to_datetime(end_date))
                                    ]
                                if not df.empty:
                                    transactions_df = pd.concat([transactions_df, df], ignore_index=True)
                                    logger.debug(f"Added {len(df)} transactions from document to total.")
                    
                    # After processing all documents, apply the overall date range filter one last time
                    if not transactions_df.empty:
                        transactions_df = transactions_df[
                            (transactions_df['date'] >= pd.to_datetime(start_date)) &
                            (transactions_df['date'] <= pd.to_datetime(end_date))
                        ]
                        logger.debug(f"Final filter applied. Transactions after filter: {len(transactions_df)}")
                    
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
                    # No chunking parameter for load_latest_bank_statement when loading from file
                    temp_df = processor.load_latest_bank_statement() 
                    
                    if not temp_df.empty:
                        temp_df = self._standardize_columns(temp_df)
                        if 'date' in temp_df.columns:
                            temp_df['date'] = pd.to_datetime(temp_df['date'], errors='coerce')
                            temp_df = temp_df[
                                (temp_df['date'] >= pd.to_datetime(start_date)) &
                                (temp_df['date'] <= pd.to_datetime(end_date))
                            ]
                        transactions_df = pd.concat([transactions_df, temp_df], ignore_index=True)
                        logger.debug(f"Processed {len(temp_df)} rows from local file. Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
                    
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
