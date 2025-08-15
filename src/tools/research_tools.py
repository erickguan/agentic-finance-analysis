"""
Research Tools for Financial Analysis

Tools that integrate with the existing data infrastructure to gather comprehensive
financial data for analysis.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.tools import Tool
from pydantic import BaseModel, Field

from ..data.processors.data_processor import stock_data_processor
from ..rag.retriever import rag_retriever

logger = logging.getLogger(__name__)

class CompanyLookupInput(BaseModel):
    """Input for company lookup tool."""
    symbol: str = Field(description="Stock symbol to look up (e.g. AAPL, GOOGL)")

class NewsSearchInput(BaseModel):
    """Input for news search tool."""
    symbol: str = Field(description="Stock symbol to search news for")
    limit: int = Field(default=10, description="Maximum number of news articles to retrieve")

class VectorSearchInput(BaseModel):
    """Input for vector database search."""
    query: str = Field(description="Search query for vector database")
    symbol: str = Field(default="", description="Optional symbol to filter results")

class ResearchTools:
    """Collection of research tools for data gathering."""
    
    def __init__(self):
        self.data_processor = stock_data_processor
        self.rag_retriever = rag_retriever
    
    async def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive company overview and current data."""
        try:
            logger.info(f"Fetching company overview for {symbol}")
            data = await self.data_processor.get_comprehensive_stock_data(symbol)
            
            if not data:
                return {"error": f"No data found for symbol {symbol}"}
            
            # Extract key information for overview
            overview = {
                "symbol": data.get("symbol"),
                "timestamp": data.get("timestamp"),
                "company_info": data.get("company", {}),
                "current_quote": data.get("quote", {}),
                "sources_used": data.get("sources_used", [])
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {e}")
            return {"error": str(e)}
    
    async def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """Get detailed financial data including statements and metrics."""
        try:
            logger.info(f"Fetching financial data for {symbol}")
            data = await self.data_processor.get_comprehensive_stock_data(symbol)
            
            if not data:
                return {"error": f"No financial data found for symbol {symbol}"}
            
            # Extract financial information
            financial_info = {
                "symbol": data.get("symbol"),
                "financial_data": data.get("financial", {}),
                "historical_data": data.get("historical", {}),
                "sources_used": data.get("sources_used", [])
            }
            
            return financial_info
            
        except Exception as e:
            logger.error(f"Error fetching financial data for {symbol}: {e}")
            return {"error": str(e)}
    
    async def search_recent_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for recent news articles about a company."""
        try:
            logger.info(f"Searching recent news for {symbol}")
            data = await self.data_processor.get_comprehensive_stock_data(symbol)
            
            if not data or not data.get("news"):
                return []
            
            # Return limited number of recent news articles
            news_articles = data["news"][:limit]
            
            return news_articles
            
        except Exception as e:
            logger.error(f"Error searching news for {symbol}: {e}")
            return []
    
    async def search_vector_database(self, query: str, symbol: str = "") -> List[Dict[str, Any]]:
        """Search the vector database for relevant information."""
        try:
            logger.info(f"Searching vector database with query: {query}")
            
            # Use the RAG retriever to search for relevant context
            context_data = await self.rag_retriever.retrieve_context(
                query=query,
                symbol=symbol if symbol else None,
                max_context_length=2000
            )
            
            return {
                "context_chunks": context_data.get("context_chunks", []),
                "sources": context_data.get("sources", []),
                "formatted_context": context_data.get("formatted_context", "")
            }
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return {"error": str(e)}
    
    async def get_analyst_data(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations and estimates."""
        try:
            logger.info(f"Fetching analyst data for {symbol}")
            data = await self.data_processor.get_comprehensive_stock_data(symbol)
            
            if not data:
                return {"error": f"No analyst data found for symbol {symbol}"}
            
            analyst_info = {
                "symbol": data.get("symbol"),
                "analyst_data": data.get("analyst", {}),
                "sources_used": data.get("sources_used", [])
            }
            
            return analyst_info
            
        except Exception as e:
            logger.error(f"Error fetching analyst data for {symbol}: {e}")
            return {"error": str(e)}
    
    async def search_companies(self, query: str) -> List[Dict[str, Any]]:
        """Search for companies by name or keywords."""
        try:
            logger.info(f"Searching companies with query: {query}")
            results = await self.data_processor.search_company(query)
            
            if not results:
                return []
            
            return results[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []
    
    def get_langchain_tools(self) -> List[Tool]:
        """Get LangChain Tool objects for use by agents."""
        
        def company_overview_wrapper(symbol: str) -> str:
            """Wrapper for async company overview function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.get_company_overview(symbol))
            return str(result)
        
        def financial_data_wrapper(symbol: str) -> str:
            """Wrapper for async financial data function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.get_financial_data(symbol))
            return str(result)
        
        def news_search_wrapper(symbol: str, limit: int = 10) -> str:
            """Wrapper for async news search function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.search_recent_news(symbol, limit))
            return str(result)
        
        def vector_search_wrapper(query: str, symbol: str = "") -> str:
            """Wrapper for async vector search function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.search_vector_database(query, symbol))
            return str(result)
        
        def analyst_data_wrapper(symbol: str) -> str:
            """Wrapper for async analyst data function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.get_analyst_data(symbol))
            return str(result)
        
        def company_search_wrapper(query: str) -> str:
            """Wrapper for async company search function."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.search_companies(query))
            return str(result)
        
        return [
            Tool(
                name="get_company_overview",
                description="Get comprehensive company overview including basic info and current stock quote. Input: stock symbol (e.g. AAPL)",
                func=company_overview_wrapper
            ),
            Tool(
                name="get_financial_data", 
                description="Get detailed financial data including statements, ratios, and historical performance. Input: stock symbol (e.g. AAPL)",
                func=financial_data_wrapper
            ),
            Tool(
                name="search_recent_news",
                description="Search for recent news articles about a company. Input: stock symbol (e.g. AAPL)",
                func=news_search_wrapper
            ),
            Tool(
                name="search_vector_database",
                description="Search the vector database for relevant information. Input: search query text",
                func=vector_search_wrapper
            ),
            Tool(
                name="get_analyst_data",
                description="Get analyst recommendations and estimates for a company. Input: stock symbol (e.g. AAPL)",
                func=analyst_data_wrapper
            ),
            Tool(
                name="search_companies",
                description="Search for companies by name or keywords to find stock symbols. Input: company name or keywords",
                func=company_search_wrapper
            )
        ]

# Global instance
research_tools = ResearchTools()