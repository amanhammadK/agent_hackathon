"""
AI Advisor Module
Provides AI-powered financial advice and recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIAdvisor:
    """AI-powered financial advisor"""
    
    def __init__(self):
        self.advice_templates = {
            "conservative": {
                "allocation": {"stocks": 0.4, "bonds": 0.5, "cash": 0.1},
                "description": "Conservative approach focusing on capital preservation"
            },
            "moderate": {
                "allocation": {"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
                "description": "Balanced approach with moderate growth potential"
            },
            "aggressive": {
                "allocation": {"stocks": 0.8, "bonds": 0.15, "cash": 0.05},
                "description": "Growth-focused approach for higher returns"
            }
        }
    
    def get_portfolio_recommendation(self, risk_profile: str, age: int, 
                                   investment_horizon: int) -> dict:
        """Get AI-powered portfolio recommendation"""
        try:
            # Adjust allocation based on age (rule of thumb: 100 - age = stock allocation)
            age_adjusted_stock_allocation = max(0.2, min(0.9, (100 - age) / 100))
            
            base_allocation = self.advice_templates.get(risk_profile, self.advice_templates["moderate"])
            
            # Adjust based on age and horizon
            if investment_horizon > 10:
                stock_boost = 0.1
            elif investment_horizon < 5:
                stock_boost = -0.1
            else:
                stock_boost = 0.0
            
            recommended_stocks = min(0.9, max(0.2, age_adjusted_stock_allocation + stock_boost))
            recommended_bonds = min(0.7, max(0.1, 1 - recommended_stocks - 0.05))
            recommended_cash = 1 - recommended_stocks - recommended_bonds
            
            return {
                "risk_profile": risk_profile,
                "age": age,
                "investment_horizon": investment_horizon,
                "recommended_allocation": {
                    "stocks": recommended_stocks,
                    "bonds": recommended_bonds,
                    "cash": recommended_cash
                },
                "rationale": f"Based on your {risk_profile} risk profile, age {age}, and {investment_horizon}-year horizon",
                "rebalancing_frequency": "quarterly" if risk_profile == "aggressive" else "semi-annually"
            }
        except Exception as e:
            logger.error(f"Error generating portfolio recommendation: {e}")
            return {}
    
    def analyze_market_sentiment(self, market_data: dict) -> dict:
        """Analyze market sentiment from data"""
        try:
            sentiment_score = 0
            signals = []
            
            # Simple sentiment analysis based on recent performance
            for symbol, data in market_data.items():
                if not data.empty:
                    recent_change = ((data['Close'].iloc[-1] / data['Close'].iloc[-5]) - 1) * 100
                    if recent_change > 2:
                        sentiment_score += 1
                        signals.append(f"{symbol} showing strong positive momentum")
                    elif recent_change < -2:
                        sentiment_score -= 1
                        signals.append(f"{symbol} showing negative momentum")
            
            if sentiment_score > 0:
                overall_sentiment = "bullish"
            elif sentiment_score < 0:
                overall_sentiment = "bearish"
            else:
                overall_sentiment = "neutral"
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": sentiment_score,
                "signals": signals,
                "recommendation": self._get_sentiment_recommendation(overall_sentiment)
            }
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {e}")
            return {"overall_sentiment": "neutral", "signals": []}
    
    def _get_sentiment_recommendation(self, sentiment: str) -> str:
        """Get recommendation based on sentiment"""
        recommendations = {
            "bullish": "Consider increasing equity allocation and look for growth opportunities",
            "bearish": "Consider defensive positioning and focus on quality assets",
            "neutral": "Maintain current allocation and focus on diversification"
        }
        return recommendations.get(sentiment, "Maintain balanced approach")
    
    def generate_financial_advice(self, user_profile: dict) -> dict:
        """Generate comprehensive financial advice"""
        try:
            advice = {
                "emergency_fund": self._assess_emergency_fund(user_profile),
                "debt_management": self._assess_debt_situation(user_profile),
                "investment_strategy": self._recommend_investment_strategy(user_profile),
                "tax_optimization": self._suggest_tax_strategies(user_profile),
                "insurance_needs": self._assess_insurance_needs(user_profile)
            }
            return advice
        except Exception as e:
            logger.error(f"Error generating financial advice: {e}")
            return {}
    
    def _assess_emergency_fund(self, profile: dict) -> str:
        """Assess emergency fund adequacy"""
        monthly_expenses = profile.get("monthly_expenses", 0)
        emergency_fund = profile.get("emergency_fund", 0)
        
        if emergency_fund >= monthly_expenses * 6:
            return "Your emergency fund is adequate (6+ months of expenses)"
        elif emergency_fund >= monthly_expenses * 3:
            return "Consider building your emergency fund to 6 months of expenses"
        else:
            return "Priority: Build emergency fund to at least 3-6 months of expenses"
    
    def _assess_debt_situation(self, profile: dict) -> str:
        """Assess debt situation"""
        total_debt = profile.get("total_debt", 0)
        monthly_income = profile.get("monthly_income", 1)
        
        debt_to_income = total_debt / (monthly_income * 12) if monthly_income > 0 else 0
        
        if debt_to_income > 0.4:
            return "High debt-to-income ratio. Focus on debt reduction strategies"
        elif debt_to_income > 0.2:
            return "Moderate debt levels. Consider debt consolidation or acceleration"
        else:
            return "Debt levels are manageable. Focus on preventing new debt"
    
    def _recommend_investment_strategy(self, profile: dict) -> str:
        """Recommend investment strategy"""
        age = profile.get("age", 30)
        risk_tolerance = profile.get("risk_tolerance", "moderate")
        
        if age < 35:
            return f"Focus on growth investments with {risk_tolerance} risk approach"
        elif age < 55:
            return f"Balanced growth and income strategy with {risk_tolerance} risk"
        else:
            return f"Income-focused strategy with capital preservation, {risk_tolerance} risk"
    
    def _suggest_tax_strategies(self, profile: dict) -> str:
        """Suggest tax optimization strategies"""
        income = profile.get("annual_income", 0)
        
        if income > 100000:
            return "Consider tax-advantaged accounts, tax-loss harvesting, and municipal bonds"
        elif income > 50000:
            return "Maximize 401(k) contributions and consider Roth IRA conversions"
        else:
            return "Focus on tax-advantaged retirement accounts and tax credits"
    
    def _assess_insurance_needs(self, profile: dict) -> str:
        """Assess insurance needs"""
        dependents = profile.get("dependents", 0)
        age = profile.get("age", 30)
        
        if dependents > 0:
            return "Life and disability insurance are essential with dependents"
        elif age > 40:
            return "Consider life insurance and long-term care coverage"
        else:
            return "Basic health and disability insurance should be priorities"
