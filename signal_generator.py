import pandas as pd
import ta

def add_indicators(df):
    if df is not None and not df.empty and 'Close' in df.columns:
        df['ema_short'] = ta.trend.ema_indicator(df['Close'], window=5)
        df['ema_long'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    else:
        raise ValueError("DataFrame is empty or missing 'Close' column.")
    return df

def generate_signal(row):
    if row['ema_short'] > row['ema_long'] and row['rsi'] < 30:
        return "BUY"
    elif row['ema_short'] < row['ema_long'] and row['rsi'] > 70:
        return "SELL"
    return "HOLD"
