import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ...utils.config import config
from ...utils.helpers import APIClient, RateLimiter, clean_text

logger = logging.getLogger(__name__)

class AlphaVantageClient:
    """Client for Alpha Vantage API to fetch stock data."""
    
    def __init__(self):
        self.api_key = config.get_api_key("alpha_vantage")
        self.rate_limiter = RateLimiter(config.ALPHA_VANTAGE_RPM, 60)
        self.base_url = config.ALPHA_VANTAGE_BASE_URL
        
        if not self.api_key:
            logger.warning("Alpha Vantage API key not found. Some features may be limited.")
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a stock symbol."""
        if not self.api_key:
            return None
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get("", params=params)
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    return {
                        "symbol": quote.get("01. symbol", symbol),
                        "price": float(quote.get("05. price", 0)),
                        "change": float(quote.get("09. change", 0)),
                        "change_percent": quote.get("10. change percent", "0%").replace("%", ""),
                        "volume": int(quote.get("06. volume", 0)),
                        "latest_trading_day": quote.get("07. latest trading day"),
                        "previous_close": float(quote.get("08. previous close", 0)),
                        "open": float(quote.get("02. open", 0)),
                        "high": float(quote.get("03. high", 0)),
                        "low": float(quote.get("04. low", 0)),
                        "source": "alpha_vantage"
                    }
                else:
                    logger.error(f"Unexpected response format from Alpha Vantage: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_daily_data(self, symbol: str, outputsize: str = "compact") -> Optional[Dict[str, Any]]:
        """Get daily time series data for a stock symbol."""
        if not self.api_key:
            return None
        
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,  # compact (100 days) or full
            "apikey": self.api_key
        }
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get("", params=params)
                
                if "Time Series (Daily)" in data:
                    time_series = data["Time Series (Daily)"]
                    meta_data = data.get("Meta Data", {})
                    
                    # Convert to more usable format
                    daily_data = []
                    for date_str, values in time_series.items():
                        daily_data.append({
                            "date": date_str,
                            "open": float(values["1. open"]),
                            "high": float(values["2. high"]),
                            "low": float(values["3. low"]),
                            "close": float(values["4. close"]),
                            "volume": int(values["5. volume"])
                        })
                    
                    # Sort by date (most recent first)
                    daily_data.sort(key=lambda x: x["date"], reverse=True)
                    
                    return {
                        "symbol": meta_data.get("2. Symbol", symbol),
                        "last_refreshed": meta_data.get("3. Last Refreshed"),
                        "data": daily_data,
                        "source": "alpha_vantage"
                    }
                else:
                    logger.error(f"Unexpected response format from Alpha Vantage: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching daily data for {symbol}: {e}")
            return None
    
    async def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company overview and fundamental data."""
        if not self.api_key:
            return None
        
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get("", params=params)
                
                if "Symbol" in data:
                    return {
                        "symbol": data.get("Symbol"),
                        "name": data.get("Name"),
                        "description": clean_text(data.get("Description", "")),
                        "exchange": data.get("Exchange"),
                        "currency": data.get("Currency"),
                        "country": data.get("Country"),
                        "sector": data.get("Sector"),
                        "industry": data.get("Industry"),
                        "market_cap": self._safe_float(data.get("MarketCapitalization")),
                        "pe_ratio": self._safe_float(data.get("PERatio")),
                        "peg_ratio": self._safe_float(data.get("PEGRatio")),
                        "book_value": self._safe_float(data.get("BookValue")),
                        "dividend_per_share": self._safe_float(data.get("DividendPerShare")),
                        "dividend_yield": self._safe_float(data.get("DividendYield")),
                        "eps": self._safe_float(data.get("EPS")),
                        "revenue_per_share": self._safe_float(data.get("RevenuePerShareTTM")),
                        "profit_margin": self._safe_float(data.get("ProfitMargin")),
                        "operating_margin": self._safe_float(data.get("OperatingMarginTTM")),
                        "return_on_assets": self._safe_float(data.get("ReturnOnAssetsTTM")),
                        "return_on_equity": self._safe_float(data.get("ReturnOnEquityTTM")),
                        "revenue_ttm": self._safe_float(data.get("RevenueTTM")),
                        "gross_profit_ttm": self._safe_float(data.get("GrossProfitTTM")),
                        "diluted_eps_ttm": self._safe_float(data.get("DilutedEPSTTM")),
                        "quarterly_earnings_growth": self._safe_float(data.get("QuarterlyEarningsGrowthYOY")),
                        "quarterly_revenue_growth": self._safe_float(data.get("QuarterlyRevenueGrowthYOY")),
                        "analyst_target_price": self._safe_float(data.get("AnalystTargetPrice")),
                        "trailing_pe": self._safe_float(data.get("TrailingPE")),
                        "forward_pe": self._safe_float(data.get("ForwardPE")),
                        "price_to_sales_ratio": self._safe_float(data.get("PriceToSalesRatioTTM")),
                        "price_to_book_ratio": self._safe_float(data.get("PriceToBookRatio")),
                        "ev_to_revenue": self._safe_float(data.get("EVToRevenue")),
                        "ev_to_ebitda": self._safe_float(data.get("EVToEBITDA")),
                        "beta": self._safe_float(data.get("Beta")),
                        "52_week_high": self._safe_float(data.get("52WeekHigh")),
                        "52_week_low": self._safe_float(data.get("52WeekLow")),
                        "50_day_moving_average": self._safe_float(data.get("50DayMovingAverage")),
                        "200_day_moving_average": self._safe_float(data.get("200DayMovingAverage")),
                        "shares_outstanding": self._safe_float(data.get("SharesOutstanding")),
                        "source": "alpha_vantage"
                    }
                else:
                    logger.error(f"Unexpected response format from Alpha Vantage: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {e}")
            return None
    
    async def get_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings data for a company."""
        if not self.api_key:
            return None
        
        params = {
            "function": "EARNINGS",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get("", params=params)
                
                if "symbol" in data:
                    annual_earnings = data.get("annualEarnings", [])
                    quarterly_earnings = data.get("quarterlyEarnings", [])
                    
                    return {
                        "symbol": data.get("symbol"),
                        "annual_earnings": [
                            {
                                "fiscal_date_ending": item.get("fiscalDateEnding"),
                                "reported_eps": self._safe_float(item.get("reportedEPS"))
                            }
                            for item in annual_earnings
                        ],
                        "quarterly_earnings": [
                            {
                                "fiscal_date_ending": item.get("fiscalDateEnding"),
                                "reported_date": item.get("reportedDate"),
                                "reported_eps": self._safe_float(item.get("reportedEPS")),
                                "estimated_eps": self._safe_float(item.get("estimatedEPS")),
                                "surprise": self._safe_float(item.get("surprise")),
                                "surprise_percentage": self._safe_float(item.get("surprisePercentage"))
                            }
                            for item in quarterly_earnings
                        ],
                        "source": "alpha_vantage"
                    }
                else:
                    logger.error(f"Unexpected response format from Alpha Vantage: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {e}")
            return None
    
    async def search_symbol(self, keywords: str) -> Optional[List[Dict[str, Any]]]:
        """Search for stock symbols by company name or keywords."""
        if not self.api_key:
            return None
        
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key
        }
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get("", params=params)
                
                if "bestMatches" in data:
                    matches = []
                    for match in data["bestMatches"]:
                        matches.append({
                            "symbol": match.get("1. symbol"),
                            "name": match.get("2. name"),
                            "type": match.get("3. type"),
                            "region": match.get("4. region"),
                            "market_open": match.get("5. marketOpen"),
                            "market_close": match.get("6. marketClose"),
                            "timezone": match.get("7. timezone"),
                            "currency": match.get("8. currency"),
                            "match_score": float(match.get("9. matchScore", 0))
                        })
                    
                    # Sort by match score (highest first)
                    matches.sort(key=lambda x: x["match_score"], reverse=True)
                    return matches
                else:
                    logger.error(f"Unexpected response format from Alpha Vantage: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching for symbol with keywords '{keywords}': {e}")
            return None
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == "None" or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

# Global instance
alpha_vantage_client = AlphaVantageClient()