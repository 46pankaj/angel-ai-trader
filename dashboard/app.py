import streamlit as st
import sys
import os

# Add 'ai' module to path if necessary
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai'))

from sentiment_analysis import get_sentiment
from technicals import get_technicals
from open_interest import analyze_oi


# Streamlit header and title
st.title("📈 AI Trading Platform Dashboard")
st.write("System is active. Monitoring live market data...")

# Show real-time sentiment
st.header("📰 Market Sentiment")
sentiment = get_sentiment()
st.write(f"Sentiment: {sentiment}")

# Show technical indicators
st.header("📊 Technical Analysis")
technical_data = get_technicals()
st.write(f"RSI: {technical_data['rsi']}, MACD: {technical_data['macd']}, Supertrend: {technical_data['supertrend']}")

# Show open interest analysis
st.header("📈 Open Interest Analysis")
oi_data = analyze_oi()
st.write(f"PCR: {oi_data['pcr']}, OI Trend: {oi_data['trend']}")

# Button for triggering trade (manual for now)
if st.button("Trigger Buy/Sell Trade"):
    # Here you can call a function to place a trade or simulate it
    st.write("Trade triggered based on strategy!")
