import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from utils.technical import TechnicalAnalyzer
from utils.oi_analysis import OIAnalyzer
from utils.sentiment import SentimentAnalyzer

class Backtester:
    def __init__(self):
        self.tech_analyzer = TechnicalAnalyzer()
        self.oi_analyzer = OIAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def backtest_strategy(self, df: pd.DataFrame, strategy_config: Dict) -> Dict:
        """
        Backtest a trading strategy
        
        Args:
            df: DataFrame with OHLC data
            strategy_config: Dictionary with strategy parameters
            
        Returns:
            Dictionary with backtest results
        """
        results = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'profit': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'trade_log': []
        }
        
        position = None
        entry_price = None
        max_profit = 0
        drawdown = 0
        
        for i in range(1, len(df)):
            current_data = df.iloc[:i]
            
            # Generate signals
            tech_signals = self.tech_analyzer.analyze(current_data, strategy_config.get('technical_indicators'))
            oi_signals = self.oi_analyzer.analyze(strategy_config.get('oi_data', {}))
            sentiment = self.sentiment_analyzer.get_news_sentiment(strategy_config['symbol'])
            
            # Combine signals based on strategy rules
            signal = self._generate_signal(tech_signals, oi_signals, sentiment, strategy_config)
            
            # Execute trades based on signal
            if signal == 'BUY' and position != 'LONG':
                if position == 'SHORT':
                    # Exit short position
                    pnl = entry_price - current_data.iloc[-1]['close']
                    results['profit'] += pnl
                    results['trade_log'].append({
                        'type': 'SHORT_EXIT',
                        'price': current_data.iloc[-1]['close'],
                        'pnl': pnl,
                        'timestamp': current_data.index[-1]
                    })
                    results['total_trades'] += 1
                    if pnl > 0:
                        results['winning_trades'] += 1
                    else:
                        results['losing_trades'] += 1
                
                # Enter long position
                position = 'LONG'
                entry_price = current_data.iloc[-1]['close']
                results['trade_log'].append({
                    'type': 'LONG_ENTRY',
                    'price': entry_price,
                    'timestamp': current_data.index[-1]
                })
            
            elif signal == 'SELL' and position != 'SHORT':
                if position == 'LONG':
                    # Exit long position
                    pnl = current_data.iloc[-1]['close'] - entry_price
                    results['profit'] += pnl
                    results['trade_log'].append({
                        'type': 'LONG_EXIT',
                        'price': current_data.iloc[-1]['close'],
                        'pnl': pnl,
                        'timestamp': current_data.index[-1]
                    })
                    results['total_trades'] += 1
                    if pnl > 0:
                        results['winning_trades'] += 1
                    else:
                        results['losing_trades'] += 1
                
                # Enter short position
                position = 'SHORT'
                entry_price = current_data.iloc[-1]['close']
                results['trade_log'].append({
                    'type': 'SHORT_ENTRY',
                    'price': entry_price,
                    'timestamp': current_data.index[-1]
                })
            
            # Calculate drawdown
            if position == 'LONG':
                current_pnl = current_data.iloc[-1]['close'] - entry_price
            elif position == 'SHORT':
                current_pnl = entry_price - current_data.iloc[-1]['close']
            else:
                current_pnl = 0
                
            if current_pnl > max_profit:
                max_profit = current_pnl
            else:
                drawdown = max(drawdown, max_profit - current_pnl)
        
        results['max_drawdown'] = drawdown
        
        # Calculate Sharpe ratio (simplified)
        if results['total_trades'] > 0:
            avg_return = results['profit'] / results['total_trades']
            returns = [trade['pnl'] for trade in results['trade_log'] if 'pnl' in trade]
            std_dev = np.std(returns) if returns else 0
            results['sharpe_ratio'] = avg_return / std_dev if std_dev != 0 else 0
        
        return results
    
    def _generate_signal(self, tech_signals, oi_signals, sentiment, strategy_config):
        """
        Combine signals based on strategy rules
        """
        # Simple example: Buy if RSI < 30 and PCR < 0.8 and sentiment is bullish
        buy_conditions = all([
            tech_signals.get('RSI', {}).get('signal') == 'BUY',
            oi_signals.get('PCR', {}).get('signal') == 'BULLISH',
            sentiment['score'].mean() > 0.6  # Average sentiment score > 0.6
        ])
        
        sell_conditions = all([
            tech_signals.get('RSI', {}).get('signal') == 'SELL',
            oi_signals.get('PCR', {}).get('signal') == 'BEARISH',
            sentiment['score'].mean() < 0.4  # Average sentiment score < 0.4
        ])
        
        if buy_conditions:
            return 'BUY'
        elif sell_conditions:
            return 'SELL'
        else:
            return 'HOLD'
