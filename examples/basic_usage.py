"""
Basic Usage Examples for Financial Analysis AI

This script demonstrates how to use the financial analysis system programmatically.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents.master_agent import master_agent
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent

def example_basic_analysis():
    """Basic stock analysis example."""
    print("🔍 Example 1: Basic Stock Analysis")
    print("=" * 50)
    
    # Simple analysis query
    query = "Analyze Apple stock"
    print(f"Query: {query}")
    
    try:
        results = master_agent.process_query_sync(query)
        
        if results.get("status") == "completed":
            print(f"\n✅ Analysis completed for {results['symbol']}")
            print(f"\n📋 Executive Summary:")
            print(results["final_response"])
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_research_only():
    """Research-only example."""
    print("\n🔍 Example 2: Research Agent Only")
    print("=" * 50)
    
    symbol = "TSLA"
    print(f"Researching: {symbol}")
    
    try:
        research_results = research_agent.research_company_sync(
            symbol, 
            research_scope=["company_overview", "financial_data", "news_analysis"]
        )
        
        if "error" not in research_results:
            print(f"\n✅ Research completed for {symbol}")
            print(f"📊 Sources used: {', '.join(research_results.get('sources_used', []))}")
            
            # Show research findings preview
            findings = research_results.get("research_findings", "")
            if findings:
                preview = findings[:300] + "..." if len(findings) > 300 else findings
                print(f"\n📝 Research preview: {preview}")
        else:
            print(f"❌ Research failed: {research_results['error']}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_analysis_only():
    """Analysis-only example with mock data."""
    print("\n📈 Example 3: Analysis Agent Only")
    print("=" * 50)
    
    # Mock research data for analysis
    mock_research_data = {
        "symbol": "MSFT",
        "research_findings": "Microsoft Corp is a technology company with strong financials and positive market sentiment.",
        "sources_used": ["financial_data_providers"]
    }
    
    try:
        analysis_results = analysis_agent.analyze_stock_sync(
            mock_research_data,
            analysis_focus=["fundamental_analysis", "sentiment_analysis"]
        )
        
        if "error" not in analysis_results:
            print(f"✅ Analysis completed for MSFT")
            
            # Show analysis findings preview
            findings = analysis_results.get("analysis_findings", "")
            if findings:
                preview = findings[:300] + "..." if len(findings) > 300 else findings
                print(f"\n📈 Analysis preview: {preview}")
            
            # Show confidence assessment
            confidence = analysis_results.get("confidence_assessment", {})
            if confidence:
                print(f"\n🎯 Confidence: {confidence.get('overall_confidence', 'Unknown').title()}")
        else:
            print(f"❌ Analysis failed: {analysis_results['error']}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_batch_analysis():
    """Batch analysis example."""
    print("\n📊 Example 4: Batch Analysis")
    print("=" * 50)
    
    symbols = ["AAPL", "GOOGL", "AMZN"]
    results = {}
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        try:
            query = f"Quick analysis of {symbol}"
            result = master_agent.process_query_sync(query)
            results[symbol] = result
            
            if result.get("status") == "completed":
                print(f"✅ {symbol} completed")
            else:
                print(f"❌ {symbol} failed: {result.get('error', 'Unknown')}")
        
        except Exception as e:
            print(f"❌ {symbol} error: {str(e)}")
            results[symbol] = {"error": str(e)}
    
    # Summary
    print(f"\n📋 Batch Analysis Summary:")
    successful = sum(1 for r in results.values() if r.get("status") == "completed")
    print(f"Successful: {successful}/{len(symbols)}")

def example_system_status():
    """System status check example."""
    print("\n⚙️ Example 5: System Status Check")
    print("=" * 50)
    
    try:
        # Master agent status
        status = master_agent.get_status()
        print("🤖 Agent Status:")
        for agent, state in status.items():
            print(f"  {agent.replace('_', ' ').title()}: {state}")
        
        # Agent information
        print(f"\n📊 Master Agent Info:")
        info = master_agent.get_agent_info()
        print(f"  Model: {info.get('model', 'Unknown')}")
        print(f"  Max Iterations: {info.get('max_iterations', 'Unknown')}")
        print(f"  Workflow Steps: {len(info.get('workflow_steps', []))}")
    
    except Exception as e:
        print(f"❌ Error checking status: {str(e)}")

def main():
    """Run all examples."""
    print("🚀 Financial Analysis AI - Usage Examples")
    print("=" * 60)
    
    # Run examples
    example_basic_analysis()
    example_research_only()
    example_analysis_only()
    example_batch_analysis()
    example_system_status()
    
    print(f"\n🎉 Examples completed!")
    print(f"For more advanced usage, check the README.md and CLI examples.")

if __name__ == "__main__":
    main()