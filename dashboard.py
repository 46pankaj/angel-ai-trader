import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from signal_generator import add_indicators, generate_signal
from risk_management import check_risk_limits
from strategy_generator import generate_strategy
import os
import pyotp

# Replace with your real secret key from Angel One
api_key = st.secrets["ANGEL_API_KEY"]
client_id = st.secrets["ANGEL_CLIENT_ID"]
client_password = st.secrets["ANGEL_PASSWORD"]
totp_secret = st.secrets["ANGEL_TOTP_SECRET"]
access_token = st.secrets["ANGEL_ACCESS_TOKEN"]

# 🔑 Generate TOTP and create session
totp = pyotp.TOTP(totp_secret).now()
smart_api = SmartConnect(api_key=api_key)
session_data = smart_api.generateSession(client_id, client_password, totp)

# Watchlist
WATCHLIST = ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"]

# Fetch historical data from Angel One API
@st.cache_data
def get_historical_data(symbol):
    try:
        # Fetch token for symbol (NSE example)
        symbol_token = smart_api.getScriptCode("NSE", symbol)
        
        if not symbol_token:
            st.warning(f"No token found for {symbol}")
            return pd.DataFrame()

        # Fetch candle data for the symbol
        params = {
            "exchange": "NSE",
            "symboltoken": symbol_token,
            "interval": "ONE_DAY",
            "fromdate": "2024-04-01 09:15",
            "todate": "2024-04-15 15:30"
        }

        response = smart_api.getCandleData(params)

        if response['status']:
            # Convert response data to DataFrame
            candles = response['data']
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')  # Convert timestamp to readable format
            return df
        else:
            st.warning(f"Failed to fetch data for {symbol}: {response.get('message')}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()

# Place order (manual trigger)
def place_order(symbol, quantity, order_type, transaction_type):
    try:
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": "YOUR_SYMBOL_TOKEN",  # Replace with correct symbol token
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
            st.line_chart(df[['close', 'ema_short', 'ema_long']])
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
