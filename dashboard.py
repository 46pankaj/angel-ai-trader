import streamlit as st
import pandas as pd
import yfinance as yf
import smartapi
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from signal_generator import add_indicators, generate_signal
from risk_management import check_risk_limits
from strategy_generator import generate_strategy
import os

# Load environment variables (use Streamlit secrets or local .env file)
api_key = os.getenv("ANGEL_API_KEY")
access_token = os.getenv("ANGEL_ACCESS_TOKEN")
client_id = os.getenv("ANGEL_CLIENT_ID")
client_password = os.getenv("ANGEL_PASSWORD")
twitter_api_key = os.getenv("TWITTER_API_KEY")
twitter_api_secret = os.getenv("TWITTER_API_SECRET")
twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Initialize APIs
smart_api = smartapi.SmartConnect(api_key=api_key)
smart_api.generateSession(client_id, client_password, access_token)

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
twitter_api = tweepy.API(auth)
analyzer = SentimentIntensityAnalyzer()

# Watchlist
WATCHLIST = ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS"]

# Fetch historical data
@st.cache_data
def get_historical_data(symbol):
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

# Fetch sentiment
def get_sentiment(symbol):
    try:
        tweets = twitter_api.search_tweets(q=f"{symbol} -filter:retweets", lang="en", count=50)
        sentiment_scores = [analyzer.polarity_scores(tweet.text)["compound"] for tweet in tweets]
        return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    except Exception as e:
        st.error(f"Failed to fetch sentiment for {symbol}: {str(e)}")
        return 0

# Place order (manual trigger)
def place_order(symbol, quantity, order_type, transaction_type):
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
sentiment = get_sentiment(selected_symbol)

if not df.empty:
    df = add_indicators(df, sentiment)
    if 'ema_short' in df.columns and 'ema_long' in df.columns:
        st.line_chart(df[['Close', 'ema_short', 'ema_long']])
    else:
        st.error("Indicator columns missing")

    signal = generate_signal(df.iloc[-1])
    st.markdown(f"### 📌 Latest Signal: `{signal}` (Sentiment: {sentiment:.2f})")
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
