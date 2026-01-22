"""
FastAPI Backend for Home Credit Loan Approval System
Integrates ML models, Supabase database, and middleware
"""

import sys
from pathlib import Path

# Add paths to Python path
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root / "middleware"))
sys.path.insert(0, str(project_root / "database"))

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

# Security scheme for Swagger
security = HTTPBearer()

# Load environment variables first
load_dotenv(project_root / ".env")

# Import middleware
sys.path.insert(0, str(project_root))
from middleware.auth import AuthMiddleware, auth_middleware, hash_password, verify_password
from middleware.logging_middleware import logging_middleware, setup_logging
from middleware.error_handler import setup_error_handlers

# Import database client
from database.client import db

# Import routers
from routers import auth as auth_module
from routers import loan_details as loan_details_module
from routers import applicants as applicants_module
from routers import predictions as predictions_module
from routers import status_management as status_management_module

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="LoanWise API",
    description="ML-powered loan approval system with explainable AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security scheme to OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title="LoanWise API",
        version="2.0.0",
        description="ML-powered loan approval system with explainable AI",
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token from /api/auth/login"
        }
    }
    
    # Apply security globally to all endpoints (Swagger will send the token)
    openapi_schema["security"] = [{"HTTPBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.middleware("http")(logging_middleware)
app.middleware("http")(auth_middleware)

# Setup error handlers
setup_error_handlers(app)

# ============================================
# MOUNT ROUTERS
# ============================================

# Mount authentication router
app.include_router(auth_module.router)

# Mount loan details router
app.include_router(loan_details_module.router)

# Mount applicants router (CRUD)
app.include_router(applicants_module.router)

# Mount predictions router (ML model predictions with reasoning)
app.include_router(predictions_module.router)

# Mount status management router (Eligibility, Application Status, Status Colors)
app.include_router(status_management_module.router)

# ============================================
# DASHBOARD ENDPOINTS
# ============================================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = db.get_dashboard_stats()
    return {
        "success": True,
        "data": stats
    }

@app.get("/api/model/health")
async def model_health():
    """Model health check"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": os.getenv("MODEL_VERSION", "2.0.0"),
            "response_time_ms": 45
        }
    }

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_DEBUG", "False").lower() == "true"
    )
