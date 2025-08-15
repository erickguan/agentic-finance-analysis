"""
Main Streamlit Application for Financial Analysis

Interactive dashboard for comprehensive stock analysis using the three-agent system.
"""

import streamlit as st
import asyncio
import logging
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# Import our agents
from ..agents.master_agent import master_agent
from ..utils.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Financial Analysis AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function."""
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .analysis-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .stAlert > div {
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<div class="main-header">📈 Financial Analysis AI</div>', unsafe_allow_html=True)
    st.markdown("*Comprehensive stock analysis powered by AI agents*")
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔍 Query Interface")
        
        # Query input
        user_query = st.text_area(
            "Ask about any stock:",
            placeholder="e.g., 'Analyze Apple stock' or 'What's the outlook for TSLA?'",
            height=100
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        analysis_depth = st.selectbox(
            "Analysis Depth:",
            ["Quick Overview", "Standard Analysis", "Comprehensive Deep Dive"],
            index=1
        )
        
        # Sample queries for convenience
        st.subheader("Sample Queries")
        sample_queries = [
            "Analyze Apple's current position",
            "What's the sentiment around Tesla?",
            "Compare Microsoft's valuation metrics",
            "Should I invest in NVIDIA?",
            "Analyze Amazon's financial health"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{hash(query)}"):
                st.session_state.selected_query = query
                user_query = query
        
        # Process query button
        if st.button("🚀 Analyze", type="primary", disabled=not user_query):
            if user_query:
                with st.spinner("Processing your query..."):
                    try:
                        # Process the query
                        results = process_query(user_query, analysis_depth)
                        st.session_state.analysis_results = results
                        st.session_state.chat_history.append({
                            "query": user_query,
                            "results": results,
                            "timestamp": datetime.now()
                        })
                        st.success("Analysis completed!")
                    except Exception as e:
                        st.error(f"Error processing query: {str(e)}")
                        logger.error(f"Query processing error: {e}")
    
    # Main content area
    if st.session_state.analysis_results:
        display_analysis_results(st.session_state.analysis_results)
    else:
        display_welcome_screen()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Financial Analysis AI • Powered by LangChain & OpenAI • For educational purposes only
    </div>
    """, unsafe_allow_html=True)

def process_query(query: str, depth: str) -> Dict[str, Any]:
    """Process user query through the master agent."""
    try:
        # Map analysis depth to scope
        depth_mapping = {
            "Quick Overview": ["company_overview"],
            "Standard Analysis": ["comprehensive"],
            "Comprehensive Deep Dive": ["comprehensive"]
        }
        
        # Use synchronous processing for Streamlit
        results = master_agent.process_query_sync(query)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in query processing: {e}")
        raise e

def display_welcome_screen():
    """Display welcome screen when no analysis is loaded."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## Welcome to Financial Analysis AI
        
        Get comprehensive stock analysis powered by advanced AI agents:
        
        ### 🔬 **Research Agent**
        - Gathers comprehensive company data
        - Collects recent news and analyst reports
        - Retrieves financial metrics and ratios
        
        ### 📊 **Analysis Agent**
        - Technical analysis with indicators
        - Fundamental valuation assessment
        - News sentiment analysis
        - Risk evaluation
        
        ### 🎯 **Master Agent**
        - Orchestrates complete workflow
        - Synthesizes multi-perspective insights
        - Generates actionable recommendations
        
        ---
        
        **To get started:**
        1. Enter a stock symbol or company name
        2. Choose your analysis depth
        3. Click "Analyze" to begin
        
        *Try asking: "Analyze Apple stock" or "What's Tesla's outlook?"*
        """)

def display_analysis_results(results: Dict[str, Any]):
    """Display comprehensive analysis results."""
    
    if results.get("status") == "failed":
        st.error(f"Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    if results.get("status") == "needs_clarification":
        st.warning(results.get("message", "Need more information"))
        if results.get("search_results"):
            st.subheader("Possible matches:")
            st.write(results["search_results"])
        return
    
    symbol = results.get("symbol", "Unknown")
    
    # Analysis header
    st.header(f"📈 Analysis Results: {symbol}")
    
    if results.get("final_response"):
        st.markdown("### Executive Summary")
        st.markdown(results["final_response"])
    
    # Create tabs for detailed results
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Research", "📈 Analysis", "⚙️ Details"])
    
    with tab1:
        display_overview_tab(results)
    
    with tab2:
        display_research_tab(results.get("research_results", {}))
    
    with tab3:
        display_analysis_tab(results.get("analysis_results", {}))
    
    with tab4:
        display_details_tab(results)

def display_overview_tab(results: Dict[str, Any]):
    """Display overview information."""
    symbol = results.get("symbol", "Unknown")
    
    st.subheader(f"Key Insights for {symbol}")
    
    # Quick metrics if available
    research_data = results.get("research_results", {})
    if research_data.get("research_findings"):
        st.markdown("#### Research Summary")
        st.info(str(research_data["research_findings"])[:500] + "..." if len(str(research_data["research_findings"])) > 500 else str(research_data["research_findings"]))
    
    analysis_data = results.get("analysis_results", {})
    if analysis_data.get("analysis_findings"):
        st.markdown("#### Analysis Summary")
        st.info(str(analysis_data["analysis_findings"])[:500] + "..." if len(str(analysis_data["analysis_findings"])) > 500 else str(analysis_data["analysis_findings"]))
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Analysis Status",
            value=results.get("status", "Unknown").title(),
            delta="Completed" if results.get("status") == "completed" else "In Progress"
        )
    
    with col2:
        confidence = "High"  # Default for POC
        if analysis_data.get("confidence_assessment"):
            confidence = analysis_data["confidence_assessment"].get("overall_confidence", "Medium").title()
        st.metric(
            label="Confidence Level",
            value=confidence,
            delta="Based on data quality"
        )
    
    with col3:
        sources_count = 0
        if research_data.get("sources_used"):
            sources_count = len(research_data["sources_used"])
        st.metric(
            label="Data Sources",
            value=sources_count,
            delta="Different sources used"
        )

