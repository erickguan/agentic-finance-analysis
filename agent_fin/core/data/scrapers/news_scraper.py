import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import re
from urllib.parse import urljoin, urlparse

from agent_fin.core.utils.config import config
from agent_fin.core.utils.helpers import RateLimiter, clean_text, parse_date

logger = logging.getLogger(__name__)

class NewsWebScraper:
    """Web scraper for financial news from various sources."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter(30, 60)  # 30 requests per minute
        self.session = None
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_marketwatch_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape news from MarketWatch."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"MarketWatch returned status {response.status} for {symbol}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_articles = []
                
                # Find news articles (MarketWatch structure may change)
                news_elements = soup.find_all('div', class_=re.compile(r'article|news'))[:limit]
                
                for element in news_elements:
                    try:
                        title_elem = element.find('h3') or element.find('h2') or element.find('a')
                        if not title_elem:
                            continue
                        
                        title = clean_text(title_elem.get_text())
                        if not title:
                            continue
                        
                        link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                        link = ""
                        if link_elem and link_elem.get('href'):
                            link = urljoin(url, link_elem['href'])
                        
                        # Try to find publication date
                        date_elem = element.find('time') or element.find(class_=re.compile(r'date|time'))
                        published = ""
                        if date_elem:
                            date_text = date_elem.get('datetime') or date_elem.get_text()
                            parsed_date = parse_date(date_text)
                            if parsed_date:
                                published = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Try to find summary/excerpt
                        summary_elem = element.find('p') or element.find(class_=re.compile(r'summary|excerpt|description'))
                        summary = ""
                        if summary_elem:
                            summary = clean_text(summary_elem.get_text())
                        
                        news_articles.append({
                            "title": title,
                            "link": link,
                            "published": published,
                            "publisher": "MarketWatch",
                            "summary": summary,
                            "symbol": symbol.upper(),
                            "source": "marketwatch_scraper"
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing MarketWatch article: {e}")
                        continue
                
                self.rate_limiter.record_call()
                logger.info(f"Scraped {len(news_articles)} articles from MarketWatch for {symbol}")
                return news_articles
                
        except Exception as e:
            logger.error(f"Error scraping MarketWatch news for {symbol}: {e}")
            return []
    
    async def scrape_seeking_alpha_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape news from Seeking Alpha."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            url = f"https://seekingalpha.com/symbol/{symbol.upper()}/news"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Seeking Alpha returned status {response.status} for {symbol}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_articles = []
                
                # Find news articles (Seeking Alpha structure)
                article_elements = soup.find_all('article')[:limit]
                
                for element in article_elements:
                    try:
                        # Find title
                        title_elem = element.find('h3') or element.find('h2') or element.find('a', {'data-test-id': 'post-list-item-title'})
                        if not title_elem:
                            continue
                        
                        title = clean_text(title_elem.get_text())
                        if not title:
                            continue
                        
                        # Find link
                        link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                        link = ""
                        if link_elem and link_elem.get('href'):
                            link = urljoin("https://seekingalpha.com", link_elem['href'])
                        
                        # Find publication date
                        date_elem = element.find('time') or element.find(attrs={'data-test-id': 'post-list-date'})
                        published = ""
                        if date_elem:
                            date_text = date_elem.get('datetime') or date_elem.get_text()
                            parsed_date = parse_date(date_text)
                            if parsed_date:
                                published = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Find summary
                        summary_elem = element.find('p') or element.find(attrs={'data-test-id': 'post-list-content'})
                        summary = ""
                        if summary_elem:
                            summary = clean_text(summary_elem.get_text())
                        
                        news_articles.append({
                            "title": title,
                            "link": link,
                            "published": published,
                            "publisher": "Seeking Alpha",
                            "summary": summary,
                            "symbol": symbol.upper(),
                            "source": "seeking_alpha_scraper"
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Seeking Alpha article: {e}")
                        continue
                
                self.rate_limiter.record_call()
                logger.info(f"Scraped {len(news_articles)} articles from Seeking Alpha for {symbol}")
                return news_articles
                
        except Exception as e:
            logger.error(f"Error scraping Seeking Alpha news for {symbol}: {e}")
            return []
    
    async def scrape_reuters_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape news from Reuters."""
        try:
            await self.rate_limiter.wait_if_needed()
            
            # Reuters search URL
            url = f"https://www.reuters.com/search/news?blob={symbol}"
            
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Reuters returned status {response.status} for {symbol}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                news_articles = []
                
                # Find news articles (Reuters structure)
                search_results = soup.find_all('div', class_=re.compile(r'search-result|story'))[:limit]
                
                for element in search_results:
                    try:
                        # Find title
                        title_elem = element.find('h3') or element.find('h2') or element.find('a')
                        if not title_elem:
                            continue
                        
                        title = clean_text(title_elem.get_text())
                        if not title:
                            continue
                        
                        # Find link
                        link_elem = title_elem if title_elem.name == 'a' else title_elem.find('a')
                        link = ""
                        if link_elem and link_elem.get('href'):
                            link = urljoin("https://www.reuters.com", link_elem['href'])
                        
                        # Find publication date
                        date_elem = element.find('time') or element.find(class_=re.compile(r'date'))
                        published = ""
                        if date_elem:
                            date_text = date_elem.get('datetime') or date_elem.get_text()
                            parsed_date = parse_date(date_text)
                            if parsed_date:
                                published = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Find summary
                        summary_elem = element.find('p')
                        summary = ""
                        if summary_elem:
                            summary = clean_text(summary_elem.get_text())
                        
                        news_articles.append({
                            "title": title,
                            "link": link,
                            "published": published,
                            "publisher": "Reuters",
                            "summary": summary,
                            "symbol": symbol.upper(),
                            "source": "reuters_scraper"
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Reuters article: {e}")
                        continue
                
                self.rate_limiter.record_call()
                logger.info(f"Scraped {len(news_articles)} articles from Reuters for {symbol}")
                return news_articles
                
        except Exception as e:
            logger.error(f"Error scraping Reuters news for {symbol}: {e}")
            return []
    
    async def get_comprehensive_news(self, symbol: str, limit_per_source: int = 5) -> List[Dict[str, Any]]:
        """Get news from all available sources."""
        logger.info(f"Scraping comprehensive news for {symbol}")
        
        # Run all scrapers concurrently
        tasks = [
            self.scrape_marketwatch_news(symbol, limit_per_source),
            self.scrape_seeking_alpha_news(symbol, limit_per_source),
            self.scrape_reuters_news(symbol, limit_per_source)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_news = []
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            elif isinstance(result, Exception):
                logger.warning(f"Scraper failed: {result}")
        
        # Deduplicate and sort
        unique_news = self._deduplicate_news(all_news)
        unique_news.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        logger.info(f"Got {len(unique_news)} unique news articles for {symbol} from web scraping")
        return unique_news
    
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

# Global instance
news_scraper = NewsWebScraper()