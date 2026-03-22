"""
Predictions Router
ML model predictions with Bayesian Network reasoning and explainability
Suitable for LoanWise v4.0 (Hybrid ANN + BN)
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import numpy as np

# Add parent directories to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Import database client
from database.client import db
from middleware.auth import AuthMiddleware

# Import credit score reasoning module
from src.models.reasoning import (
    evaluate_loan_application,
    get_credit_score_rating
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

# ============================================
# GLOBAL STATE
# ============================================

hybrid_predictor = None

# ============================================
# PYDANTIC MODELS
# ============================================

class FeatureInfluence(BaseModel):
    feature_name: str
    feature_value: float
    discretized_value: int
    influence_direction: str
    influence_strength: float
    conditional_probability: float
    explanation: str

class PredictionRequest(BaseModel):
    features: Dict[str, float] = Field(..., description="Feature values for prediction")

class EligibilityPredictionRequest(BaseModel):
    applicant_id: str = Field(..., description="Applicant ID")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_term_months: int = Field(..., ge=6, le=360, description="Loan term in months")
    monthly_income: Optional[float] = Field(None, description="Monthly income")

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    decision: str
    threshold_used: float

# ============================================
# STARTUP - LOAD MODELS
# ============================================

def load_models():
    """Load ML models at startup"""
    global hybrid_predictor
    
    try:
        from src.inference.predictor import LoanPredictor
        hybrid_predictor = LoanPredictor()
        logger.info(f"✅ Loaded Hybrid Bayesian Model (v{hybrid_predictor.MODEL_VERSION})")
        logger.info(f"✅ Optimal threshold: {hybrid_predictor.OPTIMAL_THRESHOLD}")
    except Exception as e:
        logger.error(f"❌ Could not load hybrid model: {e}")
        hybrid_predictor = None

load_models()

# ============================================
# ENDPOINTS
# ============================================

@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Basic prediction endpoint"""
    if hybrid_predictor is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model not loaded")
    
    try:
        result = hybrid_predictor.predict(request.features)
        return PredictionResponse(
            prediction=result['prediction'],
            probability=result['probability'],
            risk_level=result['risk_level'],
            decision=result['decision'],
            threshold_used=result['threshold_used']
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("/eligibility")
async def check_eligibility(
    request: EligibilityPredictionRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """Full eligibility check with reasoning"""
    if hybrid_predictor is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model not loaded")
    
    try:
        # 1. Fetch Applicant
        applicant = db.get_applicant_by_id(request.applicant_id)
        if not applicant:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Applicant not found")
        
        # 2. Prepare Data
        monthly_income = request.monthly_income or applicant.get('monthly_income') or 0
        
        features = hybrid_predictor.prepare_features_from_applicant(
            applicant, request.loan_amount, request.loan_term_months
        )
        
        # 3. Predict & Explain
        result = hybrid_predictor.explain(features)
        
        probability = result['probability']
        prediction = result['prediction']
        eligible = (prediction == 1)
        
        # 4. Multi-factor Reasoning
        # Calculate days employed from years_employed (if available)
        days_employed = int(applicant.get('years_employed', 0) * 365) if applicant.get('years_employed') is not None else None

        loan_reasoning = evaluate_loan_application(
            model_probability=probability,
            loan_amount=request.loan_amount,
            monthly_income=monthly_income,
            loan_term_months=request.loan_term_months,
            # Pass credit_score directly, default to None if missing (reasoning engine will handle or use 0)
            credit_score=applicant.get('credit_score'),
            days_employed=days_employed
        )
        
        # Override eligibility based on strict reasoning rules if needed
        final_eligible = loan_reasoning.eligible
        
        # 5. Persist Results (Crucial for Dashboard)
        update_data = {
            "eligibility_status": "eligible" if final_eligible else "not_eligible",
            "risk_score": probability,  # Store the raw probability (higher is better)
            "updated_at": datetime.utcnow().isoformat()
        }
        db.update_applicant(request.applicant_id, update_data)
        
        # Log detailed action
        db.log_action(
            user_id=user.get("user_id", "system"),
            action="CHECK_ELIGIBILITY",
            resource_type="applicant",
            resource_id=request.applicant_id,
            details={
                "eligible": final_eligible,
                "probability": probability,
                "amount": request.loan_amount
            }
        )
        
        # 6. Construct Response
        return {
            "success": True,
            "data": {
                "applicant_id": request.applicant_id,
                "decision": {
                    "eligible": final_eligible,
                    "status": "APPROVE" if final_eligible else "REJECT",
                    "risk_level": loan_reasoning.risk_level,
                    "probability_percentage": round(probability * 100, 1)
                },
                "financials": {
                    "loan_amount": request.loan_amount,
                    "monthly_income": monthly_income,
                    "term_months": request.loan_term_months
                },
                "reasoning": {
                    "summary": loan_reasoning.summary,
                    "risk_factors": [r.to_dict() for r in loan_reasoning.risk_factors],
                    "protective_factors": [r.to_dict() for r in loan_reasoning.protective_factors],
                    "suggestions": [s.to_dict() for s in loan_reasoning.suggestions]
                },
                "model_info": {
                    "version": hybrid_predictor.MODEL_VERSION,
                    "threshold": hybrid_predictor.OPTIMAL_THRESHOLD
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Eligibility error: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
