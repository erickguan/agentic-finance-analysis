"""
Research Agent for Financial Analysis

This agent handles data gathering and context preparation using the existing
data infrastructure (stock processors, RAG retriever, vector database).
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage

from agent_fin.core.tools.research_tools import research_tools
from agent_fin.core.utils.config import config

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Research Agent responsible for gathering comprehensive data for stock analysis.
    
    This agent coordinates data collection from multiple sources including:
    - Company overviews and profiles
    - Financial data and metrics
    - Recent news and sentiment indicators
    - Analyst recommendations and estimates
    - Historical performance data
    - Vector database contextual information
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.OPENAI_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.1,  # Low temperature for factual data gathering
            api_key=config.OPENAI_API_KEY
        )
        
        # Get research tools
        self.tools = research_tools.get_langchain_tools()
        
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
            max_iterations=10,
            return_intermediate_steps=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the research agent."""
        
        system_message = """You are a Financial Research Specialist expert in gathering comprehensive data for stock analysis.

Your role is to systematically collect and organize financial data from multiple sources to support thorough investment analysis.

RESEARCH METHODOLOGY:
1. Start with company overview to understand the business
2. Gather current financial data and metrics
3. Collect recent news and market sentiment
4. Obtain analyst recommendations and estimates  
5. Search for relevant historical context
6. Validate data quality and note any gaps

RESEARCH AREAS TO COVER:
- Company Profile: Basic info, sector, industry, business model
- Financial Metrics: Current ratios, performance indicators, financial health
- Market Data: Current price, volume, historical performance
- News & Sentiment: Recent developments, market perception
- Analyst Coverage: Recommendations, estimates, price targets
- Industry Context: Peer comparisons, sector trends

OUTPUT REQUIREMENTS:
- Provide structured, factual information only
- Note data sources and timestamps
- Highlight any data quality issues or gaps
- Organize findings in a clear, logical format
- Flag any conflicting information across sources

Be thorough but efficient. Focus on gathering the most relevant and recent data for analysis."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    async def research_company(self, symbol: str, research_scope: List[str] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a company.
        
        Args:
            symbol: Stock symbol to research
            research_scope: List of specific research areas to focus on
            
        Returns:
            Dict containing structured research results
        """
        try:
            if research_scope is None:
                research_scope = ["comprehensive"]
            
            logger.info(f"Starting research for {symbol} with scope: {research_scope}")
            
            # Create research query
            scope_text = ", ".join(research_scope)
            query = f"Conduct comprehensive research on {symbol}. Focus on: {scope_text}. Gather company overview, financial data, recent news, and analyst information."
            
            # Execute the research
            result = await self.executor.ainvoke({
                "input": query,
                "chat_history": []
            })
            
            # Structure the response
            research_response = {
                "symbol": symbol.upper(),
                "research_scope": research_scope,
                "timestamp": result.get("timestamp"),
                "research_findings": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "sources_used": self._extract_sources_from_steps(result.get("intermediate_steps", [])),
                "data_quality_assessment": self._assess_research_quality(result)
            }
            
            logger.info(f"Completed research for {symbol}")
            return research_response
            
        except Exception as e:
            logger.error(f"Error in research for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "research_scope": research_scope or [],
                "timestamp": None
            }
    
    def research_company_sync(self, symbol: str, research_scope: List[str] = None) -> Dict[str, Any]:
        """
        Synchronous version of company research.
        
        Args:
            symbol: Stock symbol to research
            research_scope: List of specific research areas to focus on
            
        Returns:
            Dict containing structured research results
        """
        try:
            if research_scope is None:
                research_scope = ["comprehensive"]
            
            logger.info(f"Starting sync research for {symbol} with scope: {research_scope}")
            
            # Create research query
            scope_text = ", ".join(research_scope)
            query = f"Conduct comprehensive research on {symbol}. Focus on: {scope_text}. Gather company overview, financial data, recent news, and analyst information."
            
            # Execute the research
            result = self.executor.invoke({
                "input": query,
                "chat_history": []
            })
            
            # Structure the response
            research_response = {
                "symbol": symbol.upper(),
                "research_scope": research_scope,
                "research_findings": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", []),
                "sources_used": self._extract_sources_from_steps(result.get("intermediate_steps", [])),
                "data_quality_assessment": self._assess_research_quality(result)
            }
            
            logger.info(f"Completed sync research for {symbol}")
            return research_response
            
        except Exception as e:
            logger.error(f"Error in sync research for {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "research_scope": research_scope or [],
            }
    
    def search_companies(self, query: str) -> Dict[str, Any]:
        """
        Search for companies by name or keywords.
        
        Args:
            query: Search query (company name, keywords, etc.)
            
        Returns:
            Dict containing search results
        """
        try:
            logger.info(f"Searching companies with query: {query}")
            
            search_query = f"Search for companies matching: {query}. Find stock symbols and basic company information."
            
            result = self.executor.invoke({
                "input": search_query,
                "chat_history": []
            })
            
            return {
                "query": query,
                "search_results": result.get("output"),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
            
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return {
                "query": query,
                "error": str(e)
            }
    
    def _extract_sources_from_steps(self, intermediate_steps: List) -> List[str]:
        """Extract data sources used from intermediate steps."""
        sources = set()
        
        for step in intermediate_steps:
            if len(step) >= 2:
                action, observation = step[0], step[1]
                tool_name = getattr(action, 'tool', None)
                
                # Map tool names to source categories
                source_mapping = {
                    'get_company_overview': 'financial_data_providers',
                    'get_financial_data': 'financial_data_providers', 
                    'search_recent_news': 'news_sources',
                    'get_analyst_data': 'analyst_sources',
                    'search_vector_database': 'vector_database'
                }
                
                if tool_name in source_mapping:
                    sources.add(source_mapping[tool_name])
        
        return list(sources)
    
    def _assess_research_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality and completeness of research results."""
        quality_assessment = {
            "completeness_score": 0.5,  # Default medium score
            "data_freshness": "unknown",
            "source_diversity": len(self._extract_sources_from_steps(result.get("intermediate_steps", []))),
            "potential_gaps": []
        }
        
        # Check if we have output
        if result.get("output"):
            quality_assessment["completeness_score"] += 0.3
        
        # Check for errors in intermediate steps
        intermediate_steps = result.get("intermediate_steps", [])
        error_count = 0
        
        for step in intermediate_steps:
            if len(step) >= 2:
                observation = step[1]
                if isinstance(observation, str) and "error" in observation.lower():
                    error_count += 1
        
        if error_count > 0:
            quality_assessment["potential_gaps"].append(f"{error_count} tool execution errors")
            quality_assessment["completeness_score"] -= 0.1 * error_count
        
        # Ensure score is between 0 and 1
        quality_assessment["completeness_score"] = max(0, min(1, quality_assessment["completeness_score"]))
        
        return quality_assessment
    
    def get_available_tools(self) -> List[str]:
        """Get list of available research tools."""
        return [tool.name for tool in self.tools]
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the research agent configuration."""
        return {
            "agent_type": "Research Agent",
            "model": self.model_name,
            "available_tools": self.get_available_tools(),
            "max_iterations": self.executor.max_iterations,
            "description": "Gathers comprehensive financial data for analysis"
        }

# Global instance
research_agent = ResearchAgent()