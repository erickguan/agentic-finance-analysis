"""
Advanced Usage Examples for Financial Analysis AI

This script demonstrates advanced features and customization options.
"""

import sys
from pathlib import Path
import json
import asyncio

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents.master_agent import master_agent
from tools.research_tools import research_tools
from tools.analysis_tools import analysis_tools

def example_custom_research():
    """Example of using research tools directly."""
    print("🔧 Advanced Example 1: Direct Tool Usage")
    print("=" * 50)
    
    symbol = "NVDA"
    print(f"Using research tools directly for {symbol}")
    
    try:
        # Direct tool usage (synchronous wrapper)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get company overview
        overview = loop.run_until_complete(research_tools.get_company_overview(symbol))
        print(f"\n📊 Company Overview received: {bool(overview and 'error' not in overview)}")
        
        # Get financial data
        financial = loop.run_until_complete(research_tools.get_financial_data(symbol))
        print(f"💰 Financial Data received: {bool(financial and 'error' not in financial)}")
        
        # Search recent news
        news = loop.run_until_complete(research_tools.search_recent_news(symbol, limit=5))
        print(f"📰 News Articles received: {len(news) if isinstance(news, list) else 0}")
        
        loop.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_custom_analysis():
    """Example of using analysis tools directly."""
    print("\n🔧 Advanced Example 2: Direct Analysis Tools")
    print("=" * 50)
    
    # Mock price data for demonstration
    mock_price_data = [
        {"date": "2024-01-01", "close": 100.0, "volume": 1000000},
        {"date": "2024-01-02", "close": 102.0, "volume": 1100000},
        {"date": "2024-01-03", "close": 98.0, "volume": 1200000},
        {"date": "2024-01-04", "close": 105.0, "volume": 900000},
        {"date": "2024-01-05", "close": 107.0, "volume": 950000},
    ]
    
    print("Using mock price data for analysis...")
    
    try:
        # Calculate moving averages
        ma_result = analysis_tools.calculate_moving_averages(mock_price_data, [3, 5])
        print(f"📈 Moving Averages: {ma_result.get('moving_averages', {})}")
        
        # Calculate RSI
        rsi_result = analysis_tools.calculate_rsi(mock_price_data, period=3)  # Short period for demo
        print(f"📊 RSI: {rsi_result.get('rsi', 'N/A')}")
        
        # Calculate volatility
        vol_result = analysis_tools.calculate_volatility(mock_price_data, period=3)
        print(f"📉 Volatility: {vol_result.get('volatility_percent', 'N/A')}%")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def example_comparative_analysis():
    """Example of comparing multiple stocks."""
    print("\n🔧 Advanced Example 3: Comparative Analysis")
    print("=" * 50)
    
    symbols = ["AAPL", "MSFT"]
    comparison_results = {}
    
    for symbol in symbols:
        print(f"\nAnalyzing {symbol}...")
        try:
            # Focus on fundamental analysis for comparison
            query = f"Fundamental analysis of {symbol} - focus on valuation metrics"
            result = master_agent.process_query_sync(query)
            
            if result.get("status") == "completed":
                comparison_results[symbol] = {
                    "status": "success",
                    "summary": result.get("final_response", "")[:200] + "...",
                    "confidence": result.get("analysis_results", {}).get("confidence_assessment", {}).get("overall_confidence", "unknown")
                }
                print(f"✅ {symbol} analysis completed")
            else:
                comparison_results[symbol] = {
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                }
                print(f"❌ {symbol} analysis failed")
        
        except Exception as e:
            comparison_results[symbol] = {
                "status": "error", 
                "error": str(e)
            }
            print(f"❌ {symbol} error: {str(e)}")
    
    # Display comparison
    print(f"\n📊 Comparison Summary:")
    for symbol, result in comparison_results.items():
        status = result["status"]
        if status == "success":
            print(f"  {symbol}: ✅ Confidence: {result['confidence'].title()}")
        else:
            print(f"  {symbol}: ❌ {result.get('error', 'Failed')}")

