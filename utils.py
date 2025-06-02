# utils.py
import pandas as pd
import streamlit as st
from datetime import datetime
import json
import tempfile
import os

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
    def format_currency(amount):
        """Format amount as South African Rand"""
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