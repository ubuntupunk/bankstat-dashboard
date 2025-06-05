import streamlit as st
from propelauth_py import init_base_auth
from propelauth_py.errors import UnauthorizedException # Explicitly import

# Replace me
auth_url = st.secrets["auth"]["auth_url"]
integration_api_key = st.secrets["auth"]["api_key"]

class Auth:
    def __init__(self, auth_url, integration_api_key):
        self.auth = init_base_auth(auth_url, integration_api_key)
        self.auth_url = auth_url
        self.integration_api_key = integration_api_key
        self.access_token = None

    def get_user(self, user_id):
        try:
            if self.access_token is None:
                return self.force_refresh_user(user_id)
            return self.auth.validate_access_token_and_get_user(f"Bearer {self.access_token}")
        except UnauthorizedException:
            return self.force_refresh_user(user_id)
            
    def force_refresh_user(self, user_id):
        access_token_response = self.auth.create_access_token(user_id, 10)
        self.access_token = access_token_response.access_token
        return self.auth.validate_access_token_and_get_user(f"Bearer {self.access_token}")
    
    def get_account_url(self):
        return self.auth_url + "/account"

    def log_out(self, user_id):
        self.auth.logout_all_user_sessions(user_id)
        self.access_token = None
        st.logout()


# Instantiate the Auth class
auth = Auth(
    auth_url,
    integration_api_key
)
