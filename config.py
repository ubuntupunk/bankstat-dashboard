# config.py
import os
from dotenv import load_dotenv

class Config:
    """Configuration management for the Streamlit app"""
    
    def __init__(self):
        load_dotenv()
        self.upstage_api_key = os.getenv("UPSTAGE_API_KEY")
        self.db_password = os.getenv("DB_PASSWORD")
        self.mongodb_url = os.getenv("MONGODB_URL")
        
    def validate_config(self):
        """Validate that all required environment variables are set"""
        missing = []
        if not self.upstage_api_key:
            missing.append("UPSTAGE_API_KEY")
        if not self.db_password:
            missing.append("DB_PASSWORD")
        if not self.mongodb_url:
            missing.append("MONGODB_URL")
        
        return missing