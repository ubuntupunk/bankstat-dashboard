import streamlit as st
import os
# Removed urllib.parse as it's no longer needed for URL derivation

class Config:
    """Configuration management for the application using Streamlit secrets."""

    def __init__(self):
        # Directly access st.secrets
        self.upstage_api_key = st.secrets.get("upstage", {}).get("api_key")
        self.db_password = st.secrets.get("database", {}).get("db_password")
        self.mongodb_url = st.secrets.get("database", {}).get("mongodb_url")
        
        supabase_secrets = st.secrets.get("supabase", {})
        self.supabase_api_key = supabase_secrets.get("supabase_api_key")
        self.supabase_service_role_key = supabase_secrets.get("supabase_service_role_key")
        self.supabase_password = supabase_secrets.get("supabase_password")
        self.supabase_url = supabase_secrets.get("supabase_url")
        self.supabase_direct_url = supabase_secrets.get("supabase_direct_url")
        
        # No longer deriving supabase_project_url; will use supabase_url directly for st.connection
        self.supabase_project_url = None # Explicitly set to None or remove if not used elsewhere

        self.cerebras_api_key = st.secrets.get("cerebras", {}).get("api_key")
        self.upstage_api_key = st.secrets["upstage"]["api_key"]
        self.db_password = st.secrets["database"]["db_password"]
        self.mongodb_url = st.secrets["database"]["mongodb_url"]
        self.cerebras_api_key = st.secrets["cerebras"]["api_key"]
        self.supabase_direct_url = st.secrets["supabase"]["supabase_direct_url"]
        self.supabase_url = st.secrets["supabase"]["supabase_url"] # Add supabase_url
        self.supabase_api_key = st.secrets["supabase"]["supabase_api_key"] # Add supabase_api_key
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
        if not self.supabase_url: # Validate supabase_url
            missing.append("SUPABASE_URL")
        if not self.supabase_api_key: # Validate supabase_api_key
            missing.append("SUPABASE_API_KEY")

        return missing
