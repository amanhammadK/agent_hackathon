"""
Portfolio Analyzer Module
Provides comprehensive portfolio analysis including risk metrics, performance tracking, and optimization.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta

# Try to import optional packages
try:
    from scipy.optimize import minimize
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

class PortfolioAnalyzer:
    """Class for portfolio analysis and optimization"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
    
    def calculate_portfolio_metrics(self, returns, weights=None):
        """Calculate key portfolio metrics"""
        if weights is None:
            weights = np.array([1/len(returns.columns)] * len(returns.columns))
        
        # Portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Metrics
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + portfolio_returns.mean()) ** 252 - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
        
        # Drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_returns': portfolio_returns
        }
    
    def optimize_portfolio(self, returns, method='sharpe'):
        """Optimize portfolio using different methods"""
        n_assets = len(returns.columns)

        if not HAS_SCIPY:
            # Return equal weights if scipy is not available
            st.warning("Portfolio optimization requires scipy. Using equal weights.")
            return np.array([1/n_assets] * n_assets)

        def portfolio_stats(weights, returns):
            portfolio_return = np.sum(returns.mean() * weights) * 252
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            return portfolio_return, portfolio_vol

        def neg_sharpe(weights, returns):
            p_ret, p_vol = portfolio_stats(weights, returns)
            return -(p_ret - self.risk_free_rate) / p_vol

        def portfolio_volatility(weights, returns):
            return portfolio_stats(weights, returns)[1]

        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))

        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)

        try:
            if method == 'sharpe':
                result = minimize(neg_sharpe, x0, args=(returns,), method='SLSQP',
                                bounds=bounds, constraints=constraints)
            elif method == 'min_vol':
                result = minimize(portfolio_volatility, x0, args=(returns,), method='SLSQP',
                                bounds=bounds, constraints=constraints)

            return result.x if result.success else x0
        except Exception as e:
            st.warning(f"Portfolio optimization failed: {str(e)}. Using equal weights.")
            return x0
    
    def calculate_var_cvar(self, returns, confidence_level=0.05):
        """Calculate Value at Risk and Conditional Value at Risk"""
        sorted_returns = np.sort(returns)
        index = int(confidence_level * len(sorted_returns))
        
        var = sorted_returns[index]
        cvar = sorted_returns[:index].mean()
        
        return var, cvar
    
    def monte_carlo_simulation(self, returns, weights, num_simulations=1000, time_horizon=252):
        """Run Monte Carlo simulation for portfolio"""
        mean_returns = returns.mean().values
        cov_matrix = returns.cov().values
        
        # Portfolio statistics
        portfolio_mean = np.dot(weights, mean_returns)
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_std = np.sqrt(portfolio_var)
        
        # Simulate
        simulated_returns = np.random.normal(
            portfolio_mean, portfolio_std, (num_simulations, time_horizon)
        )
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + simulated_returns, axis=1)
        final_values = cumulative_returns[:, -1]
        
        return {
            'simulations': cumulative_returns,
            'final_values': final_values,
            'percentiles': {
                '5th': np.percentile(final_values, 5),
                '50th': np.percentile(final_values, 50),
                '95th': np.percentile(final_values, 95)
            }
        }
    
    def correlation_analysis(self, returns):
        """Analyze correlations between assets"""
        correlation_matrix = returns.corr()
        
        # Create heatmap
        fig = px.imshow(
            correlation_matrix,
            title="Asset Correlation Matrix",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        
        return fig, correlation_matrix
    
    def efficient_frontier(self, returns, num_portfolios=100):
        """Calculate efficient frontier"""
        n_assets = len(returns.columns)
        results = np.zeros((3, num_portfolios))
        
        # Generate random weights
        np.random.seed(42)
        weights_array = np.zeros((num_portfolios, n_assets))
        
        for i in range(num_portfolios):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            weights_array[i] = weights
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(returns.mean() * weights) * 252
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            
            results[0, i] = portfolio_return
            results[1, i] = portfolio_vol
            results[2, i] = sharpe
        
        return results, weights_array
    
    def sector_allocation_analysis(self, portfolio_data):
        """Analyze portfolio allocation by sector"""
        # This would typically use real sector data
        # For demo purposes, we'll use mock sector assignments
        sector_mapping = {
            'AAPL': 'Technology',
            'GOOGL': 'Technology',
            'MSFT': 'Technology',
            'AMZN': 'Consumer Discretionary',
            'TSLA': 'Consumer Discretionary',
            'JPM': 'Financial Services',
            'JNJ': 'Healthcare',
            'SPY': 'Diversified ETF',
            'BND': 'Bonds',
            'GLD': 'Commodities'
        }
        
        sector_allocation = {}
        for symbol, weight in portfolio_data.items():
            sector = sector_mapping.get(symbol, 'Other')
            sector_allocation[sector] = sector_allocation.get(sector, 0) + weight
        
        return sector_allocation
    
    def rebalancing_analysis(self, current_weights, target_weights, portfolio_value):
        """Analyze portfolio rebalancing needs"""
        rebalancing_data = []
        
        for asset in current_weights.keys():
            current_value = current_weights[asset] * portfolio_value / 100
            target_value = target_weights.get(asset, 0) * portfolio_value / 100
            difference = target_value - current_value
            
            rebalancing_data.append({
                'Asset': asset,
                'Current Weight': current_weights[asset],
                'Target Weight': target_weights.get(asset, 0),
                'Current Value': current_value,
                'Target Value': target_value,
                'Rebalancing Amount': difference,
                'Action': 'Buy' if difference > 0 else 'Sell' if difference < 0 else 'Hold'
            })
        
        return pd.DataFrame(rebalancing_data)
    
    def performance_attribution(self, returns, weights, benchmark_returns):
        """Perform performance attribution analysis"""
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Calculate attribution
        active_returns = portfolio_returns - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(252)
        information_ratio = active_returns.mean() * 252 / tracking_error if tracking_error != 0 else 0
        
        # Beta calculation
        covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance if benchmark_variance != 0 else 1
        
        # Alpha calculation
        portfolio_annual_return = portfolio_returns.mean() * 252
        benchmark_annual_return = benchmark_returns.mean() * 252
        alpha = portfolio_annual_return - (self.risk_free_rate + beta * (benchmark_annual_return - self.risk_free_rate))
        
        return {
            'alpha': alpha,
            'beta': beta,
            'tracking_error': tracking_error,
            'information_ratio': information_ratio,
            'active_returns': active_returns
        }
