def run_strategy():
    from ai.sentiment_analysis import get_sentiment
    from ai.technicals import get_technicals
    from ai.open_interest import analyze_oi
    from broker.angel import place_trade

    sentiment = get_sentiment()
    technicals = get_technicals()
    oi = analyze_oi()

    if sentiment == "positive" and technicals['rsi'] < 30 and oi['trend'] == "long_buildup":
        place_trade("BUY")
    elif sentiment == "negative" and technicals['rsi'] > 70 and oi['trend'] == "short_buildup":
        place_trade("SELL")
