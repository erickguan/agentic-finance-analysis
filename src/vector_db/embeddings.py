import asyncio
from typing import List, Optional
import logging
from openai import AsyncOpenAI

from ..utils.config import config
from ..utils.helpers import retry_on_failure, RateLimiter

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manager for generating embeddings using OpenAI's API."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.EMBEDDING_MODEL
        self.dimension = config.EMBEDDING_DIMENSION
        self.rate_limiter = RateLimiter(3000, 60)  # OpenAI rate limit: 3000 RPM for embeddings
        
        if not config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found. Embeddings will not work.")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def get_embeddings(self, texts: List[str], batch_size: int = 100) -> Optional[List[List[float]]]:
        """Generate embeddings for a list of texts."""
        if not config.OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return None
        
        if not texts:
            return []
        
        try:
            all_embeddings = []
            
            # Process in batches to avoid rate limits and memory issues
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Wait for rate limit
                await self.rate_limiter.wait_if_needed()
                
                # Clean and prepare texts
                cleaned_batch = [self._clean_text(text) for text in batch]
                
                # Generate embeddings
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=cleaned_batch,
                    encoding_format="float"
                )
                
                # Record the API call
                self.rate_limiter.record_call()
                
                # Extract embeddings
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                # Small delay between batches to be respectful
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
    
    async def get_single_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text."""
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else None
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding generation."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate if too long (OpenAI has token limits)
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = 8000 * 4  # ~8000 tokens
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            logger.warning(f"Text truncated to {max_chars} characters for embedding")
        
        return text
    
    async def compute_similarity(self, text1: str, text2: str) -> Optional[float]:
        """Compute cosine similarity between two texts."""
        embeddings = await self.get_embeddings([text1, text2])
        if not embeddings or len(embeddings) != 2:
            return None
        
        # Compute cosine similarity
        import numpy as np
        
        vec1 = np.array(embeddings[0])
        vec2 = np.array(embeddings[1])
        
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # Compute cosine similarity
        similarity = np.dot(vec1_norm, vec2_norm)
        
        return float(similarity)
    
    async def find_most_similar(self, query_text: str, candidate_texts: List[str]) -> Optional[List[tuple]]:
        """Find the most similar texts to a query from a list of candidates."""
        if not candidate_texts:
            return []
        
        # Generate embeddings for query and all candidates
        all_texts = [query_text] + candidate_texts
        embeddings = await self.get_embeddings(all_texts)
        
        if not embeddings or len(embeddings) != len(all_texts):
            return None
        
        import numpy as np
        
        query_embedding = np.array(embeddings[0])
        candidate_embeddings = np.array(embeddings[1:])
        
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        candidate_norms = candidate_embeddings / np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
        
        # Compute similarities
        similarities = np.dot(candidate_norms, query_norm)
        
        # Create list of (text, similarity) tuples
        results = [(candidate_texts[i], float(similarities[i])) for i in range(len(candidate_texts))]
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def get_embedding_info(self) -> dict:
        """Get information about the embedding configuration."""
        return {
            "model": self.model,
            "dimension": self.dimension,
            "api_configured": bool(config.OPENAI_API_KEY),
            "rate_limit_rpm": self.rate_limiter.max_calls
        }

# Global instance
embedding_manager = EmbeddingManager()