def display_research_tab(research_data: Dict[str, Any]):
    """Display research results."""
    st.subheader("🔍 Research Findings")
    
    if not research_data:
        st.info("No research data available")
        return
    
    # Research findings
    if research_data.get("research_findings"):
        st.markdown("#### Comprehensive Research")
        st.write(research_data["research_findings"])
    
    # Data sources
    if research_data.get("sources_used"):
        st.markdown("#### Data Sources Used")
        for source in research_data["sources_used"]:
            st.badge(source.replace("_", " ").title())
    
    # Data quality assessment
    if research_data.get("data_quality_assessment"):
        quality = research_data["data_quality_assessment"]
        st.markdown("#### Data Quality Assessment")
        
        col1, col2 = st.columns(2)
        with col1:
            completeness = quality.get("completeness_score", 0.5)
            st.metric("Completeness Score", f"{completeness:.2f}")
        
        with col2:
            source_diversity = quality.get("source_diversity", 0)
            st.metric("Source Diversity", source_diversity)
    
    # Raw data preview (collapsible)
    with st.expander("View Raw Research Data"):
        st.json(research_data)

def display_analysis_tab(analysis_data: Dict[str, Any]):
    """Display analysis results."""
    st.subheader("📈 Analysis Results")
    
    if not analysis_data:
        st.info("No analysis data available")
        return
    
    # Analysis findings
    if analysis_data.get("analysis_findings"):
        st.markdown("#### Analysis Summary")
        st.write(analysis_data["analysis_findings"])
    
    # Metrics calculated
    if analysis_data.get("metrics_calculated"):
        metrics = analysis_data["metrics_calculated"]
        st.markdown("#### Calculated Metrics")
        
        # Technical metrics
        if metrics.get("technical_metrics"):
            st.markdown("**Technical Analysis:**")
            for metric in metrics["technical_metrics"]:
                st.write(f"- {metric.get('tool', 'Unknown')}: {str(metric.get('result', 'N/A'))[:200]}...")
        
        # Fundamental metrics
        if metrics.get("fundamental_metrics"):
            st.markdown("**Fundamental Analysis:**")
            for metric in metrics["fundamental_metrics"]:
                st.write(f"- {metric.get('tool', 'Unknown')}: {str(metric.get('result', 'N/A'))[:200]}...")
        
        # Sentiment metrics
        if metrics.get("sentiment_metrics"):
            st.markdown("**Sentiment Analysis:**")
            for metric in metrics["sentiment_metrics"]:
                st.write(f"- {metric.get('tool', 'Unknown')}: {str(metric.get('result', 'N/A'))[:200]}...")
    
    # Confidence assessment
    if analysis_data.get("confidence_assessment"):
        confidence = analysis_data["confidence_assessment"]
        st.markdown("#### Confidence Assessment")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Confidence", confidence.get("overall_confidence", "Unknown").title())
        with col2:
            st.metric("Analysis Completeness", f"{confidence.get('analysis_completeness', 0):.2f}")
        
        if confidence.get("limiting_factors"):
            st.warning("Limiting Factors: " + ", ".join(confidence["limiting_factors"]))
    
    # Raw analysis data (collapsible)
    with st.expander("View Raw Analysis Data"):
        st.json(analysis_data)

def display_details_tab(results: Dict[str, Any]):
    """Display technical details and metadata."""
    st.subheader("⚙️ Technical Details")
    
    # Processing information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Processing Info")
        st.write(f"**Symbol:** {results.get('symbol', 'Unknown')}")
        st.write(f"**Status:** {results.get('status', 'Unknown')}")
        st.write(f"**Query:** {results.get('user_query', 'Unknown')}")
        
        if results.get("processing_timestamp"):
            st.write(f"**Processed:** {results['processing_timestamp']}")
    
    with col2:
        st.markdown("#### Agent Status")
        agent_info = master_agent.get_status()
        for agent, status in agent_info.items():
            st.write(f"**{agent.replace('_', ' ').title()}:** {status}")
    
    # System information
    st.markdown("#### System Configuration")
    st.write(f"**Model:** {config.OPENAI_MODEL}")
    st.write(f"**Embedding Model:** {config.EMBEDDING_MODEL}")
    
    # Full results (collapsible)
    with st.expander("View Complete Results"):
        st.json(results)

# Error handling wrapper
def safe_main():
    """Main function with error handling."""
    try:
        main()
    except Exception as e:
        st.error("An unexpected error occurred. Please refresh the page and try again.")
        logger.error(f"Application error: {e}")
        
        # Show error details in development
        if config.get("DEBUG", False):
            st.exception(e)

if __name__ == "__main__":
    safe_main()