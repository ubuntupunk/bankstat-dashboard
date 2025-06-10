# config.py
import streamlit as st

class Config:
    """Configuration management for the Streamlit app using Streamlit secrets"""

    def __init__(self):
        self.upstage_api_key = st.secrets["upstage"]["api_key"]
        self.db_password = st.secrets["database"]["db_password"]
        self.mongodb_url = st.secrets["database"]["mongodb_url"]
        self.cerebras_api_key = st.secrets["cerebras"]["api_key"]

    def validate_config(self):
        """Validate that all required secrets are set"""
        missing = []
        if not self.upstage_api_key:
            missing.append("UPSTAGE_API_KEY")
        if not self.db_password:
            missing.append("DB_PASSWORD")
        if not self.mongodb_url:
            missing.append("MONGODB_URL")
        if not self.cerebras_api_key:
            missing.append("CEREBRAS_API_KEY")

        return missing
