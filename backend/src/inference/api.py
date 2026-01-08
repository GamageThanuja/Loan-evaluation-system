"""
Simple FastAPI for Credit Default Prediction
Ready for Postman testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
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
    global model, feature_names, optimal_threshold
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
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "info": "/info",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model is not None
    return {
        "status": "healthy" if model_loaded else "unhealthy",
        "model_loaded": model_loaded,
        "features_loaded": feature_names is not None,
        "total_features": len(feature_names) if feature_names else 0,
        "optimal_threshold": optimal_threshold
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


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
