import streamlit as st
import pandas as pd
import yfinance as yf
from signal_generator import add_indicators, generate_signal
from risk_management import check_risk_limits
from strategy_generator import generate_strategy

st.set_page_config(page_title="Angel AI Trader", layout="wide")
st.title("📈 Angel One AI Options Trading Dashboard")

# Sidebar toggles
st.sidebar.header("⚙️ Settings")
trading_enabled = st.sidebar.toggle("Auto Trading", value=False)

# Display historical price data and indicators
st.subheader("📊 Stock Chart")
df = get_historical_data()
df = add_indicators(df)
st.line_chart(df[['Close', 'ema_short', 'ema_long']])

signal = generate_signal(df.iloc[-1])
st.markdown(f"### 📌 Latest Signal: `{signal}`")

# Show Options Chain
st.subheader("📘 Options Chain (NIFTY)")
df_ce, df_pe, expiry = fetch_nse_option_chain()
st.caption(f"Expiry Date: {expiry}")
col1, col2 = st.columns(2)
col1.dataframe(df_ce[['strikePrice', 'openInterest', 'changeinOpenInterest', 'impliedVolatility']].head(10))
col2.dataframe(df_pe[['strikePrice', 'openInterest', 'changeinOpenInterest', 'impliedVolatility']].head(10))

# Trading toggle
if trading_enabled:
    st.success("✅ Auto trading is ENABLED")
else:
    st.warning("⚠️ Auto trading is DISABLED")

st.sidebar.markdown("---")
st.sidebar.code("SYMBOL: " + config.SYMBOL)
