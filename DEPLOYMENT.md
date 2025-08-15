# 🚀 Deployment Guide

This guide covers deployment options for the Financial Analysis AI system.

## 🏠 Local Development

### Quick Setup

1. **Clone and setup**
```bash
git clone <your-repo>
cd agentic-finance-analysis
uv sync  # or pip install -e .
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Test the system**
```bash
python tests/test_system.py
```

4. **Launch dashboard**
```bash
streamlit run app.py
```

## ☁️ Cloud Deployment

### Streamlit Community Cloud

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy financial analysis AI"
git push origin main
```

2. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repo
   - Set environment variables in the Streamlit Cloud UI
   - Deploy with entry point: `app.py`

3. **Environment Variables for Cloud**
```
OPENAI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
```

### Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY uv.lock .

# Install Python dependencies
RUN pip install uv
RUN uv sync --frozen

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data/vector_db

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and run**
```bash
docker build -t financial-analysis-ai .
docker run -p 8501:8501 --env-file .env financial-analysis-ai
```

### AWS Deployment

#### Option 1: EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 22.04)
# Connect via SSH

# Install dependencies
sudo apt update
sudo apt install python3 python3-pip git -y

# Clone repository
git clone <your-repo>
cd agentic-finance-analysis

# Install application
pip3 install -e .

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Install PM2 for process management
sudo npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'financial-analysis-ai',
    script: 'streamlit',
    args: 'run app.py --server.port=8501 --server.address=0.0.0.0',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start application
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Option 2: AWS App Runner

1. **Create `apprunner.yaml`**
```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - echo "Installing dependencies..."
      - pip install -e .
run:
  runtime-version: 3.13
  command: streamlit run app.py --server.port=8080 --server.address=0.0.0.0
  network:
    port: 8080
    env:
      - name: OPENAI_API_KEY
        value: ${OPENAI_API_KEY}
      - name: ALPHA_VANTAGE_API_KEY  
        value: ${ALPHA_VANTAGE_API_KEY}
```

### Google Cloud Platform

#### Cloud Run Deployment

1. **Create `cloudbuild.yaml`**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/financial-analysis-ai', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/financial-analysis-ai']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'financial-analysis-ai'
    - '--image'
    - 'gcr.io/$PROJECT_ID/financial-analysis-ai'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
```

2. **Deploy**
```bash
gcloud builds submit --config cloudbuild.yaml
```

## 🔐 Security Considerations

### API Key Management

1. **Never commit API keys to version control**
2. **Use environment variables or secret managers**
3. **Rotate keys regularly**
4. **Set up API usage monitoring**

### Access Control

1. **Enable authentication if needed**
```python
# Add to app.py for basic auth
import streamlit_authenticator as stauth

# Configure authentication
authenticator = stauth.Authenticate(
    credentials,
    'financial_analysis_ai',
    'secure_key_here',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Your existing app code
    main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
```

## 📊 Monitoring & Logging

### Application Monitoring

1. **Add logging to production**
```python
import logging
import sys

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

2. **Monitor API usage**
```python
# Track API calls and costs
import time
from collections import defaultdict

class APIUsageTracker:
    def __init__(self):
        self.usage = defaultdict(int)
        self.costs = defaultdict(float)
    
    def track_call(self, service, cost=0):
        self.usage[service] += 1
        self.costs[service] += cost
        
        # Log high usage
        if self.usage[service] % 100 == 0:
            logging.info(f"{service} usage: {self.usage[service]} calls")
```

### Health Checks

```python
# Add health check endpoint
@st.cache_data(ttl=60)
def health_check():
    try:
        # Test master agent
        status = master_agent.get_status()
        return {"status": "healthy", "agents": status}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## 🔧 Performance Optimization

### Production Settings

1. **Enable caching**
```python
# Add to streamlit config.toml
[server]
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
```

2. **Database optimization**
```python
# Optimize vector database for production
VECTOR_DB_CONFIG = {
    "index_type": "HNSW",  # Faster than flat index
    "ef_construction": 200,
    "M": 16
}
```

### Scaling Considerations

1. **Horizontal scaling**: Deploy multiple instances behind a load balancer
2. **Caching layer**: Add Redis for query result caching
3. **Rate limiting**: Implement per-user rate limiting
4. **Queue system**: Use Celery for background processing

## 📋 Production Checklist

### Pre-deployment

- [ ] All tests passing (`python tests/test_system.py`)
- [ ] API keys configured and tested
- [ ] Error handling and logging implemented
- [ ] Security measures in place
- [ ] Performance testing completed
- [ ] Documentation updated

### Post-deployment

- [ ] Health checks configured
- [ ] Monitoring and alerting set up
- [ ] Backup procedures in place
- [ ] Disaster recovery plan documented
- [ ] User training materials prepared

## 🆘 Troubleshooting

### Common Deployment Issues

1. **Module import errors**
```bash
# Ensure Python path is correct
export PYTHONPATH=/app/src:$PYTHONPATH
```

2. **API rate limits**
```python
# Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

3. **Memory issues**
```bash
# Monitor memory usage
free -h
# Adjust vector database settings
# Consider using disk-based storage
```

4. **SSL/TLS issues**
```bash
# For HTTPS deployment
pip install pyopenssl
# Configure reverse proxy (nginx)
```

## 📞 Support

For deployment issues:

1. Check the logs: `tail -f app.log`
2. Test system status: `python cli.py --status`
3. Run diagnostics: `python tests/test_system.py`
4. Review the troubleshooting guide in README.md

Remember: This system is for educational/research purposes. Ensure compliance with financial regulations if deploying for commercial use.