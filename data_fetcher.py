import yfinance as yf

def get_historical_data(symbol="RELIANCE.NS"):
    return yf.download(symbol, period="5d", interval="5m")