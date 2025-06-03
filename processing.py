import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime
from io import StringIO


class BankStatementProcessor:
    """Handles bank statement processing and data extraction"""
    
    def __init__(self):
        self.json_file_path = "latest_bank_statement.json"
    
    @st.cache_data
    def load_latest_bank_statement(_self):
        """Load the latest processed bank statement JSON from storage and convert to DataFrame."""
        try:
            if os.path.exists(_self.json_file_path):
                with open(_self.json_file_path, "r") as f:
                    json_data = json.load(f)
                
                df = _self.extract_tables_to_dataframe(json_data)
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
                    
                    # Add category column if it doesn't exist
                    if 'category' not in df.columns:
                        df['category'] = 'Uncategorized'
                    
                    return df
            
            return pd.DataFrame()  # Return empty DataFrame if no data
        
        except Exception as e:
            st.error(f"Error loading transaction data: {str(e)}")
            return pd.DataFrame()
    
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
                combined_df.columns = combined_df.columns.astype(str)  # Ensure all column names are strings
                
                # Process Balance/Running Total
                balance_col = self._find_balance_column(combined_df)
                if balance_col:
                    combined_df = self._process_balance_column(combined_df, balance_col)
                else:
                    st.warning("Balance column not found in extracted tables.")
                    combined_df['balance'] = 0.0
                
                # Ensure numeric columns
                combined_df = self._ensure_numeric_columns(combined_df)
                
                # Add category column if not exists
                if 'category' not in combined_df.columns:
                    combined_df['category'] = 'Uncategorized'
                
                return combined_df
            
            return pd.DataFrame()
        
        except Exception as e:
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
            df['balance'] = df[balance_col].astype(str).str.replace(r'[^\d.,-]', '', regex=True).str.replace(',', '', regex=True)
            
            # Handle potential multiple decimal points if comma was used as decimal separator
            if df['balance'].str.count(r'\.').max() > 1:
                df['balance'] = df['balance'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            
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