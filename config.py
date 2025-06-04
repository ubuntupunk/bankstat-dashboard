# config.py
import streamlit as st
import os

class Config:
    """Configuration management for the Streamlit app using Streamlit secrets or environment variables"""

    def __init__(self):
        self.upstage_api_key = self._get_secret("UPSTAGE_API_KEY", ["upstage", "api_key"])
        self.db_username = self._get_secret("DB_USERNAME", ["database", "db_username"])
        self.db_password = self._get_secret("DB_PASSWORD", ["database", "db_password"])
        self.mongodb_url = self._get_secret("MONGODB_URL", ["database", "mongodb_url"])
        self.auth_client_id = self._get_secret("AUTH_CLIENT_ID", ["auth", "client_id"])
        self.auth_api_key = self._get_secret("AUTH_API_KEY", ["auth", "api_key"])
        self.auth_client_secret = self._get_secret("AUTH_CLIENT_SECRET", ["auth", "client_secret"])
        self.auth_url = self._get_secret("AUTH_URL", ["auth", "auth_url"])
        self.auth_server_metadata_url = self._get_secret("AUTH_SERVER_METADATA_URL", ["auth", "server_metadata_url"])
        self.auth_redirect_uri = self._get_secret("AUTH_REDIRECT_URI", ["auth", "redirect_uri"])
        self.auth_cookie_secret = self._get_secret("AUTH_COOKIE_SECRET", ["auth", "cookie_secret"])

    def _get_secret(self, env_var_name, secrets_path):
        """Helper to get secret from environment variable or st.secrets"""
        # Try environment variable first
        if env_var_name in os.environ:
            return os.environ[env_var_name]
        
        # Fallback to st.secrets
        secret_value = st.secrets
        for key in secrets_path:
            if isinstance(secret_value, dict) and key in secret_value:
                secret_value = secret_value[key]
            else:
                return None # Secret not found in st.secrets
        return secret_value

    def validate_config(self):
        """Validate that all required secrets are set"""
        missing = []
        if not self.upstage_api_key:
            missing.append("UPSTAGE_API_KEY")
        if not self.db_username:
            missing.append("DB_USERNAME")
        if not self.db_password:
            missing.append("DB_PASSWORD")
        if not self.mongodb_url:
            missing.append("MONGODB_URL")
        if not self.auth_client_id:
            missing.append("AUTH_CLIENT_ID")
        if not self.auth_api_key:
            missing.append("AUTH_API_KEY")
        if not self.auth_client_secret:
            missing.append("AUTH_CLIENT_SECRET")
        if not self.auth_url:
            missing.append("AUTH_URL")
        if not self.auth_server_metadata_url:
            missing.append("AUTH_SERVER_METADATA_URL")
        if not self.auth_redirect_uri:
            missing.append("AUTH_REDIRECT_URI")
        if not self.auth_cookie_secret:
            missing.append("AUTH_COOKIE_SECRET")

        return missing
