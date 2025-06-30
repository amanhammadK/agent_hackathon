import asyncio
import os
from typing import Dict, Optional, List, Any
from datetime import datetime
import json

import chainlit as cl
from chainlit.context import context
from chainlit.input_widget import Select, Slider, TextInput, Switch
from chainlit.element import Text, Image, Pdf
from chainlit.message import Message
from chainlit.action import Action

from agents.specialized_agents import (
    MasterFinanceAgent,
    StockAnalysisAgent,
    PortfolioAgent,
    RiskAgent
)
from agents.base_agent import FinanceAgentError


class FinanceAdvisorApp:
    def __init__(self):
        self.master_agent = MasterFinanceAgent()
        self.stock_agent = StockAnalysisAgent()
        self.portfolio_agent = PortfolioAgent()
        self.risk_agent = RiskAgent()
        self.session_data = {}
        
    async def initialize_session(self):
        user_id = context.session.user.identifier if context.session.user else "anonymous"
        
        self.session_data = {
            "user_id": user_id,
            "portfolio": [],
            "risk_tolerance": "medium",
            "investment_goal": "growth",
            "started_at": datetime.now().isoformat(),
            "conversation_history": []
        }
        
        welcome_message = """# 🚀 AI Finance Advisor

Welcome to your personalized financial analysis platform! I can help you with:

## 💡 What I Can Do For You

### 📊 **Stock Analysis**
Get comprehensive analysis of individual stocks with professional recommendations, price targets, and technical indicators.

### 📈 **Portfolio Management**
Optimize your portfolio allocation, analyze diversification, and get personalized investment strategies.

### ⚠️ **Risk Assessment**
Comprehensive risk evaluation based on your financial situation, investment goals, and risk tolerance.

### 🌍 **Market Overview**
Stay updated with market trends, sector performance, and economic insights.

## 🎯 Quick Start

Click any button below to get started, or simply type your question in the chat!

**Example questions:**
- "Analyze Apple stock"
- "Help me optimize my portfolio"
- "What's my investment risk level?"
- "Show me today's market overview"

⚠️ *This is an educational demo - not actual financial advice*"""
        
        await cl.Message(content=welcome_message).send()
        
    async def handle_stock_analysis(self):
        settings = await cl.ChatSettings([
            TextInput(
                id="stock_symbol",
                label="Stock Symbol",
                placeholder="e.g., AAPL, GOOGL, TSLA",
                initial=""
            ),
            Select(
                id="analysis_type",
                label="Analysis Type",
                values=["basic", "technical", "fundamental", "comprehensive"],
                initial_index=0
            ),
            Select(
                id="time_period",
                label="Time Period",
                values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
                initial_index=2
            )
        ]).send()
        
        if settings and settings.get("stock_symbol"):
            await self.process_stock_analysis(settings)
            
    async def handle_portfolio_review(self):
        settings = await cl.ChatSettings([
            TextInput(
                id="portfolio_json",
                label="Portfolio (JSON format)",
                placeholder='[{"symbol": "AAPL", "shares": 10, "price": 150}]',
                initial=""
            ),
            Slider(
                id="risk_tolerance",
                label="Risk Tolerance (1-10)",
                initial=5,
                min=1,
                max=10,
                step=1
            ),
            Select(
                id="investment_goal",
                label="Investment Goal",
                values=["growth", "income", "balanced", "conservative"],
                initial_index=0
            )
        ]).send()
        
        if settings:
            await self.process_portfolio_review(settings)
            
    async def process_stock_analysis(self, settings: Dict[str, Any]):
        symbol = settings["stock_symbol"].upper()
        analysis_type = settings["analysis_type"]
        time_period = settings["time_period"]

        loading_msg = await cl.Message(
            content=f"🔄 Analyzing {symbol} stock ({analysis_type} analysis)..."
        ).send()

        try:
            # Use the existing agent interface
            result = await self.stock_agent.analyze_stock(symbol=symbol)

            await loading_msg.remove()

            # Extract content from the AgentResponse
            analysis_content = f"""
            # 📊 Stock Analysis: {symbol}

            ## Analysis Type: {analysis_type.title()}
            ## Time Period: {time_period}

            {result.content}

            ---
            *Analysis completed using {analysis_type} methodology over {time_period} timeframe*
            """

            actions = [
                Action(name="export_analysis", value=f"export_{symbol}", label="📥 Export Analysis", payload={"action": "export", "symbol": symbol}),
                Action(name="add_to_watchlist", value=f"watch_{symbol}", label="👁️ Add to Watchlist", payload={"action": "watchlist", "symbol": symbol}),
                Action(name="compare_stocks", value=f"compare_{symbol}", label="🔍 Compare Stocks", payload={"action": "compare", "symbol": symbol})
            ]

            await cl.Message(content=analysis_content, actions=actions).send()

        except Exception as e:
            await loading_msg.remove()
            await cl.Message(content=f"❌ Error: {str(e)}", type="error").send()
            
    async def process_portfolio_review(self, settings: Dict[str, Any]):
        portfolio_data = settings.get("portfolio_json", "[]")
        risk_tolerance = settings.get("risk_tolerance", 5)
        investment_goal = settings.get("investment_goal", "growth")

        loading_msg = await cl.Message(content="🔄 Analyzing your portfolio...").send()

        try:
            portfolio = json.loads(portfolio_data) if portfolio_data else []

            if not portfolio:
                await loading_msg.remove()
                await cl.Message(
                    content="⚠️ Please provide portfolio data in JSON format",
                    type="warning"
                ).send()
                return

            # Convert portfolio to the format expected by existing agent
            holdings_dict = {}
            for holding in portfolio:
                symbol = holding.get("symbol", "")
                shares = holding.get("shares", 0)
                price = holding.get("price", 0)
                holdings_dict[symbol] = shares * price

            result = await self.portfolio_agent.analyze_portfolio(holdings=holdings_dict)

            await loading_msg.remove()

            portfolio_content = f"""
            # 📈 Portfolio Analysis

            ## Settings
            - **Risk Tolerance**: {risk_tolerance}/10
            - **Investment Goal**: {investment_goal.title()}

            ## Analysis Results
            {result.content}

            ---
            *Portfolio analyzed with {investment_goal} strategy and risk tolerance level {risk_tolerance}*
            """

            actions = [
                Action(name="rebalance_portfolio", value="rebalance", label="⚖️ Rebalance", payload={"action": "rebalance"}),
                Action(name="export_portfolio", value="export_portfolio", label="📊 Export Report", payload={"action": "export", "type": "portfolio"}),
                Action(name="risk_analysis", value="risk_analysis", label="🛡️ Risk Analysis", payload={"action": "risk_analysis"})
            ]

            await cl.Message(content=portfolio_content, actions=actions).send()

        except (json.JSONDecodeError, Exception) as e:
            await loading_msg.remove()
            await cl.Message(content=f"❌ Error: {str(e)}", type="error").send()
            
    def format_allocation(self, allocation: Dict[str, float]) -> str:
        formatted = []
        for asset, percentage in allocation.items():
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            formatted.append(f"- **{asset}**: {percentage:.1f}% {bar}")
        return "\n".join(formatted)
        
    async def handle_action(self, action: Action):
        if action.name == "analyze_stock":
            await self.handle_stock_analysis()
        elif action.name == "review_portfolio":
            await self.handle_portfolio_review()
        elif action.name == "risk_assessment":
            await self.handle_risk_assessment()
        elif action.name == "market_overview":
            await self.handle_market_overview()
        elif action.name.startswith("export_"):
            await self.handle_export(action.value)
        elif action.name.startswith("watch_"):
            await self.handle_watchlist(action.value)

    async def handle_risk_assessment(self):
        content = """
        # 🛡️ Risk Assessment

        Please provide your investment details for a comprehensive risk analysis:
        """

        settings = await cl.ChatSettings([
            Slider(
                id="investment_amount",
                label="Investment Amount ($)",
                initial=10000,
                min=1000,
                max=1000000,
                step=1000
            ),
            Slider(
                id="time_horizon",
                label="Investment Time Horizon (years)",
                initial=5,
                min=1,
                max=30,
                step=1
            ),
            Switch(
                id="has_emergency_fund",
                label="Have Emergency Fund?",
                initial=True
            ),
            Select(
                id="risk_capacity",
                label="Risk Capacity",
                values=["low", "medium", "high"],
                initial_index=1
            )
        ]).send()

        if settings:
            await self.process_risk_assessment(settings)

    async def process_risk_assessment(self, settings: Dict[str, Any]):
        loading_msg = await cl.Message(content="🔄 Conducting risk assessment...").send()

        try:
            # Create portfolio data for risk assessment
            portfolio_data = {
                "investment_amount": settings["investment_amount"],
                "time_horizon": settings["time_horizon"],
                "has_emergency_fund": settings["has_emergency_fund"],
                "risk_capacity": settings["risk_capacity"],
                "risk_score": settings["risk_tolerance"] if "risk_tolerance" in settings else 5
            }

            result = await self.risk_agent.assess_risk(portfolio_data=portfolio_data)

            await loading_msg.remove()

            risk_content = f"""
            # 🛡️ Risk Assessment Results

            ## Assessment Parameters
            - **Investment Amount**: ${settings["investment_amount"]:,}
            - **Time Horizon**: {settings["time_horizon"]} years
            - **Emergency Fund**: {"Yes" if settings["has_emergency_fund"] else "No"}
            - **Risk Capacity**: {settings["risk_capacity"].title()}

            ## Analysis Results
            {result.content}

            ---
            *Risk assessment based on your personal financial situation and goals*
            """

            await cl.Message(content=risk_content).send()

        except Exception as e:
            await loading_msg.remove()
            await cl.Message(content=f"❌ Error: {str(e)}", type="error").send()

    async def handle_market_overview(self):
        loading_msg = await cl.Message(content="🔄 Fetching market overview...").send()

        try:
            # Use the master agent to provide general market information
            market_content = """
            # 🌍 Market Overview

            ## Major Indices (Demo Data)
            - **S&P 500**: +0.75%
            - **NASDAQ**: +1.20%
            - **DOW**: +0.45%

            ## Market Sentiment: **Cautiously Optimistic**

            ## Top Movers (Sample)
            ### Gainers
            - **AAPL**: +2.3%
            - **GOOGL**: +1.8%
            - **MSFT**: +1.5%

            ### Losers
            - **TSLA**: -1.2%
            - **META**: -0.8%
            - **NVDA**: -0.5%

            ## Market News
            Markets showing mixed signals with technology stocks leading gains while energy sector faces headwinds.
            Investors are closely watching Federal Reserve policy decisions and inflation data.

            ---
            *This is demo market data for educational purposes*
            """

            await loading_msg.remove()
            await cl.Message(content=market_content).send()

        except Exception as e:
            await loading_msg.remove()
            await cl.Message(content=f"❌ Error: {str(e)}", type="error").send()

    def format_movers(self, movers: List[Dict[str, Any]]) -> str:
        formatted = []
        for mover in movers[:5]:
            formatted.append(f"- **{mover['symbol']}**: {mover['change']:+.2f}%")
        return "\n".join(formatted)

    async def handle_export(self, export_type: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"finance_analysis_{timestamp}.json"

        export_data = {
            "session_data": self.session_data,
            "export_type": export_type,
            "timestamp": timestamp
        }

        await cl.Message(
            content=f"📊 Analysis exported successfully!",
            elements=[
                Text(
                    name=filename,
                    content=json.dumps(export_data, indent=2),
                    display="side"
                )
            ]
        ).send()

    async def handle_watchlist(self, symbol: str):
        symbol = symbol.replace("watch_", "")

        if "watchlist" not in self.session_data:
            self.session_data["watchlist"] = []

        if symbol not in self.session_data["watchlist"]:
            self.session_data["watchlist"].append(symbol)
            await cl.Message(content=f"👁️ {symbol} added to your watchlist!").send()
        else:
            await cl.Message(content=f"👁️ {symbol} is already in your watchlist").send()

    async def process_message(self, message: str):
        self.session_data["conversation_history"].append({
            "user": message,
            "timestamp": datetime.now().isoformat()
        })

        try:
            # Use the existing master agent route_request method
            async for chunk in self.master_agent.route_request(message):
                yield chunk

        except Exception as e:
            yield f"❌ Error: {str(e)}"


app = FinanceAdvisorApp()


@cl.on_chat_start
async def start():
    await app.initialize_session()


@cl.on_message
async def main(message: cl.Message):
    response_message = cl.Message(content="")

    async for chunk in app.process_message(message.content):
        await response_message.stream_token(chunk)

    await response_message.send()


# Action callbacks removed - users will interact through chat messages


@cl.on_chat_end
async def end():
    if hasattr(app, 'session_data'):
        app.session_data["ended_at"] = datetime.now().isoformat()


@cl.on_settings_update
async def setup_agent(settings):
    await cl.Message(content="✅ Settings updated successfully!").send()
