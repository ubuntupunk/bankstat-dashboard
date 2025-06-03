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

class FinancialAnalyzer:
    def __init__(self, base_analyzer):
        self.analyzer = base_analyzer
        self.log_file = open("financial_analyzer.log", "a")
        self.config = Config()
        self.db_password = self.config.db_password
        self.uri = f"mongodb+srv://ubuntupunk:{self.db_password}@{self.config.mongodb_url}"
        self._log("initialising FinancialAnalyser...")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_file.write(f"{log_message}\n")
        self.log_file.flush()
        print(log_message)
    
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
    def get_monthly_trends(_self, months: int = 6) -> Dict:
        """Get monthly spending trends for the last N months"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            summary = _self.get_transaction_summary()
            daily_flow = summary.get('daily_flow', {})
            
            # Group by month
            monthly_data = {}
            for date_str, data in daily_flow.items():
                try:
                    date = pd.to_datetime(date_str)
                    if date >= start_date:
                        month_key = date.strftime('%Y-%m')
                        
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {'debits': 0, 'credits': 0, 'net': 0}
                        
                        monthly_data[month_key]['debits'] += data.get('debits', 0)
                        monthly_data[month_key]['credits'] += data.get('credits', 0)
                        monthly_data[month_key]['net'] += data.get('net', 0)
                        
                except Exception:
                    continue
            
            return monthly_data
            
        except Exception as e:
            st.error(f"Error calculating monthly trends: {str(e)}")
            return {}
    
    @st.cache_data
    def get_category_insights(_self) -> Dict:
        """Get insights about spending categories"""
        try:
            summary = _self.get_transaction_summary()
            expense_types = summary.get('expense_types', {})
            
            insights = {
                'top_categories': [],
                'total_expenses': 0,
                'category_percentages': {},
                'category_details': {}
            }
            
            # Calculate totals and percentages
            category_totals = []
            total_expenses = 0
            
            for category, data in expense_types.items():
                if isinstance(data, dict) and 'debits' in data:
                    amount = data['debits']
                    if amount > 0:
                        category_totals.append((category, amount))
                        total_expenses += amount
                        insights['category_details'][category] = data
            
            # Sort by amount
            category_totals.sort(key=lambda x: x[1], reverse=True)
            
            insights['total_expenses'] = total_expenses
            insights['top_categories'] = category_totals[:5]  # Top 5
            
            # Calculate percentages
            for category, amount in category_totals:
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                insights['category_percentages'][category] = percentage
            
            return insights
            
        except Exception as e:
            st.error(f"Error getting category insights: {str(e)}")
            return {}
    
    @st.cache_data
    def detect_unusual_transactions(_self, threshold_multiplier: float = 2.0) -> List[Dict]:
        """Detect transactions that are unusually large compared to typical amounts"""
        try:
            transactions_df = _self.analyzer.process_latest_json()
            if transactions_df.empty:
                return []
            
            # Calculate mean and std for debits
            debits = transactions_df[transactions_df['debits'] > 0]['debits']
            if len(debits) < 2:
                return []
            
            mean_debit = debits.mean()
            std_debit = debits.std()
            threshold = mean_debit + (threshold_multiplier * std_debit)
            
            # Find unusual transactions
            unusual = transactions_df[transactions_df['debits'] > threshold]
            
            # Prepare return data
            result = []
            for _, row in unusual.iterrows():
                transaction = {
                    'date': str(row['date']),
                    'description': row['description'],
                    'debits': row['debits'],
                }
                
                # Add category if available
                if 'category' in row:
                    transaction['category'] = row['category']
                else:
                    transaction['category'] = _self._categorize_transaction(row['description'])
                    
                result.append(transaction)
            
            return result
            
        except Exception as e:
            st.error(f"Error detecting unusual transactions: {str(e)}")
            return []
    
    @st.cache_data
    def generate_budget_recommendations(_self) -> Dict:
        """Generate budget recommendations based on spending patterns"""
        try:
            insights = _self.get_category_insights()
            total_expenses = insights.get('total_expenses', 0)
            category_percentages = insights.get('category_percentages', {})
            
            recommendations = {
                'alerts': [],
                'suggestions': [],
                'budget_allocation': {},
                'summary': {}
            }
            
            # Standard budget allocation percentages (South African context)
            ideal_allocation = {
                'Groceries': 15,
                'Transport': 12,
                'Utilities': 10,
                'Insurance': 8,
                'Entertainment': 5,
                'Medical': 5,
                'Shopping': 8,
                'Banking': 2
            }
            
            # Calculate summary stats
            recommendations['summary'] = {
                'total_expenses': total_expenses,
                'categories_analyzed': len(category_percentages),
                'top_category': max(category_percentages.items(), key=lambda x: x[1]) if category_percentages else ('None', 0)
            }
            
            # Compare actual vs ideal
            for category, ideal_pct in ideal_allocation.items():
                actual_pct = category_percentages.get(category, 0)
                
                if actual_pct > ideal_pct * 1.5:  # 50% over ideal
                    recommendations['alerts'].append(
                        f"High spending in {category}: {actual_pct:.1f}% vs recommended {ideal_pct}%"
                    )
                elif actual_pct > 0 and actual_pct < ideal_pct * 0.3:  # Very low spending
                    recommendations['suggestions'].append(
                        f"Very low spending in {category}: {actual_pct:.1f}% - consider if this is adequate"
                    )
                
                recommendations['budget_allocation'][category] = {
                    'actual': actual_pct,
                    'recommended': ideal_pct,
                    'status': 'over' if actual_pct > ideal_pct * 1.2 else 'under' if actual_pct < ideal_pct * 0.8 else 'good'
                }
            
            # Add general recommendations
            if not recommendations['alerts'] and not recommendations['suggestions']:
                recommendations['suggestions'].append("Your spending appears to be well-balanced across categories!")
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return {}
    
    @st.cache_data
    def get_spending_velocity(_self, days: int = 30) -> Dict:
        """Calculate spending velocity (rate of spending over time)"""
        try:
            transactions_df = _self.analyzer.process_latest_json()
            if transactions_df.empty:
                return {}
            
            # Filter to recent transactions
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_transactions = transactions_df[transactions_df['date'] >= cutoff_date]
            
            if recent_transactions.empty:
                return {}
            
            # Calculate daily spending
            daily_spending = recent_transactions.groupby(recent_transactions['date'].dt.date)['debits'].sum()
            
            velocity = {
                'avg_daily_spending': daily_spending.mean(),
                'max_daily_spending': daily_spending.max(),
                'min_daily_spending': daily_spending.min(),
                'spending_trend': 'increasing' if daily_spending.iloc[-5:].mean() > daily_spending.iloc[:5].mean() else 'decreasing',
                'days_analyzed': len(daily_spending),
                'total_period_spending': daily_spending.sum()
            }
            
            return velocity
            
        except Exception as e:
            st.error(f"Error calculating spending velocity: {str(e)}")
            return {}

    @st.cache_data
    def calculate_monthly_average_balance(_self, start_date: str, end_date: str) -> Dict:
        """Calculate monthly average balance for the given date range"""
        try:
            transactions_df = _self.analyzer.process_latest_json()
            if transactions_df.empty:
                return {'average_balance': 0, 'balance_trend': 'stable'}
            
            # Filter transactions by date range
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            filtered_df = transactions_df[
                (transactions_df['date'] >= start_dt) & 
                (transactions_df['date'] <= end_dt)
            ]
            
            if filtered_df.empty:
                return {'average_balance': 0, 'balance_trend': 'stable'}
            
            # Calculate average balance
            if 'balance' in filtered_df.columns:
                # Use actual balance column if available
                avg_balance = filtered_df['balance'].mean()
                balance_trend = 'increasing' if filtered_df['balance'].iloc[-1] > filtered_df['balance'].iloc[0] else 'decreasing'
            else:
                # Estimate balance from transactions
                # This is a simplified calculation - in reality, you'd need opening balance
                total_credits = filtered_df['credits'].sum()
                total_debits = filtered_df['debits'].sum()
                net_flow = total_credits - total_debits
                
                # Assume a reasonable starting balance for estimation
                estimated_starting_balance = 10000  # You might want to make this configurable
                avg_balance = estimated_starting_balance + (net_flow / 2)
                balance_trend = 'increasing' if net_flow > 0 else 'decreasing'
            
            return {
                'average_balance': avg_balance,
                'balance_trend': balance_trend
            }
            
        except Exception as e:
            st.error(f"Error calculating monthly average balance: {str(e)}")
            return {'average_balance': 0, 'balance_trend': 'stable'}
    
    @st.cache_data
    def analyze_bank_fees(_self, start_date: str, end_date: str) -> Dict:
        """Analyze bank fees for the given date range"""
        try:
            transactions_df = _self.analyzer.process_latest_json()
            if transactions_df.empty:
                return {'total_fees': 0, 'fee_types': {}, 'fee_count': 0}
            
            # Filter transactions by date range
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            
            filtered_df = transactions_df[
                (transactions_df['date'] >= start_dt) & 
                (transactions_df['date'] <= end_dt)
            ]
            
            if filtered_df.empty:
                return {'total_fees': 0, 'fee_types': {}, 'fee_count': 0}
            
            # Identify fee transactions based on description keywords
            fee_keywords = ['fee', 'charge', 'service', 'atm', 'commission', 'monthly fee', 'transaction fee']
            
            # Create a mask for fee transactions
            fee_mask = filtered_df['description'].str.lower().str.contains('|'.join(fee_keywords), na=False)
            fee_transactions = filtered_df[fee_mask]
            
            if fee_transactions.empty:
                return {'total_fees': 0, 'fee_types': {}, 'fee_count': 0}
            
            # Calculate total fees
            total_fees = fee_transactions['debits'].sum()
            
            # Categorize fee types
            fee_types = {}
            for _, transaction in fee_transactions.iterrows():
                description = transaction['description'].lower()
                amount = transaction['debits']
                
                # Categorize based on keywords
                if 'atm' in description:
                    fee_type = 'ATM Fees'
                elif 'service' in description or 'monthly' in description:
                    fee_type = 'Service Fees'
                elif 'transaction' in description:
                    fee_type = 'Transaction Fees'
                elif 'commission' in description:
                    fee_type = 'Commission'
                else:
                    fee_type = 'Other Fees'
                
                if fee_type not in fee_types:
                    fee_types[fee_type] = {'amount': 0, 'count': 0}
                
                fee_types[fee_type]['amount'] += amount
                fee_types[fee_type]['count'] += 1
            
            return {
                'total_fees': total_fees,
                'fee_types': fee_types,
                'fee_count': len(fee_transactions)
            }
            
        except Exception as e:
            st.error(f"Error analyzing bank fees: {str(e)}")
            return {'total_fees': 0, 'fee_types': {}, 'fee_count': 0}
    
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