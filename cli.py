"""
Financial Analysis AI - Command Line Interface

Simple CLI for testing and batch processing of stock analysis queries.
"""

import asyncio
import argparse
import sys
from pathlib import Path
import json
from typing import Dict, Any

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from agent_fin.core.agents.master_agent import master_agent
from agent_fin.core.utils.config import config

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Financial Analysis AI - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --query "Analyze Apple stock"
  python cli.py --query "What's Tesla's outlook?" --output results.json
  python cli.py --symbol MSFT --analysis comprehensive
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Natural language query about a stock"
    )
    
    parser.add_argument(
        "--symbol", "-s", 
        type=str,
        help="Stock symbol to analyze (e.g., AAPL, TSLA)"
    )
    
    parser.add_argument(
        "--analysis", "-a",
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Analysis depth (default: standard)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (JSON format)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--status",
        action="store_true", 
        help="Show system status"
    )
    
    args = parser.parse_args()
    
    if args.status:
        show_system_status()
        return
    
    if not args.query and not args.symbol:
        parser.error("Either --query or --symbol is required")
    
    # Build query
    if args.symbol and not args.query:
        query = f"Analyze {args.symbol} stock - {args.analysis} analysis"
    else:
        query = args.query
    
    print(f"🔍 Processing query: {query}")
    print("=" * 60)
    
    try:
        # Process the query
        results = master_agent.process_query_sync(query)
        
        # Display results
        if args.verbose:
            display_detailed_results(results)
        else:
            display_summary_results(results)
        
        # Save to file if requested
        if args.output:
            save_results(results, args.output)
            print(f"\n💾 Results saved to: {args.output}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def show_system_status():
    """Display system status information."""
    print("🔧 Financial Analysis AI - System Status")
    print("=" * 50)
    
    # Agent status
    status = master_agent.get_status()
    print("\n📊 Agent Status:")
    for agent, state in status.items():
        print(f"  {agent.replace('_', ' ').title()}: {state}")
    
    # Configuration
    print(f"\n⚙️  Configuration:")
    print(f"  OpenAI Model: {config.OPENAI_MODEL}")
    print(f"  Embedding Model: {config.EMBEDDING_MODEL}")
    print(f"  Vector DB Path: {config.VECTOR_DB_PATH}")
    
    # API Keys status
    print(f"\n🔐 API Keys:")
    print(f"  OpenAI: {'✅ Configured' if config.OPENAI_API_KEY else '❌ Missing'}")
    print(f"  Alpha Vantage: {'✅ Configured' if config.ALPHA_VANTAGE_API_KEY else '❌ Missing'}")
    print(f"  FMP: {'✅ Configured' if config.FMP_API_KEY else '❌ Missing'}")

def display_summary_results(results: Dict[str, Any]):
    """Display concise results."""
    if results.get("status") == "failed":
        print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    if results.get("status") == "needs_clarification":
        print(f"❓ {results.get('message', 'Need more information')}")
        if results.get("search_results"):
            print("\nPossible matches:")
            print(results["search_results"])
        return
    
    symbol = results.get("symbol", "Unknown")
    print(f"📈 Analysis Results for {symbol}")
    print("-" * 40)
    
    if results.get("final_response"):
        print("\n📋 Executive Summary:")
        print(results["final_response"])
    
    print(f"\n✅ Status: {results.get('status', 'Unknown').title()}")

def display_detailed_results(results: Dict[str, Any]):
    """Display detailed results."""
    display_summary_results(results)
    
    if results.get("status") != "completed":
        return
    
    print("\n" + "=" * 60)
    print("📊 DETAILED ANALYSIS RESULTS")
    print("=" * 60)
    
    # Research results
    research_data = results.get("research_results", {})
    if research_data:
        print("\n🔍 RESEARCH FINDINGS:")
        print("-" * 30)
        if research_data.get("research_findings"):
            print(research_data["research_findings"])
        
        if research_data.get("sources_used"):
            print(f"\n📚 Data Sources: {', '.join(research_data['sources_used'])}")
    
    # Analysis results  
    analysis_data = results.get("analysis_results", {})
    if analysis_data:
        print("\n📈 ANALYSIS FINDINGS:")
        print("-" * 30)
        if analysis_data.get("analysis_findings"):
            print(analysis_data["analysis_findings"])
        
        # Confidence assessment
        if analysis_data.get("confidence_assessment"):
            confidence = analysis_data["confidence_assessment"]
            print(f"\n🎯 Confidence: {confidence.get('overall_confidence', 'Unknown').title()}")

def save_results(results: Dict[str, Any], output_path: str):
    """Save results to JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")

if __name__ == "__main__":
    main()