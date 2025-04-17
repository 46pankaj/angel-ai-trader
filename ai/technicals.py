import yfinance as yf
import pandas_ta as ta
import numpy as np

def get_technicals(symbol="^NSEI"):
    df = yf.download(symbol, period="1mo", interval="1d")

    df.ta.rsi(length=14, append=True)
    df.ta.macd(append=True)
    df.ta.supertrend(length=10, multiplier=3.0, append=True)

    latest = df.iloc[-1]
    return {
        "rsi": round(latest['RSI_14'], 2),
        "macd": round(latest['MACD_12_26_9'], 2),
        "supertrend": "buy" if latest['SUPERT_10_3.0'] < latest['Close'] else "sell"
    }
