"""
Data Fetcher Module
Handles fetching financial data from various sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataFetcher:
    """Fetches financial data from various sources"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data for a given symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_multiple_stocks(self, symbols: list, period: str = "1y") -> dict:
        """Fetch data for multiple stocks"""
        data = {}
        for symbol in symbols:
            data[symbol] = self.get_stock_data(symbol, period)
        return data
    
    def get_market_data(self) -> dict:
        """Get general market data"""
        market_symbols = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        return self.get_multiple_stocks(market_symbols, "1mo")
