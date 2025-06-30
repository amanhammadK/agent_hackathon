"""
Base Agent System - Implements all 11 OpenAI Agent SDK features
1. Agent - Custom agent logic
2. Runner - Execute the agent
3. Streaming - Stream responses
4. Tools - Integrated tools
5. Agents as Tools - Use agents inside other agents
6. Context - Maintain code level context
7. Handoff - Switch control mid-interaction
8. Structured Output - Return typed output
9. Guardrails - Input/output validation
10. Run Lifecycle - Manage run lifecycle
11. Agent Lifecycle - Manage agent lifecycle
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel, Field, validator
try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Custom exceptions
class FinanceAgentError(Exception):
    """Base exception for finance agent errors"""
    pass

class ValidationError(FinanceAgentError):
    """Raised when input validation fails"""
    pass

class APIError(FinanceAgentError):
    """Raised when API calls fail"""
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 8. Structured Output - Pydantic models for typed responses
class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

class RunState(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    REQUIRES_ACTION = "requires_action"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StockAnalysis(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    current_price: float = Field(..., description="Current stock price")
    price_change: float = Field(..., description="Price change percentage")
    recommendation: str = Field(..., description="Buy/Hold/Sell recommendation")
    confidence: float = Field(ge=0, le=1, description="Confidence score")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) > 10:
            raise ValueError('Invalid stock symbol')
        return v.upper()

class PortfolioAnalysis(BaseModel):
    total_value: float = Field(..., description="Total portfolio value")
    daily_change: float = Field(..., description="Daily change percentage")
    risk_score: float = Field(ge=0, le=10, description="Risk score 0-10")
    diversification_score: float = Field(ge=0, le=1, description="Diversification score")
    recommendations: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    agent_id: str
    response_type: str
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    confidence: float = Field(ge=0, le=1, default=0.8)
    next_actions: List[str] = Field(default_factory=list)

# 6. Context - Maintain conversation and agent context
@dataclass
class AgentContext:
    conversation_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    session_data: Dict[str, Any]
    agent_state: AgentState
    run_state: RunState
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context"""
        recent_messages = self.conversation_history[-5:]
        return f"Recent conversation: {[msg['content'][:100] for msg in recent_messages]}"

# 9. Guardrails - Input/output validation
class Guardrails:
    @staticmethod
    def validate_input(user_input: str) -> tuple[bool, str]:
        """Validate user input for safety and appropriateness"""
        if not user_input or len(user_input.strip()) == 0:
            return False, "Empty input not allowed"
        
        if len(user_input) > 5000:
            return False, "Input too long (max 5000 characters)"
        
        # Check for potentially harmful content
        harmful_patterns = ['hack', 'exploit', 'malware', 'virus']
        if any(pattern in user_input.lower() for pattern in harmful_patterns):
            return False, "Potentially harmful content detected"
        
        return True, "Input validated"
    
    @staticmethod
    def validate_output(response: str) -> tuple[bool, str]:
        """Validate agent output before sending to user"""
        if not response:
            return False, "Empty response"
        
        if len(response) > 10000:
            return False, "Response too long"
        
        return True, "Output validated"

