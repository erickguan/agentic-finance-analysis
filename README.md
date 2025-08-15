# 📈 Financial Analysis AI

A comprehensive financial analysis system powered by LangChain agents that provides multi-perspective stock analysis using advanced AI and real-time financial data.

## 🏗️ Architecture

The system uses a **three-agent architecture** for comprehensive analysis:

- **🎯 Master Agent**: Orchestrates workflow, synthesizes results, handles user interaction
- **🔍 Research Agent**: Gathers data from multiple sources (Alpha Vantage, Yahoo Finance, FMP)
- **📊 Analysis Agent**: Performs technical, fundamental, and sentiment analysis

## ✨ Features

### 📊 **Multi-Perspective Analysis**
- **Technical Analysis**: Moving averages, RSI, volatility, support/resistance
- **Fundamental Analysis**: Financial ratios, valuation metrics, earnings analysis
- **Sentiment Analysis**: News sentiment, analyst recommendations, market perception
- **Risk Assessment**: Volatility analysis, financial health, market risk

### 🎨 **Interactive Interfaces**
- **Streamlit Dashboard**: Beautiful web interface with real-time analysis
- **Command Line Interface**: Quick analysis and batch processing
- **Natural Language Queries**: Ask questions like "Analyze Apple stock" or "What's Tesla's outlook?"

### 🔄 **Intelligent Data Integration**
- **Multiple Data Sources**: Alpha Vantage, Yahoo Finance, Financial Modeling Prep
- **RAG with Vector Database**: FAISS-powered contextual information retrieval
- **Smart Fallbacks**: Automatic fallback between data sources
- **Data Quality Assessment**: Confidence scoring and source tracking

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key (required)
- Alpha Vantage API key (optional but recommended)
- Financial Modeling Prep API key (optional)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd agentic-finance-analysis
```

2. **Install dependencies**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here  # Optional
FMP_API_KEY=your_fmp_key_here  # Optional
```

### Launch the Dashboard

```bash
# Start the Streamlit dashboard
streamlit run app.py
```

Visit `http://localhost:8501` to access the interactive dashboard.

### Command Line Usage

```bash
# Quick analysis
python cli.py --query "Analyze Apple stock"

# Specific symbol analysis
python cli.py --symbol TSLA --analysis comprehensive

# Save results to file
python cli.py --query "What's Microsoft's outlook?" --output results.json

# Check system status
python cli.py --status
```

## 📖 Usage Examples

### Dashboard Queries

- `"Analyze Apple's current position"`
- `"What's the sentiment around Tesla after earnings?"`
- `"Compare Microsoft's valuation metrics"`
- `"Should I invest in NVIDIA based on recent news?"`
- `"Perform comprehensive analysis of Amazon"`

### API Usage

```python
from src.agents.master_agent import master_agent

# Process a query
results = master_agent.process_query_sync("Analyze AAPL stock")

# Access different components
print(results["final_response"])          # Executive summary
print(results["research_results"])        # Research findings
print(results["analysis_results"])        # Analysis metrics
```

### Research Agent Only

```python
from src.agents.research_agent import research_agent

# Gather comprehensive data
research = research_agent.research_company_sync("AAPL", ["comprehensive"])
print(research["research_findings"])
```

### Analysis Agent Only

```python
from src.agents.analysis_agent import analysis_agent

# Analyze with research data
analysis = analysis_agent.analyze_stock_sync(research_data, ["technical_analysis"])
print(analysis["analysis_findings"])
```

## 🛠️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_key_here

# Optional - Data Sources
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here

