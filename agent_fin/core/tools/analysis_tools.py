"""
Analysis Tools for Financial Analysis

Tools that perform technical, fundamental, and sentiment analysis on financial data.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from langchain.tools import Tool
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TechnicalAnalysisInput(BaseModel):
    """Input for technical analysis tools."""
    price_data: List[Dict[str, Any]] = Field(description="Historical price data with date, open, high, low, close, volume")

class FundamentalAnalysisInput(BaseModel):
    """Input for fundamental analysis tools."""
    financial_data: Dict[str, Any] = Field(description="Financial data including ratios and metrics")
    
class SentimentAnalysisInput(BaseModel):
    """Input for sentiment analysis tools."""
    news_articles: List[Dict[str, Any]] = Field(description="List of news articles with title and content")

class AnalysisTools:
    """Collection of analysis tools for financial calculations."""
    
    def __init__(self):
        pass
    
    def calculate_moving_averages(self, price_data: List[Dict[str, Any]], periods: List[int] = [20, 50, 200]) -> Dict[str, Any]:
        """Calculate moving averages for given periods."""
        try:
            if not price_data:
                return {"error": "No price data provided"}
            
            # Convert to DataFrame for easier calculation
            df = pd.DataFrame(price_data)
            if 'close' not in df.columns:
                return {"error": "Price data missing 'close' column"}
            
            # Sort by date to ensure proper order
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            prices = df['close'].astype(float)
            current_price = float(prices.iloc[-1])
            
            moving_averages = {}
            signals = []
            
            for period in periods:
                if len(prices) >= period:
                    ma = prices.rolling(window=period).mean()
                    current_ma = float(ma.iloc[-1])
                    moving_averages[f"MA_{period}"] = current_ma
                    
                    # Simple signal generation
                    if current_price > current_ma:
                        signals.append(f"Price above MA{period} (bullish)")
                    else:
                        signals.append(f"Price below MA{period} (bearish)")
                else:
                    moving_averages[f"MA_{period}"] = None
            
            return {
                "current_price": current_price,
                "moving_averages": moving_averages,
                "signals": signals,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return {"error": str(e)}
    
    def calculate_rsi(self, price_data: List[Dict[str, Any]], period: int = 14) -> Dict[str, Any]:
        """Calculate Relative Strength Index (RSI)."""
        try:
            if not price_data or len(price_data) < period + 1:
                return {"error": "Insufficient price data for RSI calculation"}
            
            df = pd.DataFrame(price_data)
            if 'close' not in df.columns:
                return {"error": "Price data missing 'close' column"}
            
            # Sort by date
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            prices = df['close'].astype(float)
            
            # Calculate price changes
            delta = prices.diff()
            
            # Separate gains and losses
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Calculate RSI
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = float(rsi.iloc[-1])
            
            # Generate signals
            signals = []
            if current_rsi > 70:
                signals.append("RSI above 70 (overbought)")
            elif current_rsi < 30:
                signals.append("RSI below 30 (oversold)")
            else:
                signals.append("RSI in neutral range")
            
            return {
                "rsi": current_rsi,
                "signals": signals,
                "interpretation": self._interpret_rsi(current_rsi),
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return {"error": str(e)}
    
    def calculate_volatility(self, price_data: List[Dict[str, Any]], period: int = 30) -> Dict[str, Any]:
        """Calculate price volatility."""
        try:
            if not price_data or len(price_data) < period:
                return {"error": "Insufficient price data for volatility calculation"}
            
            df = pd.DataFrame(price_data)
            if 'close' not in df.columns:
                return {"error": "Price data missing 'close' column"}
            
            # Sort by date
            if 'date' in df.columns:
                df = df.sort_values('date')
            
            prices = df['close'].astype(float)
            
            # Calculate daily returns
            returns = prices.pct_change().dropna()
            
            # Calculate volatility (annualized)
            daily_volatility = returns.rolling(window=period).std()
            annualized_volatility = daily_volatility * np.sqrt(252)  # 252 trading days
            current_volatility = float(annualized_volatility.iloc[-1])
            
            # Interpret volatility level
            interpretation = self._interpret_volatility(current_volatility)
            
            return {
                "volatility_annualized": current_volatility,
                "volatility_percent": current_volatility * 100,
                "interpretation": interpretation,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return {"error": str(e)}
    
    def calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate key financial ratios from financial data."""
        try:
            if not financial_data:
                return {"error": "No financial data provided"}
            
            ratios = {}
            company_data = financial_data.get("company", {})
            
            # P/E Ratio
            pe_ratio = company_data.get("pe_ratio")
            if pe_ratio:
                ratios["pe_ratio"] = {
                    "value": pe_ratio,
                    "interpretation": self._interpret_pe_ratio(pe_ratio)
                }
            
            # Price to Book Ratio
            pb_ratio = company_data.get("price_to_book_ratio")
            if pb_ratio:
                ratios["pb_ratio"] = {
                    "value": pb_ratio,
                    "interpretation": self._interpret_pb_ratio(pb_ratio)
                }
            
            # Debt to Equity
            debt_equity = company_data.get("debt_to_equity")
            if debt_equity:
                ratios["debt_to_equity"] = {
                    "value": debt_equity,
                    "interpretation": self._interpret_debt_equity(debt_equity)
                }
            
            # Return on Equity
            roe = company_data.get("return_on_equity")
            if roe:
                ratios["roe"] = {
                    "value": roe,
                    "interpretation": self._interpret_roe(roe)
                }
            
            # Market Cap
            market_cap = company_data.get("market_cap")
            if market_cap:
                ratios["market_cap"] = {
                    "value": market_cap,
                    "formatted": self._format_market_cap(market_cap)
                }
            
            return {
                "ratios": ratios,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {e}")
            return {"error": str(e)}
    
    def analyze_news_sentiment(self, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles (basic implementation for POC)."""
        try:
            if not news_articles:
                return {"error": "No news articles provided"}
            
            # Basic keyword-based sentiment analysis for POC
            positive_keywords = [
                'growth', 'profit', 'revenue', 'beat', 'exceed', 'strong', 'positive', 
                'bullish', 'upgrade', 'outperform', 'buy', 'surge', 'rally', 'gain'
            ]
            
            negative_keywords = [
                'loss', 'decline', 'drop', 'fall', 'weak', 'negative', 'bearish', 
                'downgrade', 'underperform', 'sell', 'crash', 'plunge', 'miss'
            ]
            
            total_articles = len(news_articles)
            sentiment_scores = []
            
            for article in news_articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                content = f"{title} {summary}"
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in content)
                negative_count = sum(1 for keyword in negative_keywords if keyword in content)
                
                # Simple scoring: +1 for positive, -1 for negative, 0 for neutral
                if positive_count > negative_count:
                    sentiment_scores.append(1)
                elif negative_count > positive_count:
                    sentiment_scores.append(-1)
                else:
                    sentiment_scores.append(0)
            
            # Calculate overall sentiment
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                positive_articles = sum(1 for score in sentiment_scores if score > 0)
                negative_articles = sum(1 for score in sentiment_scores if score < 0)
                neutral_articles = total_articles - positive_articles - negative_articles
            else:
                avg_sentiment = 0
                positive_articles = negative_articles = neutral_articles = 0
            
            # Interpret overall sentiment
            if avg_sentiment > 0.2:
                overall_sentiment = "Positive"
            elif avg_sentiment < -0.2:
                overall_sentiment = "Negative" 
            else:
                overall_sentiment = "Neutral"
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": avg_sentiment,
                "article_breakdown": {
                    "total_articles": total_articles,
                    "positive": positive_articles,
                    "negative": negative_articles,
                    "neutral": neutral_articles
                },
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {"error": str(e)}
    
    def calculate_risk_metrics(self, price_data: List[Dict[str, Any]], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various risk metrics."""
        try:
            risk_metrics = {}
            
            # Calculate volatility-based risk
            if price_data:
                volatility_result = self.calculate_volatility(price_data)
                if "volatility_annualized" in volatility_result:
                    risk_metrics["volatility_risk"] = {
                        "value": volatility_result["volatility_annualized"],
                        "level": volatility_result["interpretation"]
                    }
            
            # Financial strength risk indicators
            company_data = financial_data.get("company", {})
            
            # Debt-to-equity risk
            debt_equity = company_data.get("debt_to_equity")
            if debt_equity:
                risk_level = "High" if debt_equity > 2 else "Medium" if debt_equity > 1 else "Low"
                risk_metrics["debt_risk"] = {
                    "value": debt_equity,
                    "level": risk_level
                }
            
            # Beta risk (if available)
            beta = company_data.get("beta")
            if beta:
                risk_level = "High" if abs(beta) > 1.5 else "Medium" if abs(beta) > 1 else "Low"
                risk_metrics["market_risk"] = {
                    "value": beta,
                    "level": risk_level
                }
            
            # Overall risk assessment
            risk_factors = [
                risk_metrics.get("volatility_risk", {}).get("level", "Unknown"),
                risk_metrics.get("debt_risk", {}).get("level", "Unknown"),
                risk_metrics.get("market_risk", {}).get("level", "Unknown")
            ]
            
            high_risk_count = risk_factors.count("High")
            medium_risk_count = risk_factors.count("Medium")
            
            if high_risk_count >= 2:
                overall_risk = "High"
            elif high_risk_count >= 1 or medium_risk_count >= 2:
                overall_risk = "Medium"
            else:
                overall_risk = "Low"
            
            return {
                "risk_metrics": risk_metrics,
                "overall_risk_level": overall_risk,
                "calculation_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {"error": str(e)}
    
    # Helper methods for interpretations
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value."""
        if rsi > 70:
            return "Overbought - potential sell signal"
        elif rsi < 30:
            return "Oversold - potential buy signal"
        else:
            return "Neutral - no strong signal"
    
    def _interpret_volatility(self, volatility: float) -> str:
        """Interpret volatility level."""
        if volatility > 0.4:
            return "High"
        elif volatility > 0.2:
            return "Medium"
        else:
            return "Low"
    
    def _interpret_pe_ratio(self, pe: float) -> str:
        """Interpret P/E ratio."""
        if pe > 25:
            return "High (potentially overvalued)"
        elif pe > 15:
            return "Moderate"
        else:
            return "Low (potentially undervalued)"
    
    def _interpret_pb_ratio(self, pb: float) -> str:
        """Interpret Price-to-Book ratio."""
        if pb > 3:
            return "High (potentially overvalued)"
        elif pb > 1:
            return "Moderate"
        else:
            return "Low (potentially undervalued)"
    
    def _interpret_debt_equity(self, de: float) -> str:
        """Interpret debt-to-equity ratio."""
        if de > 2:
            return "High leverage (risky)"
        elif de > 1:
            return "Moderate leverage"
        else:
            return "Low leverage (conservative)"
    
    def _interpret_roe(self, roe: float) -> str:
        """Interpret Return on Equity."""
        if roe > 0.2:
            return "Excellent"
        elif roe > 0.15:
            return "Good"
        elif roe > 0.1:
            return "Average"
        else:
            return "Below average"
    
    def _format_market_cap(self, market_cap: float) -> str:
        """Format market cap in readable format."""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:.2f}"
    
    def get_langchain_tools(self) -> List[Tool]:
        """Get LangChain Tool objects for use by agents."""
        
        return [
            Tool(
                name="calculate_moving_averages",
                description="Calculate moving averages for stock price data. Input: JSON string of price data with date, close columns",
                func=lambda data: str(self.calculate_moving_averages(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="calculate_rsi",
                description="Calculate RSI (Relative Strength Index) for stock price data. Input: JSON string of price data",
                func=lambda data: str(self.calculate_rsi(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="calculate_volatility", 
                description="Calculate price volatility for stock data. Input: JSON string of price data",
                func=lambda data: str(self.calculate_volatility(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="calculate_financial_ratios",
                description="Calculate key financial ratios from company financial data. Input: JSON string of financial data",
                func=lambda data: str(self.calculate_financial_ratios(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="analyze_news_sentiment",
                description="Analyze sentiment of news articles. Input: JSON string of news articles list",
                func=lambda data: str(self.analyze_news_sentiment(eval(data) if isinstance(data, str) else data))
            ),
            Tool(
                name="calculate_risk_metrics",
                description="Calculate various risk metrics from price and financial data. Input: price_data,financial_data as JSON string",
                func=lambda data: str(self.calculate_risk_metrics(*eval(data) if isinstance(data, str) else data))
            )
        ]

# Global instance
analysis_tools = AnalysisTools()