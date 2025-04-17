from smartapi import SmartConnect
import streamlit as st

def login_user(client_id, password, totp=None):
    """Secure authentication with Angel One"""
    try:
        api = SmartConnect(api_key="YOUR_API_KEY")  # Replace with your API key
        session = api.generateSession(client_id, password, totp)
        
        if session:
            st.session_state['api'] = api
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False
