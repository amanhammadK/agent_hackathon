"""
Configuration Module
Contains application configuration and constants
"""

# Application Configuration
APP_TITLE = "🤖 AI Finance Advisor"
APP_ICON = "🤖"
LAYOUT = "wide"

# Default Portfolio Configuration
DEFAULT_PORTFOLIO = {
    "AAPL": 0.25,
    "GOOGL": 0.20,
    "MSFT": 0.20,
    "TSLA": 0.15,
    "NVDA": 0.20
}

# Risk-free rate for calculations
RISK_FREE_RATE = 0.02

# Default stock symbols for analysis
DEFAULT_STOCKS = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN", "META"]

# Market indices
MARKET_INDICES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI", 
    "NASDAQ": "^IXIC"
}

# Color schemes for charts
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff7f0e",
    "info": "#17a2b8"
}

# Chart configuration
CHART_CONFIG = {
    "height": 400,
    "theme": "plotly_white",
    "font_family": "Arial"
}
