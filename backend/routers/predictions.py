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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

# ============================================
# GLOBAL STATE
# ============================================

# Model instances (loaded at startup)
tabnet_model = None
bayesian_reasoner = None
feature_names = None
optimal_threshold = 0.5


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
    global tabnet_model, bayesian_reasoner, feature_names, optimal_threshold
    
    try:
        from src.config import Config
        import pandas as pd
        import json
        
        # Load TabNet model
        try:
            from pytorch_tabnet.tab_model import TabNetClassifier
            tabnet_model = TabNetClassifier()
            
            optimized_path = Config.TABNET_OPTIMIZED
            regular_path = Config.TABNET_MODEL
            
            if optimized_path.exists():
                tabnet_model.load_model(str(optimized_path))
                logger.info("✅ Loaded optimized TabNet model")
            elif regular_path.exists():
                tabnet_model.load_model(str(regular_path))
                logger.info("✅ Loaded regular TabNet model")
            else:
                logger.warning("⚠️ TabNet model not found")
                tabnet_model = None
        except Exception as e:
            logger.warning(f"⚠️ Could not load TabNet: {e}")
            tabnet_model = None
        
        # Load feature names
        try:
            test_df = pd.read_parquet(Config.DATA_PROCESSED / 'test_split.parquet')
            feature_names = test_df.drop('TARGET', axis=1).columns.tolist()
            logger.info(f"✅ Loaded {len(feature_names)} feature names")
        except Exception as e:
            logger.warning(f"⚠️ Could not load feature names: {e}")
            feature_names = []
        
        # Load optimal threshold
        try:
            threshold_path = Config.TABNET_DIR / 'optimal_threshold.json'
            if threshold_path.exists():
                with open(threshold_path, 'r') as f:
                    threshold_data = json.load(f)
                    optimal_threshold = threshold_data.get('optimal_threshold', 0.5)
                logger.info(f"✅ Loaded optimal threshold: {optimal_threshold:.3f}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load threshold: {e}")
        
        # Load Bayesian Reasoner
        try:
            from src.models.bayesian_reasoner import BayesianReasoner
            bayesian_model_path = Config.OVERALL_PROJECT_ROOT / 'ml-model' / 'models' / 'bayesian'
            if bayesian_model_path.exists():
                bayesian_reasoner = BayesianReasoner(str(bayesian_model_path))
                logger.info("✅ Loaded Bayesian Reasoner for explainability")
            else:
                logger.warning(f"⚠️ Bayesian model not found at {bayesian_model_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Bayesian Reasoner: {e}")
        
        logger.info("🎉 Predictions router models loaded!")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")


# Load models when module is imported
load_models()


# ============================================
# HELPER FUNCTIONS
# ============================================

# Feature name to human-readable mapping
FEATURE_TRANSLATIONS = {
    'EXT_SOURCE_1': 'Credit Bureau Score',
    'EXT_SOURCE_2': 'Bank Repayment History',
    'EXT_SOURCE_3': 'Financial Reliability Score',
    'EXT_SOURCE_MEAN': 'Overall Credit Standing',
    'EXT_SOURCE_STD': 'Credit Score Consistency',
    'DAYS_LAST_PHONE_CHANGE': 'Contact Information Stability',
    'inst_AMT_PAYMENT_min': 'Minimum Monthly Installment',
    'DAYS_EMPLOYED': 'Employment Duration',
    'DAYS_BIRTH': 'Age',
    'AGE_YEARS': 'Age',
    'CREDIT_INCOME_RATIO': 'Loan-to-Income Ratio',
    'ANNUITY_INCOME_RATIO': 'Monthly Payment Burden',
    'AMT_CREDIT': 'Loan Amount',
    'AMT_INCOME_TOTAL': 'Annual Income',
    'AMT_ANNUITY': 'Monthly Payment',
    'CODE_GENDER': 'Gender',
    'NAME_EDUCATION_TYPE': 'Education Level',
    'REGION_RATING_CLIENT': 'Regional Economic Rating',
    'REG_CITY_NOT_WORK_CITY': 'Work-Residence Distance',
    'bureau_DAYS_CREDIT_max': 'Oldest Credit Account Age',
    'bureau_DAYS_CREDIT_min': 'Newest Credit Account Age',
    'bureau_DAYS_CREDIT_mean': 'Average Credit History Length',
    'bureau_AMT_CREDIT_SUM_DEBT_mean': 'Existing Debt Amount',
    'inst_DAYS_INSTALMENT_min': 'Payment Timeliness',
    'prev_DAYS_DECISION_min': 'Recent Loan Applications',
    'prev_DAYS_DECISION_mean': 'Average Loan Application History',
}

