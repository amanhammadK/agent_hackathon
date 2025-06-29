"""
Specialized Financial Agents
Demonstrates Agents as Tools (Feature 5) and Handoff (Feature 7)
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base_agent import BaseAgent, AgentResponse, StockAnalysis, PortfolioAnalysis, AgentState, RunState
import logging

logger = logging.getLogger(__name__)

# Stock Analysis Agent
class StockAnalysisAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(
            agent_id="stock_analyst",
            name="Stock Analysis Agent",
            description="Specialized in stock analysis and recommendations",
            client=client
        )
    
    async def analyze_stock(self, symbol: str) -> AgentResponse:
        """Analyze a specific stock"""
        try:
            self.context.agent_state = AgentState.RUNNING
            
            # Use tool to get stock data
            stock_data = await self.tools.get_stock_data(symbol)
            
            # Generate detailed analysis
            analysis_content = f"""
📊 **Stock Analysis for {stock_data.symbol}**

💰 **Current Price:** ${stock_data.current_price:.2f}
📈 **Daily Change:** {stock_data.price_change:.2f}%
🎯 **Recommendation:** {stock_data.recommendation}
🔍 **Confidence:** {stock_data.confidence:.0%}

**Analysis:**
"""
            
            if stock_data.price_change > 5:
                analysis_content += "Strong upward momentum detected. Consider buying on any dips."
            elif stock_data.price_change > 2:
                analysis_content += "Positive momentum. Good entry point for long-term investors."
            elif stock_data.price_change < -5:
                analysis_content += "Significant decline. Consider selling or wait for reversal signals."
            elif stock_data.price_change < -2:
                analysis_content += "Negative momentum. Monitor closely for further declines."
            else:
                analysis_content += "Sideways movement. Wait for clearer directional signals."
            
            self.context.agent_state = AgentState.COMPLETED
            
            return AgentResponse(
                agent_id=self.agent_id,
                response_type="stock_analysis",
                content=analysis_content,
                structured_data=stock_data.dict(),
                confidence=stock_data.confidence
            )
            
        except Exception as e:
            logger.error(f"Stock analysis error: {e}")
            self.context.agent_state = AgentState.ERROR
            raise

# Portfolio Management Agent
class PortfolioAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(
            agent_id="portfolio_manager",
            name="Portfolio Management Agent", 
            description="Specialized in portfolio analysis and optimization",
            client=client
        )
    
    async def analyze_portfolio(self, holdings: Dict[str, float]) -> AgentResponse:
        """Analyze portfolio composition and performance"""
        try:
            self.context.agent_state = AgentState.RUNNING
            
            # Use tool to analyze portfolio
            portfolio_data = await self.tools.analyze_portfolio(holdings)
            
            analysis_content = f"""
📋 **Portfolio Analysis**

💼 **Total Value:** ${portfolio_data.total_value:,.2f}
📊 **Daily Change:** {portfolio_data.daily_change:.2f}%
⚠️ **Risk Score:** {portfolio_data.risk_score:.1f}/10
🎯 **Diversification:** {portfolio_data.diversification_score:.0%}

**Recommendations:**
"""
            
            for rec in portfolio_data.recommendations:
                analysis_content += f"• {rec}\n"
            
            if not portfolio_data.recommendations:
                analysis_content += "• Portfolio looks well-balanced. Continue monitoring."
            
            self.context.agent_state = AgentState.COMPLETED
            
            return AgentResponse(
                agent_id=self.agent_id,
                response_type="portfolio_analysis",
                content=analysis_content,
                structured_data=portfolio_data.dict(),
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Portfolio analysis error: {e}")
            self.context.agent_state = AgentState.ERROR
            raise

# Risk Management Agent
class RiskAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(
            agent_id="risk_manager",
            name="Risk Management Agent",
            description="Specialized in risk assessment and management",
            client=client
        )
    
    async def assess_risk(self, portfolio_data: Dict) -> AgentResponse:
        """Assess portfolio risk and provide recommendations"""
        try:
            self.context.agent_state = AgentState.RUNNING
            
            risk_score = portfolio_data.get('risk_score', 5)
            diversification = portfolio_data.get('diversification_score', 0.5)
            
            risk_content = f"""
🛡️ **Risk Assessment**

📊 **Overall Risk Level:** {"HIGH" if risk_score > 7 else "MEDIUM" if risk_score > 4 else "LOW"}
🎯 **Risk Score:** {risk_score:.1f}/10
📈 **Diversification:** {diversification:.0%}