# Optional - Configuration
VECTOR_DB_PATH=./data/vector_db
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CACHE_DURATION_HOURS=1
```

### Model Configuration

You can customize the AI models used:

```python
# In src/utils/config.py
OPENAI_MODEL = "gpt-4o-mini"           # Main reasoning model
EMBEDDING_MODEL = "text-embedding-3-small"  # For vector search
```

## 📊 Data Sources

### Primary Sources
- **Alpha Vantage**: Company overviews, financial data, earnings
- **Yahoo Finance**: Real-time quotes, news, analyst recommendations  
- **Financial Modeling Prep**: Financial statements, ratios, metrics

### Intelligent Fallbacks
The system automatically tries multiple sources:
1. **Alpha Vantage** (comprehensive data)
2. **Yahoo Finance** (real-time quotes, news)
3. **Financial Modeling Prep** (detailed financials)

## 🏛️ Project Structure

```
agentic-finance-analysis/
├── src/
│   ├── agents/              # LangChain agents
│   │   ├── master_agent.py     # Main orchestrator
│   │   ├── research_agent.py   # Data gathering
│   │   └── analysis_agent.py   # Multi-perspective analysis
│   ├── tools/               # Agent tools
│   │   ├── research_tools.py   # Data retrieval tools
│   │   ├── analysis_tools.py   # Analysis calculations
│   │   └── orchestration_tools.py # Workflow coordination
│   ├── data/               # Existing data infrastructure
│   │   ├── collectors/        # API clients
│   │   ├── processors/        # Data processing
│   │   └── scrapers/         # Web scraping
│   ├── rag/                # RAG and vector search
│   ├── vector_db/          # Vector database management
│   ├── dashboard/          # Streamlit interface
│   └── utils/              # Configuration and helpers
├── app.py                  # Streamlit app entry point
├── cli.py                  # Command line interface
└── README.md              # This file
```

## 🧪 Testing

### Manual Testing

```bash
# Test system status
python cli.py --status

# Test with a simple query
python cli.py --query "Analyze AAPL"

# Test dashboard
streamlit run app.py
```

### Sample Queries

```bash
# Different analysis types
python cli.py --query "Technical analysis of Tesla"
python cli.py --query "Fundamental analysis of Microsoft"
python cli.py --query "News sentiment around Apple"

# Risk assessment
python cli.py --query "What are the risks of investing in NVIDIA?"

# Comparative analysis
python cli.py --query "Compare Amazon and Google valuation metrics"
```

## 🔧 Development

### Adding New Analysis Tools

1. Create tool functions in `src/tools/analysis_tools.py`
2. Add LangChain Tool wrappers in `get_langchain_tools()`
3. Update agent prompts to utilize new tools

### Adding Data Sources

1. Create collector in `src/data/collectors/`
2. Integrate with `src/data/processors/data_processor.py`
3. Add to research tools in `src/tools/research_tools.py`

### Customizing Agents

- **Prompts**: Modify agent prompts in respective agent files
- **Tools**: Add/remove tools from agent configurations
- **Workflow**: Adjust orchestration in `master_agent.py`

## 📈 Performance

### Optimization Features
- **Concurrent Execution**: Parallel data gathering and analysis
- **Multi-level Caching**: Query, data, and analysis result caching
- **Smart Rate Limiting**: Respects API limits across sources
- **Lazy Loading**: Only loads data when needed

### Monitoring
- **Confidence Scoring**: Each analysis includes confidence metrics
- **Data Quality Assessment**: Tracks completeness and source diversity
- **Error Tracking**: Comprehensive logging and error handling

## ⚠️ Limitations & Disclaimers

- **Investment Advice**: This system is for educational and research purposes only. Not financial advice.
- **Data Accuracy**: Analysis quality depends on data source availability and API limits
- **API Dependencies**: Requires external APIs which may have rate limits or costs
- **Model Limitations**: AI analysis should be verified with additional research

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the agent framework
- **Streamlit**: For the interactive dashboard
- **OpenAI**: For the language models
- **Financial Data Providers**: Alpha Vantage, Yahoo Finance, Financial Modeling Prep

---

## 🔍 Troubleshooting

### Common Issues

**1. "No module named 'src'"**
```bash
# Make sure you're in the project root directory
cd agentic-finance-analysis
python -m src.dashboard.main_app  # Alternative launch method
```

**2. "API key not found"**
```bash
# Check your .env file exists and has the correct keys
cat .env
# Verify environment variables are loaded
python cli.py --status
```

**3. "Agent execution failed"**
```bash
# Check the logs for detailed error information
python cli.py --query "test query" --verbose
```

**4. Dashboard not loading**
```bash
# Try alternative port
streamlit run app.py --server.port 8502
```

### Getting Help

- Check the logs in verbose mode: `--verbose`
- Test system status: `python cli.py --status`
- Verify API keys are configured correctly
- Ensure all dependencies are installed

For more detailed troubleshooting, see the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide.