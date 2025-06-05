import streamlit as st
from propelauth_py import init_base_auth, UnauthorizedException
from config import Config # Import the Config class
import requests # Import requests for HTTP calls
import jwt # For decoding JWT
import secrets # For generating secure random strings
from urllib.parse import urlencode # For URL encoding parameters

class Auth:
    def __init__(self, auth_url, integration_api_key, client_id, client_secret, redirect_uri):
        self.auth = init_base_auth(auth_url, integration_api_key)
        self.auth_url = auth_url
        self.integration_api_key = integration_api_key
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    def get_user(self, user_id):
        print(f"DEBUG: get_user called with user_id: {user_id}")
        try:
            if self.access_token is None:
                return self.force_refresh_user(user_id)
            return self.auth.validate_access_token_and_get_user(f"Bearer {self.access_token}")
        except UnauthorizedException:
            print(f"DEBUG: UnauthorizedException in get_user for user_id: {user_id}. Forcing refresh.")
            return self.force_refresh_user(user_id)
            
    def force_refresh_user(self, user_id):
        print(f"DEBUG: force_refresh_user called with user_id: {user_id}")
        access_token_response = self.auth.create_access_token(user_id, 10)
        print(f"DEBUG: access_token_response: {access_token_response}")
        self.access_token = access_token_response.access_token
        return self.auth.validate_access_token_and_get_user(f"Bearer {self.access_token}")
    
    def get_account_url(self):
        return self.auth_url + "/account"
    
    def log_out(self, user_id):
        self.auth.logout_all_user_sessions(user_id)
        self.access_token = None
        st.session_state.clear() # Clear Streamlit session state on logout
        st.experimental_rerun() # Rerun to reflect logout

    def get_login_url(self):
        """Constructs the full OAuth2 authorization URL with state parameter."""
        state = secrets.token_urlsafe(32) # Generate a random state
        st.session_state["oauth_state"] = state # Store state in session for verification
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile", # Standard OIDC scopes
            "state": state, # Include state parameter
        }
        return f"{self.auth_url}/propelauth/oauth/authorize?{urlencode(params)}"

    def exchange_code_for_user_id(self, code):
        """Exchanges authorization code for tokens and extracts user_id."""
        token_endpoint = f"{self.auth_url}/propelauth/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(token_endpoint, headers=headers, data=data)
            response.raise_for_status() # Raise an exception for HTTP errors
            tokens = response.json()
            
            if "id_token" in tokens:
                decoded_id_token = jwt.decode(tokens["id_token"], options={"verify_signature": False})
                return decoded_id_token.get("sub") # 'sub' is the user ID
            else:
                st.error("ID Token not found in response.")
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Error exchanging code for tokens: {e}")
            return None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return None

def init_auth():
    config = Config() # Instantiate Config
    missing_secrets = config.validate_config()
    if missing_secrets:
        raise ValueError(f"Missing required configuration secrets: {', '.join(missing_secrets)}. Please ensure they are set as environment variables or in .streamlit/secrets.toml")

    auth_url = config.auth_url
    integration_api_key = config.auth_api_key
    client_id = config.auth_client_id
    client_secret = config.auth_client_secret
    redirect_uri = config.auth_redirect_uri
    return Auth(auth_url, integration_api_key, client_id, client_secret, redirect_uri)

auth = init_auth()
