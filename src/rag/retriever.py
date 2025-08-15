import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

from ..vector_db.faiss_manager import vector_db
from ..data.processors.data_processor import stock_data_processor
from ..data.scrapers.news_scraper import news_scraper
from ..utils.helpers import clean_text

logger = logging.getLogger(__name__)

class StockRAGRetriever:
    """RAG retriever for stock information with intelligent context selection."""
    
    def __init__(self):
        self.vector_db = vector_db
        self.data_processor = stock_data_processor
        self.news_scraper = news_scraper
        
        # Cache for recent queries to avoid redundant API calls
        self.query_cache = {}
        self.cache_duration = timedelta(minutes=30)
    
    async def retrieve_context(self, query: str, symbol: str = None, max_context_length: int = 4000) -> Dict[str, Any]:
        """Retrieve relevant context for a query about a stock."""
        logger.info(f"Retrieving context for query: '{query}' (symbol: {symbol})")
        
        context_data = {
            "query": query,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "context_chunks": [],
            "raw_data": {}
        }
        
        # Step 1: If no symbol provided, try to extract it from the query
        if not symbol:
            symbol = await self._extract_symbol_from_query(query)
            context_data["symbol"] = symbol
        
        if symbol:
            # Step 2: Get or update company data
            company_data = await self._get_company_data(symbol)
            if company_data:
                context_data["raw_data"]["company_data"] = company_data
                context_data["sources"].extend(company_data.get("sources_used", []))
            
            # Step 3: Search vector database for relevant information
            vector_results = await self._search_vector_db(query, symbol)
            if vector_results:
                context_data["context_chunks"].extend(vector_results)
            
            # Step 4: Get additional web-scraped news if needed
            if self._needs_recent_news(query):
                web_news = await self._get_web_news(symbol)
                if web_news:
                    context_data["raw_data"]["web_news"] = web_news
                    context_data["sources"].append("web_scraping")
        
        # Step 5: Rank and select best context chunks
        selected_context = self._select_best_context(
            context_data["context_chunks"], 
            query, 
            max_context_length
        )
        context_data["selected_context"] = selected_context
        
        # Step 6: Format final context
        formatted_context = self._format_context_for_llm(context_data)
        context_data["formatted_context"] = formatted_context
        
        logger.info(f"Retrieved context with {len(selected_context)} chunks from {len(context_data['sources'])} sources")
        return context_data
    
    async def _extract_symbol_from_query(self, query: str) -> Optional[str]:
        """Extract stock symbol from query using various methods."""
        # Simple pattern matching for common formats
        import re
        
        # Look for patterns like "AAPL", "$AAPL", "AAPL stock", etc.
        patterns = [
            r'\b([A-Z]{1,5})\b(?:\s+stock|\s+shares?|\s+company)?',
            r'\$([A-Z]{1,5})\b',
            r'\b([A-Z]{1,5})\s+(?:stock|shares?|company|corp|inc)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query.upper())
            if matches:
                # Return the first match that looks like a valid symbol
                for match in matches:
                    if 1 <= len(match) <= 5 and match.isalpha():
                        return match
        
        # Try to search for company names
        company_keywords = self._extract_company_keywords(query)
        if company_keywords:
            search_results = await stock_data_processor.search_company(company_keywords)
            if search_results:
                return search_results[0].get("symbol")
        
        return None
    
    def _extract_company_keywords(self, query: str) -> str:
        """Extract potential company name keywords from query."""
        # Remove common stock-related words
        stop_words = {
            'stock', 'share', 'shares', 'company', 'corp', 'corporation', 'inc', 'ltd',
            'price', 'performance', 'analysis', 'recent', 'latest', 'current',
            'tell', 'me', 'about', 'what', 'how', 'is', 'the', 'a', 'an', 'and', 'or'
        }
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(keywords[:3])  # Take first 3 meaningful words
    
    async def _get_company_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive company data, using cache if available."""
        cache_key = f"company_data_{symbol}"
        
        # Check cache
        if cache_key in self.query_cache:
            cached_data, timestamp = self.query_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                logger.debug(f"Using cached data for {symbol}")
                return cached_data
        
        # Fetch fresh data
        try:
            company_data = await stock_data_processor.get_comprehensive_stock_data(symbol)
            
            # Cache the result
            self.query_cache[cache_key] = (company_data, datetime.now())
            
            # Add to vector database for future searches
            if company_data:
                await vector_db.add_company_data(symbol, company_data)
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching company data for {symbol}: {e}")
            return None
    
    async def _search_vector_db(self, query: str, symbol: str = None) -> List[Dict[str, Any]]:
        """Search the vector database for relevant information."""
        try:
            # Search with symbol filter if provided
            results = await vector_db.search(query, k=10, symbol_filter=symbol)
            
            # If no results with symbol filter, try broader search
            if not results and symbol:
                results = await vector_db.search(query, k=5)
            
            # Filter and enhance results
            enhanced_results = []
            for result in results:
                if result["score"] > 0.7:  # Only include high-confidence matches
                    enhanced_results.append({
                        "text": result["text"],
                        "metadata": result["metadata"],
                        "score": result["score"],
                        "source": "vector_db"
                    })
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def _needs_recent_news(self, query: str) -> bool:
        """Determine if the query requires recent news information."""
        news_keywords = [
            'recent', 'latest', 'news', 'current', 'today', 'yesterday',
            'this week', 'this month', 'breaking', 'announcement',
            'earnings', 'report', 'update', 'development'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in news_keywords)
    
    async def _get_web_news(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """Get recent news from web scraping."""
        cache_key = f"web_news_{symbol}"
        
        # Check cache
        if cache_key in self.query_cache:
            cached_news, timestamp = self.query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(minutes=15):  # Shorter cache for news
                return cached_news
        
        try:
            async with news_scraper:
                web_news = await news_scraper.get_comprehensive_news(symbol, limit_per_source=3)
            
            # Cache the result
            self.query_cache[cache_key] = (web_news, datetime.now())
            
            return web_news
            
        except Exception as e:
            logger.error(f"Error fetching web news for {symbol}: {e}")
            return None
    
    def _select_best_context(self, context_chunks: List[Dict[str, Any]], query: str, max_length: int) -> List[Dict[str, Any]]:
        """Select the best context chunks based on relevance and diversity."""
        if not context_chunks:
            return []
        
        # Sort by relevance score
        sorted_chunks = sorted(context_chunks, key=lambda x: x.get("score", 0), reverse=True)
        
        selected = []
        total_length = 0
        seen_types = set()
        
        for chunk in sorted_chunks:
            chunk_text = chunk.get("text", "")
            chunk_length = len(chunk_text)
            chunk_type = chunk.get("metadata", {}).get("type", "unknown")
            
            # Skip if adding this chunk would exceed max length
            if total_length + chunk_length > max_length:
                continue
            
            # Prefer diversity in chunk types
            type_penalty = 0.1 if chunk_type in seen_types else 0
            adjusted_score = chunk.get("score", 0) - type_penalty
            
            if adjusted_score > 0.6:  # Minimum relevance threshold
                selected.append(chunk)
                total_length += chunk_length
                seen_types.add(chunk_type)
                
                # Stop if we have enough diverse content
                if len(selected) >= 8 or total_length > max_length * 0.8:
                    break
        
        return selected
    
    def _format_context_for_llm(self, context_data: Dict[str, Any]) -> str:
        """Format the retrieved context for LLM consumption."""
        parts = []
        
        symbol = context_data.get("symbol")
        if symbol:
            parts.append(f"=== CONTEXT FOR {symbol} ===")
        
        # Add selected context chunks
        selected_context = context_data.get("selected_context", [])
        if selected_context:
            parts.append("\n--- RELEVANT INFORMATION ---")
            
            for i, chunk in enumerate(selected_context, 1):
                metadata = chunk.get("metadata", {})
                chunk_type = metadata.get("type", "information")
                timestamp = metadata.get("timestamp", "")
                
                parts.append(f"\n{i}. [{chunk_type.upper()}]")
                if timestamp:
                    parts.append(f"   Timestamp: {timestamp}")
                parts.append(f"   Content: {chunk.get('text', '')}")
        
        # Add summary of raw data if available
        raw_data = context_data.get("raw_data", {})
        if raw_data.get("company_data"):
            company_data = raw_data["company_data"]
            if company_data.get("quote"):
                quote = company_data["quote"]
                parts.append(f"\n--- CURRENT MARKET DATA ---")
                parts.append(f"Price: ${quote.get('price', 'N/A')}")
                parts.append(f"Change: {quote.get('change', 'N/A')} ({quote.get('change_percent', 'N/A')}%)")
                parts.append(f"Volume: {quote.get('volume', 'N/A'):,}")
        
        # Add sources
        sources = context_data.get("sources", [])
        if sources:
            parts.append(f"\n--- DATA SOURCES ---")
            parts.append(f"Sources: {', '.join(set(sources))}")
        
        return "\n".join(parts)
    
    async def get_company_summary(self, symbol: str) -> Optional[str]:
        """Get a formatted summary of a company."""
        try:
            company_data = await self._get_company_data(symbol)
            if not company_data:
                return None
            
            return stock_data_processor.format_stock_summary(company_data)
            
        except Exception as e:
            logger.error(f"Error getting company summary for {symbol}: {e}")
            return None
    
    async def search_companies(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for companies matching a query."""
        try:
            return await stock_data_processor.search_company(query)
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return None
    
    def clear_cache(self):
        """Clear the query cache."""
        self.query_cache.clear()
        logger.info("Query cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for key, (data, timestamp) in self.query_cache.items():
            if now - timestamp < self.cache_duration:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.query_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_duration_minutes": self.cache_duration.total_seconds() / 60
        }

# Global instance
rag_retriever = StockRAGRetriever()