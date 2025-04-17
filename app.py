import streamlit as st
from core.auth import login_user  # Now this import will work

def main():
    st.title("Trading Dashboard")
    
    # Authentication
    if 'api' not in st.session_state:
        with st.sidebar:
            st.header("Login")
            client_id = st.text_input("Client ID")
            password = st.text_input("Password", type="password")
            totp = st.text_input("TOTP (if 2FA enabled)")
            
            if st.button("Login"):
                if login_user(client_id, password, totp):
                    st.success("Logged in successfully")
                else:
                    st.error("Invalid credentials")

if __name__ == "__main__":
    main()
