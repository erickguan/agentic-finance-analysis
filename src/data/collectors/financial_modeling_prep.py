import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ...utils.config import config
from ...utils.helpers import APIClient, RateLimiter, clean_text

logger = logging.getLogger(__name__)

class FinancialModelingPrepClient:
    """Client for Financial Modeling Prep API to fetch stock data."""
    
    def __init__(self):
        self.api_key = config.get_api_key("fmp")
        self.rate_limiter = RateLimiter(config.FMP_RPM, 60)
        self.base_url = config.FMP_BASE_URL
        
        if not self.api_key:
            logger.warning("Financial Modeling Prep API key not found. Some features may be limited.")
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a stock symbol."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(f"quote/{symbol}", params={"apikey": self.api_key})
                
                if data and len(data) > 0:
                    quote = data[0]
                    return {
                        "symbol": quote.get("symbol", symbol),
                        "price": quote.get("price", 0),
                        "change": quote.get("change", 0),
                        "change_percent": quote.get("changesPercentage", 0),
                        "volume": quote.get("volume", 0),
                        "latest_trading_day": quote.get("timestamp", ""),
                        "previous_close": quote.get("previousClose", 0),
                        "open": quote.get("open", 0),
                        "high": quote.get("dayHigh", 0),
                        "low": quote.get("dayLow", 0),
                        "market_cap": quote.get("marketCap", 0),
                        "pe": quote.get("pe", 0),
                        "eps": quote.get("eps", 0),
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_daily_data(self, symbol: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """Get daily time series data for a stock symbol."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"historical-price-full/{symbol}",
                    params={"apikey": self.api_key, "limit": limit}
                )
                
                if data and "historical" in data:
                    historical = data["historical"]
                    
                    daily_data = []
                    for item in historical:
                        daily_data.append({
                            "date": item.get("date"),
                            "open": item.get("open", 0),
                            "high": item.get("high", 0),
                            "low": item.get("low", 0),
                            "close": item.get("close", 0),
                            "volume": item.get("volume", 0)
                        })
                    
                    return {
                        "symbol": data.get("symbol", symbol),
                        "last_refreshed": daily_data[0]["date"] if daily_data else None,
                        "data": daily_data,
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"Unexpected response format from FMP: {data}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching daily data for {symbol}: {e}")
            return None
    
    async def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company profile and fundamental data."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(f"profile/{symbol}", params={"apikey": self.api_key})
                
                if data and len(data) > 0:
                    profile = data[0]
                    return {
                        "symbol": profile.get("symbol"),
                        "name": profile.get("companyName"),
                        "description": clean_text(profile.get("description", "")),
                        "exchange": profile.get("exchangeShortName"),
                        "currency": profile.get("currency"),
                        "country": profile.get("country"),
                        "sector": profile.get("sector"),
                        "industry": profile.get("industry"),
                        "market_cap": profile.get("mktCap", 0),
                        "price": profile.get("price", 0),
                        "beta": profile.get("beta"),
                        "volume_avg": profile.get("volAvg"),
                        "last_div": profile.get("lastDiv"),
                        "range": profile.get("range"),
                        "changes": profile.get("changes"),
                        "cik": profile.get("cik"),
                        "isin": profile.get("isin"),
                        "cusip": profile.get("cusip"),
                        "website": profile.get("website"),
                        "ceo": profile.get("ceo"),
                        "employees": profile.get("fullTimeEmployees"),
                        "phone": profile.get("phone"),
                        "address": profile.get("address"),
                        "city": profile.get("city"),
                        "state": profile.get("state"),
                        "zip": profile.get("zip"),
                        "dcf_diff": profile.get("dcfDiff"),
                        "dcf": profile.get("dcf"),
                        "image": profile.get("image"),
                        "ipo_date": profile.get("ipoDate"),
                        "default_image": profile.get("defaultImage"),
                        "is_etf": profile.get("isEtf"),
                        "is_actively_trading": profile.get("isActivelyTrading"),
                        "is_adr": profile.get("isAdr"),
                        "is_fund": profile.get("isFund"),
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {e}")
            return None
    
    async def get_key_metrics(self, symbol: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get key financial metrics for a company."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"key-metrics/{symbol}",
                    params={"apikey": self.api_key, "limit": limit}
                )
                
                if data and len(data) > 0:
                    metrics_data = []
                    for item in data:
                        metrics_data.append({
                            "date": item.get("date"),
                            "calendar_year": item.get("calendarYear"),
                            "period": item.get("period"),
                            "revenue_per_share": item.get("revenuePerShare"),
                            "net_income_per_share": item.get("netIncomePerShare"),
                            "operating_cash_flow_per_share": item.get("operatingCashFlowPerShare"),
                            "free_cash_flow_per_share": item.get("freeCashFlowPerShare"),
                            "cash_per_share": item.get("cashPerShare"),
                            "book_value_per_share": item.get("bookValuePerShare"),
                            "tangible_book_value_per_share": item.get("tangibleBookValuePerShare"),
                            "shareholders_equity_per_share": item.get("shareholdersEquityPerShare"),
                            "interest_debt_per_share": item.get("interestDebtPerShare"),
                            "market_cap": item.get("marketCap"),
                            "enterprise_value": item.get("enterpriseValue"),
                            "pe_ratio": item.get("peRatio"),
                            "price_to_sales_ratio": item.get("priceToSalesRatio"),
                            "pocfratio": item.get("pocfratio"),
                            "pfcf_ratio": item.get("pfcfRatio"),
                            "pb_ratio": item.get("pbRatio"),
                            "ptb_ratio": item.get("ptbRatio"),
                            "ev_to_sales": item.get("evToSales"),
                            "enterprise_value_over_ebitda": item.get("enterpriseValueOverEBITDA"),
                            "ev_to_operating_cash_flow": item.get("evToOperatingCashFlow"),
                            "ev_to_free_cash_flow": item.get("evToFreeCashFlow"),
                            "earnings_yield": item.get("earningsYield"),
                            "free_cash_flow_yield": item.get("freeCashFlowYield"),
                            "debt_to_equity": item.get("debtToEquity"),
                            "debt_to_assets": item.get("debtToAssets"),
                            "net_debt_to_ebitda": item.get("netDebtToEBITDA"),
                            "current_ratio": item.get("currentRatio"),
                            "interest_coverage": item.get("interestCoverage"),
                            "income_quality": item.get("incomeQuality"),
                            "dividend_yield": item.get("dividendYield"),
                            "payout_ratio": item.get("payoutRatio"),
                            "sales_general_and_administrative_to_revenue": item.get("salesGeneralAndAdministrativeToRevenue"),
                            "research_and_development_to_revenue": item.get("researchAndDdevelopementToRevenue"),
                            "intangibles_to_total_assets": item.get("intangiblesToTotalAssets"),
                            "capex_to_operating_cash_flow": item.get("capexToOperatingCashFlow"),
                            "capex_to_revenue": item.get("capexToRevenue"),
                            "capex_to_depreciation": item.get("capexToDepreciation"),
                            "stock_based_compensation_to_revenue": item.get("stockBasedCompensationToRevenue"),
                            "graham_number": item.get("grahamNumber"),
                            "roic": item.get("roic"),
                            "return_on_tangible_assets": item.get("returnOnTangibleAssets"),
                            "graham_net_net": item.get("grahamNetNet"),
                            "working_capital": item.get("workingCapital"),
                            "tangible_asset_value": item.get("tangibleAssetValue"),
                            "net_current_asset_value": item.get("netCurrentAssetValue"),
                            "invested_capital": item.get("investedCapital"),
                            "average_receivables": item.get("averageReceivables"),
                            "average_payables": item.get("averagePayables"),
                            "average_inventory": item.get("averageInventory"),
                            "days_sales_outstanding": item.get("daysSalesOutstanding"),
                            "days_payables_outstanding": item.get("daysPayablesOutstanding"),
                            "days_of_inventory_on_hand": item.get("daysOfInventoryOnHand"),
                            "receivables_turnover": item.get("receivablesTurnover"),
                            "payables_turnover": item.get("payablesTurnover"),
                            "inventory_turnover": item.get("inventoryTurnover"),
                            "roe": item.get("roe"),
                            "capex_per_share": item.get("capexPerShare")
                        })
                    
                    return {
                        "symbol": symbol,
                        "key_metrics": metrics_data,
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching key metrics for {symbol}: {e}")
            return None
    
    async def get_financial_ratios(self, symbol: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Get financial ratios for a company."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"ratios/{symbol}",
                    params={"apikey": self.api_key, "limit": limit}
                )
                
                if data and len(data) > 0:
                    return {
                        "symbol": symbol,
                        "financial_ratios": data,
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching financial ratios for {symbol}: {e}")
            return None
    
    async def get_earnings_calendar(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings calendar for a company."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"earning_calendar",
                    params={"apikey": self.api_key, "symbol": symbol}
                )
                
                if data and len(data) > 0:
                    earnings_data = []
                    for item in data:
                        earnings_data.append({
                            "date": item.get("date"),
                            "symbol": item.get("symbol"),
                            "eps": item.get("eps"),
                            "eps_estimated": item.get("epsEstimated"),
                            "time": item.get("time"),
                            "revenue": item.get("revenue"),
                            "revenue_estimated": item.get("revenueEstimated"),
                            "updated_from_date": item.get("updatedFromDate"),
                            "fiscal_date_ending": item.get("fiscalDateEnding")
                        })
                    
                    return {
                        "symbol": symbol,
                        "earnings_calendar": earnings_data,
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No earnings calendar data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {symbol}: {e}")
            return None
    
    async def get_analyst_estimates(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst estimates for a company."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"analyst-estimates/{symbol}",
                    params={"apikey": self.api_key}
                )
                
                if data and len(data) > 0:
                    return {
                        "symbol": symbol,
                        "analyst_estimates": data,
                        "source": "financial_modeling_prep"
                    }
                else:
                    logger.error(f"No analyst estimates returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching analyst estimates for {symbol}: {e}")
            return None
    
    async def get_stock_news(self, symbol: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """Get recent news for a stock symbol."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"stock_news",
                    params={"apikey": self.api_key, "tickers": symbol, "limit": limit}
                )
                
                if data and len(data) > 0:
                    news_data = []
                    for article in data:
                        news_data.append({
                            "title": clean_text(article.get("title", "")),
                            "url": article.get("url", ""),
                            "published_date": article.get("publishedDate", ""),
                            "site": article.get("site", ""),
                            "text": clean_text(article.get("text", "")),
                            "symbol": article.get("symbol", symbol),
                            "source": "financial_modeling_prep"
                        })
                    
                    return news_data
                else:
                    logger.error(f"No news data returned from FMP for symbol: {symbol}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return None
    
    async def search_symbol(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Search for stock symbols by company name or keywords."""
        if not self.api_key:
            return None
        
        try:
            async with APIClient(self.base_url, self.rate_limiter) as client:
                data = await client.get(
                    f"search",
                    params={"apikey": self.api_key, "query": query, "limit": limit}
                )
                
                if data and len(data) > 0:
                    matches = []
                    for match in data:
                        matches.append({
                            "symbol": match.get("symbol"),
                            "name": match.get("name"),
                            "currency": match.get("currency"),
                            "stock_exchange": match.get("stockExchange"),
                            "exchange_short_name": match.get("exchangeShortName")
                        })
                    
                    return matches
                else:
                    logger.error(f"No search results returned from FMP for query: {query}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching for symbol with query '{query}': {e}")
            return None

# Global instance
fmp_client = FinancialModelingPrepClient()