# Human-readable explanations for risk factors
RISK_EXPLANATIONS = {
    'EXT_SOURCE_1': {
        'low': 'The credit bureau score indicates a history of missed or late payments, suggesting the applicant may have difficulty repaying loans.',
        'medium': 'The credit bureau score is moderate, showing some past credit issues but not severe concerns.',
        'high': 'The credit bureau score is excellent, indicating a strong history of timely repayments.'
    },
    'EXT_SOURCE_2': {
        'low': 'Bank records show inconsistent repayment behavior, which increases the likelihood of loan default.',
        'medium': 'Bank repayment history is acceptable but shows occasional delays in payments.',
        'high': 'Bank repayment history is excellent, demonstrating reliable financial behavior.'
    },
    'EXT_SOURCE_3': {
        'low': 'The overall financial reliability assessment indicates significant risk in loan repayment.',
        'medium': 'Financial reliability is moderate, with some areas of concern.',
        'high': 'Financial reliability is strong, indicating a trustworthy borrower.'
    },
    'EXT_SOURCE_MEAN': {
        'low': 'The combined credit assessment shows poor overall creditworthiness.',
        'medium': 'The combined credit assessment is moderate, requiring careful consideration.',
        'high': 'The combined credit assessment is excellent, supporting loan approval.'
    },
    'DAYS_LAST_PHONE_CHANGE': {
        'low': 'Recent changes to contact information suggest instability, which is a minor risk indicator.',
        'medium': 'Contact information has been moderately stable.',
        'high': 'Contact information has been very stable, indicating a settled lifestyle.'
    },
    'inst_AMT_PAYMENT_min': {
        'low': 'The required monthly payment is manageable relative to income.',
        'medium': 'The monthly payment represents a moderate portion of income.',
        'high': 'The monthly payment is high relative to income, which may strain the applicant\'s finances.'
    },
    'CREDIT_INCOME_RATIO': {
        'low': 'The loan amount is reasonable compared to the applicant\'s income.',
        'medium': 'The loan amount is moderate relative to income.',
        'high': 'The loan amount is very high compared to the applicant\'s income, creating significant repayment risk.'
    },
    'ANNUITY_INCOME_RATIO': {
        'low': 'Monthly payments are affordable based on the applicant\'s income.',
        'medium': 'Monthly payments represent a moderate burden on the applicant\'s income.',
        'high': 'Monthly payments would consume a large portion of income, making repayment difficult.'
    }
}

# Default interest rate for calculations (annual)
DEFAULT_INTEREST_RATE = 12.0  # 12% per annum


