"""
Financial Planner Module
Provides financial planning and advice functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class FinancialPlanner:
    """Provides financial planning services"""
    
    def __init__(self):
        self.inflation_rate = 0.03
        self.default_return_rate = 0.07
    
    def calculate_future_value(self, present_value: float, rate: float, periods: int) -> float:
        """Calculate future value of investment"""
        try:
            return present_value * (1 + rate) ** periods
        except Exception as e:
            logger.error(f"Error calculating future value: {e}")
            return 0.0
    
    def calculate_retirement_needs(self, current_age: int, retirement_age: int, 
                                 annual_expenses: float, life_expectancy: int = 85) -> dict:
        """Calculate retirement planning needs"""
        try:
            years_to_retirement = retirement_age - current_age
            years_in_retirement = life_expectancy - retirement_age
            
            # Adjust for inflation
            future_annual_expenses = annual_expenses * (1 + self.inflation_rate) ** years_to_retirement
            
            # Calculate total needed at retirement
            total_needed = future_annual_expenses * years_in_retirement
            
            # Calculate required monthly savings
            monthly_rate = self.default_return_rate / 12
            months_to_retirement = years_to_retirement * 12
            
            if monthly_rate > 0:
                monthly_savings = total_needed * monthly_rate / ((1 + monthly_rate) ** months_to_retirement - 1)
            else:
                monthly_savings = total_needed / months_to_retirement
            
            return {
                "years_to_retirement": years_to_retirement,
                "future_annual_expenses": future_annual_expenses,
                "total_needed_at_retirement": total_needed,
                "required_monthly_savings": monthly_savings,
                "current_annual_expenses": annual_expenses
            }
        except Exception as e:
            logger.error(f"Error in retirement planning: {e}")
            return {}
    
    def create_investment_plan(self, goal_amount: float, time_horizon: int, 
                             risk_tolerance: str = "moderate") -> dict:
        """Create an investment plan for a financial goal"""
        try:
            # Adjust return rate based on risk tolerance
            rate_adjustments = {
                "conservative": -0.02,
                "moderate": 0.0,
                "aggressive": 0.02
            }
            
            expected_return = self.default_return_rate + rate_adjustments.get(risk_tolerance, 0.0)
            
            # Calculate required monthly investment
            monthly_rate = expected_return / 12
            months = time_horizon * 12
            
            if monthly_rate > 0:
                monthly_investment = goal_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
            else:
                monthly_investment = goal_amount / months
            
            return {
                "goal_amount": goal_amount,
                "time_horizon_years": time_horizon,
                "expected_annual_return": expected_return,
                "required_monthly_investment": monthly_investment,
                "risk_tolerance": risk_tolerance,
                "total_invested": monthly_investment * months,
                "investment_growth": goal_amount - (monthly_investment * months)
            }
        except Exception as e:
            logger.error(f"Error creating investment plan: {e}")
            return {}
    
    def analyze_debt_payoff(self, debt_amount: float, interest_rate: float, 
                           monthly_payment: float) -> dict:
        """Analyze debt payoff scenarios"""
        try:
            monthly_rate = interest_rate / 12
            
            if monthly_rate > 0:
                months_to_payoff = -np.log(1 - (debt_amount * monthly_rate) / monthly_payment) / np.log(1 + monthly_rate)
                total_interest = (monthly_payment * months_to_payoff) - debt_amount
            else:
                months_to_payoff = debt_amount / monthly_payment
                total_interest = 0
            
            return {
                "debt_amount": debt_amount,
                "monthly_payment": monthly_payment,
                "months_to_payoff": months_to_payoff,
                "years_to_payoff": months_to_payoff / 12,
                "total_interest_paid": total_interest,
                "total_amount_paid": debt_amount + total_interest
            }
        except Exception as e:
            logger.error(f"Error analyzing debt payoff: {e}")
            return {}
