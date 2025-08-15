"""
Orchestration Tools for Master Agent

Tools that help the master agent coordinate workflow between research and analysis agents.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

class ResearchRequestInput(BaseModel):
    """Input for research coordination."""
    symbol: str = Field(description="Stock symbol to research")
    research_scope: List[str] = Field(description="List of research areas needed")

class AnalysisRequestInput(BaseModel):
    """Input for analysis coordination."""
    research_data: Dict[str, Any] = Field(description="Research data to analyze")
    analysis_focus: List[str] = Field(description="Areas of analysis to focus on")

class OrchestrationTools:
    """Collection of tools for coordinating agent workflow."""
    
    def __init__(self):
        pass
    
    def coordinate_research_request(self, symbol: str, research_scope: List[str]) -> Dict[str, Any]:
        """Create a structured research request for the research agent."""
        try:
            research_request = {
                "symbol": symbol.upper(),
                "research_scope": research_scope,
                "timestamp": datetime.now().isoformat(),
                "request_id": f"research_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "required_data": []
            }
            
            # Map research scope to specific data requirements
            scope_mapping = {
                "company_overview": ["get_company_overview"],
                "financial_data": ["get_financial_data"],
                "news_analysis": ["search_recent_news"],
                "analyst_data": ["get_analyst_data"],
                "historical_performance": ["get_financial_data"],
                "market_sentiment": ["search_recent_news", "search_vector_database"],
                "comprehensive": ["get_company_overview", "get_financial_data", "search_recent_news", "get_analyst_data"]
            }
            
            # Determine required tools based on scope
            required_tools = set()
            for scope in research_scope:
                if scope in scope_mapping:
                    required_tools.update(scope_mapping[scope])
                else:
                    # Default to comprehensive if scope not recognized
                    required_tools.update(scope_mapping["comprehensive"])
            
            research_request["required_tools"] = list(required_tools)
            
            return research_request
            
        except Exception as e:
            logger.error(f"Error coordinating research request: {e}")
            return {"error": str(e)}
    
    def coordinate_analysis_request(self, research_data: Dict[str, Any], analysis_focus: List[str]) -> Dict[str, Any]:
        """Create a structured analysis request for the analysis agent."""
        try:
            analysis_request = {
                "research_data": research_data,
                "analysis_focus": analysis_focus,
                "timestamp": datetime.now().isoformat(),
                "request_id": f"analysis_{research_data.get('symbol', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "required_tools": []
            }
            
            # Map analysis focus to specific tools
            focus_mapping = {
                "technical_analysis": ["calculate_moving_averages", "calculate_rsi", "calculate_volatility"],
                "fundamental_analysis": ["calculate_financial_ratios"],
                "sentiment_analysis": ["analyze_news_sentiment"],
                "risk_assessment": ["calculate_risk_metrics"],
                "comprehensive": [
                    "calculate_moving_averages", "calculate_rsi", "calculate_volatility",
                    "calculate_financial_ratios", "analyze_news_sentiment", "calculate_risk_metrics"
                ]
            }
            
            # Determine required tools based on focus
            required_tools = set()
            for focus in analysis_focus:
                if focus in focus_mapping:
                    required_tools.update(focus_mapping[focus])
                else:
                    # Default to comprehensive if focus not recognized
                    required_tools.update(focus_mapping["comprehensive"])
            
            analysis_request["required_tools"] = list(required_tools)
            
            return analysis_request
            
        except Exception as e:
            logger.error(f"Error coordinating analysis request: {e}")
            return {"error": str(e)}
    
    def synthesize_agent_responses(self, research_response: Dict[str, Any], analysis_response: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize responses from research and analysis agents."""
        try:
            synthesis = {
                "symbol": research_response.get("symbol") or analysis_response.get("symbol"),
                "synthesis_timestamp": datetime.now().isoformat(),
                "research_summary": self._summarize_research(research_response),
                "analysis_summary": self._summarize_analysis(analysis_response),
                "key_insights": [],
                "recommendations": [],
                "confidence_level": "medium",
                "data_quality": self._assess_data_quality(research_response, analysis_response)
            }
            
            # Extract key insights from both responses
            insights = []
            
            # From research
            if research_response.get("company_info"):
                company = research_response["company_info"]
                if company.get("name"):
                    insights.append(f"Company: {company['name']} ({synthesis['symbol']})")
                if company.get("sector"):
                    insights.append(f"Sector: {company['sector']}")
            
            # From analysis
            if analysis_response.get("technical_analysis"):
                tech = analysis_response["technical_analysis"]
                if tech.get("signals"):
                    insights.extend(tech["signals"])
            
            if analysis_response.get("fundamental_analysis"):
                fund = analysis_response["fundamental_analysis"]
                if fund.get("ratios"):
                    pe_ratio = fund["ratios"].get("pe_ratio", {}).get("value")
                    if pe_ratio:
                        insights.append(f"P/E Ratio: {pe_ratio}")
            
            if analysis_response.get("sentiment_analysis"):
                sentiment = analysis_response["sentiment_analysis"]
                if sentiment.get("overall_sentiment"):
                    insights.append(f"News Sentiment: {sentiment['overall_sentiment']}")
            
            synthesis["key_insights"] = insights
            
            # Generate basic recommendations
            recommendations = self._generate_basic_recommendations(research_response, analysis_response)
            synthesis["recommendations"] = recommendations
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error synthesizing agent responses: {e}")
            return {"error": str(e)}
    
    def generate_executive_summary(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an executive summary from synthesized data."""
        try:
            symbol = synthesis_data.get("symbol", "Unknown")
            
            # Build executive summary
            summary_parts = []
            
            # Company overview
            research_summary = synthesis_data.get("research_summary", {})
            if research_summary.get("company_name"):
                summary_parts.append(f"Analysis of {research_summary['company_name']} ({symbol})")
            else:
                summary_parts.append(f"Analysis of {symbol}")
            
            # Key findings
            insights = synthesis_data.get("key_insights", [])
            if insights:
                summary_parts.append("Key Findings:")
                summary_parts.extend([f"• {insight}" for insight in insights[:5]])  # Top 5 insights
            
            # Recommendations
            recommendations = synthesis_data.get("recommendations", [])
            if recommendations:
                summary_parts.append("Recommendations:")
                summary_parts.extend([f"• {rec}" for rec in recommendations[:3]])  # Top 3 recommendations
            
            # Data quality note
            data_quality = synthesis_data.get("data_quality", {})
            if data_quality.get("completeness", 0) < 0.8:
                summary_parts.append("Note: Analysis based on limited data availability")
            
            executive_summary = {
                "symbol": symbol,
                "summary_text": "\n".join(summary_parts),
                "confidence_level": synthesis_data.get("confidence_level", "medium"),
                "generation_timestamp": datetime.now().isoformat(),
                "data_sources": data_quality.get("sources", [])
            }
            
            return executive_summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return {"error": str(e)}
    
    def format_user_response(self, executive_summary: Dict[str, Any]) -> str:
        """Format the final response for the user."""
        try:
            if "error" in executive_summary:
                return f"Error generating analysis: {executive_summary['error']}"
            
            response_parts = [
                f"# Financial Analysis Report: {executive_summary['symbol']}",
                f"*Generated: {executive_summary.get('generation_timestamp', 'Unknown')}*",
                "",
                executive_summary.get("summary_text", "No summary available"),
                "",
                f"**Confidence Level:** {executive_summary.get('confidence_level', 'Unknown').title()}",
            ]
            
            # Add data sources if available
            sources = executive_summary.get("data_sources", [])
            if sources:
                response_parts.extend([
                    "",
                    f"**Data Sources:** {', '.join(sources)}"
                ])
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error formatting user response: {e}")
            return f"Error formatting response: {str(e)}"
    
    def _summarize_research(self, research_response: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of research findings."""
        summary = {
            "symbol": research_response.get("symbol"),
            "company_name": None,
            "sector": None,
            "current_price": None,
            "news_count": 0,
            "data_sources": []
        }
        
        # Extract company info
        if research_response.get("company_info"):
            company = research_response["company_info"]
            summary["company_name"] = company.get("name")
            summary["sector"] = company.get("sector")
        
        # Extract current quote
        if research_response.get("current_quote"):
            quote = research_response["current_quote"]
            summary["current_price"] = quote.get("price")
        
        # Count news articles
        if research_response.get("news_articles"):
            summary["news_count"] = len(research_response["news_articles"])
        
        # Track data sources
        summary["data_sources"] = research_response.get("sources_used", [])
        
        return summary
    
    def _summarize_analysis(self, analysis_response: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis findings."""
        summary = {
            "technical_signals": [],
            "fundamental_health": "unknown",
            "sentiment": "neutral",
            "risk_level": "unknown"
        }
        
        # Technical analysis summary
        if analysis_response.get("technical_analysis"):
            tech = analysis_response["technical_analysis"]
            summary["technical_signals"] = tech.get("signals", [])
        
        # Fundamental analysis summary
        if analysis_response.get("fundamental_analysis"):
            fund = analysis_response["fundamental_analysis"]
            # Simple health assessment based on available ratios
            summary["fundamental_health"] = "moderate"  # Placeholder
        
        # Sentiment analysis summary
        if analysis_response.get("sentiment_analysis"):
            sentiment = analysis_response["sentiment_analysis"]
            summary["sentiment"] = sentiment.get("overall_sentiment", "neutral").lower()
        
        # Risk assessment summary
        if analysis_response.get("risk_assessment"):
            risk = analysis_response["risk_assessment"]
            summary["risk_level"] = risk.get("overall_risk_level", "unknown").lower()
        
        return summary
    
    def _assess_data_quality(self, research_response: Dict[str, Any], analysis_response: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality and completeness of available data."""
        quality_metrics = {
            "completeness": 0.0,
            "sources": [],
            "missing_data": []
        }
        
        # Check research data completeness
        research_score = 0
        total_research_categories = 4  # company, financial, news, analyst
        
        if research_response.get("company_info"):
            research_score += 1
        if research_response.get("financial_data"):
            research_score += 1
        if research_response.get("news_articles"):
            research_score += 1
        if research_response.get("analyst_data"):
            research_score += 1
        
        research_completeness = research_score / total_research_categories
        
        # Check analysis data completeness
        analysis_score = 0
        total_analysis_categories = 4  # technical, fundamental, sentiment, risk
        
        if analysis_response.get("technical_analysis"):
            analysis_score += 1
        if analysis_response.get("fundamental_analysis"):
            analysis_score += 1
        if analysis_response.get("sentiment_analysis"):
            analysis_score += 1
        if analysis_response.get("risk_assessment"):
            analysis_score += 1
        
        analysis_completeness = analysis_score / total_analysis_categories
        
        # Overall completeness
        quality_metrics["completeness"] = (research_completeness + analysis_completeness) / 2
        
        # Collect sources
        quality_metrics["sources"] = list(set(
            research_response.get("sources_used", []) + 
            analysis_response.get("sources_used", [])
        ))
        
        return quality_metrics
    
    def _generate_basic_recommendations(self, research_response: Dict[str, Any], analysis_response: Dict[str, Any]) -> List[str]:
        """Generate basic investment recommendations based on analysis."""
        recommendations = []
        
        # Basic rule-based recommendations for POC
        try:
            # Sentiment-based recommendations
            if analysis_response.get("sentiment_analysis"):
                sentiment = analysis_response["sentiment_analysis"].get("overall_sentiment", "").lower()
                if sentiment == "positive":
                    recommendations.append("Positive news sentiment supports bullish outlook")
                elif sentiment == "negative":
                    recommendations.append("Negative news sentiment suggests caution")
            
            # Risk-based recommendations
            if analysis_response.get("risk_assessment"):
                risk_level = analysis_response["risk_assessment"].get("overall_risk_level", "").lower()
                if risk_level == "high":
                    recommendations.append("High risk profile - suitable only for risk-tolerant investors")
                elif risk_level == "low":
                    recommendations.append("Low risk profile - suitable for conservative investors")
            
            # Technical analysis recommendations
            if analysis_response.get("technical_analysis"):
                tech = analysis_response["technical_analysis"]
                signals = tech.get("signals", [])
                bullish_signals = [s for s in signals if "bullish" in s.lower()]
                bearish_signals = [s for s in signals if "bearish" in s.lower()]
                
                if len(bullish_signals) > len(bearish_signals):
                    recommendations.append("Technical indicators show bullish momentum")
                elif len(bearish_signals) > len(bullish_signals):
                    recommendations.append("Technical indicators show bearish momentum")
            
            # Default recommendation if no specific signals
            if not recommendations:
                recommendations.append("Conduct additional research before making investment decisions")
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations = ["Unable to generate recommendations due to data analysis error"]
        
        return recommendations
    
    def get_langchain_tools(self) -> List[Tool]:
        """Get LangChain Tool objects for use by agents."""
        
        return [
            Tool(
                name="coordinate_research_request",
                description="Create a structured research request. Input: 'symbol,research_scope_list' (e.g., 'AAPL,company_overview,financial_data')",
                func=lambda data: str(self.coordinate_research_request(*data.split(',', 1) if ',' in data else [data, "comprehensive"]))
            ),
            Tool(
                name="coordinate_analysis_request", 
                description="Create a structured analysis request. Input: 'research_data_json,analysis_focus_list'",
                func=lambda data: str(self.coordinate_analysis_request(*eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="synthesize_agent_responses",
                description="Synthesize research and analysis responses. Input: 'research_response_json,analysis_response_json'",
                func=lambda data: str(self.synthesize_agent_responses(*eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="generate_executive_summary",
                description="Generate executive summary from synthesized data. Input: synthesis_data_json",
                func=lambda data: str(self.generate_executive_summary(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="format_user_response",
                description="Format final response for user. Input: executive_summary_json",
                func=lambda data: self.format_user_response(eval(data) if isinstance(data, str) else data)
            )
        ]

# Global instance
orchestration_tools = OrchestrationTools()