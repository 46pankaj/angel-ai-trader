import pandas as pd
import numpy as np
import talib
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = 1
    SELL = 2
    NEUTRAL = 0

@dataclass
class TechnicalSignal:
    indicator: str
    value: float
    signal: SignalType
    timestamp: pd.Timestamp

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {
            'RSI': self._calculate_rsi,
            'MACD': self._calculate_macd,
            'BBANDS': self._calculate_bbands,
            'EMA': self._calculate_ema,
            'ADX': self._calculate_adx
        }
    
    def analyze(self, df: pd.DataFrame, indicators: List[str] = None) -> Dict[str, TechnicalSignal]:
        """
        Calculate technical indicators and generate signals
        """
        if indicators is None:
            indicators = list(self.indicators.keys())
            
        signals = {}
        for indicator in indicators:
            if indicator in self.indicators:
                signals[indicator] = self.indicators[indicator](df)
        
        return signals
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> TechnicalSignal:
        close = df['close'].values
        rsi = talib.RSI(close, timeperiod=period)[-1]
        
        if rsi < 30:
            signal = SignalType.BUY
        elif rsi > 70:
            signal = SignalType.SELL
        else:
            signal = SignalType.NEUTRAL
            
        return TechnicalSignal(
            indicator='RSI',
            value=rsi,
            signal=signal,
            timestamp=df.index[-1]
        )
    
    def _calculate_macd(self, df: pd.DataFrame) -> TechnicalSignal:
        close = df['close'].values
        macd, signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        
        if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
            signal_type = SignalType.BUY
        elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.NEUTRAL
            
        return TechnicalSignal(
            indicator='MACD',
            value=macd[-1] - signal[-1],  # MACD histogram value
            signal=signal_type,
            timestamp=df.index[-1]
        )
    
    # Add similar methods for other indicators (BBANDS, EMA, ADX, etc.)