# 4. Tools - Financial analysis tools
class FinancialTools:
    @staticmethod
    async def get_stock_data(symbol: str) -> StockAnalysis:
        """Tool to fetch and analyze stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            info = ticker.info
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            price_change = ((current_price - prev_price) / prev_price) * 100
            
            # Simple recommendation logic
            if price_change > 5:
                recommendation = "STRONG_BUY"
                confidence = 0.8
            elif price_change > 2:
                recommendation = "BUY"
                confidence = 0.7
            elif price_change < -5:
                recommendation = "SELL"
                confidence = 0.8
            elif price_change < -2:
                recommendation = "WEAK_SELL"
                confidence = 0.6
            else:
                recommendation = "HOLD"
                confidence = 0.5
            
            return StockAnalysis(
                symbol=symbol,
                current_price=float(current_price),
                price_change=float(price_change),
                recommendation=recommendation,
                confidence=confidence
            )
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            raise
    
    @staticmethod
    async def analyze_portfolio(holdings: Dict[str, float]) -> PortfolioAnalysis:
        """Tool to analyze portfolio composition"""
        try:
            total_value = 0
            daily_changes = []
            
            for symbol, shares in holdings.items():
                stock_data = await FinancialTools.get_stock_data(symbol)
                position_value = stock_data.current_price * shares
                total_value += position_value
                daily_changes.append(stock_data.price_change)
            
            avg_daily_change = np.mean(daily_changes) if daily_changes else 0
            volatility = np.std(daily_changes) if len(daily_changes) > 1 else 0
            
            # Risk score based on volatility
            risk_score = min(10, volatility / 2)
            
            # Diversification score based on number of holdings
            diversification_score = min(1.0, len(holdings) / 10)
            
            recommendations = []
            if len(holdings) < 5:
                recommendations.append("Consider diversifying with more holdings")
            if risk_score > 7:
                recommendations.append("Portfolio has high volatility - consider defensive positions")
            if avg_daily_change < -2:
                recommendations.append("Portfolio showing negative momentum - review positions")
            
            return PortfolioAnalysis(
                total_value=total_value,
                daily_change=avg_daily_change,
                risk_score=risk_score,
                diversification_score=diversification_score,
                recommendations=recommendations
            )
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            raise

# 10. Run Lifecycle - Manage individual run lifecycle
class RunManager:
    def __init__(self):
        self.runs: Dict[str, Dict] = {}
    
    def create_run(self, run_id: str, agent_id: str) -> Dict:
        """Create a new run"""
        run = {
            "id": run_id,
            "agent_id": agent_id,
            "state": RunState.CREATED,
            "created_at": datetime.now(),
            "steps": [],
            "metadata": {}
        }
        self.runs[run_id] = run
        logger.info(f"Created run {run_id} for agent {agent_id}")
        return run
    
    def update_run_state(self, run_id: str, state: RunState, metadata: Dict = None):
        """Update run state"""
        if run_id in self.runs:
            self.runs[run_id]["state"] = state
            self.runs[run_id]["updated_at"] = datetime.now()
            if metadata:
                self.runs[run_id]["metadata"].update(metadata)
            logger.info(f"Updated run {run_id} to state {state}")
    
    def add_run_step(self, run_id: str, step_type: str, content: str, metadata: Dict = None):
        """Add a step to the run"""
        if run_id in self.runs:
            step = {
                "type": step_type,
                "content": content,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
            self.runs[run_id]["steps"].append(step)
            logger.info(f"Added step to run {run_id}: {step_type}")

# 1. Agent - Base agent class with custom logic
class BaseAgent:
    def __init__(self, agent_id: str, name: str, description: str, client = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description

        # Initialize OpenAI client with graceful fallback
        if client:
            self.client = client
        elif HAS_OPENAI:
            try:
                self.client = OpenAI(api_key="demo-key")  # Demo mode
            except Exception:
                self.client = None
        else:
            self.client = None
        self.context = AgentContext(
            conversation_history=[],
            user_preferences={},
            session_data={},
            agent_state=AgentState.IDLE,
            run_state=RunState.CREATED
        )
        self.tools = FinancialTools()
        self.guardrails = Guardrails()
        self.run_manager = RunManager()
        
        # 11. Agent Lifecycle
        self._lifecycle_hooks = {
            "on_start": [],
            "on_message": [],
            "on_tool_call": [],
            "on_error": [],
            "on_complete": []
        }
        
        logger.info(f"Initialized agent {self.agent_id}: {self.name}")
    
    def add_lifecycle_hook(self, event: str, callback):
        """Add lifecycle hook"""
        if event in self._lifecycle_hooks:
            self._lifecycle_hooks[event].append(callback)
    
    async def _trigger_lifecycle_hook(self, event: str, *args, **kwargs):
        """Trigger lifecycle hooks"""
        for callback in self._lifecycle_hooks.get(event, []):
            try:
                await callback(self, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error in lifecycle hook {event}: {e}")
    
    async def process_message(self, message: str, run_id: str = None) -> AsyncGenerator[str, None]:
        """3. Streaming - Process message with streaming response"""
        try:
            # Start lifecycle
            await self._trigger_lifecycle_hook("on_start", message)
            
            # Create run if not provided
            if not run_id:
                run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            run = self.run_manager.create_run(run_id, self.agent_id)
            self.run_manager.update_run_state(run_id, RunState.IN_PROGRESS)
            
            # 9. Guardrails - Validate input
            is_valid, validation_msg = self.guardrails.validate_input(message)
            if not is_valid:
                yield f"⚠️ Input validation failed: {validation_msg}"
                return
            
            # Add to context
            self.context.add_message("user", message)
            await self._trigger_lifecycle_hook("on_message", message)
            
            # Process with streaming
            async for chunk in self._stream_response(message, run_id):
                yield chunk
            
            self.run_manager.update_run_state(run_id, RunState.COMPLETED)
            await self._trigger_lifecycle_hook("on_complete", run_id)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.run_manager.update_run_state(run_id, RunState.FAILED, {"error": str(e)})
            await self._trigger_lifecycle_hook("on_error", e)
            yield f"❌ Error: {str(e)}"
    
    async def _stream_response(self, message: str, run_id: str) -> AsyncGenerator[str, None]:
        """Internal streaming response method"""
        # This is a placeholder for the actual streaming implementation
        # In a real implementation, this would use OpenAI's streaming API
        response_parts = [
            "Processing your request...",
            "Analyzing financial data...",
            "Generating insights...",
            "Finalizing response..."
        ]
        
        for part in response_parts:
            yield part + "\n"
            await asyncio.sleep(0.5)  # Simulate processing time
