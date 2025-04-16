import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.angel_api import AngelOneAPI
from utils.sentiment import SentimentAnalyzer
from utils.technical import TechnicalAnalyzer
from utils.oi_analysis import OIAnalyzer
from backtester import Backtester
from config.config import MAX_RISK_PER_TRADE, MAX_DAILY_LOSS
import time

# Initialize API clients
@st.cache_resource
def get_angel_client():
    return AngelOneAPI()

@st.cache_resource
def get_sentiment_analyzer():
    return SentimentAnalyzer()

@st.cache_resource
def get_tech_analyzer():
    return TechnicalAnalyzer()

@st.cache_resource
def get_oi_analyzer():
    return OIAnalyzer()

@st.cache_resource
def get_backtester():
    return Backtester()

# Streamlit app
def main():
    st.title("AI Trading Platform - Angel One Integration")
    
    # Sidebar configuration
    st.sidebar.header("Trading Configuration")
    symbol = st.sidebar.selectbox("Symbol", ["NIFTY", "BANKNIFTY", "RELIANCE", "TATASTEEL"])
    exchange = st.sidebar.selectbox("Exchange", ["NSE", "BSE"])
    interval = st.sidebar.selectbox("Interval", ["ONE_MINUTE", "FIVE_MINUTE", "FIFTEEN_MINUTE", "ONE_HOUR"])
    strategy_type = st.sidebar.selectbox("Strategy Type", ["Mean Reversion", "Trend Following", "Breakout"])
    
    # Risk management
    capital = st.sidebar.number_input("Capital", min_value=1000, value=100000)
    risk_per_trade = st.sidebar.slider("Risk per Trade (%)", 0.1, 5.0, 1.0) / 100
    daily_loss_limit = st.sidebar.slider("Daily Loss Limit (%)", 1.0, 10.0, 5.0) / 100
    
    # Initialize clients
    angel_client = get_angel_client()
    sentiment_analyzer = get_sentiment_analyzer()
    tech_analyzer = get_tech_analyzer()
    oi_analyzer = get_oi_analyzer()
    backtester = get_backtester()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Market Data", "Backtesting", "Live Trading"])
    
    with tab1:
        st.header("Trading Dashboard")
        
        # Fetch market data
        market_data = angel_client.get_market_data(exchange, symbol, interval)
        if market_data:
            df = pd.DataFrame(market_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Display candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )])
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display indicators
            tech_signals = tech_analyzer.analyze(df)
            st.subheader("Technical Signals")
            tech_cols = st.columns(3)
            for i, (indicator, signal) in enumerate(tech_signals.items()):
                with tech_cols[i % 3]:
                    st.metric(
                        label=indicator,
                        value=f"{signal.value:.2f}",
                        delta="BUY" if signal.signal.name == "BUY" else "SELL" if signal.signal.name == "SELL" else "NEUTRAL"
                    )
            
            # Display sentiment analysis
            st.subheader("Sentiment Analysis")
            sentiment_data = sentiment_analyzer.get_news_sentiment(symbol)
            if not sentiment_data.empty:
                avg_sentiment = sentiment_data['score'].mean()
                st.metric(
                    label="Average Sentiment Score",
                    value=f"{avg_sentiment:.2f}",
                    delta="Bullish" if avg_sentiment > 0.5 else "Bearish" if avg_sentiment < 0.5 else "Neutral"
                )
                
                # Show recent news headlines
                st.write("Recent News Headlines")
                for _, row in sentiment_data.head(3).iterrows():
                    st.write(f"- {row['title']} ({row['sentiment']}, {row['score']:.2f})")
            else:
                st.warning("No sentiment data available")
    
    with tab2:
        st.header("Market Data Analysis")
        
        if st.button("Refresh Data"):
            st.experimental_rerun()
        
        if market_data:
            # Show raw data
            st.subheader("OHLC Data")
            st.dataframe(df)
            
            # Show technical indicators
            st.subheader("Technical Indicators")
            selected_indicators = st.multiselect(
                "Select indicators to display",
                options=list(tech_analyzer.indicators.keys()),
                default=["RSI", "MACD"]
            )
            
            for indicator in selected_indicators:
                if indicator == "RSI":
                    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
                    st.line_chart(df.set_index('timestamp')['RSI'])
                elif indicator == "MACD":
                    macd, signal, _ = talib.MACD(df['close'])
                    df['MACD'] = macd
                    df['Signal'] = signal
                    st.line_chart(df.set_index('timestamp')[['MACD', 'Signal']])
                # Add more indicators as needed
    
    with tab3:
        st.header("Strategy Backtesting")
        
        backtest_days = st.slider("Backtest Period (days)", 1, 365, 30)
        
        if st.button("Run Backtest"):
            with st.spinner("Running backtest..."):
                # Get historical data (in a real app, you'd fetch more data)
                historical_data = angel_client.get_market_data(
                    exchange, 
                    symbol, 
                    interval, 
                    from_date=(pd.Timestamp.now() - pd.Timedelta(days=backtest_days)).strftime('%Y-%m-%d')
                )
                
                if historical_data:
                    df = pd.DataFrame(historical_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Run backtest
                    strategy_config = {
                        'symbol': symbol,
                        'technical_indicators': ['RSI', 'MACD'],
                        'oi_data': {'pcr': 0.9}  # Example OI data
                    }
                    
                    results = backtester.backtest_strategy(df, strategy_config)
                    
                    # Display results
                    st.subheader("Backtest Results")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Trades", results['total_trades'])
                    col2.metric("Winning Trades", f"{results['winning_trades']} ({results['winning_trades']/results['total_trades']*100:.1f}%)" if results['total_trades'] > 0 else "0")
                    col3.metric("Profit", f"₹{results['profit']:.2f}")
                    
                    st.metric("Max Drawdown", f"₹{results['max_drawdown']:.2f}")
                    st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                    
                    # Show trade log
                    st.subheader("Trade Log")
                    st.dataframe(pd.DataFrame(results['trade_log']))
                else:
                    st.error("Failed to fetch historical data for backtesting")
    
    with tab4:
        st.header("Live Trading")
        
        st.warning("Live trading is potentially risky. Use with caution.")
        
        if st.checkbox("Enable Live Trading", False):
            trading_status = st.empty()
            pnl_chart = st.empty()
            trade_log = st.empty()
            
            # Initialize trading variables
            pnl_history = []
            trades = []
            
            # Start trading loop
            while True:
                # Get latest market data
                latest_data = angel_client.get_market_data(exchange, symbol, interval)
                if latest_data:
                    df = pd.DataFrame(latest_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    
                    # Generate signals
                    tech_signals = tech_analyzer.analyze(df)
                    sentiment = sentiment_analyzer.get_news_sentiment(symbol)
                    oi_signals = oi_analyzer.analyze({'pcr': 0.9})  # Example OI data
                    
                    # Combine signals (simplified logic)
                    buy_signal = all([
                        tech_signals['RSI'].signal.name == "BUY",
                        sentiment['score'].mean() > 0.6,
                        oi_signals['PCR'].signal.name == "BULLISH"
                    ])
                    
                    sell_signal = all([
                        tech_signals['RSI'].signal.name == "SELL",
                        sentiment['score'].mean() < 0.4,
                        oi_signals['PCR'].signal.name == "BEARISH"
                    ])
                    
                    # Execute trade (simplified example)
                    if buy_signal:
                        order_params = {
                            "symbol": symbol,
                            "exchange": exchange,
                            "transactiontype": "BUY",
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "quantity": int((capital * risk_per_trade) / df.iloc[-1]['close']),
                            "price": 0,
                            "triggerprice": 0
                        }
                        
                        order_result = angel_client.place_order(order_params)
                        if order_result and order_result.get('status') == 'success':
                            trades.append({
                                'type': 'BUY',
                                'price': df.iloc[-1]['close'],
                                'timestamp': pd.Timestamp.now()
                            })
                    
                    elif sell_signal:
                        order_params = {
                            "symbol": symbol,
                            "exchange": exchange,
                            "transactiontype": "SELL",
                            "ordertype": "MARKET",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "quantity": int((capital * risk_per_trade) / df.iloc[-1]['close']),
                            "price": 0,
                            "triggerprice": 0
                        }
                        
                        order_result = angel_client.place_order(order_params)
                        if order_result and order_result.get('status') == 'success':
                            trades.append({
                                'type': 'SELL',
                                'price': df.iloc[-1]['close'],
                                'timestamp': pd.Timestamp.now()
                            })
                    
                    # Update dashboard
                    trading_status.info(f"Monitoring {symbol} - Last Price: {df.iloc[-1]['close']}")
                    
                    if trades:
                        trade_log.dataframe(pd.DataFrame(trades))
                    
                    # Update PnL chart (simplified)
                    if len(pnl_history) > 0:
                        fig = go.Figure(data=go.Scatter(
                            x=[t['timestamp'] for t in trades],
                            y=pnl_history,
                            mode='lines+markers'
                        ))
                        pnl_chart.plotly_chart(fig, use_container_width=True)
                    
                    time.sleep(60)  # Wait 1 minute between checks
                else:
                    st.error("Failed to fetch market data")
                    break

if __name__ == "__main__":
    main()
