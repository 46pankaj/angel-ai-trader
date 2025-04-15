import ta

def add_indicators(df):
    df['ema_short'] = ta.trend.ema_indicator(df['Close'], window=5)
    df['ema_long'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['rsi'] = ta.momentum.rsi(df['Close'], window=14)
    return df

def generate_signal(row):
    if row['ema_short'] > row['ema_long'] and row['rsi'] < 30:
        return "BUY"
    elif row['ema_short'] < row['ema_long'] and row['rsi'] > 70:
        return "SELL"
    return "HOLD"