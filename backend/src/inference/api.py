"""
Simple FastAPI for Credit Default Prediction
Ready for Postman testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Home Credit Default Risk API",
    description="TabNet model for credit default prediction with imbalance optimization",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import routers
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from routers.loan_details import router as loan_details_router

# Include routers
app.include_router(loan_details_router)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
model = None
feature_names = None
optimal_threshold = 0.5
bayesian_reasoner = None


class FeatureInfluenceResponse(BaseModel):
    """Feature influence in the prediction"""
    feature_name: str
    feature_value: float
    discretized_value: int
    influence_direction: str
    influence_strength: float
    conditional_probability: float
    explanation: str


class InferencePathResponse(BaseModel):
    """Inference path in the Bayesian Network"""
    parent_nodes: List[str]
    child_nodes: List[str]
    path_strength: float
    description: str


class ReasoningResponse(BaseModel):
    """Complete reasoning response from Bayesian Network"""
    prediction: int
    probability: float
    risk_level: str
    decision: str
    
    # Reasoning components
    top_risk_factors: List[FeatureInfluenceResponse]
    top_protective_factors: List[FeatureInfluenceResponse]
    inference_paths: List[InferencePathResponse]
    
    # Natural language explanation
    summary_explanation: str
    detailed_explanation: str
    
    # Conditional probabilities
    conditional_probabilities: Dict[str, float]
    
    # Confidence metrics
    confidence_score: float
    evidence_strength: str


class PredictionRequest(BaseModel):
    """Input features for prediction"""
    features: Dict[str, float]
    
    class Config:
        schema_extra = {
            "example": {
                "features": {
                    "EXT_SOURCE_2": 0.6,
                    "EXT_SOURCE_3": 0.4,
                    "AGE_YEARS": 35,
                    "CREDIT_INCOME_RATIO": 2.1,
                    "DAYS_EMPLOYED": -2000
                }
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    probability: float
    prediction: int
    risk_level: str
    threshold_used: float
    message: str


@app.on_event("startup")
async def load_model():
    """Load model on startup"""
    global model, feature_names, optimal_threshold, bayesian_reasoner
    from src.config import Config
    
    logger.info("🚀 Starting API and loading model...")
    
    try:
        # Load TabNet model
        from pytorch_tabnet.tab_model import TabNetClassifier
        model = TabNetClassifier()
        
        # Try optimized model first
        optimized_path = Config.TABNET_OPTIMIZED
        regular_path = Config.TABNET_MODEL
        
        if optimized_path.exists():
            model.load_model(str(optimized_path))
            logger.info("✅ Loaded optimized TabNet model")
        elif regular_path.exists():
            model.load_model(str(regular_path))
            logger.info("✅ Loaded regular TabNet model")
        else:
            raise FileNotFoundError("No TabNet model found!")
        
        # Load feature names
        test_df = pd.read_parquet(Config.DATA_PROCESSED / 'test_split.parquet')
        feature_names = test_df.drop('TARGET', axis=1).columns.tolist()
        logger.info(f"✅ Loaded {len(feature_names)} feature names")
        
        # Load optimal threshold
        threshold_path = Config.OPTIMAL_THRESHOLD
        if threshold_path.exists():
            with open(threshold_path, 'r') as f:
                threshold_data = json.load(f)
                optimal_threshold = threshold_data['optimal_threshold']
            logger.info(f"✅ Loaded optimal threshold: {optimal_threshold:.3f}")
        
        # Load Bayesian Reasoner for explainability
        try:
            from src.models.bayesian_reasoner import BayesianReasoner
            bayesian_model_path = Config.OVERALL_PROJECT_ROOT / 'ml-model' / 'models' / 'bayesian'
            if bayesian_model_path.exists():
                bayesian_reasoner = BayesianReasoner(str(bayesian_model_path))
                logger.info("✅ Loaded Bayesian Reasoner for explainability")
            else:
                logger.warning(f"⚠️ Bayesian model not found at {bayesian_model_path}, reasoning will use heuristics")
        except Exception as e:
            logger.warning(f"⚠️ Could not load Bayesian Reasoner: {str(e)}")
        
        logger.info("🎉 API ready!")
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Home Credit Default Risk API",
        "version": "2.0.0",
        "status": "running",
        "bayesian_reasoning": bayesian_reasoner is not None,
        "endpoints": {
            "predict": "/predict",
            "predict_with_explanation": "/predict/explain",
            "explain_feature": "/explain/feature/{feature_name}",
            "explain_network": "/explain/network",
            "compare_scenarios": "/explain/compare",
            "health": "/health",
            "info": "/info",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model is not None
    reasoner_loaded = bayesian_reasoner is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
        "bayesian_reasoner_loaded": reasoner_loaded,
        "features_loaded": feature_names is not None,
        "total_features": len(feature_names) if feature_names else 0,
        "optimal_threshold": optimal_threshold,
        "reasoning_capability": "full" if reasoner_loaded else "basic"
    }


@app.get("/info")
async def model_info():
    """Get model information"""
    return {
        "model_type": "TabNet with Imbalance Optimization",
        "total_features": len(feature_names) if feature_names else 0,
        "feature_names": feature_names[:10] if feature_names else [],  # First 10
        "optimal_threshold": optimal_threshold,
        "training_info": {
            "technique": "SMOTEENN",
            "class_weights": [1.0, 5.16],
            "recall_achieved": 0.712
        }
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make credit default prediction
    
    Send feature values as a dictionary. Missing features will be filled with 0.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Create feature array in correct order
        feature_array = np.zeros(len(feature_names))
        
        for i, feature_name in enumerate(feature_names):
            if feature_name in request.features:
                feature_array[i] = request.features[feature_name]
        
        # Reshape for prediction
        X = feature_array.reshape(1, -1)
        
        # Get probability
        probability = float(model.predict_proba(X)[0, 1])
        
        # Make prediction using optimal threshold
        prediction = 1 if probability > optimal_threshold else 0
        
        # Determine risk level
        if probability < 0.2:
            risk_level = "Low Risk"
        elif probability < optimal_threshold:
            risk_level = "Medium Risk"
        elif probability < 0.6:
            risk_level = "High Risk"
        else:
            risk_level = "Very High Risk"
        
        message = "Likely to default - REJECT" if prediction == 1 else "Unlikely to default - APPROVE"
        
        return PredictionResponse(
            probability=round(probability, 4),
            prediction=prediction,
            risk_level=risk_level,
            threshold_used=round(optimal_threshold, 3),
            message=message
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch")
async def predict_batch(features_list: List[Dict[str, float]]):
    """
    Batch prediction endpoint
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        predictions = []
        
        for features in features_list:
            # Create feature array
            feature_array = np.zeros(len(feature_names))
            for i, feature_name in enumerate(feature_names):
                if feature_name in features:
                    feature_array[i] = features[feature_name]
            
            # Predict
            X = feature_array.reshape(1, -1)
            probability = float(model.predict_proba(X)[0, 1])
            prediction = 1 if probability > optimal_threshold else 0
            
            predictions.append({
                "probability": round(probability, 4),
                "prediction": prediction,
                "decision": "REJECT" if prediction == 1 else "APPROVE"
            })
        
        return {
            "total": len(predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BAYESIAN REASONING ENDPOINTS
# ============================================

@app.post("/predict/explain")
async def predict_with_explanation(request: PredictionRequest):
    """
    Make credit default prediction with full Bayesian reasoning explanation
    
    Returns:
    - Prediction and probability
    - Top risk factors with explanations
    - Top protective factors with explanations
    - Inference paths showing how features influence the decision
    - Natural language summary: "Because X is high and Y is low, the model predicts Z"
    - Conditional probabilities for each feature
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # First, get TabNet prediction
        feature_array = np.zeros(len(feature_names))
        for i, feature_name in enumerate(feature_names):
            if feature_name in request.features:
                feature_array[i] = request.features[feature_name]
        
        X = feature_array.reshape(1, -1)
        tabnet_probability = float(model.predict_proba(X)[0, 1])
        
        # Get Bayesian reasoning
        if bayesian_reasoner is not None:
            from src.models.bayesian_reasoner import reasoning_to_dict
            reasoning = bayesian_reasoner.get_reasoning(
                features=request.features,
                threshold=optimal_threshold
            )
            reasoning_dict = reasoning_to_dict(reasoning)
            
            # Update with TabNet probability for hybrid approach
            reasoning_dict['tabnet_probability'] = round(tabnet_probability, 4)
            reasoning_dict['hybrid_probability'] = round(
                (tabnet_probability + reasoning_dict['probability']) / 2, 4
            )
            
            return {
                "success": True,
                "model_type": "Hybrid TabNet + Bayesian Network",
                "reasoning": reasoning_dict
            }
        else:
            # Fallback: provide basic explanation without full BN
            prediction = 1 if tabnet_probability > optimal_threshold else 0
            
            return {
                "success": True,
                "model_type": "TabNet (Bayesian Reasoner not available)",
                "reasoning": {
                    "prediction": prediction,
                    "probability": round(tabnet_probability, 4),
                    "risk_level": _get_risk_level(tabnet_probability),
                    "decision": "REJECT" if prediction == 1 else "APPROVE",
                    "summary_explanation": _generate_basic_explanation(
                        request.features, tabnet_probability, prediction
                    ),
                    "top_risk_factors": [],
                    "top_protective_factors": [],
                    "inference_paths": [],
                    "detailed_explanation": "Full Bayesian reasoning not available.",
                    "conditional_probabilities": {},
                    "confidence_score": 0.5,
                    "evidence_strength": "Unknown"
                }
            }
        
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain/feature/{feature_name}")
async def explain_feature(feature_name: str, value: float):
    """
    Get explanation for how a specific feature influences the prediction
    
    Args:
        feature_name: Name of the feature (e.g., EXT_SOURCE_2)
        value: Value of the feature
    
    Returns:
        Explanation of the feature's role in the Bayesian Network
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=503, 
            detail="Bayesian Reasoner not loaded"
        )
    
    try:
        explanation = bayesian_reasoner.explain_feature(feature_name, value)
        return {
            "success": True,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Feature explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain/network")
async def get_network_structure():
    """
    Get the Bayesian Network structure for visualization
    
    Returns:
        Network nodes, edges, and descriptions for visualization
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=503,
            detail="Bayesian Reasoner not loaded"
        )
    
    try:
        structure = bayesian_reasoner.get_network_structure()
        return {
            "success": True,
            "network": structure
        }
    except Exception as e:
        logger.error(f"Network structure error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain/compare")
async def compare_scenarios(
    scenario_a: Dict[str, float],
    scenario_b: Dict[str, float]
):
    """
    Compare two scenarios and explain the difference in predictions
    
    Useful for understanding what changes would improve/worsen the outcome
    """
    if bayesian_reasoner is None:
        raise HTTPException(
            status_code=503,
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
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# HELPER FUNCTIONS
# ============================================

def _get_risk_level(probability: float) -> str:
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


def _generate_basic_explanation(
    features: Dict[str, float],
    probability: float,
    prediction: int
) -> str:
    """Generate a basic explanation without full BN"""
    decision = "likely to default" if prediction == 1 else "unlikely to default"
    
    # Check key features
    explanations = []
    
    ext_source_2 = features.get('EXT_SOURCE_2', 0.5)
    ext_source_3 = features.get('EXT_SOURCE_3', 0.5)
    ext_source_mean = features.get('EXT_SOURCE_MEAN', 0.5)
    
    if ext_source_mean < 0.3:
        explanations.append("external credit scores are low")
    elif ext_source_mean > 0.6:
        explanations.append("external credit scores are good")
    
    age = features.get('AGE_YEARS', 35)
    if age < 25:
        explanations.append("the applicant is young with limited credit history")
    elif age > 50:
        explanations.append("the applicant has mature credit history")
    
    credit_ratio = features.get('CREDIT_INCOME_RATIO', 3)
    if credit_ratio > 5:
        explanations.append("the credit-to-income ratio is high")
    elif credit_ratio < 2:
        explanations.append("the credit-to-income ratio is healthy")
    
    if explanations:
        reasons = ", ".join(explanations)
        return f"The applicant is {decision} (probability: {probability:.1%}) because {reasons}."
    else:
        return f"The applicant is {decision} with a probability of {probability:.1%}."


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
