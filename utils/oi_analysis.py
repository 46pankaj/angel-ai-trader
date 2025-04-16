import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class OISignalType(Enum):
    BULLISH = 1
    BEARISH = 2
    NEUTRAL = 0

@dataclass
class OISignal:
    indicator: str
    value: float
    signal: OISignalType
    timestamp: pd.Timestamp

class OIAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, oi_data: Dict) -> Dict[str, OISignal]:
        """
        Analyze Open Interest data
        """
        signals = {}
        
        # PCR (Put-Call Ratio) Analysis
        if 'pcr' in oi_data:
            signals['PCR'] = self._analyze_pcr(oi_data['pcr'])
        
        # OI Change Analysis
        if 'oi_change' in oi_data:
            signals['OI_CHANGE'] = self._analyze_oi_change(oi_data['oi_change'])
        
        # Max Pain Analysis
        if 'max_pain' in oi_data:
            signals['MAX_PAIN'] = self._analyze_max_pain(oi_data['max_pain'])
        
        return signals
    
    def _analyze_pcr(self, pcr: float) -> OISignal:
        if pcr > 1.2:
            signal = OISignalType.BEARISH
        elif pcr < 0.8:
            signal = OISignalType.BULLISH
        else:
            signal = OISignalType.NEUTRAL
            
        return OISignal(
            indicator='PCR',
            value=pcr,
            signal=signal,
            timestamp=pd.Timestamp.now()
        )
    
    def _analyze_oi_change(self, oi_change: Dict) -> OISignal:
        call_oi_change = oi_change.get('call', 0)
        put_oi_change = oi_change.get('put', 0)
        
        if call_oi_change > put_oi_change * 1.5:
            signal = OISignalType.BEARISH
        elif put_oi_change > call_oi_change * 1.5:
            signal = OISignalType.BULLISH
        else:
            signal = OISignalType.NEUTRAL
            
        return OISignal(
            indicator='OI_CHANGE',
            value=put_oi_change - call_oi_change,
            signal=signal,
            timestamp=pd.Timestamp.now()
        )
    
    # Add more analysis methods as needed
