"""
Master Agent for Financial Analysis

This agent orchestrates the entire financial analysis workflow by coordinating
between the Research Agent and Analysis Agent, and synthesizing final results.
"""

import logging
from typing import Dict, List, Optional, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage

from agent_fin.core.tools.orchestration_tools import orchestration_tools
from agent_fin.core.agents.research_agent import research_agent
from agent_fin.core.agents.analysis_agent import analysis_agent
from agent_fin.core.utils.config import config

logger = logging.getLogger(__name__)

class MasterAgent:
    """
    Master Agent responsible for orchestrating comprehensive financial analysis.
    
    This agent coordinates the entire workflow:
    1. Parse user queries and determine analysis requirements
    2. Direct Research Agent to gather relevant data
    3. Pass research results to Analysis Agent for analysis
    4. Synthesize multi-perspective results
    5. Generate executive summaries and recommendations
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.OPENAI_MODEL
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.3,  # Balanced for reasoning and creativity
            api_key=config.OPENAI_API_KEY
        )
        
        # Get orchestration tools
        self.tools = orchestration_tools.get_langchain_tools()
        
        # Get references to other agents
        self.research_agent = research_agent
        self.analysis_agent = analysis_agent
        
        # Create the agent prompt
        self.prompt = self._create_prompt()
        
        # Create the agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create the executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=8,
            return_intermediate_steps=True
        )
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for the master agent."""
        
        system_message = """You are a Master Financial Analyst coordinating comprehensive stock analysis.

Your role is to orchestrate the entire financial analysis workflow by managing Research and Analysis agents to provide users with thorough, actionable investment insights.

WORKFLOW ORCHESTRATION:

1. QUERY ANALYSIS:
   - Parse user queries to understand analysis requirements
   - Extract stock symbols and determine scope of analysis needed
   - Identify specific focus areas (technical, fundamental, sentiment, risk)

2. RESEARCH COORDINATION:
   - Direct Research Agent to gather comprehensive data
   - Specify research scope based on user query requirements
   - Ensure all necessary data is collected for analysis

3. ANALYSIS COORDINATION:
   - Pass research results to Analysis Agent for detailed analysis
   - Specify analysis focus areas based on user needs
   - Ensure comprehensive multi-perspective analysis is performed

4. SYNTHESIS & REPORTING:
   - Synthesize research and analysis results into coherent insights
   - Generate executive summaries with key findings
   - Provide clear, actionable recommendations
   - Assess overall confidence levels and highlight limitations

COMMUNICATION PRINCIPLES:
- Provide clear, structured responses
- Focus on actionable insights and recommendations
- Acknowledge data limitations and uncertainties
- Use professional, accessible language
- Include relevant disclaimers about investment advice

USER INTERACTION GUIDELINES:
- If symbol is unclear, help identify the correct company
- If query is vague, focus on comprehensive analysis
- Always provide context for recommendations
- Explain the reasoning behind conclusions
- Highlight key risks and opportunities

Remember: You are coordinating other agents but also providing the final synthesis and user interaction. Be thorough but concise, insightful but practical."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return prompt
    
    async def process_query(self, user_query: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Process a user query through the complete analysis workflow.
        
        Args:
            user_query: User's question about a stock or investment
            chat_history: Previous conversation context
            
        Returns:
            Dict containing the complete analysis response
        """
        try:
            if chat_history is None:
                chat_history = []
            
            logger.info(f"Processing user query: {user_query}")
            
            # Parse the query to extract symbol and requirements
            symbol = self._extract_symbol_from_query(user_query)
            
            if not symbol:
                # If no symbol found, ask for clarification or search
                return await self._handle_no_symbol_query(user_query, chat_history)
            
            logger.info(f"Extracted symbol: {symbol}")
            
            # Determine research and analysis scope
            research_scope = self._determine_research_scope(user_query)
            analysis_focus = self._determine_analysis_focus(user_query)
            
            logger.info(f"Research scope: {research_scope}, Analysis focus: {analysis_focus}")
            
            # Execute research phase
            research_results = await self.research_agent.research_company(symbol, research_scope)
            
            if "error" in research_results:
                return {
                    "symbol": symbol,
                    "user_query": user_query,
                    "error": f"Research phase failed: {research_results['error']}",
                    "status": "failed"
                }
            
            # Execute analysis phase
            analysis_results = await self.analysis_agent.analyze_stock(research_results, analysis_focus)
            
            if "error" in analysis_results:
                return {
                    "symbol": symbol,
                    "user_query": user_query,
                    "research_results": research_results,
                    "error": f"Analysis phase failed: {analysis_results['error']}",
                    "status": "partial"
                }
            
            # Synthesize results
            synthesis = await self._synthesize_results(research_results, analysis_results, user_query)
            
            # Generate final response
            final_response = await self._generate_final_response(synthesis, user_query)
            
            logger.info(f"Completed processing query for {symbol}")
            
            return {
                "symbol": symbol,
                "user_query": user_query,
                "research_results": research_results,
                "analysis_results": analysis_results,
                "synthesis": synthesis,
                "final_response": final_response,
                "status": "completed",
                "processing_timestamp": research_results.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "user_query": user_query,
                "error": str(e),
                "status": "failed"
            }
    
    def process_query_sync(self, user_query: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Synchronous version of query processing.
        
        Args:
            user_query: User's question about a stock or investment
            chat_history: Previous conversation context
            
        Returns:
            Dict containing the complete analysis response
        """
        try:
            if chat_history is None:
                chat_history = []
            
            logger.info(f"Processing sync user query: {user_query}")
            
            # Parse the query to extract symbol and requirements
            symbol = self._extract_symbol_from_query(user_query)
            
            if not symbol:
                # If no symbol found, try to search or ask for clarification
                return self._handle_no_symbol_query_sync(user_query, chat_history)
            
            logger.info(f"Extracted symbol: {symbol}")
            
            # Determine research and analysis scope
            research_scope = self._determine_research_scope(user_query)
            analysis_focus = self._determine_analysis_focus(user_query)
            
            logger.info(f"Research scope: {research_scope}, Analysis focus: {analysis_focus}")
            
            # Execute research phase
            research_results = self.research_agent.research_company_sync(symbol, research_scope)
            
            if "error" in research_results:
                return {
                    "symbol": symbol,
                    "user_query": user_query,
                    "error": f"Research phase failed: {research_results['error']}",
                    "status": "failed"
                }
            
            # Execute analysis phase
            analysis_results = self.analysis_agent.analyze_stock_sync(research_results, analysis_focus)
            
            if "error" in analysis_results:
                return {
                    "symbol": symbol,
                    "user_query": user_query,
                    "research_results": research_results,
                    "error": f"Analysis phase failed: {analysis_results['error']}",
                    "status": "partial"
                }
            
            # Synthesize results
            synthesis = self._synthesize_results_sync(research_results, analysis_results, user_query)
            
            # Generate final response
            final_response = self._generate_final_response_sync(synthesis, user_query)
            
            logger.info(f"Completed sync processing query for {symbol}")
            
            return {
                "symbol": symbol,
                "user_query": user_query,
                "research_results": research_results,
                "analysis_results": analysis_results,
                "synthesis": synthesis,
                "final_response": final_response,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error processing sync query: {e}")
            return {
                "user_query": user_query,
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_symbol_from_query(self, query: str) -> Optional[str]:
        """Extract stock symbol from user query."""
        import re
        
        query_upper = query.upper()
        
        # Look for common stock symbol patterns
        patterns = [
            r'\b([A-Z]{1,5})\b(?:\s+(?:stock|shares?|company|corp))?',
            r'\$([A-Z]{1,5})\b',
            r'(?:ticker|symbol):\s*([A-Z]{1,5})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            for match in matches:
                if 1 <= len(match) <= 5 and match.isalpha():
                    # Filter out common English words that might match
                    excluded_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
                    if match not in excluded_words:
                        return match
        
        return None
    
    def _determine_research_scope(self, query: str) -> List[str]:
        """Determine what research scope is needed based on query."""
        query_lower = query.lower()
        
        scope = []
        
        if any(word in query_lower for word in ['comprehensive', 'complete', 'full', 'detailed']):
            return ['comprehensive']
        
        if any(word in query_lower for word in ['company', 'business', 'overview', 'profile']):
            scope.append('company_overview')
        
        if any(word in query_lower for word in ['financial', 'ratios', 'earnings', 'revenue', 'balance']):
            scope.append('financial_data')
        
        if any(word in query_lower for word in ['news', 'sentiment', 'recent', 'developments']):
            scope.append('news_analysis')
        
        if any(word in query_lower for word in ['analyst', 'recommendation', 'rating', 'target']):
            scope.append('analyst_data')
        
        # Default to comprehensive if no specific scope identified
        return scope if scope else ['comprehensive']
    
    def _determine_analysis_focus(self, query: str) -> List[str]:
        """Determine what analysis focus is needed based on query."""
        query_lower = query.lower()
        
        focus = []
        
        if any(word in query_lower for word in ['comprehensive', 'complete', 'full', 'detailed']):
            return ['comprehensive']
        
        if any(word in query_lower for word in ['technical', 'chart', 'price', 'trend', 'momentum']):
            focus.append('technical_analysis')
        
        if any(word in query_lower for word in ['fundamental', 'valuation', 'ratios', 'financial']):
            focus.append('fundamental_analysis')
        
        if any(word in query_lower for word in ['sentiment', 'news', 'market perception']):
            focus.append('sentiment_analysis')
        
        if any(word in query_lower for word in ['risk', 'volatility', 'safety']):
            focus.append('risk_assessment')
        
        # Default to comprehensive if no specific focus identified
        return focus if focus else ['comprehensive']
    
    async def _handle_no_symbol_query(self, query: str, chat_history: List) -> Dict[str, Any]:
        """Handle queries where no stock symbol could be extracted."""
        
        # Try to search for companies mentioned in the query
        search_query = f"Help identify stock symbol or search for companies related to: {query}"
        
        try:
            search_results = self.research_agent.search_companies(query)
            
            if search_results.get("search_results"):
                return {
                    "user_query": query,
                    "message": "I couldn't identify a specific stock symbol. Here are some companies that might match your query:",
                    "search_results": search_results["search_results"],
                    "status": "needs_clarification"
                }
            else:
                return {
                    "user_query": query,
                    "message": "I couldn't identify a specific stock symbol from your query. Please provide a stock symbol (e.g., AAPL for Apple) or be more specific about the company you're interested in.",
                    "status": "needs_clarification"
                }
        
        except Exception as e:
            return {
                "user_query": query,
                "message": "I couldn't identify a specific stock symbol from your query. Please provide a stock symbol (e.g., AAPL for Apple) for analysis.",
                "error": str(e),
                "status": "needs_clarification"
            }
    
    def _handle_no_symbol_query_sync(self, query: str, chat_history: List) -> Dict[str, Any]:
        """Synchronous version of handling no symbol queries."""
        try:
            search_results = self.research_agent.search_companies(query)
            
            if search_results.get("search_results"):
                return {
                    "user_query": query,
                    "message": "I couldn't identify a specific stock symbol. Here are some companies that might match your query:",
                    "search_results": search_results["search_results"],
                    "status": "needs_clarification"
                }
            else:
                return {
                    "user_query": query,
                    "message": "I couldn't identify a specific stock symbol from your query. Please provide a stock symbol (e.g., AAPL for Apple) or be more specific about the company you're interested in.",
                    "status": "needs_clarification"
                }
        
        except Exception as e:
            return {
                "user_query": query,
                "message": "I couldn't identify a specific stock symbol from your query. Please provide a stock symbol (e.g., AAPL for Apple) for analysis.",
                "error": str(e),
                "status": "needs_clarification"
            }
    
    async def _synthesize_results(self, research_results: Dict[str, Any], analysis_results: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Synthesize research and analysis results."""
        try:
            synthesis_query = f"""Synthesize the research and analysis results for the user query: "{user_query}"

Research Results: {research_results.get('research_findings', 'Not available')}
Analysis Results: {analysis_results.get('analysis_findings', 'Not available')}

Provide a comprehensive synthesis that integrates both research findings and analysis insights."""
            
            result = await self.executor.ainvoke({
                "input": synthesis_query,
                "chat_history": []
            })
            
            return {
                "synthesis_findings": result.get("output"),
                "research_summary": research_results,
                "analysis_summary": analysis_results,
                "user_query": user_query
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            return {
                "error": str(e),
                "research_summary": research_results,
                "analysis_summary": analysis_results
            }
    
    def _synthesize_results_sync(self, research_results: Dict[str, Any], analysis_results: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Synchronous version of result synthesis."""
        try:
            synthesis_query = f"""Synthesize the research and analysis results for the user query: "{user_query}"

Research Results: {research_results.get('research_findings', 'Not available')}
Analysis Results: {analysis_results.get('analysis_findings', 'Not available')}

Provide a comprehensive synthesis that integrates both research findings and analysis insights."""
            
            result = self.executor.invoke({
                "input": synthesis_query,
                "chat_history": []
            })
            
            return {
                "synthesis_findings": result.get("output"),
                "research_summary": research_results,
                "analysis_summary": analysis_results,
                "user_query": user_query
            }
            
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            return {
                "error": str(e),
                "research_summary": research_results,
                "analysis_summary": analysis_results
            }
    
    async def _generate_final_response(self, synthesis: Dict[str, Any], user_query: str) -> str:
        """Generate the final response for the user."""
        try:
            response_query = f"""Generate a final response for the user based on the synthesis results:

User Query: "{user_query}"
Synthesis: {synthesis.get('synthesis_findings', 'Not available')}

Create a clear, actionable response that directly addresses the user's question.
Include key findings, recommendations, and any important disclaimers."""
            
            result = await self.executor.ainvoke({
                "input": response_query,
                "chat_history": []
            })
            
            return result.get("output", "Analysis completed but response generation failed.")
            
        except Exception as e:
            logger.error(f"Error generating final response: {e}")
            return f"Analysis completed with some issues. Error in response generation: {str(e)}"
    
    def _generate_final_response_sync(self, synthesis: Dict[str, Any], user_query: str) -> str:
        """Synchronous version of final response generation."""
        try:
            response_query = f"""Generate a final response for the user based on the synthesis results:

User Query: "{user_query}"
Synthesis: {synthesis.get('synthesis_findings', 'Not available')}

Create a clear, actionable response that directly addresses the user's question.
Include key findings, recommendations, and any important disclaimers."""
            
            result = self.executor.invoke({
                "input": response_query,
                "chat_history": []
            })
            
            return result.get("output", "Analysis completed but response generation failed.")
            
        except Exception as e:
            logger.error(f"Error generating final response: {e}")
            return f"Analysis completed with some issues. Error in response generation: {str(e)}"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the master agent configuration."""
        return {
            "agent_type": "Master Agent",
            "model": self.model_name,
            "max_iterations": self.executor.max_iterations,
            "coordinated_agents": [
                self.research_agent.get_agent_info(),
                self.analysis_agent.get_agent_info()
            ],
            "workflow_steps": [
                "Query Analysis",
                "Research Coordination", 
                "Analysis Coordination",
                "Result Synthesis",
                "Response Generation"
            ],
            "description": "Orchestrates comprehensive financial analysis workflow"
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the master agent and sub-agents."""
        return {
            "master_agent": "ready",
            "research_agent": "ready" if self.research_agent else "unavailable",
            "analysis_agent": "ready" if self.analysis_agent else "unavailable",
            "orchestration_tools": len(self.tools)
        }

# Global instance
master_agent = MasterAgent()