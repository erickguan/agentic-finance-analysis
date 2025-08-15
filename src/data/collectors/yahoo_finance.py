import asyncio
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import pandas as pd

from ...utils.config import config
from ...utils.helpers import RateLimiter, clean_text

logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """Client for Yahoo Finance API to fetch stock data."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(config.YAHOO_FINANCE_RPM, 60)
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a stock symbol."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Run yfinance in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            self.rate_limiter.record_call()
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            return {
                "symbol": info.get("symbol", symbol),
                "price": info.get("regularMarketPrice", 0),
                "change": info.get("regularMarketChange", 0),
                "change_percent": info.get("regularMarketChangePercent", 0) * 100,  # Convert to percentage
                "volume": info.get("regularMarketVolume", 0),
                "latest_trading_day": datetime.now().strftime("%Y-%m-%d"),
                "previous_close": info.get("previousClose", 0),
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "market_cap": info.get("marketCap", 0),
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    async def get_daily_data(self, symbol: str, period: str = "1y") -> Optional[Dict[str, Any]]:
        """Get daily time series data for a stock symbol."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            hist = await loop.run_in_executor(None, lambda: ticker.history(period=period))
            
            self.rate_limiter.record_call()
            
            if hist.empty:
                return None
            
            # Convert DataFrame to list of dictionaries
            daily_data = []
            for date, row in hist.iterrows():
                daily_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            # Sort by date (most recent first)
            daily_data.sort(key=lambda x: x["date"], reverse=True)
            
            return {
                "symbol": symbol,
                "last_refreshed": daily_data[0]["date"] if daily_data else None,
                "data": daily_data,
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching daily data for {symbol}: {e}")
            return None
    
    async def get_company_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company information and fundamental data."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            
            self.rate_limiter.record_call()
            
            if not info:
                return None
            
            return {
                "symbol": info.get("symbol", symbol),
                "name": info.get("longName", info.get("shortName", "")),
                "description": clean_text(info.get("longBusinessSummary", "")),
                "exchange": info.get("exchange", ""),
                "currency": info.get("currency", "USD"),
                "country": info.get("country", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "book_value": info.get("bookValue"),
                "dividend_rate": info.get("dividendRate"),
                "dividend_yield": info.get("dividendYield"),
                "eps": info.get("trailingEps"),
                "revenue_per_share": info.get("revenuePerShare"),
                "profit_margin": info.get("profitMargins"),
                "operating_margin": info.get("operatingMargins"),
                "return_on_assets": info.get("returnOnAssets"),
                "return_on_equity": info.get("returnOnEquity"),
                "revenue_ttm": info.get("totalRevenue"),
                "gross_profit": info.get("grossProfits"),
                "ebitda": info.get("ebitda"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash"),
                "free_cash_flow": info.get("freeCashflow"),
                "operating_cash_flow": info.get("operatingCashflow"),
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation_mean": info.get("recommendationMean"),
                "recommendation_key": info.get("recommendationKey"),
                "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
                "beta": info.get("beta"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "50_day_average": info.get("fiftyDayAverage"),
                "200_day_average": info.get("twoHundredDayAverage"),
                "shares_outstanding": info.get("sharesOutstanding"),
                "float_shares": info.get("floatShares"),
                "held_percent_insiders": info.get("heldPercentInsiders"),
                "held_percent_institutions": info.get("heldPercentInstitutions"),
                "short_ratio": info.get("shortRatio"),
                "short_percent_of_float": info.get("shortPercentOfFloat"),
                "website": info.get("website", ""),
                "employees": info.get("fullTimeEmployees"),
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            return None
    
    async def get_earnings_calendar(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get earnings calendar data."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            calendar = await loop.run_in_executor(None, lambda: ticker.calendar)
            
            self.rate_limiter.record_call()
            
            if calendar is None or calendar.empty:
                return None
            
            # Convert calendar data to dictionary
            earnings_data = []
            for date, row in calendar.iterrows():
                earnings_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "eps_estimate": float(row.get("Earnings Estimate", 0)) if pd.notna(row.get("Earnings Estimate")) else None,
                    "revenue_estimate": float(row.get("Revenue Estimate", 0)) if pd.notna(row.get("Revenue Estimate")) else None,
                })
            
            return {
                "symbol": symbol,
                "earnings_calendar": earnings_data,
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching earnings calendar for {symbol}: {e}")
            return None
    
    async def get_analyst_recommendations(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst recommendations."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            recommendations = await loop.run_in_executor(None, lambda: ticker.recommendations)
            
            self.rate_limiter.record_call()
            
            if recommendations is None or recommendations.empty:
                return None
            
            # Convert recommendations to list of dictionaries
            rec_data = []
            for date, row in recommendations.iterrows():
                rec_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "firm": row.get("Firm", ""),
                    "to_grade": row.get("To Grade", ""),
                    "from_grade": row.get("From Grade", ""),
                    "action": row.get("Action", "")
                })
            
            # Sort by date (most recent first)
            rec_data.sort(key=lambda x: x["date"], reverse=True)
            
            return {
                "symbol": symbol,
                "recommendations": rec_data,
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching analyst recommendations for {symbol}: {e}")
            return None
    
    async def get_news(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """Get recent news for a stock symbol."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            news = await loop.run_in_executor(None, lambda: ticker.news)
            
            self.rate_limiter.record_call()
            
            if not news:
                return None
            
            news_data = []
            for article in news:
                news_data.append({
                    "title": clean_text(article.get("title", "")),
                    "link": article.get("link", ""),
                    "published": datetime.fromtimestamp(article.get("providerPublishTime", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                    "publisher": article.get("publisher", ""),
                    "summary": clean_text(article.get("summary", "")),
                    "source": "yahoo_finance"
                })
            
            return news_data
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return None
    
    async def search_symbol(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Search for stock symbols by company name."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Use yfinance's Ticker to search (limited functionality)
            # This is a basic implementation - Yahoo Finance doesn't have a great search API
            loop = asyncio.get_event_loop()
            
            # Try to get info for the query as a symbol first
            try:
                ticker = await loop.run_in_executor(None, yf.Ticker, query.upper())
                info = await loop.run_in_executor(None, lambda: ticker.info)
                
                if info and info.get("symbol"):
                    return [{
                        "symbol": info.get("symbol"),
                        "name": info.get("longName", info.get("shortName", "")),
                        "exchange": info.get("exchange", ""),
                        "currency": info.get("currency", "USD"),
                        "match_score": 1.0
                    }]
            except:
                pass
            
            self.rate_limiter.record_call()
            return None
            
        except Exception as e:
            logger.error(f"Error searching for symbol with query '{query}': {e}")
            return None
    
    async def get_financial_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive financial data including income statement, balance sheet, and cash flow."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            
            # Get financial statements
            financials = await loop.run_in_executor(None, lambda: ticker.financials)
            balance_sheet = await loop.run_in_executor(None, lambda: ticker.balance_sheet)
            cash_flow = await loop.run_in_executor(None, lambda: ticker.cashflow)
            
            self.rate_limiter.record_call()
            
            result = {"symbol": symbol, "source": "yahoo_finance"}
            
            # Process financials (income statement)
            if financials is not None and not financials.empty:
                result["income_statement"] = self._process_financial_dataframe(financials)
            
            # Process balance sheet
            if balance_sheet is not None and not balance_sheet.empty:
                result["balance_sheet"] = self._process_financial_dataframe(balance_sheet)
            
            # Process cash flow
            if cash_flow is not None and not cash_flow.empty:
                result["cash_flow"] = self._process_financial_dataframe(cash_flow)
            
            return result if len(result) > 2 else None  # Return only if we have actual data
            
        except Exception as e:
            logger.error(f"Error fetching financial data for {symbol}: {e}")
            return None
    
    def _process_financial_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert financial DataFrame to list of dictionaries."""
        result = []
        for date, column in df.items():
            date_data = {"date": date.strftime("%Y-%m-%d")}
            for index, value in column.items():
                if pd.notna(value):
                    date_data[str(index)] = float(value) if isinstance(value, (int, float)) else str(value)
            result.append(date_data)
        
        # Sort by date (most recent first)
        result.sort(key=lambda x: x["date"], reverse=True)
        return result

# Global instance
yahoo_finance_client = YahooFinanceClient()