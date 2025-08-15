"""
Basic Test Framework for Financial Analysis AI

Simple tests to validate system functionality with sample company queries.
"""

import sys
from pathlib import Path
import time
import json

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents.master_agent import master_agent
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent

# Sample test queries
SAMPLE_QUERIES = [
    "Analyze Apple's current technical and fundamental position",
    "What's the sentiment around Tesla after the latest earnings?", 
    "Compare Microsoft and Google's valuation metrics",
    "Should I buy Amazon stock based on recent news?",
    "Perform a comprehensive analysis of NVIDIA"
]

# Known symbols for testing
TEST_SYMBOLS = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA"]

class TestResults:
    """Simple test results tracker."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"✅ {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 Test Summary: {self.passed}/{total} passed")
        if self.errors:
            print("❌ Failures:")
            for error in self.errors:
                print(f"   - {error}")
        return self.failed == 0

def test_system_status():
    """Test system components are available."""
    print("🔧 Testing System Status...")
    results = TestResults()
    
    try:
        # Test master agent status
        status = master_agent.get_status()
        if status.get("master_agent") == "ready":
            results.add_pass("Master Agent Status")
        else:
            results.add_fail("Master Agent Status", "Not ready")
        
        if status.get("research_agent") == "ready":
            results.add_pass("Research Agent Status")
        else:
            results.add_fail("Research Agent Status", "Not ready")
        
        if status.get("analysis_agent") == "ready":
            results.add_pass("Analysis Agent Status")
        else:
            results.add_fail("Analysis Agent Status", "Not ready")
        
        # Test agent info
        info = master_agent.get_agent_info()
        if info.get("agent_type") == "Master Agent":
            results.add_pass("Master Agent Info")
        else:
            results.add_fail("Master Agent Info", "Invalid agent info")
        
    except Exception as e:
        results.add_fail("System Status Test", str(e))
    
    return results.summary()

def test_research_agent():
    """Test research agent functionality."""
    print("\n🔍 Testing Research Agent...")
    results = TestResults()
    
    test_symbol = "AAPL"
    
    try:
        # Test basic research
        research_result = research_agent.research_company_sync(
            test_symbol, 
            research_scope=["company_overview"]
        )
        
        if "error" not in research_result:
            results.add_pass(f"Research Agent - {test_symbol}")
            
            # Check for expected fields
            if research_result.get("symbol") == test_symbol:
                results.add_pass("Research Result Symbol")
            else:
                results.add_fail("Research Result Symbol", "Symbol mismatch")
            
            if research_result.get("research_findings"):
                results.add_pass("Research Findings")
            else:
                results.add_fail("Research Findings", "No findings returned")
                
        else:
            results.add_fail(f"Research Agent - {test_symbol}", research_result["error"])
    
    except Exception as e:
        results.add_fail("Research Agent Test", str(e))
    
    return results.summary()

def test_analysis_agent():
    """Test analysis agent functionality."""
    print("\n📊 Testing Analysis Agent...")
    results = TestResults()
    
    # Mock research data for analysis testing
    mock_research_data = {
        "symbol": "TEST",
        "research_findings": "Test company with good fundamentals and positive sentiment.",
        "sources_used": ["test_source"]
    }
    
    try:
        # Test basic analysis
        analysis_result = analysis_agent.analyze_stock_sync(
            mock_research_data,
            analysis_focus=["comprehensive"]
        )
        
        if "error" not in analysis_result:
            results.add_pass("Analysis Agent - Mock Data")
            
            # Check for expected fields
            if analysis_result.get("symbol") == "TEST":
                results.add_pass("Analysis Result Symbol")
            else:
                results.add_fail("Analysis Result Symbol", "Symbol mismatch")
            
            if analysis_result.get("analysis_findings"):
                results.add_pass("Analysis Findings")
            else:
                results.add_fail("Analysis Findings", "No findings returned")
                
        else:
            results.add_fail("Analysis Agent - Mock Data", analysis_result["error"])
    
    except Exception as e:
        results.add_fail("Analysis Agent Test", str(e))
    
    return results.summary()

def test_master_agent():
    """Test master agent orchestration."""
    print("\n🎯 Testing Master Agent...")
    results = TestResults()
    
    # Test with a simple query
    test_query = "Quick analysis of Apple stock"
    
    try:
        start_time = time.time()
        result = master_agent.process_query_sync(test_query)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if result.get("status") in ["completed", "partial"]:
            results.add_pass(f"Master Agent Query Processing ({processing_time:.1f}s)")
            
            # Check for expected fields
            if result.get("symbol"):
                results.add_pass("Symbol Extraction")
            else:
                results.add_fail("Symbol Extraction", "No symbol extracted")
            
            if result.get("final_response"):
                results.add_pass("Final Response Generation")
            else:
                results.add_fail("Final Response Generation", "No final response")
                
        elif result.get("status") == "needs_clarification":
            results.add_pass("Master Agent - Clarification Handling")
        else:
            results.add_fail("Master Agent Query Processing", result.get("error", "Unknown error"))
    
    except Exception as e:
        results.add_fail("Master Agent Test", str(e))
    
    return results.summary()

def test_sample_queries():
    """Test with sample queries."""
    print("\n📝 Testing Sample Queries...")
    results = TestResults()
    
    # Test first two sample queries only (to avoid long test times)
    test_queries = SAMPLE_QUERIES[:2]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n  Query {i}: {query[:50]}...")
        
        try:
            result = master_agent.process_query_sync(query)
            
            if result.get("status") in ["completed", "partial", "needs_clarification"]:
                results.add_pass(f"Sample Query {i}")
            else:
                results.add_fail(f"Sample Query {i}", result.get("error", "Unknown error"))
        
        except Exception as e:
            results.add_fail(f"Sample Query {i}", str(e))
    
    return results.summary()

def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n⚠️ Testing Error Handling...")
    results = TestResults()
    
    # Test invalid symbol
    try:
        result = master_agent.process_query_sync("Analyze INVALID123 stock")
        
        if result.get("status") in ["failed", "needs_clarification"]:
            results.add_pass("Invalid Symbol Handling")
        else:
            results.add_fail("Invalid Symbol Handling", "Should have failed or asked for clarification")
    
    except Exception as e:
        results.add_pass("Invalid Symbol Exception Handling")
    
    # Test empty query
    try:
        result = master_agent.process_query_sync("")
        
        if result.get("status") == "failed":
            results.add_pass("Empty Query Handling")
        else:
            results.add_fail("Empty Query Handling", "Should have failed")
    
    except Exception as e:
        results.add_pass("Empty Query Exception Handling")
    
    return results.summary()

def run_performance_benchmark():
    """Simple performance benchmark."""
    print("\n⏱️ Performance Benchmark...")
    
    query = "Quick analysis of Apple"
    iterations = 3
    times = []
    
    print(f"Running {iterations} iterations of: {query}")
    
    for i in range(iterations):
        try:
            start_time = time.time()
            result = master_agent.process_query_sync(query)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            
            status = result.get("status", "unknown")
            print(f"  Iteration {i+1}: {processing_time:.2f}s ({status})")
            
        except Exception as e:
            print(f"  Iteration {i+1}: Failed - {str(e)}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n📊 Performance Results:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        
        if avg_time < 30:  # Reasonable threshold for demo
            print("✅ Performance: Acceptable")
        else:
            print("⚠️ Performance: May be slow")

def main():
    """Run all tests."""
    print("🧪 Financial Analysis AI - System Tests")
    print("=" * 60)
    print("Running basic functionality tests...\n")
    
    # Track overall results
    all_passed = True
    
    # Run test suites
    test_suites = [
        test_system_status,
        test_research_agent,
        test_analysis_agent,
        test_master_agent,
        test_sample_queries,
        test_error_handling
    ]
    
    for test_suite in test_suites:
        passed = test_suite()
        if not passed:
            all_passed = False
    
    # Run performance benchmark
    run_performance_benchmark()
    
    # Final summary
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 All tests passed! System appears to be working correctly.")
        print("\n💡 Next steps:")
        print("  - Set up your API keys in .env file")
        print("  - Try the Streamlit dashboard: streamlit run app.py")
        print("  - Test with CLI: python cli.py --query 'Analyze Apple'")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("  - Ensure all dependencies are installed")
        print("  - Check your API keys are configured")
        print("  - Review the error messages for specific issues")
    
    return all_passed

if __name__ == "__main__":
    main()