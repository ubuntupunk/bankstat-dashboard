# utils.py
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import json
import tempfile
import os
import plotly.express as px
import plotly.graph_objects as go

class StreamlitUtils:
    """Utility functions for Streamlit app"""
    
    @staticmethod
    def display_success_message(message):
        """Display a styled success message"""
        st.markdown(f"""
        <div class="status-success">
            ✅ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_error_message(message):
        """Display a styled error message"""
        st.markdown(f"""
        <div class="status-error">
            ❌ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_info_message(message):
        """Display a styled info message"""
        st.markdown(f"""
        <div class="status-info">
            ℹ️ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def format_currency(amount):
        """Format amount as South African Rand"""
        if pd.isna(amount) or amount is None:
            return "R 0.00"
        return f"R {amount:,.2f}"
    
    @staticmethod
    def safe_divide(numerator, denominator):
        """Safely divide two numbers, returning 0 if denominator is 0"""
        try:
            return numerator / denominator if denominator != 0 else 0
        except (TypeError, ZeroDivisionError):
            return 0
    
    @staticmethod
    def create_download_button(data, filename, label, file_type="text/csv"):
        """Create a download button with proper formatting"""
        return st.download_button(
            label=label,
            data=data,
            file_name=filename,
            mime=file_type,
            use_container_width=True
        )
    
    @staticmethod
    def create_metric_card(title, value, delta=None, help_text=None):
        """Create a styled metric card"""
        if delta:
            st.metric(
                label=title,
                value=value,
                delta=delta,
                help=help_text
            )
        else:
            st.metric(
                label=title,
                value=value,
                help=help_text
            )
    
    @staticmethod
    def validate_dataframe(df, required_columns=None):
        """Validate that a dataframe has the required structure"""
        if df is None or df.empty:
            return False, "DataFrame is empty or None"
        
        if required_columns:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                return False, f"Missing required columns: {missing_cols}"
        
        return True, "DataFrame is valid"
    
    @staticmethod
    def safe_get_value(dictionary, key, default=0):
        """Safely get a value from a dictionary with error handling"""
        try:
            return dictionary.get(key, default) if dictionary else default
        except (AttributeError, KeyError):
            return default
    
    @staticmethod
    def format_percentage(value, decimal_places=1):
        """Format a decimal as a percentage"""
        try:
            return f"{value:.{decimal_places}f}%"
        except (TypeError, ValueError):
            return "0.0%"
    
    @staticmethod
    def create_category_chart(category_data, title="Category Spending"):
        """Create a pie chart for category spending"""
        if not category_data:
            st.info("No category data available to display")
            return
        
        try:
            # Prepare data for plotting
            categories = list(category_data.keys())
            values = [category_data[cat].get('debits', 0) if isinstance(category_data[cat], dict) 
                     else category_data[cat] for cat in categories]
            
            # Filter out zero values
            filtered_data = [(cat, val) for cat, val in zip(categories, values) if val > 0]
            
            if not filtered_data:
                st.info("No spending data to display")
                return
            
            categories, values = zip(*filtered_data)
            
            fig = px.pie(
                values=values,
                names=categories,
                title=title,
                hole=0.4  # Makes it a donut chart
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Amount: R %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
            )
            
            fig.update_layout(
                showlegend=True,
                height=500,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating category chart: {str(e)}")
    
    @staticmethod
    def create_trend_chart(trend_data, title="Monthly Trends"):
        """Create a line chart for monthly trends"""
        if not trend_data:
            st.info("No trend data available to display")
            return
        
        try:
            # Prepare data
            months = list(trend_data.keys())
            debits = [trend_data[month].get('debits', 0) for month in months]
            credits = [trend_data[month].get('credits', 0) for month in months]
            
            # Sort by month
            sorted_data = sorted(zip(months, debits, credits))
            months, debits, credits = zip(*sorted_data) if sorted_data else ([], [], [])
            
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=months,
                y=debits,
                mode='lines+markers',
                name='Expenses',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ))
            
            fig.add_trace(go.Scatter(
                x=months,
                y=credits,
                mode='lines+markers',
                name='Income',
                line=dict(color='green', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="Month",
                yaxis_title="Amount (R)",
                hovermode='x unified',
                height=400,
                showlegend=True
            )
            
            fig.update_traces(
                hovertemplate='<b>%{fullData.name}</b><br>Amount: R %{y:,.2f}<extra></extra>'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating trend chart: {str(e)}")
    
    @staticmethod
    def display_summary_cards(summary_data):
        """Display summary information in card format"""
        if not summary_data:
            st.info("No summary data available")
            return
        
        try:
            # Create columns for metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_debits = summary_data.get('total_debits', 0)
                StreamlitUtils.create_metric_card(
                    "Total Expenses",
                    StreamlitUtils.format_currency(total_debits),
                    help_text="Total amount spent in the period"
                )
            
            with col2:
                total_credits = summary_data.get('total_credits', 0)
                StreamlitUtils.create_metric_card(
                    "Total Income",
                    StreamlitUtils.format_currency(total_credits),
                    help_text="Total amount received in the period"
                )
            
            with col3:
                net_flow = summary_data.get('net_flow', 0)
                delta_color = "normal" if net_flow >= 0 else "inverse"
                StreamlitUtils.create_metric_card(
                    "Net Flow",
                    StreamlitUtils.format_currency(net_flow),
                    help_text="Income minus expenses"
                )
            
            with col4:
                transaction_count = summary_data.get('transaction_count', 0)
                StreamlitUtils.create_metric_card(
                    "Transactions",
                    f"{transaction_count:,}",
                    help_text="Total number of transactions"
                )
                
        except Exception as e:
            st.error(f"Error displaying summary cards: {str(e)}")
    
    @staticmethod
    def format_date_range(start_date, end_date):
        """Format a date range for display"""
        try:
            if isinstance(start_date, str):
                start_date = pd.to_datetime(start_date)
            if isinstance(end_date, str):
                end_date = pd.to_datetime(end_date)
            
            return f"{start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')}"
        except Exception:
            return f"{start_date} - {end_date}"
    
    @staticmethod
    def get_color_for_category(category):
        """Get a consistent color for a spending category"""
        color_map = {
            'Groceries': '#FF6B6B',
            'Transport': '#4ECDC4',
            'Utilities': '#45B7D1',
            'Insurance': '#FFA07A',
            'Entertainment': '#98D8C8',
            'Medical': '#F7DC6F',
            'Shopping': '#BB8FCE',
            'Banking': '#85C1E9',
            'Investment': '#82E0AA',
            'Transfer': '#F8C471',
            'Other': '#D5DBDB'
        }
        return color_map.get(category, '#D5DBDB')