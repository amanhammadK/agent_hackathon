"""
Risk Manager Module
Handles risk assessment and management
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class RiskManager:
    """Manages portfolio and investment risk"""
    
    def __init__(self):
        self.risk_free_rate = 0.02
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Value at Risk"""
        try:
            return np.percentile(returns, confidence_level * 100)
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return 0.0
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.05) -> float:
        """Calculate Conditional Value at Risk"""
        try:
            var = self.calculate_var(returns, confidence_level)
            return returns[returns <= var].mean()
        except Exception as e:
            logger.error(f"Error calculating CVaR: {e}")
            return 0.0
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns.mean() - self.risk_free_rate / 252
            return excess_returns / returns.std() * np.sqrt(252)
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    def assess_portfolio_risk(self, portfolio_returns: pd.Series) -> dict:
        """Comprehensive portfolio risk assessment"""
        try:
            return {
                "var_95": self.calculate_var(portfolio_returns, 0.05),
                "cvar_95": self.calculate_cvar(portfolio_returns, 0.05),
                "sharpe_ratio": self.calculate_sharpe_ratio(portfolio_returns),
                "volatility": portfolio_returns.std() * np.sqrt(252),
                "max_drawdown": self.calculate_max_drawdown(portfolio_returns)
            }
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return {}
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            return drawdown.min()
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
