try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
import os
from urllib.parse import urlparse # New import

class Config:
    """Configuration management for the application"""

    def __init__(self):
        if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
            # Running in Streamlit context
            self.upstage_api_key = st.secrets.get("upstage", {}).get("api_key")
            self.db_password = st.secrets.get("database", {}).get("db_password")
            self.mongodb_url = st.secrets.get("database", {}).get("mongodb_url")
            
            supabase = st.secrets.get("supabase", {})
            self.supabase_client_key = supabase.get("supabase_client_key")
            self.supabase_service_role_key = supabase.get("supabase_service_role_key")
            self.supabase_password = supabase.get("supabase_password")
            self.supabase_url = supabase.get("supabase_url")
            self.supabase_direct_url = supabase.get("supabase_direct_url")
            
            # Derive Supabase project URL from the PostgreSQL URL
            if self.supabase_url:
                parsed_url = urlparse(self.supabase_url)
                # Extract project ref from hostname (e.g., postgres.rflcvvnrdulzzyqiiltl.pooler.supabase.com)
                host_parts = parsed_url.hostname.split('.')
                if len(host_parts) >= 2 and 'supabase' in host_parts:
                    # Find the index of 'supabase' and construct the URL
                    supabase_idx = host_parts.index('supabase')
                    project_ref = host_parts[supabase_idx - 1] if supabase_idx > 0 else None
                    if project_ref:
                        self.supabase_project_url = f"https://{project_ref}.supabase.co"
                    else:
                        self.supabase_project_url = None
                else:
                    self.supabase_project_url = None
            else:
                self.supabase_project_url = None

            self.cerebras_api_key = st.secrets.get("cerebras", {}).get("api_key")
        else:
            # Running outside Streamlit (e.g., in scripts)
            import toml
            from pathlib import Path
            
            # Load secrets from .streamlit/secrets.toml
            secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
            with open(secrets_path) as f:
                secrets = toml.load(f)
            
            self.upstage_api_key = secrets.get("upstage", {}).get("api_key")
            self.db_password = secrets.get("database", {}).get("db_password")
            self.mongodb_url = secrets.get("database", {}).get("mongodb_url")
            
            supabase = secrets.get("supabase", {})
            self.supabase_client_key = supabase.get("supabase_client_key")
            self.supabase_service_role_key = supabase.get("supabase_service_role_key")
            self.supabase_password = supabase.get("supabase_password")
            self.supabase_url = supabase.get("supabase_url")
            self.supabase_direct_url = supabase.get("supabase_direct_url")

            # Derive Supabase project URL from the PostgreSQL URL
            if self.supabase_url:
                parsed_url = urlparse(self.supabase_url)
                host_parts = parsed_url.hostname.split('.')
                if len(host_parts) >= 2 and 'supabase' in host_parts:
                    supabase_idx = host_parts.index('supabase')
                    project_ref = host_parts[supabase_idx - 1] if supabase_idx > 0 else None
                    if project_ref:
                        self.supabase_project_url = f"https://{project_ref}.supabase.co"
                    else:
                        self.supabase_project_url = None
                else:
                    self.supabase_project_url = None
            else:
                self.supabase_project_url = None
            
            self.cerebras_api_key = secrets.get("cerebras", {}).get("api_key")

    def validate_config(self):
        """Validate that all required secrets are set"""
        missing = []
        if not self.upstage_api_key:
            missing.append("UPSTAGE_API_KEY")
        if not self.db_password:
            missing.append("DB_PASSWORD")
        if not self.mongodb_url:
            missing.append("MONGODB_URL")
        if not self.supabase_client_key:
            missing.append("SUPABASE_CLIENT_KEY")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if not self.supabase_password:
            missing.append("SUPABASE_PASSWORD")
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_direct_url:
            missing.append("SUPABASE_DIRECT_URL")
        if not self.supabase_project_url: # New validation
            missing.append("SUPABASE_PROJECT_URL (derived)")
        if not self.cerebras_api_key:
            missing.append("CEREBRAS_API_KEY")

        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")

        return True
