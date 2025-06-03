# financial_analyzer.py
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from config import Config
from financial_insights import FinancialInsights

class FinancialAnalyzer:
    def __init__(self, base_analyzer):
        self.analyzer = base_analyzer
        self.log_file = open("financial_analyzer.log", "a")
        self.config = Config()
        self.db_password = self.config.db_password
        self.uri = f"mongodb+srv://ubuntupunk:{self.db_password}@{self.config.mongodb_url}"
        self.insights = FinancialInsights(self)
        self._log("initialising FinancialAnalyser...")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_file.write(f"{log_message}\n")
        self.log_file.flush()
        print(log_message)
    
    @st.cache_resource
    def connect_to_db(self):
        try:
            client = MongoClient(self.uri, server_api=ServerApi('1'))
            db = client["bankstat"]
            self._log("Connected to database")
            return db["statements"]
        except Exception as e:
            print(f"❌ MongoDB upload failed: {str(e)}")
            self._log(f"Error connecting to database: {str(e)}")
            raise

    def _categorize_transaction(self, description: str) -> str:
        """Simple transaction categorization based on description keywords"""
        description_lower = str(description).lower()
        
        # Define keyword mappings
        categories = {
            'Groceries': ['woolworths', 'checkers', 'pick n pay', 'spar', 'food', 'grocery'],
            'Transport': ['uber', 'bolt', 'petrol', 'fuel', 'taxi', 'transport', 'parking'],
            'Utilities': ['electricity', 'water', 'municipal', 'rates', 'internet', 'cell'],
            'Banking': ['bank', 'fee', 'charge', 'atm', 'service'],
            'Entertainment': ['movies', 'cinema', 'restaurant', 'bar', 'club', 'entertainment'],
            'Insurance': ['insurance', 'medical aid', 'cover'],
            'Shopping': ['clothing', 'retail', 'store', 'shop'],
            'Medical': ['pharmacy', 'doctor', 'hospital', 'medical', 'clinic'],
            'Investment': ['investment', 'dividend', 'interest', 'savings'],
            'Transfer': ['transfer', 'payment', 'deposit']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'Other'

    @st.cache_data
    def get_transaction_summary(_self: "FinancialAnalyzer") -> Dict:
        """Generate comprehensive transaction summary from the base analyzer's data"""
        try:
            # Get the processed transactions DataFrame
            transactions_df = _self.analyzer.process_latest_json()
            
            if transactions_df.empty:
                return {
                    'daily_flow': {},
                    'expense_types': {},
                    'total_debits': 0,
                    'total_credits': 0,
                    'net_flow': 0,
                    'transaction_count': 0
                }
            
            summary = {
                'daily_flow': {},
                'expense_types': {},
                'total_debits': 0,
                'total_credits': 0,
                'net_flow': 0,
                'transaction_count': len(transactions_df)
            }
            
            # Calculate totals
            summary['total_debits'] = transactions_df['debits'].sum()
            summary['total_credits'] = transactions_df['credits'].sum()
            summary['net_flow'] = summary['total_credits'] - summary['total_debits']
            
            # Daily flow analysis
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            daily_groups = transactions_df.groupby(transactions_df['date'].dt.date)
            
            for date, group in daily_groups:
                date_str = str(date)
                summary['daily_flow'][date_str] = {
                    'debits': group['debits'].sum(),
                    'credits': group['credits'].sum(),
                    'net': group['credits'].sum() - group['debits'].sum(),
                    'transaction_count': len(group)
                }
            
            # Category/expense type analysis
            if 'category' in transactions_df.columns:
                category_groups = transactions_df.groupby('category')
                for category, group in category_groups:
                    summary['expense_types'][category] = {
                        'debits': group['debits'].sum(),
                        'credits': group['credits'].sum(),
                        'net': group['credits'].sum() - group['debits'].sum(),
                        'transaction_count': len(group),
                        'avg_transaction': group['debits'].mean() if group['debits'].sum() > 0 else 0
                    }
            else:
                # If no category column, try to group by description patterns
                transactions_df['simple_category'] = transactions_df['description'].apply(_self._categorize_transaction)
                category_groups = transactions_df.groupby('simple_category')
                for category, group in category_groups:
                    summary['expense_types'][category] = {
                        'debits': group['debits'].sum(),
                        'credits': group['credits'].sum(),
                        'net': group['credits'].sum() - group['debits'].sum(),
                        'transaction_count': len(group),
                        'avg_transaction': group['debits'].mean() if group['debits'].sum() > 0 else 0
                    }
            
            return summary
            
        except Exception as e:
            st.error(f"Error generating transaction summary: {str(e)}")
            return {
                'daily_flow': {},
                'expense_types': {},
                'total_debits': 0,
                'total_credits': 0,
                'net_flow': 0,
                'transaction_count': 0
            }

    @st.cache_data
    def add_category_mapping(_self, term: str, category: str, category_type: str) -> bool:
        """Add a new category mapping (placeholder implementation)"""
        try:
            # In a real implementation, you might store this in a database or config file
            # For now, we'll just log it
            _self._log(f"Added category mapping: '{term}' -> '{category}' ({category_type})")
            return True
        except Exception as e:
            st.error(f"Error adding category mapping: {str(e)}")
            return False

    def process_latest_json(self):
        """Delegate to the base analyzer's process_latest_json method"""
        return self.analyzer.process_latest_json()

    # Delegate methods to insights module
    def get_monthly_trends(self, months: int = 6):
        """Get monthly spending trends - delegated to insights module"""
        return self.insights.get_monthly_trends(months)

    def get_category_insights(self):
        """Get category insights - delegated to insights module"""
        return self.insights.get_category_insights()

    def detect_unusual_transactions(self, threshold_multiplier: float = 2.0):
        """Detect unusual transactions - delegated to insights module"""
        return self.insights.detect_unusual_transactions(threshold_multiplier)

    def generate_budget_recommendations(self):
        """Generate budget recommendations - delegated to insights module"""
        return self.insights.generate_budget_recommendations()

    def get_spending_velocity(self, days: int = 30):
        """Get spending velocity - delegated to insights module"""
        return self.insights.get_spending_velocity(days)

    def calculate_monthly_average_balance(self, start_date: str, end_date: str):
        """Calculate monthly average balance - delegated to insights module"""
        return self.insights.calculate_monthly_average_balance(start_date, end_date)

    def analyze_bank_fees(self, start_date: str, end_date: str):
        """Analyze bank fees - delegated to insights module"""
        return self.insights.analyze_bank_fees(start_date, end_date)