**Risk Factors:**
"""
            
            if risk_score > 7:
                risk_content += "• High volatility detected - consider defensive positions\n"
                risk_content += "• Reduce position sizes in volatile assets\n"
            elif risk_score > 4:
                risk_content += "• Moderate risk level - maintain current strategy\n"
                risk_content += "• Monitor for increased volatility\n"
            else:
                risk_content += "• Low risk profile - consider growth opportunities\n"
                risk_content += "• Portfolio may be too conservative\n"
            
            if diversification < 0.5:
                risk_content += "• Insufficient diversification - add more asset classes\n"
            
            self.context.agent_state = AgentState.COMPLETED
            
            return AgentResponse(
                agent_id=self.agent_id,
                response_type="risk_assessment",
                content=risk_content,
                structured_data={"risk_score": risk_score, "diversification": diversification},
                confidence=0.9
            )
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            self.context.agent_state = AgentState.ERROR
            raise

# 7. Handoff - Master Agent that coordinates other agents
class MasterFinanceAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(
            agent_id="master_finance",
            name="Master Finance Agent",
            description="Coordinates all financial analysis agents",
            client=client
        )
        
        # 5. Agents as Tools - Initialize specialized agents
        self.stock_agent = StockAnalysisAgent(client)
        self.portfolio_agent = PortfolioAgent(client)
        self.risk_agent = RiskAgent(client)
        
        self.agents = {
            "stock": self.stock_agent,
            "portfolio": self.portfolio_agent,
            "risk": self.risk_agent
        }
    
    async def route_request(self, message: str, context: Dict = None) -> AsyncGenerator[str, None]:
        """Route requests to appropriate specialized agents"""
        message_lower = message.lower()
        
        try:
            # Determine which agent(s) to use
            if any(word in message_lower for word in ['stock', 'ticker', 'symbol', 'price']):
                yield "🔄 **Routing to Stock Analysis Agent...**\n\n"
                
                # Extract stock symbol
                words = message.upper().split()
                symbol = None
                for word in words:
                    if len(word) <= 5 and word.isalpha():
                        symbol = word
                        break
                
                if symbol:
                    response = await self.stock_agent.analyze_stock(symbol)
                    yield response.content
                else:
                    yield "❌ Please provide a valid stock symbol (e.g., AAPL, GOOGL)"
            
            elif any(word in message_lower for word in ['portfolio', 'holdings', 'allocation']):
                yield "🔄 **Routing to Portfolio Management Agent...**\n\n"
                
                # Mock portfolio for demo
                demo_portfolio = {
                    "AAPL": 10,
                    "GOOGL": 5,
                    "MSFT": 8,
                    "TSLA": 3
                }
                
                portfolio_response = await self.portfolio_agent.analyze_portfolio(demo_portfolio)
                yield portfolio_response.content
                
                # 7. Handoff - Pass to risk agent for additional analysis
                yield "\n🔄 **Handing off to Risk Management Agent...**\n\n"
                
                risk_response = await self.risk_agent.assess_risk(portfolio_response.structured_data)
                yield risk_response.content
            
            elif any(word in message_lower for word in ['risk', 'volatility', 'safety']):
                yield "🔄 **Routing to Risk Management Agent...**\n\n"
                
                # Mock risk data for demo
                risk_data = {"risk_score": 6.5, "diversification_score": 0.7}
                response = await self.risk_agent.assess_risk(risk_data)
                yield response.content
            
            else:
                # General financial advice
                yield """
🤖 **AI Finance Advisor**

I can help you with:

📊 **Stock Analysis** - "Analyze AAPL stock"
📋 **Portfolio Review** - "Analyze my portfolio"
🛡️ **Risk Assessment** - "What's my portfolio risk?"

**Available Commands:**
• Stock analysis: "analyze [SYMBOL]"
• Portfolio review: "review portfolio"
• Risk assessment: "assess risk"

What would you like to explore?
                """
        
        except Exception as e:
            logger.error(f"Routing error: {e}")
            yield f"❌ Error processing request: {str(e)}"

# 2. Runner - Execute agents with proper lifecycle management
class AgentRunner:
    def __init__(self):
        self.active_runs: Dict[str, Dict] = {}
        self.master_agent = MasterFinanceAgent()
    
    async def execute_agent(self, agent_id: str, message: str, context: Dict = None) -> AsyncGenerator[str, None]:
        """Execute an agent with full lifecycle management"""
        run_id = f"run_{agent_id}_{len(self.active_runs)}"
        
        try:
            # Start run
            self.active_runs[run_id] = {
                "agent_id": agent_id,
                "status": "running",
                "start_time": asyncio.get_event_loop().time(),
                "context": context or {}
            }
            
            # Route to master agent
            async for chunk in self.master_agent.route_request(message, context):
                yield chunk
            
            # Complete run
            self.active_runs[run_id]["status"] = "completed"
            self.active_runs[run_id]["end_time"] = asyncio.get_event_loop().time()
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            self.active_runs[run_id]["status"] = "failed"
            self.active_runs[run_id]["error"] = str(e)
            yield f"❌ Execution failed: {str(e)}"
    
    def get_run_status(self, run_id: str) -> Dict:
        """Get status of a specific run"""
        return self.active_runs.get(run_id, {"status": "not_found"})
    
    def list_active_runs(self) -> List[Dict]:
        """List all active runs"""
        return [
            {"run_id": run_id, **run_data}
            for run_id, run_data in self.active_runs.items()
            if run_data["status"] == "running"
        ]
