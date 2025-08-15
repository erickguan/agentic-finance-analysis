"""
Analysis Agent for Financial Analysis

This agent performs comprehensive multi-perspective analysis including technical,
fundamental, and sentiment analysis using the research data provided.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage

from ..tools.analysis_tools import analysis_tools
from ..utils.config import config

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Analysis Agent responsible for comprehensive financial analysis.
    
    This agent performs multi-perspective analysis including:
    - Technical Analysis: Price trends, indicators, momentum
    - Fundamental Analysis: Financial ratios, valuation metrics
    - Sentiment Analysis: News sentiment, market perception
    - Risk Assessment: Volatility, financial health, market risk
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.OPENAI_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.2,  # Slightly higher for analysis insights
            api_key=config.OPENAI_API_KEY
        )
        
        # Get analysis tools
        self.tools = analysis_tools.get_langchain_tools()
        
        # Create the agent prompt
        self.prompt = self._create_prompt()
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create the executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=12,
            return_intermediate_steps=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the analysis agent."""
        
        system_message = """You are a Senior Financial Analyst expert in comprehensive stock analysis.

Your role is to perform detailed multi-perspective analysis using research data to generate actionable investment insights.

ANALYSIS FRAMEWORK:

1. TECHNICAL ANALYSIS:
   - Price trends and momentum indicators
   - Moving averages and trend signals
   - RSI for overbought/oversold conditions  
   - Volatility analysis and risk assessment
   - Support/resistance levels

2. FUNDAMENTAL ANALYSIS:
   - Financial ratios and valuation metrics
   - P/E, P/B, debt-to-equity analysis
   - Financial health and stability
   - Growth indicators and profitability
   - Industry and peer comparisons

3. SENTIMENT ANALYSIS:
   - News sentiment and market perception
   - Analyst recommendation trends
   - Market timing considerations
   - Event impact assessment

4. RISK ASSESSMENT:
   - Volatility and market risk
   - Financial leverage and debt risk
   - Industry and sector risk factors
   - Overall risk-reward profile

ANALYSIS METHODOLOGY:
- Use quantitative tools for objective analysis
- Integrate multiple perspectives for comprehensive view
- Provide clear interpretations of metrics
- Generate actionable insights and recommendations
- Assess confidence levels and data quality
- Identify key risks and opportunities

OUTPUT REQUIREMENTS:
- Structure findings by analysis type
- Provide specific numerical metrics
- Include clear interpretations and implications
- Generate investment thesis and recommendations
- Assess confidence levels for each conclusion
- Highlight key risks and catalysts

Be thorough, objective, and data-driven in your analysis."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    async def analyze_stock(self, research_data: Dict[str, Any], analysis_focus: List[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive stock analysis using research data.
        
        Args:
            research_data: Data gathered by research agent
            analysis_focus: List of analysis areas to focus on
            
        Returns:
            Dict containing structured analysis results
        """
        try:
            symbol = research_data.get("symbol", "Unknown")
            
            if analysis_focus is None:
                analysis_focus = ["comprehensive"]
            
            logger.info(f"Starting analysis for {symbol} with focus: {analysis_focus}")
            
            # Create analysis query
            focus_text = ", ".join(analysis_focus)
            query = f"""Perform comprehensive financial analysis for {symbol} using the provided research data.

Focus areas: {focus_text}

Research Data Summary:
- Symbol: {symbol}
- Research Findings: {research_data.get('research_findings', 'Not available')}

Conduct detailed analysis including:
1. Technical analysis of price data and indicators
2. Fundamental analysis of financial metrics and ratios
3. Sentiment analysis of news and market perception
4. Risk assessment and overall investment evaluation

Provide specific metrics, clear interpretations, and actionable recommendations."""
            
            # Execute the analysis
            result = await self.executor.ainvoke({
                "input": query,
                "chat_history": []
            })
            
            # Structure the response
            analysis_response = {
                "symbol": symbol,
                "analysis_focus": analysis_focus,
                "research_data_used": research_data,
                "analysis_findings": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "metrics_calculated": self._extract_metrics_from_steps(result.get("intermediate_steps", [])),
                "confidence_assessment": self._assess_analysis_confidence(result, research_data)
            }
            
            logger.info(f"Completed analysis for {symbol}")
            return analysis_response
            
        except Exception as e:
            logger.error(f"Error in analysis for {symbol}: {e}")
            return {
                "symbol": research_data.get("symbol", "Unknown"),
                "error": str(e),
                "analysis_focus": analysis_focus or [],
                "research_data_used": research_data
            }
    
    def analyze_stock_sync(self, research_data: Dict[str, Any], analysis_focus: List[str] = None) -> Dict[str, Any]:
        """
        Synchronous version of stock analysis.
        
        Args:
            research_data: Data gathered by research agent
            analysis_focus: List of analysis areas to focus on
            
        Returns:
            Dict containing structured analysis results
        """
        try:
            symbol = research_data.get("symbol", "Unknown")
            
            if analysis_focus is None:
                analysis_focus = ["comprehensive"]
            
            logger.info(f"Starting sync analysis for {symbol} with focus: {analysis_focus}")
            
            # Create analysis query
            focus_text = ", ".join(analysis_focus)
            query = f"""Perform comprehensive financial analysis for {symbol} using the provided research data.

Focus areas: {focus_text}

Research Data Summary:
- Symbol: {symbol}
- Research Findings: {research_data.get('research_findings', 'Not available')}

Conduct detailed analysis including:
1. Technical analysis of price data and indicators
2. Fundamental analysis of financial metrics and ratios  
3. Sentiment analysis of news and market perception
4. Risk assessment and overall investment evaluation

Provide specific metrics, clear interpretations, and actionable recommendations."""
            
            # Execute the analysis
            result = self.executor.invoke({
                "input": query,
                "chat_history": []
            })
            
            # Structure the response
            analysis_response = {
                "symbol": symbol,
                "analysis_focus": analysis_focus,
                "research_data_used": research_data,
                "analysis_findings": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "metrics_calculated": self._extract_metrics_from_steps(result.get("intermediate_steps", [])),
                "confidence_assessment": self._assess_analysis_confidence(result, research_data)
            }
            
            logger.info(f"Completed sync analysis for {symbol}")
            return analysis_response
            
        except Exception as e:
            logger.error(f"Error in sync analysis for {symbol}: {e}")
            return {
                "symbol": research_data.get("symbol", "Unknown"),
                "error": str(e),
                "analysis_focus": analysis_focus or [],
                "research_data_used": research_data
            }
    
    def quick_analysis(self, symbol: str, data_snippet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quick analysis with limited data.
        
        Args:
            symbol: Stock symbol
            data_snippet: Limited data for quick analysis
            
        Returns:
            Dict containing quick analysis results
        """
        try:
            logger.info(f"Starting quick analysis for {symbol}")
            
            query = f"""Perform quick analysis for {symbol} using available data:

Data: {data_snippet}

Focus on key insights that can be derived from the available information.
Provide essential metrics and basic assessment."""
            
            result = self.executor.invoke({
                "input": query,
                "chat_history": []
            })
            
            return {
                "symbol": symbol,
                "analysis_type": "quick",
                "findings": result.get("output"),
                "confidence_level": "limited_data"
            }
            
        except Exception as e:
            logger.error(f"Error in quick analysis for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "analysis_type": "quick"
            }
    
    def _extract_metrics_from_steps(self, intermediate_steps: List) -> Dict[str, Any]:
        """Extract calculated metrics from intermediate steps."""
        metrics = {
            "technical_metrics": [],
            "fundamental_metrics": [],
            "sentiment_metrics": [],
            "risk_metrics": []
        }
        
        for step in intermediate_steps:
            if len(step) >= 2:
                action, observation = step[0], step[1]
                tool_name = getattr(action, 'tool', None)
                
                # Categorize metrics by tool type
                if tool_name in ['calculate_moving_averages', 'calculate_rsi', 'calculate_volatility']:
                    metrics["technical_metrics"].append({
                        "tool": tool_name,
                        "result": observation
                    })
                elif tool_name in ['calculate_financial_ratios']:
                    metrics["fundamental_metrics"].append({
                        "tool": tool_name,
                        "result": observation
                    })
                elif tool_name in ['analyze_news_sentiment']:
                    metrics["sentiment_metrics"].append({
                        "tool": tool_name,
                        "result": observation
                    })
                elif tool_name in ['calculate_risk_metrics']:
                    metrics["risk_metrics"].append({
                        "tool": tool_name,
                        "result": observation
                    })
        
        return metrics
    
    def _assess_analysis_confidence(self, result: Dict[str, Any], research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess confidence level of the analysis."""
        confidence_assessment = {
            "overall_confidence": "medium",
            "data_quality_score": 0.5,
            "analysis_completeness": 0.5,
            "limiting_factors": []
        }
        
        # Check research data quality
        research_quality = research_data.get("data_quality_assessment", {})
        if research_quality:
            data_completeness = research_quality.get("completeness_score", 0.5)
            confidence_assessment["data_quality_score"] = data_completeness
            
            if data_completeness < 0.3:
                confidence_assessment["limiting_factors"].append("Low data completeness")
            elif data_completeness > 0.8:
                confidence_assessment["overall_confidence"] = "high"
        
        # Check analysis execution
        intermediate_steps = result.get("intermediate_steps", [])
        successful_tools = 0
        total_tools = len(intermediate_steps)
        
        for step in intermediate_steps:
            if len(step) >= 2:
                observation = step[1]
                if not (isinstance(observation, str) and "error" in observation.lower()):
                    successful_tools += 1
        
        if total_tools > 0:
            analysis_completeness = successful_tools / total_tools
            confidence_assessment["analysis_completeness"] = analysis_completeness
            
            if analysis_completeness < 0.5:
                confidence_assessment["limiting_factors"].append("Multiple analysis tool failures")
                confidence_assessment["overall_confidence"] = "low"
            elif analysis_completeness > 0.8 and confidence_assessment["data_quality_score"] > 0.6:
                confidence_assessment["overall_confidence"] = "high"
        
        return confidence_assessment
    
    def get_available_tools(self) -> List[str]:
        """Get list of available analysis tools."""
        return [tool.name for tool in self.tools]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the analysis agent configuration."""
        return {
            "agent_type": "Analysis Agent",
            "model": self.model_name,
            "available_tools": self.get_available_tools(),
            "max_iterations": self.executor.max_iterations,
            "analysis_capabilities": [
                "Technical Analysis",
                "Fundamental Analysis", 
                "Sentiment Analysis",
                "Risk Assessment"
            ],
            "description": "Performs comprehensive multi-perspective financial analysis"
        }

# Global instance
analysis_agent = AnalysisAgent()