def example_error_handling():
    """Example of error handling and fallback scenarios."""
    print("\n🔧 Advanced Example 4: Error Handling")
    print("=" * 50)
    
    # Test with invalid symbol
    invalid_symbol = "INVALID123"
    print(f"Testing with invalid symbol: {invalid_symbol}")
    
    try:
        result = master_agent.process_query_sync(f"Analyze {invalid_symbol}")
        
        if result.get("status") == "failed":
            print(f"✅ Error handled gracefully: {result.get('error', 'Unknown error')}")
        elif result.get("status") == "needs_clarification":
            print(f"✅ Clarification requested: {result.get('message', 'Need more info')}")
        else:
            print(f"⚠️ Unexpected result: {result.get('status', 'Unknown')}")
    
    except Exception as e:
        print(f"✅ Exception handled: {str(e)}")
    
    # Test with ambiguous query
    ambiguous_query = "Tell me about the stock market"
    print(f"\nTesting with ambiguous query: {ambiguous_query}")
    
    try:
        result = master_agent.process_query_sync(ambiguous_query)
        
        if result.get("status") == "needs_clarification":
            print(f"✅ Clarification requested for ambiguous query")
            if result.get("search_results"):
                print(f"🔍 Search suggestions provided")
        else:
            print(f"⚠️ Unexpected handling of ambiguous query: {result.get('status', 'Unknown')}")
    
    except Exception as e:
        print(f"✅ Exception handled: {str(e)}")

def example_performance_monitoring():
    """Example of monitoring system performance."""
    print("\n🔧 Advanced Example 5: Performance Monitoring")
    print("=" * 50)
    
    import time
    
    # Measure query processing time
    query = "Quick analysis of Apple stock"
    print(f"Measuring performance for: {query}")
    
    try:
        start_time = time.time()
        result = master_agent.process_query_sync(query)
        end_time = time.time()
        
        processing_time = end_time - start_time
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        
        if result.get("status") == "completed":
            # Analyze the processing steps
            research_steps = len(result.get("research_results", {}).get("intermediate_steps", []))
            analysis_steps = len(result.get("analysis_results", {}).get("intermediate_steps", []))
            
            print(f"🔍 Research steps: {research_steps}")
            print(f"📊 Analysis steps: {analysis_steps}")
            
            # Data quality metrics
            research_quality = result.get("research_results", {}).get("data_quality_assessment", {})
            if research_quality:
                completeness = research_quality.get("completeness_score", 0)
                print(f"📈 Data completeness: {completeness:.2%}")
        
        else:
            print(f"⚠️ Query failed, cannot measure full performance")
    
    except Exception as e:
        print(f"❌ Performance monitoring error: {str(e)}")

def example_configuration_info():
    """Example of accessing system configuration and capabilities."""
    print("\n🔧 Advanced Example 6: System Configuration")
    print("=" * 50)
    
    try:
        # Master agent information
        master_info = master_agent.get_agent_info()
        print(f"🤖 Master Agent:")
        print(f"   Model: {master_info.get('model', 'Unknown')}")
        print(f"   Max Iterations: {master_info.get('max_iterations', 'Unknown')}")
        print(f"   Workflow Steps: {len(master_info.get('workflow_steps', []))}")
        
        # Research agent capabilities
        research_tools_list = research_tools.get_langchain_tools()
        print(f"\n🔍 Research Agent:")
        print(f"   Available Tools: {len(research_tools_list)}")
        for tool in research_tools_list:
            print(f"     - {tool.name}")
        
        # Analysis agent capabilities
        analysis_tools_list = analysis_tools.get_langchain_tools()
        print(f"\n📊 Analysis Agent:")
        print(f"   Available Tools: {len(analysis_tools_list)}")
        for tool in analysis_tools_list:
            print(f"     - {tool.name}")
        
        # System status
        status = master_agent.get_status()
        print(f"\n⚙️ System Status:")
        for component, state in status.items():
            print(f"   {component.replace('_', ' ').title()}: {state}")
    
    except Exception as e:
        print(f"❌ Configuration info error: {str(e)}")

def main():
    """Run all advanced examples."""
    print("🚀 Financial Analysis AI - Advanced Usage Examples")
    print("=" * 70)
    print("These examples demonstrate advanced features and customization options.")
    print()
    
    # Run advanced examples
    example_custom_research()
    example_custom_analysis()
    example_comparative_analysis()
    example_error_handling()
    example_performance_monitoring()
    example_configuration_info()
    
    print(f"\n🎉 Advanced examples completed!")
    print(f"💡 These examples show how to:")
    print(f"   - Use tools directly for custom workflows")
    print(f"   - Handle errors and edge cases gracefully")
    print(f"   - Monitor system performance and capabilities")
    print(f"   - Compare multiple stocks efficiently")

if __name__ == "__main__":
    main()