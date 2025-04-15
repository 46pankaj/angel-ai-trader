import config

def place_order(obj, signal):
    if config.TRADING_MODE == "paper":
        print(f"[PAPER] {signal} {config.SYMBOL}")
        return

    order_params = {
        "variety": "NORMAL",
        "tradingsymbol": config.SYMBOL,
        "symboltoken": "2885",  # Replace with actual token for F&O if needed
        "transactiontype": signal,
        "exchange": config.EXCHANGE,
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "quantity": config.QUANTITY
    }
    obj.placeOrder(order_params)