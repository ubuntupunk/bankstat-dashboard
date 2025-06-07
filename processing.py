import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime
from io import StringIO
import logging
import re

class StreamlitAnalytics:
    """Handles bank statement processing and data extraction"""
    
    def __init__(self):
        self.json_file_path = "latest_bank_statement.json"
        logging.basicConfig(level=logging.DEBUG)  # Enable debug logging
    
    @st.cache_data(ttl=3600) # Cache for 1 hour
    def load_latest_bank_statement(_self):
        """Load the latest processed bank statement JSON from storage and convert to DataFrame."""
        try:
            if os.path.exists(_self.json_file_path):
                with open(_self.json_file_path, "r") as f:
                    json_data = json.load(f)
                
                df = _self._extract_tables_to_dataframe(json_data)
                if not df.empty:
                    # Ensure 'date' column is datetime and handle missing columns
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
                    
                    # Add description if missing
                    if 'description' not in df.columns:
                        df['description'] = 'Unknown'
                    
                    # Add category column if it doesn't exist
                    if 'category' not in df.columns:
                        df['category'] = 'Uncategorized'
                    
                    logging.debug(f"Loaded DataFrame columns: {df.columns.tolist()}")
                    return df
            
            logging.warning("No bank statement JSON file found")
            return pd.DataFrame()
        
        except Exception as e:
            logging.error(f"Error loading transaction data: {str(e)}")
            st.error(f"Error loading transaction data: {str(e)}")
            return pd.DataFrame()
    
    def process_latest_json(self):
        """Process the latest JSON bank statement and return a standardized DataFrame."""
        return self.load_latest_bank_statement()
    
    def _extract_tables_to_dataframe(self, json_data):
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
                        # Only include transaction tables (based on expected columns)
                        if any(col in df.columns for col in ['Date', 'Description', 'Debits (R)', 'Credits (R)', 'Balance (R)']):
                            all_tables.append(df)
            
            if all_tables:
                combined_df = pd.concat(all_tables, ignore_index=True)
                combined_df.columns = combined_df.columns.astype(str)  # Ensure all column names are strings
                
                # Log raw column names for debugging
                logging.debug(f"Raw DataFrame columns: {combined_df.columns.tolist()}")
                
                # Standardize column names
                column_mapping = {
                    'Date': 'date',
                    'Transaction Date': 'date',
                    'Trans Date': 'date',
                    'Description': 'description',
                    'Details': 'description',
                    'Trans Details': 'description',
                    'Narrative Description': 'description',
                    'Debit': 'debits',
                    'Debits': 'debits',
                    'Debits (R)': 'debits',
                    'Fees (R) Debits (R)': 'debits',  # Handle merged column
                    'Credit': 'credits',
                    'Credits': 'credits',
                    'Credits (R)': 'credits',
                    'Balance': 'balance',
                    'Balance (R)': 'balance',
                    'Running Balance': 'balance',
                    'Saldo': 'balance',
                    'Fees (R)': 'fees'  # Separate fees for clarity
                }
                combined_df = combined_df.rename(columns={k: v for k, v in column_mapping.items() if k in combined_df.columns})
                
                # Filter out summary rows (e.g., "Total Charges", "Closing balance")
                if 'description' in combined_df.columns:
                    combined_df = combined_df[~combined_df['description'].str.contains(
                        'Total Charges|Closing balance|Opening balance|Balance brought forward', 
                        case=False, na=False)]
                
                # Handle multiple values in debits/credits (e.g., "242.20 126.86")
                for col in ['debits', 'credits', 'fees']:
                    if col in combined_df.columns:
                        def parse_multi_values(x):
                            if pd.isna(x):
                                return 0.0
                            # Split by whitespace and sum valid numbers
                            values = str(x).split()
                            total = 0.0
                            for val in values:
                                cleaned = re.sub(r'[^\d.-]', '', val)
                                try:
                                    total += float(cleaned)
                                except ValueError:
                                    continue
                            return total
                        combined_df[col] = combined_df[col].apply(parse_multi_values)
                
                # Ensure numeric columns
                for col in ['debits', 'credits', 'balance', 'fees']:
                    if col in combined_df.columns:
                        combined_df[col] = combined_df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                        # Remove multiple decimal points
                        combined_df[col] = combined_df[col].str.replace(r'\.(?=.*\.)', '', regex=True)
                        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0.0)
                
                # Process Balance/Running Total
                balance_col = self._find_balance_column(combined_df)
                if balance_col and balance_col != 'balance':
                    combined_df = self._process_balance_column(combined_df, balance_col)
                else:
                    combined_df['balance'] = pd.to_numeric(combined_df['balance'], errors='coerce').fillna(0.0)
                
                # Ensure date is datetime
                if 'date' in combined_df.columns:
                    combined_df['date'] = pd.to_datetime(combined_df['date'], errors='coerce')
                
                # Add category column if not exists
                if 'category' not in combined_df.columns:
                    combined_df['category'] = 'Uncategorized'
                
                # Drop redundant columns
                keep_columns = ['date', 'description', 'debits', 'credits', 'balance', 'category', 'fees']
                existing_columns = [col for col in keep_columns if col in combined_df.columns]
                combined_df = combined_df[existing_columns]
                
                logging.debug(f"Processed DataFrame columns: {combined_df.columns.tolist()}")
                return combined_df
            
            logging.warning("No transaction tables found in JSON data")
            return pd.DataFrame()
        
        except Exception as e:
            logging.error(f"Error extracting tables: {str(e)}")
            st.error(f"Error extracting tables: {str(e)}")
            return pd.DataFrame()
    
    def _find_balance_column(self, df):
        """Find the balance column in the dataframe"""
        for col in df.columns:
            if isinstance(col, str) and ('balance' in col.lower() or 'saldo' in col.lower()):
                return col
        return None
    
    def _process_balance_column(self, df, balance_col):
        """Process and clean the balance column"""
        try:
            df['balance'] = df[balance_col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            # Handle multiple decimal points
            df['balance'] = df['balance'].str.replace(r'\.(?=.*\.)', '', regex=True)
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0.0)
            
            # Ensure date column is datetime and sort for running total
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.sort_values('date')
            
            return df
            
        except Exception as e:
            st.warning(f"Could not process balance column '{balance_col}': {str(e)}")
            df['balance'] = 0.0
            return df
    
    def _ensure_numeric_columns(self, df):
        """Ensure debits and credits are numeric"""
        if 'debits' in df.columns:
            df['debits'] = pd.to_numeric(df['debits'], errors='coerce').fillna(0.0)
        else:
            df['debits'] = 0.0
        
        if 'credits' in df.columns:
            df['credits'] = pd.to_numeric(df['credits'], errors='coerce').fillna(0.0)
        else:
            df['credits'] = 0.0
        
        return df
    
    def save_bank_statement(self, json_data):
        """Save bank statement JSON to file"""
        try:
            with open(self.json_file_path, "w") as f:
                json.dump(json_data, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving bank statement: {str(e)}")
            return False
    
    def get_statement_info(self):
        """Get information about the loaded statement"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, "r") as f:
                    json_data = json.load(f)
                
                return {
                    'filename': json_data.get('filename', 'Unknown'),
                    'period': json_data.get('period', {}),
                    'processed_date': datetime.fromtimestamp(os.path.getmtime(self.json_file_path)),
                    'file_size': os.path.getsize(self.json_file_path)
                }
            return None
        except Exception as e:
            st.error(f"Error getting statement info: {str(e)}")
            return None
