import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the stock analysis system."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    FMP_API_KEY: str = os.getenv("FMP_API_KEY", "")
    
    # Vector Database
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    
    # Cache and Performance
    CACHE_DURATION_HOURS: int = int(os.getenv("CACHE_DURATION_HOURS", "1"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # API Endpoints
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
    YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    # OpenAI Settings
    OPENAI_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSION = 1536
    
    # Data Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    MAX_TOKENS_PER_CHUNK = 8000
    
    # Rate Limiting (requests per minute)
    ALPHA_VANTAGE_RPM = 5  # Free tier limit
    FMP_RPM = 250  # Free tier limit
    YAHOO_FINANCE_RPM = 2000  # No official limit, being conservative
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        required_keys = [
            cls.OPENAI_API_KEY,
        ]
        
        missing_keys = [key for key in required_keys if not key]
        
        if missing_keys:
            print(f"Missing required configuration: {missing_keys}")
            return False
            
        return True
    
    @classmethod
    def get_api_key(cls, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        keys = {
            "openai": cls.OPENAI_API_KEY,
            "alpha_vantage": cls.ALPHA_VANTAGE_API_KEY,
            "fmp": cls.FMP_API_KEY,
        }
        return keys.get(service.lower())

# Global config instance
config = Config()