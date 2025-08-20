"""
FastAPI Application for Financial Analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Import our agents
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agent_fin.core.agents.master_agent import master_agent
from agent_fin.core.utils.config import config

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Analysis API",
    description="AI-powered financial analysis and research API",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results (replace with database in production)
analysis_cache: Dict[str, Dict[str, Any]] = {}

# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    query: str
    depth: Optional[str] = "Standard Analysis"

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    symbol: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    user_query: str
    error: Optional[str] = None
    timestamp: datetime

class StatusResponse(BaseModel):
    status: str
    agents: Dict[str, str]
    meta: Dict[str, Any]
    config: Dict[str, Any]

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Financial Analysis API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "analysis": "/api/v1/analyze",
            "status": "/api/v1/status",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/v1/status", response_model=StatusResponse)
async def get_status():
    """Get system status and agent information."""
    try:
        agent_status = master_agent.get_status()
        meta = agent_status.pop("meta")
        
        return StatusResponse(
            status="active",
            agents=agent_status,
            meta=meta,
            config={
                "model": config.OPENAI_MODEL,
                "embedding_model": config.EMBEDDING_MODEL
            }
        )
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new financial analysis."""
    try:
        # Generate unique analysis ID
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(request.query) % 10000}"
        
        # Initialize analysis record
        analysis_cache[analysis_id] = {
            "status": "processing",
            "query": request.query,
            "depth": request.depth,
            "started_at": datetime.now(),
            "results": None,
            "error": None
        }
        
        # Start background processing
        background_tasks.add_task(process_analysis, analysis_id, request)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/api/v1/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """Get analysis results by ID."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analysis_cache[analysis_id]
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status=analysis["status"],
        symbol=analysis.get("symbol"),
        results=analysis.get("results"),
        user_query=analysis.get("query"),
        error=analysis.get("error"),
        timestamp=analysis.get("completed_at", analysis.get("started_at", datetime.now()))
    )

@app.get("/api/v1/analyses")
async def list_analyses():
    """List all analysis records."""
    analyses = []
    for analysis_id, data in analysis_cache.items():
        analyses.append({
            "analysis_id": analysis_id,
            "query": data["query"],
            "status": data["status"],
            "started_at": data["started_at"],
            "completed_at": data.get("completed_at")
        })
    
    return {"analyses": analyses}

@app.delete("/api/v1/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis record."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_cache[analysis_id]
    return {"message": "Analysis deleted successfully"}

async def process_analysis(analysis_id: str, request: AnalysisRequest):
    """Background task to process analysis."""
    try:
        logger.info(f"Starting analysis {analysis_id} for query: {request.query}")
        
        # Process the query through master agent
        results = await master_agent.process_query(request.query)
        
        # Update cache with results
        analysis_cache[analysis_id].update({
            "status": results.get("status", "completed"),
            "symbol": results.get("symbol"),
            "results": results,
            "completed_at": datetime.now()
        })
        
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {e}")
        analysis_cache[analysis_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now()
        })

# Sample queries endpoint for frontend convenience
@app.get("/api/v1/sample-queries")
async def get_sample_queries():
    """Get sample analysis queries."""
    return {
        "queries": [
            {
                "id": "apple_analysis",
                "title": "Apple Stock Analysis",
                "query": "Analyze Apple's current position",
                "category": "stock_analysis"
            },
            {
                "id": "tesla_sentiment",
                "title": "Tesla Sentiment",
                "query": "What's the sentiment around Tesla?",
                "category": "sentiment"
            },
            {
                "id": "microsoft_valuation",
                "title": "Microsoft Valuation",
                "query": "Compare Microsoft's valuation metrics",
                "category": "valuation"
            },
            {
                "id": "nvidia_investment",
                "title": "NVIDIA Investment",
                "query": "Should I invest in NVIDIA?",
                "category": "investment_advice"
            },
            {
                "id": "amazon_health",
                "title": "Amazon Financial Health",
                "query": "Analyze Amazon's financial health",
                "category": "financial_health"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)