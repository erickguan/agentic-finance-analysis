import os
import pickle
import asyncio
import numpy as np
import faiss
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from agent_fin.core.utils.config import config
from .embeddings import embedding_manager

logger = logging.getLogger(__name__)

class FAISSVectorDB:
    """FAISS vector database manager for storing and retrieving company information."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.VECTOR_DB_PATH
        self.dimension = config.EMBEDDING_DIMENSION
        self.index = None
        self.documents = []  # Store original documents
        self.metadata = []   # Store metadata for each document
        self.company_index = {}  # Map company symbols to document indices
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize or load existing index
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index or load existing one."""
        index_file = f"{self.db_path}/faiss.index"
        metadata_file = f"{self.db_path}/metadata.pkl"
        documents_file = f"{self.db_path}/documents.pkl"
        company_index_file = f"{self.db_path}/company_index.pkl"
        
        if os.path.exists(index_file) and os.path.exists(metadata_file):
            try:
                # Load existing index
                self.index = faiss.read_index(index_file)
                
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                with open(documents_file, 'rb') as f:
                    self.documents = pickle.load(f)
                
                if os.path.exists(company_index_file):
                    with open(company_index_file, 'rb') as f:
                        self.company_index = pickle.load(f)
                
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            except Exception as e:
                logger.error(f"Error loading existing index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Use IndexFlatIP for cosine similarity (after L2 normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.documents = []
        self.metadata = []
        self.company_index = {}
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    async def add_company_data(self, symbol: str, company_data: Dict[str, Any]) -> bool:
        """Add comprehensive company data to the vector database."""
        try:
            documents_to_add = []
            
            # Process different types of data
            if company_data.get("company"):
                company_info = company_data["company"]
                
                # Company overview document
                overview_text = self._format_company_overview(symbol, company_info)
                documents_to_add.append({
                    "text": overview_text,
                    "type": "company_overview",
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Financial data
            if company_data.get("financial"):
                financial_info = company_data["financial"]
                financial_text = self._format_financial_data(symbol, financial_info)
                documents_to_add.append({
                    "text": financial_text,
                    "type": "financial_data",
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Historical performance
            if company_data.get("historical"):
                historical_info = company_data["historical"]
                historical_text = self._format_historical_data(symbol, historical_info)
                documents_to_add.append({
                    "text": historical_text,
                    "type": "historical_data",
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat()
                })
            
            # News articles
            if company_data.get("news"):
                for article in company_data["news"][:10]:  # Limit to recent 10 articles
                    news_text = self._format_news_article(symbol, article)
                    documents_to_add.append({
                        "text": news_text,
                        "type": "news_article",
                        "symbol": symbol,
                        "timestamp": datetime.now().isoformat(),
                        "article_date": article.get("published", ""),
                        "source": article.get("source", "")
                    })
            
            # Analyst data
            if company_data.get("analyst"):
                analyst_info = company_data["analyst"]
                analyst_text = self._format_analyst_data(symbol, analyst_info)
                documents_to_add.append({
                    "text": analyst_text,
                    "type": "analyst_data",
                    "symbol": symbol,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Generate embeddings and add to index
            if documents_to_add:
                await self._add_documents(documents_to_add)
                logger.info(f"Added {len(documents_to_add)} documents for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding company data for {symbol}: {e}")
            return False
    
    async def _add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the FAISS index."""
        texts = [doc["text"] for doc in documents]
        
        # Generate embeddings
        embeddings = await embedding_manager.get_embeddings(texts)
        
        if not embeddings:
            logger.error("Failed to generate embeddings")
            return
        
        # Convert to numpy array and normalize for cosine similarity
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        start_idx = len(self.documents)
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        for i, doc in enumerate(documents):
            self.documents.append(doc["text"])
            self.metadata.append(doc)
            
            # Update company index
            symbol = doc["symbol"]
            if symbol not in self.company_index:
                self.company_index[symbol] = []
            self.company_index[symbol].append(start_idx + i)
        
        # Save to disk
        self._save_index()
    
    def _save_index(self):
        """Save the FAISS index and metadata to disk."""
        try:
            index_file = f"{self.db_path}/faiss.index"
            metadata_file = f"{self.db_path}/metadata.pkl"
            documents_file = f"{self.db_path}/documents.pkl"
            company_index_file = f"{self.db_path}/company_index.pkl"
            
            faiss.write_index(self.index, index_file)
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            with open(documents_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            with open(company_index_file, 'wb') as f:
                pickle.dump(self.company_index, f)
            
            logger.debug("Saved FAISS index to disk")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    async def search(self, query: str, k: int = 5, symbol_filter: str = None) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database."""
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector database is empty")
                return []
            
            # Generate query embedding
            query_embeddings = await embedding_manager.get_embeddings([query])
            if not query_embeddings:
                logger.error("Failed to generate query embedding")
                return []
            
            # Convert to numpy array and normalize
            query_vector = np.array(query_embeddings, dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Search
            if symbol_filter:
                # Filter by symbol
                candidate_indices = self.company_index.get(symbol_filter.upper(), [])
                if not candidate_indices:
                    return []
                
                # Create a subset index for the specific company
                candidate_vectors = np.array([
                    self.index.reconstruct(idx) for idx in candidate_indices
                ], dtype=np.float32)
                
                # Search within the subset
                scores, indices = faiss.knn(query_vector, candidate_vectors, min(k, len(candidate_indices)))
                
                # Map back to original indices
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx < len(candidate_indices):
                        original_idx = candidate_indices[idx]
                        results.append({
                            "text": self.documents[original_idx],
                            "metadata": self.metadata[original_idx],
                            "score": float(score),
                            "index": original_idx
                        })
            else:
                # Search entire index
                scores, indices = self.index.search(query_vector, k)
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.documents):
                        results.append({
                            "text": self.documents[idx],
                            "metadata": self.metadata[idx],
                            "score": float(score),
                            "index": idx
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def get_company_documents(self, symbol: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific company."""
        indices = self.company_index.get(symbol.upper(), [])
        
        documents = []
        for idx in indices:
            if idx < len(self.documents):
                documents.append({
                    "text": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "index": idx
                })
        
        return documents
    
    def remove_company_data(self, symbol: str) -> bool:
        """Remove all data for a specific company."""
        try:
            indices = self.company_index.get(symbol.upper(), [])
            if not indices:
                return False
            
            # Mark documents for removal (FAISS doesn't support direct removal)
            # We'll need to rebuild the index
            remaining_documents = []
            remaining_metadata = []
            new_company_index = {}
            
            for i, (doc, meta) in enumerate(zip(self.documents, self.metadata)):
                if i not in indices:
                    new_idx = len(remaining_documents)
                    remaining_documents.append(doc)
                    remaining_metadata.append(meta)
                    
                    # Update company index
                    doc_symbol = meta.get("symbol", "").upper()
                    if doc_symbol not in new_company_index:
                        new_company_index[doc_symbol] = []
                    new_company_index[doc_symbol].append(new_idx)
            
            # Rebuild index if we removed documents
            if len(remaining_documents) < len(self.documents):
                self.documents = remaining_documents
                self.metadata = remaining_metadata
                self.company_index = new_company_index
                
                # Rebuild FAISS index
                if remaining_documents:
                    asyncio.create_task(self._rebuild_index())
                else:
                    self._create_new_index()
                
                logger.info(f"Removed data for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing company data for {symbol}: {e}")
            return False
    
    async def _rebuild_index(self):
        """Rebuild the FAISS index from existing documents."""
        try:
            if not self.documents:
                self._create_new_index()
                return
            
            # Generate embeddings for all documents
            embeddings = await embedding_manager.get_embeddings(self.documents)
            if not embeddings:
                logger.error("Failed to generate embeddings for index rebuild")
                return
            
            # Create new index
            self.index = faiss.IndexFlatIP(self.dimension)
            
            # Add embeddings
            embeddings_array = np.array(embeddings, dtype=np.float32)
            faiss.normalize_L2(embeddings_array)
            self.index.add(embeddings_array)
            
            # Save to disk
            self._save_index()
            
            logger.info(f"Rebuilt FAISS index with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
    
    def _format_company_overview(self, symbol: str, company_info: Dict[str, Any]) -> str:
        """Format company information into a searchable text."""
        parts = [f"Company: {company_info.get('name', symbol)} ({symbol})"]
        
        if company_info.get('description'):
            parts.append(f"Description: {company_info['description']}")
        
        if company_info.get('sector'):
            parts.append(f"Sector: {company_info['sector']}")
        
        if company_info.get('industry'):
            parts.append(f"Industry: {company_info['industry']}")
        
        if company_info.get('market_cap'):
            parts.append(f"Market Cap: ${company_info['market_cap']:,}")
        
        if company_info.get('employees'):
            parts.append(f"Employees: {company_info['employees']:,}")
        
        return " | ".join(parts)
    
    def _format_financial_data(self, symbol: str, financial_info: Dict[str, Any]) -> str:
        """Format financial data into searchable text."""
        parts = [f"Financial Data for {symbol}"]
        
        # Key metrics
        if "key_metrics" in financial_info:
            metrics = financial_info["key_metrics"].get("key_metrics", [])
            if metrics:
                latest = metrics[0]
                if latest.get("pe_ratio"):
                    parts.append(f"P/E Ratio: {latest['pe_ratio']:.2f}")
                if latest.get("debt_to_equity"):
                    parts.append(f"Debt-to-Equity: {latest['debt_to_equity']:.2f}")
                if latest.get("roe"):
                    parts.append(f"ROE: {latest['roe']:.2%}")
        
        return " | ".join(parts)
    
    def _format_historical_data(self, symbol: str, historical_info: Dict[str, Any]) -> str:
        """Format historical data into searchable text."""
        data = historical_info.get("data", [])
        if not data:
            return f"Historical data for {symbol}"
        
        recent_data = data[:30]  # Last 30 days
        prices = [d["close"] for d in recent_data if d.get("close")]
        
        if len(prices) >= 2:
            current_price = prices[0]
            month_ago_price = prices[-1]
            change_percent = ((current_price - month_ago_price) / month_ago_price) * 100
            
            return f"Historical Performance for {symbol}: Current ${current_price:.2f}, 30-day change: {change_percent:+.2f}%"
        
        return f"Historical data for {symbol}"
    
    def _format_news_article(self, symbol: str, article: Dict[str, Any]) -> str:
        """Format news article into searchable text."""
        parts = [f"News for {symbol}"]
        
        if article.get("title"):
            parts.append(f"Title: {article['title']}")
        
        if article.get("summary"):
            parts.append(f"Summary: {article['summary']}")
        
        if article.get("published"):
            parts.append(f"Published: {article['published']}")
        
        if article.get("publisher"):
            parts.append(f"Source: {article['publisher']}")
        
        return " | ".join(parts)
    
    def _format_analyst_data(self, symbol: str, analyst_info: Dict[str, Any]) -> str:
        """Format analyst data into searchable text."""
        parts = [f"Analyst Data for {symbol}"]
        
        if "recommendations" in analyst_info:
            recs = analyst_info["recommendations"].get("recommendations", [])
            if recs:
                recent_recs = recs[:5]
                rec_summary = ", ".join([r.get("to_grade", "") for r in recent_recs if r.get("to_grade")])
                if rec_summary:
                    parts.append(f"Recent Recommendations: {rec_summary}")
        
        return " | ".join(parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        return {
            "total_documents": len(self.documents),
            "total_companies": len(self.company_index),
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "companies": list(self.company_index.keys())
        }

# Global instance
vector_db = FAISSVectorDB()