import streamlit as st
from core.auth import login_user
from core.order_manager import OrderManager
from strategies.rsi_macd import RsiMacdStrategy

st.set_page_config(layout="wide")

def main():
    st.title("Production Trading Dashboard")
    
    # Authentication
    if 'user' not in st.session_state:
        with st.sidebar.form("login"):
            st.write("Angel One Login")
            client_id = st.text_input("Client ID")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = login_user(client_id, password)
                st.session_state.user = user

    # Trading Interface
    if 'user' in st.session_state:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("Live Chart")
            # Add live plotting here
        
        with col2:
            st.subheader("Execute Trade")
            symbol = st.selectbox("Symbol", ["NIFTY", "BANKNIFTY"])
            strategy = RsiMacdStrategy()
            if st.button("Run Analysis"):
                signal = strategy.analyze_latest()
                st.write(f"Signal: **{signal['signal']}**")
                
                if signal['signal'] != "HOLD":
                    if st.button("Execute"):
                        OrderManager().execute_order(signal)

if __name__ == "__main__":
    main()