def get_risk_level(probability: float) -> str:
    """Get risk level string from probability"""
    if probability < 0.2:
        return "Very Low Risk"
    elif probability < 0.35:
        return "Low Risk"
    elif probability < 0.5:
        return "Medium Risk"
    elif probability < 0.7:
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
    """
    human_name = translate_feature_name(feature_name)
    
    # For CONCERNS (increases_risk) - explain why this factor is worrying
    if influence_direction == 'increases_risk':
        concern_explanations = {
            'EXT_SOURCE_1': "The credit bureau score is lower than expected, indicating past credit issues.",
            'EXT_SOURCE_2': "External credit assessment shows concerning patterns in credit behavior.",
            'EXT_SOURCE_3': "Third-party risk assessment indicates elevated risk for this applicant.",
            'DAYS_LAST_PHONE_CHANGE': "Recent changes to phone number may indicate instability or possible fraud concerns.",
            'sk_bureau_DAYS_CREDIT_min': "The credit account history is shorter than preferred, limiting risk assessment ability.",
            'sk_bureau_DAYS_CREDIT_max': "The longest credit relationship is recent, showing limited track record.",
            'inst_AMT_PAYMENT_min': "The payment history shows lower than expected payment amounts in the past.",
            'bb_MONTHS_BALANCE_min': "Recent bank balance history shows concerning patterns.",
            'prev_SK_ID_PREV_count': "The number of previous applications raises questions about credit seeking behavior.",
            'prev_AMT_CREDIT_min': "Previous credit amounts suggest a pattern that increases default risk.",
            'CREDIT_INCOME_RATIO': "The ratio of credit to income is high, creating potential repayment strain.",
            'ANNUITY_INCOME_RATIO': "Monthly payment obligations are high relative to income.",
            'DAYS_EMPLOYED': "Employment duration is shorter than preferred for this loan amount.",
            'DAYS_BIRTH': "Age profile suggests higher risk based on historical patterns.",
            'FLAG_OWN_CAR': "Lack of vehicle ownership may indicate limited asset base.",
            'FLAG_OWN_REALTY': "Lack of property ownership may indicate limited financial stability."
        }
        return concern_explanations.get(
            feature_name, 
            f"The {human_name.lower()} indicates elevated risk for this application."
        )
    
    # For POSITIVE FACTORS (decreases_risk) - explain why this factor is good
    else:
        positive_explanations = {
            'EXT_SOURCE_1': "The credit bureau score is excellent, indicating a strong history of timely repayments.",
            'EXT_SOURCE_2': "External credit assessment shows reliable credit behavior.",
            'EXT_SOURCE_3': "Third-party risk assessment indicates low risk for this applicant.",
            'DAYS_LAST_PHONE_CHANGE': "Stable contact information over time indicates reliability.",
            'sk_bureau_DAYS_CREDIT_min': "Established credit history demonstrates experience with credit management.",
            'sk_bureau_DAYS_CREDIT_max': "Long-standing credit relationships show financial stability.",
            'inst_AMT_PAYMENT_min': "Payment history shows consistent and reliable payment behavior.",
            'bb_MONTHS_BALANCE_min': "Bank balance history shows healthy financial patterns.",
            'prev_SK_ID_PREV_count': "Previous credit applications were managed responsibly.",
            'prev_AMT_CREDIT_min': "Previous credit history indicates responsible borrowing.",
            'CREDIT_INCOME_RATIO': "The loan amount is reasonable compared to income.",
            'ANNUITY_INCOME_RATIO': "Monthly payments are well within affordable limits.",
            'DAYS_EMPLOYED': "Stable employment history supports repayment capacity.",
            'DAYS_BIRTH': "Age profile suggests financial maturity and stability.",
            'FLAG_OWN_CAR': "Vehicle ownership indicates financial responsibility.",
            'FLAG_OWN_REALTY': "Property ownership indicates strong financial foundation."
        }
        return positive_explanations.get(
            feature_name, 
            f"The {human_name.lower()} is favorable for this application."
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
    """Generate a human-friendly summary explanation"""
    
    risk_percent = probability * 100
    
    # Base explanation about what default means
    default_explanation = "Default means the customer may fail to repay the loan on time or in full."
    
    if eligible:
        # APPROVED case
        summary = f"**APPROVED**: Based on the comprehensive financial analysis, this loan application has been approved. "
        summary += f"The system estimates a {risk_percent:.1f}% probability of repayment difficulty, which is within acceptable limits. "
        
        # Explain why approved
        if loan_to_income_ratio < 2:
            summary += f"The requested loan amount ({format_currency(loan_amount)}) is reasonable at {loan_to_income_ratio:.1f}x the applicant's annual income. "
        
        if payment_to_income_ratio < 0.3:
            summary += f"Monthly payments would only consume {payment_to_income_ratio*100:.1f}% of monthly income, which is affordable. "
        
        # Add protective factors
        if protective_factors:
            summary += "Positive factors include: "
            positives = []
            for pf in protective_factors[:2]:
                human_name = translate_feature_name(pf.get('feature_name', ''))
                positives.append(human_name.lower())
            summary += ", ".join(positives) + ". "
        
    else:
        # REJECTED case
        summary = f"**REJECTED**: Based on the comprehensive financial analysis, this loan application cannot be approved at this time. "
        summary += f"The system estimates a {risk_percent:.1f}% probability of repayment difficulty. {default_explanation} "
        
        # Explain the main concerns
        concerns = []
        
        if loan_to_income_ratio > 5:
            concerns.append(f"the requested loan amount ({format_currency(loan_amount)}) is {loan_to_income_ratio:.1f}x the applicant's annual income, which is extremely high")
        elif loan_to_income_ratio > 2:
            concerns.append(f"the loan amount relative to income ({loan_to_income_ratio:.1f}x annual income) is elevated")
        
        if payment_to_income_ratio > 0.5:
            concerns.append(f"monthly payments would consume {payment_to_income_ratio*100:.1f}% of monthly income, making repayment unsustainable")
        elif payment_to_income_ratio > 0.4:
            concerns.append(f"monthly payments ({payment_to_income_ratio*100:.1f}% of income) are high")
        
        # Add risk factors from model
        for rf in risk_factors[:2]:
            human_name = translate_feature_name(rf.get('feature_name', ''))
            if 'credit' in human_name.lower() or 'score' in human_name.lower():
                concerns.append(f"the {human_name.lower()} indicates past repayment issues")
        
        if concerns:
            summary += "The main concerns are: " + "; ".join(concerns) + ". "
    
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
    """Generate dynamic, data-driven recommendations based on eligibility"""
    
    recommendations = []
    
    if eligible:
        # APPROVED - no fixes needed
        recommendations.append("The applicant meets all financial and credit requirements for this loan.")
        recommendations.append("No corrective actions are required.")
        recommendations.append("The loan can proceed to documentation and disbursement stages.")
        
        if loan_to_income_ratio < 1 and payment_to_income_ratio < 0.2:
            recommendations.append("Given the strong financial position, consider offering the applicant a higher credit limit for future needs.")
    else:
        # REJECTED - provide specific improvement advice
        
        # Calculate suggested improvements
        max_affordable_payment = monthly_income * 0.4  # 40% of income
        max_affordable_loan_current = max_affordable_payment * loan_term_months
        max_affordable_loan_long = max_affordable_payment * 60  # 5 years
        max_affordable_loan_very_long = max_affordable_payment * 120  # 10 years
        safe_loan_amount = annual_income * 3  # 3x annual income
        
        # Check if loan amount is too high relative to income
        if loan_to_income_ratio > 3:
            recommendations.append(
                f"Reduce the requested loan amount. Based on the applicant's income, a loan up to {format_currency(safe_loan_amount)} would be more appropriate."
            )
        
        # Check if monthly payment is too high
        if payment_to_income_ratio > 0.4:
            # Only suggest extending term if not already at max
            if loan_term_months < 60:
                recommendations.append(
                    f"Extend the repayment period to 60 months (5 years). This would make payments more affordable at {format_currency(max_affordable_payment)} per month."
                )
            elif loan_term_months < 120:
                # Already at 60 months, suggest even longer term
                recommendations.append(
                    f"Consider extending to a 120-month (10-year) term to reduce monthly payments. Current {loan_term_months}-month term creates high payments."
                )
            else:
                # Already at max term, must reduce amount
                recommendations.append(
                    f"The loan amount is too high even with the maximum term. Consider reducing to {format_currency(max_affordable_loan_very_long)} or less."
                )
            
            # Add specific advice about current term creating unaffordable payments
            if loan_term_months <= 24:
                recommendations.append(
                    f"Current {loan_term_months}-month term creates unaffordable payments. Consider extending to at least 36 months."
                )
            elif loan_term_months <= 48 and loan_term_months < 60:
                recommendations.append(
                    f"Current {loan_term_months}-month term results in high payments. A 60-month term would be more manageable."
                )
        
        # Check for credit-related risk factors
        for rf in risk_factors:
            feature = rf.get('feature_name', '')
            if 'EXT_SOURCE' in feature or 'CREDIT' in feature.upper():
                recommendations.append(
                    "Improve credit standing by paying off existing debts and maintaining timely payments for 6-12 months before reapplying."
                )
                break
        
        if loan_amount > annual_income * 5:
            recommendations.append(
                "Consider adding a co-borrower or guarantor with additional income to support this loan amount."
            )
        
        recommendations.append(
            "The applicant may reapply after addressing these concerns or with a modified loan request."
        )
    
    return recommendations[:5]


def humanize_risk_factors(factors: List[Dict], is_positive: bool = False) -> List[Dict]:
    """Convert technical risk factors to human-readable format
    
    Args:
        factors: List of factor dictionaries from the model
        is_positive: If True, these are positive/protective factors (reduces risk)
                     If False, these are concern factors (increases risk)
    """
    humanized = []
    
    for factor in factors:
        technical_name = factor.get('feature_name', '')
        discretized = factor.get('discretized_value', 1)
        
        # Determine direction based on context (is_positive flag)
        # This ensures consistency regardless of what the raw data says
        direction = 'decreases_risk' if is_positive else 'increases_risk'
        
        humanized.append({
            'factor': translate_feature_name(technical_name),
            'impact': 'Reduces Risk' if is_positive else 'Increases Risk',
            'severity': 'High' if discretized == 2 else ('Moderate' if discretized == 1 else 'Low'),
            'explanation': get_risk_explanation(technical_name, discretized, direction)
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
    if tabnet_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TabNet model not loaded"
        )
    
    try:
        # Prepare features
        X = prepare_features_array(request.features)
        
        # Get prediction from TabNet
        probability = float(tabnet_model.predict_proba(X)[0, 1])
        prediction = 1 if probability > optimal_threshold else 0
        
        return PredictionResponse(
            prediction=prediction,
            probability=round(probability, 4),
            risk_level=get_risk_level(probability),
            decision="REJECT" if prediction == 1 else "APPROVE",
            threshold_used=round(optimal_threshold, 3)
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
    Create prediction with full Bayesian Network reasoning
    
    **Access**: Loan Officers and Managers
    
    The hybrid model combines:
    - **TabNet**: Deep learning for accurate probability estimation
    - **Bayesian Network**: Probabilistic reasoning for explainability
    
    Returns:
    - Prediction and probability
    - Risk factors with explanations (e.g., "External credit score is low, which increases default risk")
    - Protective factors
    - Inference paths showing how features influence the decision
    - Natural language summary explanation
    - Confidence score
    """
    try:
        # Get TabNet probability if available
        tabnet_probability = None
        if tabnet_model is not None:
            X = prepare_features_array(request.features)
            tabnet_probability = float(tabnet_model.predict_proba(X)[0, 1])
        
        # Get Bayesian reasoning
        if bayesian_reasoner is not None:
            from src.models.bayesian_reasoner import reasoning_to_dict
            reasoning = bayesian_reasoner.get_reasoning(
                features=request.features,
                threshold=optimal_threshold
            )
            reasoning_dict = reasoning_to_dict(reasoning)
            
            # Combine with TabNet for hybrid model
            if tabnet_probability is not None:
                hybrid_probability = (tabnet_probability + reasoning_dict['probability']) / 2
                reasoning_dict['tabnet_probability'] = round(tabnet_probability, 4)
                reasoning_dict['bayesian_probability'] = reasoning_dict['probability']
                reasoning_dict['probability'] = round(hybrid_probability, 4)
                reasoning_dict['prediction'] = 1 if hybrid_probability > optimal_threshold else 0
                reasoning_dict['decision'] = "REJECT" if reasoning_dict['prediction'] == 1 else "APPROVE"
                reasoning_dict['risk_level'] = get_risk_level(hybrid_probability)
            
            reasoning_dict['model_type'] = "Hybrid TabNet + Bayesian Network"
            
            return {
                "success": True,
                "reasoning": reasoning_dict
            }
        
        elif tabnet_model is not None:
            # Fallback: TabNet only with basic explanation
            prediction = 1 if tabnet_probability > optimal_threshold else 0
            
            return {
                "success": True,
                "reasoning": {
                    "prediction": prediction,
                    "probability": round(tabnet_probability, 4),
                    "risk_level": get_risk_level(tabnet_probability),
                    "decision": "REJECT" if prediction == 1 else "APPROVE",
                    "summary_explanation": f"The applicant has a {tabnet_probability:.1%} probability of default. " +
                                         ("High risk - recommend rejection." if prediction == 1 else "Low risk - recommend approval."),
                    "top_risk_factors": [],
                    "top_protective_factors": [],
                    "inference_paths": [],
                    "detailed_explanation": "Full Bayesian reasoning not available. Using TabNet prediction only.",
                    "confidence_score": 0.7,
                    "evidence_strength": "Moderate",
                    "model_type": "TabNet Only"
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No ML models available"
            )
            
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
    3. Runs prediction through TabNet + Bayesian Network
    4. Returns eligibility decision with full reasoning
    """
    try:
        # Get applicant from database
        applicant = db.get_applicant_by_id(request.applicant_id)
        if not applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applicant not found"
            )
        
        # Get applicant income for response
        monthly_income = applicant.get('monthly_income', 50000)
        annual_income = monthly_income * 12
        loan_to_income_ratio = request.loan_amount / annual_income if annual_income > 0 else 999
        monthly_payment = request.loan_amount / request.loan_term_months
        payment_to_income_ratio = monthly_payment / monthly_income if monthly_income > 0 else 999
        
        # Prepare features from applicant data - model will decide based on these
        features = prepare_applicant_features(applicant, request.loan_amount, request.loan_term_months)
        
        # Get prediction with reasoning
        tabnet_probability = None
        if tabnet_model is not None:
            X = prepare_features_array(features)
            tabnet_probability = float(tabnet_model.predict_proba(X)[0, 1])
        
        # Get Bayesian reasoning
        risk_factors = []
        protective_factors = []
        summary_explanation = ""
        confidence_score = 0.5
        
        if bayesian_reasoner is not None:
            from src.models.bayesian_reasoner import reasoning_to_dict
            reasoning = bayesian_reasoner.get_reasoning(features, optimal_threshold)
            reasoning_dict = reasoning_to_dict(reasoning)
            
            risk_factors = reasoning_dict.get('top_risk_factors', [])
            protective_factors = reasoning_dict.get('top_protective_factors', [])
            summary_explanation = reasoning_dict.get('summary_explanation', '')
            confidence_score = reasoning_dict.get('confidence_score', 0.5)
            
            bayesian_probability = reasoning_dict.get('probability', 0.5)
            
            if tabnet_probability is not None:
                probability = (tabnet_probability + bayesian_probability) / 2
            else:
                probability = bayesian_probability
        elif tabnet_probability is not None:
            probability = tabnet_probability
            summary_explanation = f"Based on the ML model analysis, the applicant has a {probability:.1%} probability of default."
        else:
            # Fallback heuristic
            probability = 0.5
            summary_explanation = "ML models not available. Using default assessment."
        
        # Determine eligibility
        prediction = 1 if probability > optimal_threshold else 0
        eligible = prediction == 0
        decision = "APPROVE" if eligible else "REJECT"
        risk_level = get_risk_level(probability)
        
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
            "risk_score": round(probability, 4),
            "updated_at": datetime.utcnow().isoformat()
        }
        db.update_applicant(request.applicant_id, eligibility_data)
        
        # Log action
        db.log_action(
            user_id=user["user_id"],
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
                    "positive_factors": human_protective_factors
                },
                
                # Recommendations
                "recommendations": smart_recommendations,
                
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
    """Convert applicant data to model features with realistic risk mapping"""
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
    
    # Credit-to-income ratio (higher = riskier)
    annual_income = monthly_income * 12
    credit_income_ratio = loan_amount / annual_income if annual_income > 0 else 10
    
    # Monthly payment ratio (higher = riskier)
    monthly_payment = loan_amount / loan_term_months
    annuity_income_ratio = monthly_payment / monthly_income if monthly_income > 0 else 0.5
    
    # Debt-to-income ratio consideration
    total_debt = existing_debt + loan_amount
    debt_ratio = total_debt / annual_income if annual_income > 0 else 10
    
    # Employment years
    years_employed = applicant.get('years_employed', applicant.get('employment_length', 3))
    if years_employed is None:
        years_employed = 3
    
    # External sources (use credit score as proxy with more realistic mapping)
    credit_score = applicant.get('credit_score', 650)
    
    # More aggressive mapping: 300-500 = very risky, 500-650 = risky, 650-750 = moderate, 750+ = good
    if credit_score < 500:
        ext_source = 0.1 + (credit_score - 300) / 200 * 0.2  # 0.1 to 0.3
    elif credit_score < 650:
        ext_source = 0.3 + (credit_score - 500) / 150 * 0.2  # 0.3 to 0.5
    elif credit_score < 750:
        ext_source = 0.5 + (credit_score - 650) / 100 * 0.3  # 0.5 to 0.8
    else:
        ext_source = 0.8 + (credit_score - 750) / 100 * 0.2  # 0.8 to 1.0
    
    # Add some variance between external sources
    ext_source_1 = min(1.0, ext_source * (0.85 + 0.15 * (credit_score % 10) / 10))
    ext_source_2 = min(1.0, ext_source * (0.90 + 0.10 * ((credit_score + 3) % 10) / 10))
    ext_source_3 = min(1.0, ext_source * (0.88 + 0.12 * ((credit_score + 7) % 10) / 10))
    
    # CRITICAL: Penalize based on loan-to-income ratio
    # The higher the ratio, the lower the external scores should be
    # This directly affects the model's prediction
    if credit_income_ratio > 100:  # Absurdly high (100x+ annual income)
        penalty = 0.01  # Almost zero - very high risk
    elif credit_income_ratio > 50:  # Very high (50-100x annual income)
        penalty = 0.05
    elif credit_income_ratio > 20:  # High (20-50x annual income)
        penalty = 0.1
    elif credit_income_ratio > 10:  # Elevated (10-20x annual income)
        penalty = 0.2
    elif credit_income_ratio > 5:   # Moderate-high (5-10x annual income)
        penalty = 0.4
    elif credit_income_ratio > 3:   # Moderate (3-5x annual income)
        penalty = 0.6
    elif credit_income_ratio > 2:   # Acceptable (2-3x annual income)
        penalty = 0.8
    else:  # Good (<2x annual income)
        penalty = 1.0
    
    ext_source_1 *= penalty
    ext_source_2 *= penalty
    ext_source_3 *= penalty
    
    # CRITICAL: Penalize based on monthly payment burden
    if annuity_income_ratio > 5:    # Payment is 5x+ monthly income - impossible
        payment_penalty = 0.01
    elif annuity_income_ratio > 2:  # Payment is 2-5x monthly income
        payment_penalty = 0.05
    elif annuity_income_ratio > 1:  # Payment exceeds monthly income
        payment_penalty = 0.1
    elif annuity_income_ratio > 0.7:  # Payment is 70%+ of income
        payment_penalty = 0.3
    elif annuity_income_ratio > 0.5:  # Payment is 50-70% of income
        payment_penalty = 0.5
    elif annuity_income_ratio > 0.4:  # Payment is 40-50% of income
        payment_penalty = 0.7
    else:  # Payment is <40% of income - manageable
        payment_penalty = 1.0
    
    ext_source_1 *= payment_penalty
    ext_source_2 *= payment_penalty
    ext_source_3 *= payment_penalty
    
    # Ensure minimum values
    ext_source_1 = max(0.01, ext_source_1)
    ext_source_2 = max(0.01, ext_source_2)
    ext_source_3 = max(0.01, ext_source_3)
    
    features = {
        'EXT_SOURCE_1': ext_source_1,
        'EXT_SOURCE_2': ext_source_2,
        'EXT_SOURCE_3': ext_source_3,
        'EXT_SOURCE_MEAN': (ext_source_1 + ext_source_2 + ext_source_3) / 3,
        'EXT_SOURCE_STD': abs(ext_source_1 - ext_source_3) / 2,
        'AGE_YEARS': age_years,
        'DAYS_BIRTH': -age_years * 365.25,
        'DAYS_EMPLOYED': -years_employed * 365,
        'CODE_GENDER': 1 if applicant.get('gender', 'M') == 'F' else 0,
        'NAME_EDUCATION_TYPE': 0,  # Simplified
        'REGION_RATING_CLIENT': 2,  # Default
        'REG_CITY_NOT_WORK_CITY': 0,
        'CREDIT_INCOME_RATIO': credit_income_ratio,
        'ANNUITY_INCOME_RATIO': annuity_income_ratio,
        'AMT_CREDIT': loan_amount,
        'AMT_INCOME_TOTAL': annual_income,
        'AMT_ANNUITY': monthly_payment,
        'bureau_DAYS_CREDIT_max': -365,
        'bureau_DAYS_CREDIT_min': -730,
        'bureau_DAYS_CREDIT_mean': -500,
        'bureau_AMT_CREDIT_SUM_DEBT_mean': existing_debt,
        'inst_AMT_PAYMENT_min': monthly_payment * 0.9,
        'inst_DAYS_INSTALMENT_min': -30,
        'prev_DAYS_DECISION_min': -180,
        'prev_DAYS_DECISION_mean': -365,
        'DAYS_LAST_PHONE_CHANGE': -180,
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
