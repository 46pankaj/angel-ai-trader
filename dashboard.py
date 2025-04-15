import streamlit as st
import pandas as pd
import yfinance as yf
import smartapi
from signal_generator import add_indicators, generate_signal
from risk_management import check_risk_limits
from strategy_generator import generate_strategy
import os

# Load environment variables (managed via Streamlit Secrets)
api_key = os.getenv("ANGEL_API_KEY")
access_token = os.getenv("ANGEL_ACCESS_TOKEN")
client_id = os.getenv("ANGEL_CLIENT_ID")
client_password = os.getenv("ANGEL_PASSWORD")

# Initialize SmartAPI
smart_api = smartapi.SmartConnect(api_key=api_key)
smart_api.generateSession(client_id, client_password, access_token)

# Watchlist
WATCHLIST = ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"]

# Fetch historical data
@st.cache_data
def get_historical_data(symbol):
    """
    Fetch historical stock data using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d", interval="1h")
        if df.empty:
            st.warning(f"No data available for {symbol}")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Failed to fetch data for {symbol}: {str(e)}")
        return pd.DataFrame()

# Place order (manual trigger)
def place_order(symbol, quantity, order_type, transaction_type):
    """
    Place a buy or sell order via SmartAPI.
    """
    try:
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": "YOUR_SYMBOL_TOKEN",  # Replace with actual token from Scrip Master
            "exchange": "NSE",
            "ordertype": order_type,
            "producttype": "FUTURE" if "FUT" in symbol else "OPTION",
            "duration": "DAY",
            "quantity": quantity,
            "transactiontype": transaction_type,
            "price": "0" if order_type == "MARKET" else "YOUR_PRICE"
        }
        order_id = smart_api.placeOrder(order_params)
        st.success(f"Order placed: {order_id}")
        return order_id
    except Exception as e:
        st.error(f"Order placement failed: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Angel AI Auto Trader", layout="wide")
st.title("📈 Angel One AI Auto Trading Dashboard")

st.sidebar.header("⚙️ Settings")
trading_enabled = st.sidebar.toggle("Auto Trading", value=False)
selected_symbol = st.sidebar.selectbox("Select Symbol", WATCHLIST)

# Fetch and process data
df = get_historical_data(selected_symbol)

if not df.empty:
    try:
        df = add_indicators(df)
        if 'ema_short' in df.columns and 'ema_long' in df.columns:
            st.line_chart(df[['Close', 'ema_short', 'ema_long']])
        else:
            st.error("Indicator columns (ema_short, ema_long) missing")
    except Exception as e:
        st.error(f"Error adding indicators: {e}")

    signal = generate_signal(df.iloc[-1])
    st.markdown(f"### 📌 Latest Signal: `{signal}`")
    strategy = generate_strategy(signal)
    st.markdown(f"### 📋 Strategy: `{strategy}`")
else:
    st.warning("No historical data available")

# Trading controls
if trading_enabled and not df.empty:
    st.success("✅ Auto Trading is ENABLED")
    risk_status = check_risk_limits(df.iloc[-1])
    if risk_status:
        if st.button("Execute Buy Order"):
            place_order(selected_symbol + "24JANFUT", 50, "MARKET", "BUY")
        if st.button("Execute Sell Order"):
            place_order(selected_symbol + "24JANFUT", 50, "MARKET", "SELL")
    else:
        st.error("Risk limits exceeded")
else:
    st.warning("⚠️ Auto Trading is DISABLED")

# Placeholder for options chain
st.subheader("📘 Options Chain (NIFTY)")
st.warning("Options chain fetching not implemented")
