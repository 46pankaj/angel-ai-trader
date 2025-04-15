import pandas as pd
import streamlit as st
import ta

def add_indicators(df):
    """
    Add technical indicators (EMA short, EMA long, RSI) to the DataFrame.
    Stops execution if the DataFrame is invalid.
    """
    if df is not None and not df.empty and 'Close' in df.columns:
        df['ema_short'] = ta.trend.ema_indicator(df['Close'], window=5)
        df['ema_long'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    else:
        st.error("Error: DataFrame is empty or missing 'Close' column.")
        st.stop()
    return df

def generate_signal(row):
    """
    Generate a trading signal based on EMA and RSI indicators.
    """
    if row['ema_short'] > row['ema_long'] and row['rsi'] < 30:
        return "BUY"
    elif row['ema_short'] < row['ema_long'] and row['rsi'] > 70:
        return "SELL"
    return "HOLD"
