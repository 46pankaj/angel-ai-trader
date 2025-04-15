import streamlit as st
import pandas as pd
from signal_generator import add_indicators, generate_signal
from data_fetcher import get_historical_data
from options_chain_analyzer import fetch_nse_option_chain
import config

st.set_page_config(layout="wide")
st.title("📈 AI Trading Dashboard")

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