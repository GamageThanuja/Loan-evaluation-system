# 🚀 Production Deployment Guide

## Quick Start

**Test Local APIs:**
```bash
source venv/bin/activate

# Option 1: Flask API
python src/inference/deployment_api.py

# Option 2: FastAPI (Recommended)
python src/inference/fastapi_app.py
```

Access at: http://localhost:8080
Docs (FastAPI): http://localhost:8080/docs

## 🐳 Docker Deployment

```bash
# Automated deployment
./deployment/deploy.sh

# Manual
docker build -t home-credit-hybrid:latest -f deployment/docker/Dockerfile .
docker run -d -p 8080:8080 --name home-credit-api home-credit-hybrid:latest
```

## 📋 Files Created

1. `deployment/docker/Dockerfile` - Container image
2. `deployment/requirements.txt` - Production dependencies  
3. `deployment/deploy.sh` - Automated deployment
4. `deployment/test_api.sh` - API testing script
5. `deployment/docker-compose.yml` - Multi-service orchestration
6. `src/inference/fastapi_app.py` - FastAPI application
7. `src/inference/deployment_api.py` - Flask application

## ✅ Complete!
