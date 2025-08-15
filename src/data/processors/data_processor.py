import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

from ..collectors.alpha_vantage import alpha_vantage_client
from ..collectors.yahoo_finance import yahoo_finance_client
from ..collectors.financial_modeling_prep import fmp_client
from ...utils.helpers import clean_text, format_currency, format_percentage

logger = logging.getLogger(__name__)

class StockDataProcessor:
    """Processes and aggregates stock data from multiple sources."""
    
    def __init__(self):
        self.sources = {
            "alpha_vantage": alpha_vantage_client,
            "yahoo_finance": yahoo_finance_client,
            "financial_modeling_prep": fmp_client
        }
    
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data from all available sources."""
        logger.info(f"Fetching comprehensive data for {symbol}")
        
        # Run all data collection tasks concurrently
        tasks = [
            self._get_quote_data(symbol),
            self._get_company_data(symbol),
            self._get_historical_data(symbol),
            self._get_financial_data(symbol),
            self._get_news_data(symbol),
            self._get_analyst_data(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        quote_data, company_data, historical_data, financial_data, news_data, analyst_data = results
        
        # Aggregate all data
        comprehensive_data = {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "quote": quote_data if not isinstance(quote_data, Exception) else None,
            "company": company_data if not isinstance(company_data, Exception) else None,
            "historical": historical_data if not isinstance(historical_data, Exception) else None,
            "financial": financial_data if not isinstance(financial_data, Exception) else None,
            "news": news_data if not isinstance(news_data, Exception) else None,
            "analyst": analyst_data if not isinstance(analyst_data, Exception) else None,
            "sources_used": []
        }
        
        # Track which sources provided data
        for key, value in comprehensive_data.items():
            if isinstance(value, dict) and "source" in value:
                if value["source"] not in comprehensive_data["sources_used"]:
                    comprehensive_data["sources_used"].append(value["source"])
            elif isinstance(value, list) and value and isinstance(value[0], dict) and "source" in value[0]:
                source = value[0]["source"]
                if source not in comprehensive_data["sources_used"]:
                    comprehensive_data["sources_used"].append(source)
        
        return comprehensive_data
    
    async def _get_quote_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote data from the best available source."""
        # Try sources in order of preference
        sources = ["yahoo_finance", "alpha_vantage", "financial_modeling_prep"]
        
        for source_name in sources:
            try:
                source = self.sources[source_name]
                quote = await source.get_quote(symbol)
                if quote:
                    logger.info(f"Got quote data for {symbol} from {source_name}")
                    return quote
            except Exception as e:
                logger.warning(f"Failed to get quote from {source_name}: {e}")
                continue
        
        logger.warning(f"Could not get quote data for {symbol} from any source")
        return None
    
    async def _get_company_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information from the best available source."""
        # Try Alpha Vantage first for comprehensive overview, then Yahoo Finance
        sources = ["alpha_vantage", "yahoo_finance", "financial_modeling_prep"]
        
        for source_name in sources:
            try:
                source = self.sources[source_name]
                if source_name == "alpha_vantage":
                    company_data = await source.get_company_overview(symbol)
                elif source_name == "yahoo_finance":
                    company_data = await source.get_company_info(symbol)
                else:  # financial_modeling_prep
                    company_data = await source.get_company_profile(symbol)
                
                if company_data:
                    logger.info(f"Got company data for {symbol} from {source_name}")
                    return company_data
            except Exception as e:
                logger.warning(f"Failed to get company data from {source_name}: {e}")
                continue
        
        logger.warning(f"Could not get company data for {symbol} from any source")
        return None
    
    async def _get_historical_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get historical price data from the best available source."""
        sources = ["yahoo_finance", "alpha_vantage", "financial_modeling_prep"]
        
        for source_name in sources:
            try:
                source = self.sources[source_name]
                if source_name == "yahoo_finance":
                    historical = await source.get_daily_data(symbol, period="1y")
                elif source_name == "alpha_vantage":
                    historical = await source.get_daily_data(symbol, outputsize="compact")
                else:  # financial_modeling_prep
                    historical = await source.get_daily_data(symbol, limit=252)  # ~1 year
                
                if historical:
                    logger.info(f"Got historical data for {symbol} from {source_name}")
                    return historical
            except Exception as e:
                logger.warning(f"Failed to get historical data from {source_name}: {e}")
                continue
        
        logger.warning(f"Could not get historical data for {symbol} from any source")
        return None
    
    async def _get_financial_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get financial statements and metrics."""
        financial_data = {}
        
        # Try to get key metrics from FMP
        try:
            fmp_metrics = await fmp_client.get_key_metrics(symbol, limit=5)
            if fmp_metrics:
                financial_data["key_metrics"] = fmp_metrics
        except Exception as e:
            logger.warning(f"Failed to get key metrics from FMP: {e}")
        
        # Try to get financial ratios from FMP
        try:
            fmp_ratios = await fmp_client.get_financial_ratios(symbol, limit=5)
            if fmp_ratios:
                financial_data["financial_ratios"] = fmp_ratios
        except Exception as e:
            logger.warning(f"Failed to get financial ratios from FMP: {e}")
        
        # Try to get financial statements from Yahoo Finance
        try:
            yf_financials = await yahoo_finance_client.get_financial_data(symbol)
            if yf_financials:
                financial_data["financial_statements"] = yf_financials
        except Exception as e:
            logger.warning(f"Failed to get financial statements from Yahoo Finance: {e}")
        
        # Try to get earnings from Alpha Vantage
        try:
            av_earnings = await alpha_vantage_client.get_earnings(symbol)
            if av_earnings:
                financial_data["earnings"] = av_earnings
        except Exception as e:
            logger.warning(f"Failed to get earnings from Alpha Vantage: {e}")
        
        if financial_data:
            financial_data["source"] = "multiple"
            return financial_data
        
        logger.warning(f"Could not get financial data for {symbol} from any source")
        return None
    
    async def _get_news_data(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """Get news data from available sources."""
        all_news = []
        
        # Try Yahoo Finance news
        try:
            yf_news = await yahoo_finance_client.get_news(symbol)
            if yf_news:
                all_news.extend(yf_news)
        except Exception as e:
            logger.warning(f"Failed to get news from Yahoo Finance: {e}")
        
        # Try FMP news
        try:
            fmp_news = await fmp_client.get_stock_news(symbol, limit=20)
            if fmp_news:
                all_news.extend(fmp_news)
        except Exception as e:
            logger.warning(f"Failed to get news from FMP: {e}")
        
        if all_news:
            # Remove duplicates based on title similarity
            unique_news = self._deduplicate_news(all_news)
            # Sort by date (most recent first)
            unique_news.sort(key=lambda x: x.get("published", x.get("published_date", "")), reverse=True)
            logger.info(f"Got {len(unique_news)} unique news articles for {symbol}")
            return unique_news
        
        logger.warning(f"Could not get news data for {symbol} from any source")
        return None
    
    async def _get_analyst_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst recommendations and estimates."""
        analyst_data = {}
        
        # Try to get analyst recommendations from Yahoo Finance
        try:
            yf_recommendations = await yahoo_finance_client.get_analyst_recommendations(symbol)
            if yf_recommendations:
                analyst_data["recommendations"] = yf_recommendations
        except Exception as e:
            logger.warning(f"Failed to get analyst recommendations from Yahoo Finance: {e}")
        
        # Try to get analyst estimates from FMP
        try:
            fmp_estimates = await fmp_client.get_analyst_estimates(symbol)
            if fmp_estimates:
                analyst_data["estimates"] = fmp_estimates
        except Exception as e:
            logger.warning(f"Failed to get analyst estimates from FMP: {e}")
        
        # Try to get earnings calendar from multiple sources
        try:
            # Try Yahoo Finance first
            yf_calendar = await yahoo_finance_client.get_earnings_calendar(symbol)
            if yf_calendar:
                analyst_data["earnings_calendar"] = yf_calendar
            else:
                # Try FMP as fallback
                fmp_calendar = await fmp_client.get_earnings_calendar(symbol)
                if fmp_calendar:
                    analyst_data["earnings_calendar"] = fmp_calendar
        except Exception as e:
            logger.warning(f"Failed to get earnings calendar: {e}")
        
        if analyst_data:
            analyst_data["source"] = "multiple"
            return analyst_data
        
        logger.warning(f"Could not get analyst data for {symbol} from any source")
        return None
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news articles based on title similarity."""
        unique_news = []
        seen_titles = set()
        
        for article in news_list:
            title = article.get("title", "").lower().strip()
            if not title:
                continue
            
            # Simple deduplication based on title
            title_words = set(title.split())
            is_duplicate = False
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # If more than 70% of words are the same, consider it a duplicate
                if len(title_words & seen_words) / max(len(title_words), len(seen_words)) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_news.append(article)
                seen_titles.add(title)
        
        return unique_news
    
    async def search_company(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for companies across all sources."""
        all_results = []
        
        # Try all sources
        sources = [
            ("alpha_vantage", alpha_vantage_client.search_symbol),
            ("yahoo_finance", yahoo_finance_client.search_symbol),
            ("financial_modeling_prep", fmp_client.search_symbol)
        ]
        
        for source_name, search_func in sources:
            try:
                results = await search_func(query)
                if results:
                    for result in results:
                        result["source"] = source_name
                    all_results.extend(results)
            except Exception as e:
                logger.warning(f"Failed to search from {source_name}: {e}")
        
        if all_results:
            # Deduplicate by symbol
            unique_results = {}
            for result in all_results:
                symbol = result.get("symbol", "").upper()
                if symbol and symbol not in unique_results:
                    unique_results[symbol] = result
            
            # Sort by match score if available
            sorted_results = list(unique_results.values())
            sorted_results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            
            return sorted_results
        
        return None
    
    def format_stock_summary(self, data: Dict[str, Any]) -> str:
        """Format comprehensive stock data into a readable summary."""
        if not data:
            return "No data available."
        
        summary_parts = []
        symbol = data.get("symbol", "Unknown")
        
        # Company info
        company = data.get("company", {})
        if company:
            name = company.get("name", symbol)
            sector = company.get("sector", "")
            industry = company.get("industry", "")
            
            summary_parts.append(f"**{name} ({symbol})**")
            if sector:
                summary_parts.append(f"Sector: {sector}")
            if industry:
                summary_parts.append(f"Industry: {industry}")
            
            description = company.get("description", "")
            if description:
                # Truncate description if too long
                if len(description) > 300:
                    description = description[:300] + "..."
                summary_parts.append(f"Description: {description}")
        
        # Current quote
        quote = data.get("quote", {})
        if quote:
            price = quote.get("price", 0)
            change = quote.get("change", 0)
            change_percent = quote.get("change_percent", 0)
            volume = quote.get("volume", 0)
            
            summary_parts.append(f"\n**Current Price:** ${price:.2f}")
            summary_parts.append(f"**Change:** {change:+.2f} ({change_percent:+.2f}%)")
            if volume:
                summary_parts.append(f"**Volume:** {volume:,}")
        
        # Key metrics
        financial = data.get("financial", {})
        if financial and "key_metrics" in financial:
            metrics = financial["key_metrics"].get("key_metrics", [])
            if metrics:
                latest_metrics = metrics[0]  # Most recent
                summary_parts.append(f"\n**Key Metrics:**")
                
                pe_ratio = latest_metrics.get("pe_ratio")
                if pe_ratio:
                    summary_parts.append(f"P/E Ratio: {pe_ratio:.2f}")
                
                market_cap = latest_metrics.get("market_cap")
                if market_cap:
                    summary_parts.append(f"Market Cap: {format_currency(market_cap)}")
                
                debt_to_equity = latest_metrics.get("debt_to_equity")
                if debt_to_equity:
                    summary_parts.append(f"Debt-to-Equity: {debt_to_equity:.2f}")
        
        # Recent news count
        news = data.get("news", [])
        if news:
            summary_parts.append(f"\n**Recent News:** {len(news)} articles available")
        
        # Analyst data
        analyst = data.get("analyst", {})
        if analyst and "recommendations" in analyst:
            recommendations = analyst["recommendations"].get("recommendations", [])
            if recommendations:
                summary_parts.append(f"**Analyst Recommendations:** {len(recommendations)} recent ratings")
        
        return "\n".join(summary_parts)

# Global instance
stock_data_processor = StockDataProcessor()