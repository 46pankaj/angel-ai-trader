import talib
import numpy as np
from strategies.base import BaseStrategy

class RsiMacdStrategy(BaseStrategy):
    def __init__(self):
        self.min_rsi = 30
        self.max_rsi = 70

    def analyze(self, data):
        closes = np.array([d['close'] for d in data])
        rsi = talib.RSI(closes, timeperiod=14)[-1]
        macd, _, _ = talib.MACD(closes)

        signal = "HOLD"
        if rsi < self.min_rsi and macd[-1] > 0:
            signal = "BUY"
        elif rsi > self.max_rsi:
            signal = "SELL"
        
        return {
            'signal': signal,
            'rsi': round(rsi, 2),
            'macd': round(macd[-1], 2)
        }
