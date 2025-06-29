"""
Stock Analyzer Module
Provides stock analysis functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """Analyzes individual stocks"""
    
    def __init__(self):
        pass
    
    def analyze_stock(self, data: pd.DataFrame, symbol: str) -> dict:
        """Analyze a single stock"""
        if data.empty:
            return {"error": "No data available"}
        
        try:
            current_price = data['Close'].iloc[-1]
            daily_change = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100
            
            # Calculate technical indicators
            sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
            
            # Volatility
            volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100
            
            return {
                "symbol": symbol,
                "current_price": current_price,
                "daily_change": daily_change,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "volatility": volatility,
                "recommendation": "BUY" if daily_change > 0 else "HOLD"
            }
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {"error": str(e)}
    
    def compare_stocks(self, stocks_data: dict) -> dict:
        """Compare multiple stocks"""
        comparison = {}
        for symbol, data in stocks_data.items():
            comparison[symbol] = self.analyze_stock(data, symbol)
        return comparison
