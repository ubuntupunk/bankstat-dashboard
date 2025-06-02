# financial_analyzer.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st

class FinancialAnalyzer:
    """Enhanced financial analyzer with better error handling and additional features"""
    
    def __init__(self, base_analyzer):
        self.analyzer = base_analyzer
    
    def get_monthly_trends(self, months: int = 6) -> Dict:
        """Get monthly spending trends for the last N months"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            summary = self.analyzer.get_transaction_summary()
            daily_flow = summary.get('daily_flow', {})
            
            # Group by month
            monthly_data = {}
            for date_str, data in daily_flow.items():
                try:
                    date = pd.to_datetime(date_str)
                    month_key = date.strftime('%Y-%m')
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'debits': 0, 'credits': 0}
                    
                    monthly_data[month_key]['debits'] += data.get('debits', 0)
                    monthly_data[month_key]['credits'] += data.get('credits', 0)
                    
                except Exception:
                    continue
            
            return monthly_data
            
        except Exception as e:
            st.error(f"Error calculating monthly trends: {str(e)}")
            return {}
    
    def get_category_insights(self) -> Dict:
        """Get insights about spending categories"""
        try:
            summary = self.analyzer.get_transaction_summary()
            expense_types = summary.get('expense_types', {})
            
            insights = {
                'top_categories': [],
                'total_expenses': 0,
                'category_percentages': {}
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
    
    def detect_unusual_transactions(self, threshold_multiplier: float = 2.0) -> List[Dict]:
        """Detect transactions that are unusually large compared to typical amounts"""
        try:
            transactions_df = self.analyzer.process_latest_json()
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
            
            return unusual[['date', 'description', 'debits', 'category']].to_dict('records')
            
        except Exception as e:
            st.error(f"Error detecting unusual transactions: {str(e)}")
            return []
    
    def generate_budget_recommendations(self) -> Dict:
        """Generate budget recommendations based on spending patterns"""
        try:
            insights = self.get_category_insights()
            total_expenses = insights.get('total_expenses', 0)
            category_percentages = insights.get('category_percentages', {})
            
            recommendations = {
                'alerts': [],
                'suggestions': [],
                'budget_allocation': {}
            }
            
            # Standard budget allocation percentages
            ideal_allocation = {
                'Groceries': 15,
                'Transport': 10,
                'Utilities': 8,
                'Insurance': 5,
                'Entertainment': 5,
                'Dining Out': 3
            }
            
            # Compare actual vs ideal
            for category, ideal_pct in ideal_allocation.items():
                actual_pct = category_percentages.get(category, 0)
                
                if actual_pct > ideal_pct * 1.5:  # 50% over ideal
                    recommendations['alerts'].append(
                        f"High spending in {category}: {actual_pct:.1f}% vs recommended {ideal_pct}%"
                    )
                elif actual_pct < ideal_pct * 0.5:  # 50% under ideal
                    recommendations['suggestions'].append(
                        f"Consider allocating more to {category}: currently {actual_pct:.1f}%"
                    )
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return {}