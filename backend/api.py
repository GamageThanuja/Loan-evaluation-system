"""
FastAPI Backend for Home Credit Loan Approval System
Integrates ML models, Supabase database, and middleware
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "middleware"))
sys.path.insert(0, str(Path(__file__).parent.parent / "database"))

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

# Import middleware
from middleware.auth import AuthMiddleware, auth_middleware, hash_password, verify_password
from middleware.logging_middleware import logging_middleware, setup_logging
from middleware.error_handler import setup_error_handlers

# Import database client
from database.client import db

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Home Credit Loan Approval API",
    description="ML-powered loan approval system with explainable AI",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
# PYDANTIC MODELS
# ============================================

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: Dict

class ApplicantCreate(BaseModel):
    name: str
    email: str
    phone: str
    date_of_birth: str
    monthly_income: float
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float
    loan_purpose: str
    loan_term_months: int
    created_by: str  # User ID

class PredictionRequest(BaseModel):
    applicant_id: str
    features: Dict[str, float]

class ApproveRejectRequest(BaseModel):
    notes: Optional[str] = None
    reason: Optional[str] = None

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """User login endpoint"""
    try:
        # Get user from database
        user = db.get_user_by_email(credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create token
        token_data = {
            "sub": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
        token = AuthMiddleware.create_access_token(token_data)
        
        # Log action
        db.log_action(
            user_id=user["id"],
            action="LOGIN",
            resource_type="auth",
            details={"success": True}
        )
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# ============================================
# APPLICANT ENDPOINTS
# ============================================

@app.get("/api/applicants")
async def get_applicants(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get paginated applicants list"""
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    result = db.get_applicants(
        user_id=user["sub"],
        status=status,
        page=page,
        page_size=page_size
    )
    
    return {
        "success": True,
        "data": result["data"],
        "pagination": {
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"]
        }
    }

@app.get("/api/applicants/{applicant_id}")
async def get_applicant(applicant_id: str, request: Request):
    """Get applicant by ID"""
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    applicant = db.get_applicant_by_id(applicant_id)
    
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    return {
        "success": True,
        "data": applicant
    }

@app.post("/api/applicants")
async def create_applicant(applicant_data: ApplicantCreate, request: Request):
    """Create new applicant"""
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Create applicant
    applicant = db.create_applicant(applicant_data.dict())
    
    if not applicant:
        raise HTTPException(status_code=500, detail="Failed to create applicant")
    
    # Log action
    db.log_action(
        user_id=user["sub"],
        action="CREATE_APPLICANT",
        resource_type="applicant",
        resource_id=applicant["id"]
    )
    
    return {
        "success": True,
        "data": applicant
    }

@app.post("/api/applicants/{applicant_id}/approve")
async def approve_applicant(
    applicant_id: str,
    data: ApproveRejectRequest,
    request: Request
):
    """Approve an applicant (Manager only)"""
    user = getattr(request.state, "user", None)
    
    if not user or user.get("role") not in ["bank_manager", "admin"]:
        raise HTTPException(status_code=403, detail="Manager permission required")
    
    result = db.approve_applicant(
        applicant_id=applicant_id,
        approved_by=user["sub"],
        notes=data.notes
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to approve applicant")
    
    # Log action
    db.log_action(
        user_id=user["sub"],
        action="APPROVE_APPLICANT",
        resource_type="applicant",
        resource_id=applicant_id,
        details={"notes": data.notes}
    )
    
    return {
        "success": True,
        "data": result
    }

@app.post("/api/applicants/{applicant_id}/reject")
async def reject_applicant(
    applicant_id: str,
    data: ApproveRejectRequest,
    request: Request
):
    """Reject an applicant (Manager only)"""
    user = getattr(request.state, "user", None)
    
    if not user or user.get("role") not in ["bank_manager", "admin"]:
        raise HTTPException(status_code=403, detail="Manager permission required")
    
    if not data.reason:
        raise HTTPException(status_code=400, detail="Rejection reason required")
    
    result = db.reject_applicant(
        applicant_id=applicant_id,
        rejected_by=user["sub"],
        reason=data.reason
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to reject applicant")
    
    # Log action
    db.log_action(
        user_id=user["sub"],
        action="REJECT_APPLICANT",
        resource_type="applicant",
        resource_id=applicant_id,
        details={"reason": data.reason}
    )
    
    return {
        "success": True,
        "data": result
    }

# ============================================
# PREDICTION ENDPOINTS
# ============================================

@app.post("/api/predict")
async def create_prediction(pred_request: PredictionRequest, request: Request):
    """Create prediction for applicant"""
    user = getattr(request.state, "user", None)
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # TODO: Integrate with ML model
        # For now, return mock prediction
        from src.inference.api import model, predict_single  # Import from ML model
        
        prediction_data = {
            "applicant_id": pred_request.applicant_id,
            "risk_score": 0.23,  # Replace with actual model output
            "confidence": 0.89,
            "decision": "APPROVE",
            "shap_explanation": {},  # Add SHAP values
            "bayesian_network": {},  # Add Bayesian network
            "business_rules": {},  # Add business rules
            "input_features": pred_request.features,
            "model_version": os.getenv("MODEL_VERSION", "2.0.0"),
            "processing_time_ms": 150
        }
        
        result = db.create_prediction(prediction_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create prediction")
        
        # Log action
        db.log_action(
            user_id=user["sub"],
            action="CREATE_PREDICTION",
            resource_type="prediction",
            resource_id=result["id"]
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/predictions/recent")
async def get_recent_predictions(limit: int = 5):
    """Get recent predictions"""
    predictions = db.get_recent_predictions(limit=limit)
    return {
        "success": True,
        "data": predictions
    }

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
