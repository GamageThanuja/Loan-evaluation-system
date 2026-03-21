"""
Predictions Router
ML model predictions with Bayesian Network reasoning and explainability
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
    get_credit_score_rating,
    CreditScoreRating
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

# ============================================
# GLOBAL STATE
# ============================================

# Model instances (loaded at startup)
hybrid_predictor = None
feature_names = None
optimal_threshold = 0.15


# ============================================
# PYDANTIC MODELS
# ============================================

class FeatureInfluence(BaseModel):
    """Feature influence on prediction"""
    feature_name: str
    feature_value: float
    discretized_value: int
    influence_direction: str  # "increases_risk", "decreases_risk", "neutral"
    influence_strength: float
    conditional_probability: float
    explanation: str


class InferencePath(BaseModel):
    """Inference path in the Bayesian Network"""
    parent_nodes: List[str]
    child_nodes: List[str]
    path_strength: float
    description: str


class PredictionRequest(BaseModel):
    """Request for prediction with features"""
    features: Dict[str, float] = Field(..., description="Feature values for prediction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": {
                    "EXT_SOURCE_2": 0.6,
                    "EXT_SOURCE_3": 0.4,
                    "EXT_SOURCE_MEAN": 0.5,
                    "AGE_YEARS": 35,
                    "CREDIT_INCOME_RATIO": 2.1,
                    "DAYS_EMPLOYED": -2000
                }
            }
        }


class EligibilityPredictionRequest(BaseModel):
    """Request for eligibility prediction"""
    applicant_id: int = Field(..., description="Applicant ID")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_term_months: int = Field(..., ge=6, le=360, description="Loan term in months")
    monthly_income: Optional[float] = Field(None, description="Monthly income (optional, will use database value if not provided)")


class PredictionResponse(BaseModel):
    """Basic prediction response"""
    prediction: int
    probability: float
    risk_level: str
    decision: str
    threshold_used: float


class ReasoningResponse(BaseModel):
    """Full prediction with Bayesian reasoning"""
    prediction: int
    probability: float
    risk_level: str
    decision: str
    
    # Reasoning from Bayesian Network
    top_risk_factors: List[FeatureInfluence]
    top_protective_factors: List[FeatureInfluence]
    inference_paths: List[InferencePath]
    
    # Natural language explanations
    summary_explanation: str
    detailed_explanation: str
    
    # Confidence metrics
    confidence_score: float
    evidence_strength: str
    
    # Model info
    model_type: str = "Hybrid TabNet + Bayesian Network"


class EligibilityResponse(BaseModel):
    """Eligibility check response with reasoning"""
    eligible: bool
    risk_score: float
    probability: float
    decision: str
    risk_level: str
    
    # Reasoning
    summary_explanation: str
    risk_factors: List[Dict[str, Any]]
    protective_factors: List[Dict[str, Any]]
    
    # Recommendations
    recommendations: List[str]
    
    # Confidence
    confidence_score: float


# ============================================
# STARTUP - LOAD MODELS
# ============================================

def load_models():
    """Load ML models at startup"""
    global hybrid_predictor, feature_names, optimal_threshold
    
    try:
        # Load the new Hybrid Bayesian Model predictor
        from src.inference.predictor import LoanPredictor
        
        try:
            hybrid_predictor = LoanPredictor()
            feature_names = hybrid_predictor.feature_names
            optimal_threshold = hybrid_predictor.OPTIMAL_THRESHOLD
            logger.info(f"✅ Loaded Hybrid Bayesian Model (v{hybrid_predictor.MODEL_VERSION})")
            logger.info(f"   Architecture: BN (PGMPY) + BNN (PyTorch MC-Dropout)")
            logger.info(f"✅ Loaded {len(feature_names)} feature names")
            logger.info(f"✅ Optimal threshold: {optimal_threshold:.3f}")
        except Exception as e:
            logger.error(f"❌ Could not load hybrid model: {e}")
            hybrid_predictor = None
        
        logger.info("🎉 Predictions router models loaded!")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")


# Load models when module is imported
load_models()


# ============================================
# HELPER FUNCTIONS
# ============================================

# Feature name to human-readable mapping (Plain English, no technical jargon)
FEATURE_TRANSLATIONS = {
    'EXT_SOURCE_1': 'Credit History',
    'EXT_SOURCE_2': 'Payment Track Record',
    'EXT_SOURCE_3': 'Financial Trustworthiness',
    'EXT_SOURCE_MEAN': 'Overall Credit Standing',
    'EXT_SOURCE_STD': 'Credit Score Consistency',
    'DAYS_LAST_PHONE_CHANGE': 'Contact Stability',
    'inst_AMT_PAYMENT_min': 'Monthly Payment Amount',
    'DAYS_EMPLOYED': 'Job Stability',
    'DAYS_BIRTH': 'Age',
    'AGE_YEARS': 'Age',
    'CREDIT_INCOME_RATIO': 'Loan Size vs Income',
    'ANNUITY_INCOME_RATIO': 'Monthly Payment vs Salary',
    'AMT_CREDIT': 'Loan Amount',
    'AMT_INCOME_TOTAL': 'Annual Income',
    'AMT_ANNUITY': 'Monthly Payment',
    'CODE_GENDER': 'Gender',
    'NAME_EDUCATION_TYPE': 'Education',
    'REGION_RATING_CLIENT': 'Living Area',
    'REG_CITY_NOT_WORK_CITY': 'Work Location',
    'bureau_DAYS_CREDIT_max': 'Credit History Length',
    'bureau_DAYS_CREDIT_min': 'Recent Credit Activity',
    'bureau_DAYS_CREDIT_mean': 'Credit Experience',
    'bureau_AMT_CREDIT_SUM_DEBT_mean': 'Existing Loans',
    'inst_DAYS_INSTALMENT_min': 'Payment Habits',
    'prev_DAYS_DECISION_min': 'Past Loan Applications',
    'prev_DAYS_DECISION_mean': 'Borrowing History',
    # Additional simplified names
    'sk_bureau_DAYS_CREDIT_min': 'Credit Account Age',
    'sk_bureau_DAYS_CREDIT_max': 'Oldest Credit Account',
    'bb_MONTHS_BALANCE_min': 'Bank Account History',
    'prev_SK_ID_PREV_count': 'Past Applications',
    'prev_AMT_CREDIT_min': 'Previous Loan Amounts',
    'FLAG_OWN_CAR': 'Vehicle Ownership',
    'FLAG_OWN_REALTY': 'Property Ownership',
}

# Human-readable explanations for risk factors (Plain English for everyday people)
RISK_EXPLANATIONS = {
    'EXT_SOURCE_1': {
        'low': 'Your credit history shows some missed or late payments in the past.',
        'medium': 'Your credit history is okay, with a few minor issues.',
        'high': 'Your credit history is excellent - you always pay on time!'
    },
    'EXT_SOURCE_2': {
        'low': 'Bank records show you may have struggled with payments before.',
        'medium': 'Your bank payment history is average - mostly on time.',
        'high': 'Your bank payment history is great - very reliable!'
    },
    'EXT_SOURCE_3': {
        'low': 'Overall, the financial check shows some concerns about paying back this loan.',
        'medium': 'The financial check shows you are a moderate risk borrower.',
        'high': 'The financial check shows you are a very trustworthy borrower!'
    },
    'EXT_SOURCE_MEAN': {
        'low': 'Looking at all credit checks together, there are some concerns.',
        'medium': 'Your overall credit standing is average.',
        'high': 'Your overall credit standing is excellent!'
    },
    'DAYS_LAST_PHONE_CHANGE': {
        'low': 'You recently changed your phone number, which can be a minor concern.',
        'medium': 'Your contact details have been fairly stable.',
        'high': 'Your contact details have been stable for a long time - that is good!'
    },
    'inst_AMT_PAYMENT_min': {
        'low': 'The monthly payment amount is affordable for you.',
        'medium': 'The monthly payment takes up a fair portion of your income.',
        'high': 'The monthly payment is quite high compared to what you earn.'
    },
    'CREDIT_INCOME_RATIO': {
        'low': 'The loan amount is reasonable compared to what you earn.',
        'medium': 'The loan amount is moderate compared to your income.',
        'high': 'The loan amount is very high compared to what you earn - this is a concern.'
    },
    'ANNUITY_INCOME_RATIO': {
        'low': 'Your monthly payments will be easy to manage with your salary.',
        'medium': 'Your monthly payments will take up a fair amount of your salary.',
        'high': 'Your monthly payments would use up too much of your salary.'
    }
}

# Default interest rate for calculations (annual)
DEFAULT_INTEREST_RATE = 12.0  # 12% per annum


def get_risk_level(probability: float) -> str:
    """Get risk level string from probability.
    
    Note: In our model, higher probability = more likely to be APPROVED.
    So high probability = low risk, low probability = high risk.
    """
    if probability >= 0.8:
        return "Very Low Risk"
    elif probability >= 0.65:
        return "Low Risk"
    elif probability >= 0.5:
        return "Medium Risk"
    elif probability >= 0.35:
        return "High Risk"
    else:
        return "Very High Risk"


def translate_feature_name(technical_name: str) -> str:
    """Convert technical feature name to human-readable term"""
    return FEATURE_TRANSLATIONS.get(technical_name, technical_name.replace('_', ' ').title())


def get_risk_explanation(feature_name: str, discretized_value: int, influence_direction: str) -> str:
    """Get human-readable explanation for a risk factor
    
    The explanation must be CONSISTENT with the influence_direction:
    - If 'increases_risk' (concern), explain why it's a problem
    - If 'decreases_risk' (positive), explain why it's good
    
    Uses simple, everyday language that anyone can understand.
    """
    human_name = translate_feature_name(feature_name)
    
    # For CONCERNS (increases_risk) - explain why this factor is worrying in plain English
    if influence_direction == 'increases_risk':
        concern_explanations = {
            'EXT_SOURCE_1': "Your credit history shows some past payment problems.",
            'EXT_SOURCE_2': "Your bank payment records show some late or missed payments.",
            'EXT_SOURCE_3': "The financial check shows some concerns about paying back loans.",
            'DAYS_LAST_PHONE_CHANGE': "You recently changed your phone number, which can suggest instability.",
            'sk_bureau_DAYS_CREDIT_min': "You don't have a long credit history yet.",
            'sk_bureau_DAYS_CREDIT_max': "Your credit accounts are relatively new.",
            'inst_AMT_PAYMENT_min': "Your past payments have been smaller than expected.",
            'bb_MONTHS_BALANCE_min': "Your bank account history shows some concerning patterns.",
            'prev_SK_ID_PREV_count': "You've applied for several loans before, which can be a concern.",
            'prev_AMT_CREDIT_min': "Your past borrowing pattern shows higher risk.",
            'CREDIT_INCOME_RATIO': "The loan amount is high compared to what you earn.",
            'ANNUITY_INCOME_RATIO': "The monthly payments would be difficult to afford with your income.",
            'DAYS_EMPLOYED': "You haven't been at your current job for very long.",
            'DAYS_BIRTH': "Your age group tends to have more difficulty with loan repayments.",
            'FLAG_OWN_CAR': "Not owning a vehicle means you have fewer assets.",
            'FLAG_OWN_REALTY': "Not owning property means you have fewer assets as security."
        }
        return concern_explanations.get(
            feature_name, 
            f"Your {human_name.lower()} raises some concerns for this loan."
        )
    
    # For POSITIVE FACTORS (decreases_risk) - explain why this factor is good in plain English
    else:
        positive_explanations = {
            'EXT_SOURCE_1': "Your credit history is excellent - you always pay on time!",
            'EXT_SOURCE_2': "Your bank payment records show you're very reliable.",
            'EXT_SOURCE_3': "The financial check shows you're a trustworthy borrower.",
            'DAYS_LAST_PHONE_CHANGE': "Your contact details have been stable, showing reliability.",
            'sk_bureau_DAYS_CREDIT_min': "You have good experience managing credit.",
            'sk_bureau_DAYS_CREDIT_max': "You've had credit accounts for a long time, showing stability.",
            'inst_AMT_PAYMENT_min': "You have a good track record of making payments.",
            'bb_MONTHS_BALANCE_min': "Your bank account history looks healthy.",
            'prev_SK_ID_PREV_count': "You've managed your previous loans responsibly.",
            'prev_AMT_CREDIT_min': "Your past borrowing shows responsible behavior.",
            'CREDIT_INCOME_RATIO': "The loan amount is reasonable for your income level.",
            'ANNUITY_INCOME_RATIO': "You can easily afford the monthly payments.",
            'DAYS_EMPLOYED': "You've been at your job for a good amount of time.",
            'DAYS_BIRTH': "Your age shows financial maturity and stability.",
            'FLAG_OWN_CAR': "Owning a vehicle shows you're financially responsible.",
            'FLAG_OWN_REALTY': "Owning property gives you a strong financial foundation."
        }
        return positive_explanations.get(
            feature_name, 
            f"Your {human_name.lower()} is a positive point for this loan."
        )


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    if amount >= 1_000_000_000:
        return f"LKR {amount/1_000_000_000:.2f} Billion"
    elif amount >= 1_000_000:
        return f"LKR {amount/1_000_000:.2f} Million"
    elif amount >= 1_000:
        return f"LKR {amount:,.2f}"
    else:
        return f"LKR {amount:.2f}"


def generate_human_summary(
    eligible: bool,
    probability: float,
    loan_amount: float,
    monthly_income: float,
    loan_to_income_ratio: float,
    payment_to_income_ratio: float,
    risk_factors: List[Dict],
    protective_factors: List[Dict]
) -> str:
    """Generate a simple, human-friendly summary explanation"""
    
    if eligible:
        summary = "Good News - Loan Approved. "
        summary += "We have reviewed your application and you qualify for this loan. "
        
        if loan_to_income_ratio < 2:
            summary += f"The loan amount of {format_currency(loan_amount)} is reasonable for your income level. "
        
        if payment_to_income_ratio < 0.3:
            payment_percent = int(payment_to_income_ratio * 100)
            summary += f"Your monthly payments will be about {payment_percent}% of your income, which is very manageable. "
        elif payment_to_income_ratio < 0.4:
            payment_percent = int(payment_to_income_ratio * 100)
            summary += f"Your monthly payments will be about {payment_percent}% of your income. "
        
    else:
        summary = "Loan Not Approved. "
        summary += "We are sorry, but we cannot approve this loan at this time. "
        
        concerns = []
        
        if loan_to_income_ratio > 5:
            concerns.append(f"the loan amount ({format_currency(loan_amount)}) is too large for your current income")
        elif loan_to_income_ratio > 2:
            concerns.append(f"the loan amount is high compared to your income")
        
        if payment_to_income_ratio > 0.5:
            concerns.append(f"the monthly payments would take more than half your salary")
        elif payment_to_income_ratio > 0.4:
            concerns.append(f"the monthly payments would be difficult to manage")
        
        if concerns:
            summary += "Here is why: " + "; ".join(concerns) + ". "
        
        summary += "You may want to try a smaller loan amount or work on improving your credit score first."
    
    return summary


def generate_smart_recommendations(
    eligible: bool,
    probability: float,
    loan_amount: float,
    loan_term_months: int,
    monthly_income: float,
    annual_income: float,
    loan_to_income_ratio: float,
    payment_to_income_ratio: float,
    risk_factors: List[Dict]
) -> List[str]:
    """Generate simple, practical recommendations"""
    
    recommendations = []
    
    if eligible:
        recommendations.append("Great news! You qualify for this loan.")
        recommendations.append("You can now proceed to complete the paperwork.")
        recommendations.append("Keep making timely payments to maintain your good credit standing.")
        
        if loan_to_income_ratio < 1 and payment_to_income_ratio < 0.2:
            recommendations.append("Your strong financial position may qualify you for better rates in the future.")
    else:
        max_affordable_payment = monthly_income * 0.4
        safe_loan_amount = annual_income * 3
        
        if loan_to_income_ratio > 3:
            recommendations.append(
                f"Consider a smaller loan amount. Based on your income, you could afford up to {format_currency(safe_loan_amount)}."
            )
        
        if payment_to_income_ratio > 0.4:
            if loan_term_months < 60:
                recommendations.append(
                    "Spread payments over a longer period (such as 60 months) to make them more affordable."
                )
            elif loan_term_months < 120:
                recommendations.append(
                    "Consider a 10-year repayment plan to lower your monthly payments."
                )
            else:
                max_affordable_loan_very_long = max_affordable_payment * 120
                recommendations.append(
                    f"The loan amount is too large. Consider reducing it to {format_currency(max_affordable_loan_very_long)} or less."
                )
        
        for rf in risk_factors:
            feature = rf.get('feature_name', '')
            if 'credit' in feature.lower() or 'cibil' in feature.lower():
                recommendations.append(
                    "Work on improving your credit score by paying bills on time for 6-12 months."
                )
                break
        
        if loan_amount > annual_income * 5:
            recommendations.append(
                "You could apply with a family member or friend as a co-borrower to strengthen your application."
            )
        
        recommendations.append(
            "You can apply again after making these improvements or with a smaller loan amount."
        )
    
    return recommendations[:5]


def humanize_risk_factors(factors: List[Dict], is_positive: bool = False) -> List[Dict]:
    """Convert technical factors to human-readable format"""
    humanized = []
    
    # Clear, simple explanations for each factor type
    positive_explanations = {
        'cibil_score': 'Your credit score is a positive point for this loan.',
        'loan_to_income_ratio': 'Your loan to income ratio is a positive point for this loan.',
        'total_assets': 'Your total assets is a positive point for this loan.',
        'payment_to_income_ratio': 'Your payment to income ratio is a positive point for this loan.',
        'income_annum': 'Your annual income is a positive point for this loan.',
        'loan_amount': 'Your requested loan amount is reasonable for your profile.'
    }
    
    concern_explanations = {
        'cibil_score': 'Your credit score raises some concerns for this loan.',
        'loan_to_income_ratio': 'Your loan to income ratio raises some concerns for this loan.',
        'total_assets': 'Your total assets raises some concerns for this loan.',
        'payment_to_income_ratio': 'Your payment to income ratio raises some concerns for this loan.',
        'income_annum': 'Your annual income level raises some concerns for this loan.',
        'loan_amount': 'Your requested loan amount is high relative to your financial profile.'
    }
    
    for factor in factors:
        technical_name = factor.get('feature_name', '')
        
        if is_positive:
            explanation = positive_explanations.get(technical_name, 
                f'Your {technical_name.replace("_", " ")} is a positive point for this loan.')
        else:
            explanation = concern_explanations.get(technical_name,
                f'Your {technical_name.replace("_", " ")} raises some concerns for this loan.')
        
        humanized.append({
            'factor': technical_name.replace('_', ' ').title(),
            'explanation': explanation
        })
    
    return humanized


def prepare_features_array(features: Dict[str, float]) -> np.ndarray:
    """Prepare feature array for TabNet prediction"""
    if not feature_names:
        raise ValueError("Feature names not loaded")
    
    feature_array = np.zeros(len(feature_names))
    for i, name in enumerate(feature_names):
        if name in features:
            feature_array[i] = features[name]
    
    return feature_array.reshape(1, -1)


def generate_recommendations(probability: float, risk_factors: List[Dict]) -> List[str]:
    """Generate recommendations based on prediction - LEGACY, use generate_smart_recommendations instead"""
    recommendations = []
    
    if probability > 0.5:
        recommendations.append("Consider requesting additional collateral or a guarantor")
        recommendations.append("Review applicant's credit history in detail")
    else:
        recommendations.append("Application meets standard approval criteria")
        recommendations.append("Consider fast-track processing for this applicant")
    
    return recommendations[:5]


# ============================================
# PREDICTION ENDPOINTS
# ============================================

@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Create a basic prediction without detailed reasoning
    
    **Access**: Loan Officers and Managers
    
    Returns:
    - Prediction (0 = no default, 1 = default)
    - Probability of default
    - Risk level
    - Decision (APPROVE/REJECT)
    """
    if hybrid_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Get prediction from hybrid model
        result = hybrid_predictor.predict(request.features)
        
        return PredictionResponse(
            prediction=result['prediction'],
            probability=result['probability'],
            risk_level=result['risk_level'],
            decision="REJECT" if result['prediction'] == 1 else "APPROVE",
            threshold_used=result['threshold_used']
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/explain")
async def predict_with_explanation(
    request: PredictionRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Create prediction with full reasoning and explanation
    
    **Access**: Loan Officers and Managers
    
    The Hybrid Bayesian Model combines:
    - **Bayesian Network (PGMPY)**: Causal structure learning & risk embeddings
    - **Bayesian Neural Network (PyTorch)**: MC-Dropout for uncertainty quantification
    - **ELBO Loss**: BCE + KL Divergence with class weights
    
    Returns:
    - Prediction and probability
    - Risk factors with explanations
    - Recommendations
    - Confidence score with uncertainty estimates
    """
    if hybrid_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Get full explanation from hybrid model
        result = hybrid_predictor.explain(request.features)
        
        # Format risk factors for display
        risk_factors = []
        protective_factors = []
        
        for factor in result.get('top_factors', []):
            factor_info = {
                'feature_name': factor['feature'],
                'importance': factor['importance'],
                'feature_value': factor.get('value', 0),
                'discretized_value': 1,
                'influence_direction': 'increases_risk',
                'influence_strength': factor['importance'],
                'conditional_probability': result['probability'],
                'explanation': get_risk_explanation(factor['feature'], 1, 'increases_risk')
            }
            
            # Classify based on influence
            if result['prediction'] == 1:
                risk_factors.append(factor_info)
            else:
                factor_info['influence_direction'] = 'decreases_risk'
                factor_info['explanation'] = get_risk_explanation(factor['feature'], 1, 'decreases_risk')
                protective_factors.append(factor_info)
        
        reasoning_dict = {
            "prediction": result['prediction'],
            "probability": result['probability'],
            "risk_level": result['risk_level'],
            "decision": result['decision'],
            "summary_explanation": result['message'],
            "top_risk_factors": risk_factors[:3],
            "top_protective_factors": protective_factors[:3],
            "inference_paths": [],
            "detailed_explanation": result.get('recommendation', ''),
            "confidence_score": result.get('confidence', 95.0) / 100,
            "evidence_strength": "High" if result.get('confidence', 95) > 80 else "Moderate",
            "model_type": "Hybrid Bayesian (BN + BNN with MC-Dropout)"
        }
        
        return {
            "success": True,
            "reasoning": reasoning_dict
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction with explanation failed: {str(e)}"
        )


@router.post("/eligibility")
async def check_eligibility(
    request: EligibilityPredictionRequest,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Check loan eligibility for an applicant with ML-based reasoning
    
    **Access**: Loan Officers and Managers
    
    This endpoint:
    1. Retrieves applicant data from the database
    2. Prepares features for the hybrid ML model
    3. Runs prediction through GradientBoost + Bayesian
    4. Returns eligibility decision with full reasoning
    """
    if hybrid_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Get applicant from database
        applicant = db.get_applicant_by_id(request.applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Get applicant income for response
        monthly_income = request.monthly_income if request.monthly_income is not None else applicant.get('monthly_income', 50000)
        annual_income = monthly_income * 12
        loan_to_income_ratio = request.loan_amount / annual_income if annual_income > 0 else 999
        monthly_payment = request.loan_amount / request.loan_term_months
        payment_to_income_ratio = monthly_payment / monthly_income if monthly_income > 0 else 999
        
        # Prepare features from applicant data using predictor's method
        features = hybrid_predictor.prepare_features_from_applicant(
            applicant, request.loan_amount, request.loan_term_months
        )
        
        # Get prediction with explanation from hybrid model
        result = hybrid_predictor.explain(features)
        
        probability = result['probability']
        prediction = result['prediction']
        confidence_score = result.get('confidence', 95.0) / 100
        summary_explanation = result.get('message', '')
        
        # Format risk/protective factors
        risk_factors = []
        protective_factors = []
        
        for factor in result.get('top_factors', []):
            factor_info = {
                'feature_name': factor['feature'],
                'importance': factor['importance'],
                'explanation': get_risk_explanation(factor['feature'], 1, 
                    'decreases_risk' if prediction == 1 else 'increases_risk')
            }
            # prediction=1 means APPROVED, so factors are protective
            # prediction=0 means REJECTED, so factors are risks
            if prediction == 1:
                protective_factors.append(factor_info)
            else:
                risk_factors.append(factor_info)
        
        # Determine eligibility
        # Note: Model trained with Approved=1, Rejected=0
        # So prediction=1 means eligible, prediction=0 means not eligible
        eligible = prediction == 1
        decision = "APPROVE" if eligible else "REJECT"
        risk_level = get_risk_level(probability)
        
        # Get credit score from applicant data
        applicant_credit_score = applicant.get('credit_score', 650)
        
        # Use the new reasoning module for multi-factor analysis
        try:
            loan_reasoning = evaluate_loan_application(
                model_probability=probability,
                loan_amount=request.loan_amount,
                monthly_income=monthly_income,
                loan_term_months=request.loan_term_months,
                credit_score=applicant_credit_score
            )
            
            # Extract credit score info with proper classification
            credit_score_info = {
                "score": loan_reasoning.credit_score.score,
                "rating": loan_reasoning.credit_score.rating.value,
                "description": loan_reasoning.credit_score.description,
                "rating_scale": {
                    "Poor": "Below 580",
                    "Fair": "580-669",
                    "Good": "670-739",
                    "Very Good": "740-799",
                    "Exceptional": "800+"
                }
            }
            
            # Extract actionable suggestions from reasoning
            actionable_suggestions = [
                {
                    "action": s.action,
                    "reason": s.reason,
                    "expected_improvement": s.expected_improvement
                }
                for s in loan_reasoning.suggestions
            ]
            
            # Extract risk factors from reasoning
            detailed_risk_factors = [
                {
                    "factor": rf.name,
                    "severity": rf.severity,
                    "impact": rf.impact,
                    "description": rf.description
                }
                for rf in loan_reasoning.risk_factors
            ]
            
            # Get alternative offer if rejected
            alternative_offer = None
            if not eligible and loan_reasoning.alternative_amount:
                alternative_offer = {
                    "suggested_amount": loan_reasoning.alternative_amount,
                    "suggested_amount_formatted": format_currency(loan_reasoning.alternative_amount),
                    "suggested_term_months": loan_reasoning.alternative_term or request.loan_term_months,
                    "reason": "Based on your income and credit profile, this amount may be more appropriate."
                }
            
        except Exception as reasoning_error:
            logger.warning(f"Reasoning module error: {reasoning_error}")
            # Fallback to basic credit score classification
            credit_score_info = {
                "score": applicant_credit_score,
                "rating": get_credit_score_rating(applicant_credit_score).value,
                "description": f"Based on credit score of {applicant_credit_score}"
            }
            actionable_suggestions = []
            detailed_risk_factors = []
            alternative_offer = None
        
        # Generate HUMAN-FRIENDLY explanations
        human_summary = generate_human_summary(
            eligible=eligible,
            probability=probability,
            loan_amount=request.loan_amount,
            monthly_income=monthly_income,
            loan_to_income_ratio=loan_to_income_ratio,
            payment_to_income_ratio=payment_to_income_ratio,
            risk_factors=risk_factors,
            protective_factors=protective_factors
        )
        
        # Generate SMART recommendations based on eligibility
        smart_recommendations = generate_smart_recommendations(
            eligible=eligible,
            probability=probability,
            loan_amount=request.loan_amount,
            loan_term_months=request.loan_term_months,
            monthly_income=monthly_income,
            annual_income=annual_income,
            loan_to_income_ratio=loan_to_income_ratio,
            payment_to_income_ratio=payment_to_income_ratio,
            risk_factors=risk_factors
        )
        
        # Convert risk/protective factors to human-readable format
        human_risk_factors = humanize_risk_factors(risk_factors[:5], is_positive=False)
        human_protective_factors = humanize_risk_factors(protective_factors[:5], is_positive=True)
        
        # Calculate interest-adjusted payment (for transparency)
        monthly_interest_rate = DEFAULT_INTEREST_RATE / 100 / 12
        if monthly_interest_rate > 0:
            # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
            n = request.loan_term_months
            r = monthly_interest_rate
            emi_with_interest = request.loan_amount * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
        else:
            emi_with_interest = monthly_payment
        
        # Update applicant eligibility status in database
        eligibility_data = {
            "eligibility_status": "eligible" if eligible else "not_eligible",
            "updated_at": datetime.utcnow().isoformat()
        }
        db.update_applicant(request.applicant_id, eligibility_data)
        
        # Log action
        db.log_action(
            user_id=user.get("sub") or user.get("user_id") or "unknown",
            action="CHECK_ELIGIBILITY",
            resource_type="applicant",
            resource_id=request.applicant_id,
            details={"eligible": eligible, "risk_score": probability}
        )
        
        # Build human-friendly response
        return {
            "success": True,
            "data": {
                # Application Details
                "applicant_id": request.applicant_id,
                "applicant_name": applicant.get('name', applicant.get('full_name', 'Unknown')),
                
                # Loan Details
                "loan_details": {
                    "requested_amount": request.loan_amount,
                    "requested_amount_formatted": format_currency(request.loan_amount),
                    "loan_term_months": request.loan_term_months,
                    "loan_term_description": f"{request.loan_term_months} months ({request.loan_term_months/12:.1f} years)" if request.loan_term_months >= 12 else f"{request.loan_term_months} months",
                    "interest_rate": f"{DEFAULT_INTEREST_RATE}% per annum",
                    "monthly_payment_principal_only": round(monthly_payment, 2),
                    "monthly_payment_principal_only_formatted": format_currency(monthly_payment),
                    "monthly_payment_with_interest": round(emi_with_interest, 2),
                    "monthly_payment_with_interest_formatted": format_currency(emi_with_interest),
                    "interest_note": f"Monthly installment calculated using {DEFAULT_INTEREST_RATE}% annual interest rate."
                },
                
                # Applicant Financial Profile
                "financial_profile": {
                    "monthly_income": monthly_income,
                    "monthly_income_formatted": format_currency(monthly_income),
                    "annual_income": annual_income,
                    "annual_income_formatted": format_currency(annual_income),
                    "loan_to_income_ratio": round(loan_to_income_ratio, 2),
                    "loan_to_income_description": f"Loan is {loan_to_income_ratio:.1f}x the annual income",
                    "payment_to_income_ratio": round(payment_to_income_ratio * 100, 1),
                    "payment_to_income_description": f"Monthly payment is {payment_to_income_ratio*100:.1f}% of monthly income"
                },
                
                # Credit Score Classification (Mandatory - Per FYP Requirements)
                "credit_score": credit_score_info,
                
                # Decision
                "decision": {
                    "eligible": eligible,
                    "status": decision,
                    "risk_level": risk_level,
                    "risk_score_percentage": round(probability * 100, 1),
                    "risk_explanation": f"The system estimates a {probability*100:.1f}% probability that the applicant may face difficulty repaying this loan. {'This is within acceptable risk limits.' if eligible else 'This exceeds the acceptable risk threshold of ' + str(round(optimal_threshold*100, 1)) + '%.'}"
                },
                
                # Human-Friendly Explanation
                "explanation": {
                    "summary": human_summary,
                    "what_is_default": "Default means the customer may fail to repay the loan on time or in full, resulting in financial loss for the lender.",
                    "decision_basis": "This decision was produced using a hybrid AI system combining deep learning (TabNet) and probabilistic risk analysis (Bayesian Network) trained on historical loan data."
                },
                
                # Risk Analysis (Human-Readable)
                "risk_analysis": {
                    "concerns": human_risk_factors,
                    "positive_factors": human_protective_factors,
                    "detailed_factors": detailed_risk_factors  # From reasoning module
                },
                
                # Recommendations
                "recommendations": smart_recommendations,
                
                # Actionable Suggestions (Multi-factor reasoning)
                "actionable_suggestions": actionable_suggestions,
                
                # Alternative Offer (if rejected)
                "alternative_offer": alternative_offer,
                
                # Feature Importance (for SHAP-like charts)
                "feature_importance": [
                    {
                        "feature": f.get('feature_name', f.get('feature', 'Unknown')).replace('_', ' ').title(),
                        "importance": f.get('influence_strength', f.get('importance', 0)),
                        "direction": f.get('influence_direction', 'increases_risk' if not eligible else 'decreases_risk')
                    }
                    for f in (risk_factors[:5] + protective_factors[:5])
                ],
                
                # Model Transparency
                "model_info": {
                    "model_type": "Hybrid AI System (Machine Learning + Probabilistic Analysis)",
                    "confidence_score": round(confidence_score * 100, 1),
                    "confidence_description": f"The model has {confidence_score*100:.0f}% confidence in this assessment.",
                    "threshold_used": round(optimal_threshold * 100, 1),
                    "note": "This is an AI-assisted decision. Final approval should consider additional factors and human judgment."
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Eligibility check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eligibility check failed: {str(e)}"
        )


def prepare_applicant_features(applicant: Dict, loan_amount: float, loan_term_months: int) -> Dict[str, float]:
    """
    Convert applicant data to ALL model features (73+ features required)
    Creates comprehensive feature set matching the trained model's expectations
    """
    from datetime import datetime
    
    # Calculate age
    dob = applicant.get('date_of_birth', '')
    try:
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        age_years = (datetime.now() - birth_date).days / 365.25
    except:
        age_years = 35  # Default
    
    # Calculate ratios
    monthly_income = applicant.get('monthly_income', 50000)
    existing_debt = applicant.get('existing_debt_amount', 0)
    existing_loans = applicant.get('existing_loans_count', 0)
    
    # Credit-to-income ratio (higher = riskier)
    annual_income = monthly_income * 12
    
    # Monthly payment
    monthly_payment = loan_amount / loan_term_months
    
    # Employment years
    years_employed = applicant.get('years_employed', applicant.get('employment_length', 3))
    if years_employed is None:
        years_employed = 3
    
    # Credit score
    credit_score = applicant.get('credit_score', 650)
    
    # Create ALL 73+ features required by the model
    features = {
        # Primary identifier
        'SK_ID_CURR': applicant.get('id', 0),
        
        # Contract information
        'NAME_CONTRACT_TYPE': 0,  # 0=Cash loans, 1=Revolving loans
        
        # Property ownership flags
        'FLAG_OWN_CAR': 1 if applicant.get('assets_value', 0) > 50000 else 0,
        'FLAG_OWN_REALTY': 1 if applicant.get('assets_value', 0) > 100000 else 0,
        
        # Family information
        'CNT_CHILDREN': 0,  # Default: no children
        'NAME_TYPE_SUITE': 0,  # Who accompanied client
        
        # Income type (map employment status)
        'NAME_INCOME_TYPE': 0,  # Working, State servant, Commercial associate, Pensioner
        
        # Family status (map marital status)
        'NAME_FAMILY_STATUS': 0 if applicant.get('marital_status', 'Single') == 'Married' else 1,
        
        # Housing type
        'NAME_HOUSING_TYPE': 0,  # House/apartment, With parents, etc.
        
        # Registration and identification days
        'DAYS_REGISTRATION': -365 * 5,  # Days since address registration (negative)
        'DAYS_ID_PUBLISH': -365 * 3,  # Days since ID was issued (negative)
        
        # Car age (based on assets)
        'OWN_CAR_AGE': 5.0 if applicant.get('assets_value', 0) > 50000 else 0,
        
        # Contact information flags
        'FLAG_EMP_PHONE': 1,  # Has work phone
        'FLAG_WORK_PHONE': 1,
        'FLAG_PHONE': 1 if applicant.get('phone') else 0,
        'FLAG_EMAIL': 1 if applicant.get('email') else 0,
        
        # Occupation (map from occupation field)
        'OCCUPATION_TYPE': 0,  # Laborers, Core staff, Sales staff, etc.
        
        # Family members count
        'CNT_FAM_MEMBERS': 2.0,  # Default 2
        
        # Application process timing
        'WEEKDAY_APPR_PROCESS_START': 1,  # Monday=0, Sunday=6
        'HOUR_APPR_PROCESS_START': 12,  # Hour of day (0-23)
        
        # Regional matching flags
        'REG_REGION_NOT_LIVE_REGION': 0,
        'REG_REGION_NOT_WORK_REGION': 0,
        'LIVE_REGION_NOT_WORK_REGION': 0,
        'REG_CITY_NOT_LIVE_CITY': 0,
        'LIVE_CITY_NOT_WORK_CITY': 0,
        
        # Organization type
        'ORGANIZATION_TYPE': 0,  # Business Entity Type 3, School, etc.
        
        # Building information (apartment building features)
        'ELEVATORS_AVG': 1.0,
        'FLOORSMAX_AVG': 10.0,
        'FONDKAPREMONT_MODE': 0,  # Foundation repair mode
        'HOUSETYPE_MODE': 0,  # block of flats, terraced house
        'WALLSMATERIAL_MODE': 0,  # Panel, Block, etc.
        
        # Social circle (credit bureau checks)
        'OBS_30_CNT_SOCIAL_CIRCLE': 2.0,  # Observations in social circle
        'DEF_30_CNT_SOCIAL_CIRCLE': 0,  # Defaults in social circle (30 days)
        'DEF_60_CNT_SOCIAL_CIRCLE': 0,  # Defaults in social circle (60 days)
        
        # Document submission flags
        'FLAG_DOCUMENT_3': 1,
        'FLAG_DOCUMENT_5': 0,
        'FLAG_DOCUMENT_6': 1,
        'FLAG_DOCUMENT_8': 0,
        
        # Credit bureau inquiries
        'AMT_REQ_CREDIT_BUREAU_DAY': 0,  # Inquiries in last day
        'AMT_REQ_CREDIT_BUREAU_WEEK': 0,  # Inquiries in last week
        'AMT_REQ_CREDIT_BUREAU_MON': 1,  # Inquiries in last month
        'AMT_REQ_CREDIT_BUREAU_QRT': 2,  # Inquiries in last quarter
        'AMT_REQ_CREDIT_BUREAU_YEAR': existing_loans,  # Inquiries in last year
        
        # Bureau features (credit history from credit bureau)
        'bureau_CREDIT_DAY_OVERDUE_max': 0,  # Max days overdue
        'bureau_CREDIT_DAY_OVERDUE_mean': 0,  # Mean days overdue
        'bureau_AMT_CREDIT_MAX_OVERDUE_max': 0,  # Max overdue amount
        'bureau_AMT_CREDIT_SUM_sum': existing_debt,  # Total credit sum
        'bureau_AMT_CREDIT_SUM_mean': existing_debt / max(existing_loans, 1),
        'bureau_AMT_CREDIT_SUM_DEBT_sum': existing_debt,  # Total current debt
        'bureau_AMT_CREDIT_SUM_LIMIT_sum': annual_income * 3,  # Credit card limits
        'bureau_CNT_CREDIT_PROLONG_sum': 0,  # Times credit was prolonged
        'bureau_bb_months_count': 12 * existing_loans,  # Months balance reported
        'bureau_bb_status_good': 1 if credit_score > 650 else 0,  # Good credit status
        
        # Previous application features
        'prev_AMT_ANNUITY_min': monthly_payment * 0.5,
        'prev_AMT_ANNUITY_max': monthly_payment * 1.5,
        'prev_AMT_ANNUITY_mean': monthly_payment,
        'prev_AMT_APPLICATION_min': loan_amount * 0.5,
        'prev_AMT_APPLICATION_max': loan_amount * 1.5,
        'prev_AMT_APPLICATION_mean': loan_amount,
        'prev_DAYS_DECISION_max': -30,  # Days since last decision
        'prev_NAME_CONTRACT_STATUS_<lambda>': 1,  # Previous contract approved
        'prev_NAME_TYPE_SUITE_count': 1,
        
        # Installment payments features
        'inst_NUM_INSTALMENT_NUMBER_count': loan_term_months,
        'inst_NUM_INSTALMENT_NUMBER_max': loan_term_months,
        'inst_NUM_INSTALMENT_VERSION_nunique': 1,
        'inst_DAYS_INSTALMENT_max': -30,
        'inst_DAYS_ENTRY_PAYMENT_mean': -30,
        'inst_AMT_INSTALMENT_min': monthly_payment * 0.9,
        'inst_AMT_INSTALMENT_max': monthly_payment * 1.1,
        'inst_AMT_INSTALMENT_mean': monthly_payment,
        
        # Credit card balance features
        'cc_drawings_current_mean': monthly_income * 0.1,  # Credit card drawings
        'cc_instalment_mature_mean': monthly_payment * 0.5,
        
        # Calculated features
        'CREDIT_TERM': loan_term_months,  # Loan term in months
        'DAYS_EMPLOYED_PERC': (years_employed * 365) / (age_years * 365) if age_years > 0 else 0.1,
    }
    
    return features


@router.get("/recent")
async def get_recent_predictions(
    limit: int = 10,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get recent predictions
    
    **Access**: Loan Officers and Managers
    """
    try:
        predictions = db.get_recent_predictions(limit=limit)
        return {
            "success": True,
            "data": predictions
        }
    except Exception as e:
        logger.error(f"Error fetching recent predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/explain/feature/{feature_name}")
async def explain_feature(
    feature_name: str,
    value: float,
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get explanation for how a specific feature influences predictions
    
    **Access**: Loan Officers and Managers
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bayesian Reasoner not loaded"
        )
    
    try:
        explanation = bayesian_reasoner.explain_feature(feature_name, value)
        return {
            "success": True,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Feature explanation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/explain/network")
async def get_bayesian_network_structure(
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get the Bayesian Network structure for visualization
    
    **Access**: Loan Officers and Managers
    
    Returns network nodes, edges, and descriptions for visualization
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bayesian Reasoner not loaded"
        )
    
    try:
        structure = bayesian_reasoner.get_network_structure()
        return {
            "success": True,
            "network": structure
        }
    except Exception as e:
        logger.error(f"Network structure error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/compare")
async def compare_scenarios(
    scenario_a: Dict[str, float],
    scenario_b: Dict[str, float],
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Compare two loan scenarios and explain the difference in predictions
    
    **Access**: Loan Officers and Managers
    
    Useful for understanding what changes would improve/worsen the outcome
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bayesian Reasoner not loaded"
        )
    
    try:
        from src.models.bayesian_reasoner import reasoning_to_dict
        
        reasoning_a = bayesian_reasoner.get_reasoning(scenario_a, optimal_threshold)
        reasoning_b = bayesian_reasoner.get_reasoning(scenario_b, optimal_threshold)
        
        # Calculate differences
        prob_diff = reasoning_b.probability - reasoning_a.probability
        
        # Find changed features
        changed_features = []
        for key in set(scenario_a.keys()) | set(scenario_b.keys()):
            val_a = scenario_a.get(key, 0)
            val_b = scenario_b.get(key, 0)
            if val_a != val_b:
                changed_features.append({
                    "feature": key,
                    "original_value": val_a,
                    "new_value": val_b,
                    "change": val_b - val_a
                })
        
        # Generate comparison explanation
        if prob_diff > 0.05:
            comparison_summary = f"Scenario B has {abs(prob_diff):.1%} HIGHER default risk than Scenario A."
        elif prob_diff < -0.05:
            comparison_summary = f"Scenario B has {abs(prob_diff):.1%} LOWER default risk than Scenario A."
        else:
            comparison_summary = "Both scenarios have similar default risk levels."
        
        return {
            "success": True,
            "scenario_a": reasoning_to_dict(reasoning_a),
            "scenario_b": reasoning_to_dict(reasoning_b),
            "comparison": {
                "probability_difference": round(prob_diff, 4),
                "changed_features": changed_features,
                "summary": comparison_summary,
                "decision_changed": reasoning_a.decision != reasoning_b.decision
            }
        }
        
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/model/info")
async def get_model_info(
    user=Depends(AuthMiddleware.require_role(["manager", "loan_officer"]))
):
    """
    Get information about the loaded ML models
    
    **Access**: Loan Officers and Managers
    """
    return {
        "success": True,
        "data": {
            "tabnet_loaded": tabnet_model is not None,
            "bayesian_reasoner_loaded": bayesian_reasoner is not None,
            "total_features": len(feature_names) if feature_names else 0,
            "optimal_threshold": optimal_threshold,
            "model_type": "Hybrid TabNet + Bayesian Network",
            "capabilities": {
                "basic_prediction": tabnet_model is not None,
                "bayesian_reasoning": bayesian_reasoner is not None,
                "feature_explanation": bayesian_reasoner is not None,
                "network_visualization": bayesian_reasoner is not None,
                "scenario_comparison": bayesian_reasoner is not None
            }
        }
    }
