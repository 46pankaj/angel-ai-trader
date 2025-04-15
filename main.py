from login import angel_login
from data_fetcher import get_historical_data
from signal_generator import add_indicators, generate_signal
from trader import place_order
import time

obj, jwt, feed_token = angel_login()

while True:
    df = get_historical_data()
    df = add_indicators(df)
    signal = generate_signal(df.iloc[-1])

    if signal in ["BUY", "SELL"]:
        place_order(obj, signal)

    time.sleep(300)  # wait 5 minutes