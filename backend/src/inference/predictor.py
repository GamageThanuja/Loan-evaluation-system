"""
============================================================================
INFERENCE MODULE - Hybrid Model Predictor (v3.0)
============================================================================
Production inference using the Hybrid Bayesian Model.

Model Architecture:
- Bayesian Neural Network (BNN) with MC Dropout
- Gradient Boosting Bayesian Network  
- Ensemble combining both with optimized weights (60% BNN + 40% GB)

Features (22 total):
- Loan details: amount, term, purpose
- Applicant info: income, employment, dependents, education
- Assets: residential, commercial, luxury, bank
- Credit score (CIBIL)
- Engineered features: ratios, monthly payments, asset totals
============================================================================
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Add ml-model to path for imports
ML_MODEL_PATH = Path(__file__).parent.parent.parent.parent / 'ml-model'
sys.path.insert(0, str(ML_MODEL_PATH))


class LoanPredictor:
    """
    Loan Approval Predictor using Hybrid Bayesian Model.
    
    The model expects 22 features from loan application data:
    - Basic info: no_of_dependents, education, self_employed
    - Financial: income_annum, loan_amount, loan_term, cibil_score
    - Assets: residential, commercial, luxury, bank assets
    - Engineered: loan_to_income_ratio, total_assets, various ratios
    - CIBIL categories: excellent, good, fair, poor
    """
    
    MODEL_VERSION = "3.0.0"
    OPTIMAL_THRESHOLD = 0.5  # Default threshold, will be updated from model if available
    
    def __init__(self, model_path: str = None):
        """Initialize predictor with hybrid model."""
        self.model = None
        self.scaler = None
        self.pca = None
        self.feature_names = []
        self.model_path = model_path or self._get_default_model_path()
        self._load_model()
        logger.info(f"✅ LoanPredictor initialized (v{self.MODEL_VERSION}) - {len(self.feature_names)} features")
    
    def _get_default_model_path(self) -> str:
        """Get default model path."""
        model_path = ML_MODEL_PATH / 'models' / 'hybrid_model.joblib'
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at: {model_path}")
        logger.info(f"Found model at: {model_path}")
        return str(model_path)
    
    def _load_model(self):
        """Load the hybrid model and supporting files."""
        # Load the trained model
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        try:
            # Import the HybridModel class to enable unpickling
            from training.hybrid_model import HybridModel
            
            # Use the custom load method
            self.model = HybridModel.load(self.model_path)
            logger.info(f"✅ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
        
        # Load feature names
        feature_names_path = ML_MODEL_PATH / 'data' / 'processed' / 'feature_names.json'
        if feature_names_path.exists():
            with open(feature_names_path, 'r') as f:
                self.feature_names = json.load(f)
            logger.info(f"✅ Loaded {len(self.feature_names)} feature names")
        else:
            logger.warning(f"Feature names file not found: {feature_names_path}")
            # Fallback feature names
            self.feature_names = [
                "no_of_dependents", "education", "self_employed", "income_annum",
                "loan_amount", "loan_term", "cibil_score", "residential_assets_value",
                "commercial_assets_value", "luxury_assets_value", "bank_asset_value",
                "loan_to_income_ratio", "total_assets", "assets_to_loan_ratio",
                "assets_to_income_ratio", "debt_to_asset_ratio", "monthly_payment",
                "payment_to_income_ratio", "cibil_excellent", "cibil_good",
                "cibil_fair", "cibil_poor"
            ]
        
        # Load scaler
        scaler_path = ML_MODEL_PATH / 'data' / 'processed' / 'scaler.joblib'
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✅ Scaler loaded")
        else:
            logger.warning(f"Scaler file not found: {scaler_path}")
            self.scaler = None
        
        # Load PCA transformer
        pca_path = ML_MODEL_PATH / 'data' / 'processed' / 'pca.joblib'
        if pca_path.exists():
            self.pca = joblib.load(pca_path)
            logger.info(f"✅ PCA loaded ({self.pca.n_components_} components, {self.pca.explained_variance_ratio_.sum()*100:.2f}% variance)")
        else:
            logger.warning(f"PCA file not found: {pca_path}")
            self.pca = None
    
    def prepare_features_from_applicant(self, applicant: Dict, 
                                        loan_amount: float, 
                                        loan_term_years: int) -> Dict[str, float]:
        """
        Prepare all 22 model features from applicant database record.
        
        Maps database fields to model features with proper engineering.
        
        Args:
            applicant: Dict with keys like 'monthly_income', 'credit_score', 
                      'no_of_dependents', 'education_level', 'self_employed',
                      'residential_assets_value', 'commercial_assets_value', 
                      'luxury_assets_value', 'bank_asset_value'
            loan_amount: Requested loan amount
            loan_term_years: Loan term in years
            
        Returns:
            Dict with 22 features ready for model prediction
        """
        # Extract applicant data with defaults
        no_of_dependents = applicant.get('no_of_dependents', 0)
        education = self._encode_education(applicant.get('education_level', 'Graduate'))
        
        # Derive self_employed from employment_status field
        employment_status = str(applicant.get('employment_status', 'Employed')).lower()
        self_employed = 1 if 'self' in employment_status else 0
        
        # Financial data
        monthly_income = applicant.get('monthly_income', 50000)
        income_annum = monthly_income * 12
        
        # Credit score
        cibil_score = applicant.get('credit_score', 650)
        
        # Asset values - use total assets_value or individual breakdown if available
        total_assets_db = applicant.get('assets_value', 0)
        
        # Check if individual asset values are provided, otherwise use total
        if 'residential_assets_value' in applicant:
            residential_assets_value = applicant.get('residential_assets_value', 0)
            commercial_assets_value = applicant.get('commercial_assets_value', 0)
            luxury_assets_value = applicant.get('luxury_assets_value', 0)
            bank_asset_value = applicant.get('bank_asset_value', 0)
        else:
            # Distribute total assets: assume 70% residential, 30% bank for simplicity
            residential_assets_value = total_assets_db * 0.7
            commercial_assets_value = 0
            luxury_assets_value = 0
            bank_asset_value = total_assets_db * 0.3
        
        # Calculate engineered features (same as training)
        loan_to_income_ratio = loan_amount / (income_annum + 1)
        total_assets = residential_assets_value + commercial_assets_value + \
                      luxury_assets_value + bank_asset_value
        assets_to_loan_ratio = total_assets / (loan_amount + 1)
        assets_to_income_ratio = total_assets / (income_annum + 1)
        debt_to_asset_ratio = loan_amount / (total_assets + 1)
        monthly_payment = loan_amount / (loan_term_years * 12 + 1)
        payment_to_income_ratio = monthly_payment / (monthly_income + 1)
        
        # CIBIL score categories
        cibil_excellent = 1 if cibil_score >= 750 else 0
        cibil_good = 1 if 650 <= cibil_score < 750 else 0
        cibil_fair = 1 if 550 <= cibil_score < 650 else 0
        cibil_poor = 1 if cibil_score < 550 else 0
        
        # Build feature dictionary matching training feature order
        features = {
            "no_of_dependents": no_of_dependents,
            "education": education,
            "self_employed": self_employed,
            "income_annum": income_annum,
            "loan_amount": loan_amount,
            "loan_term": loan_term_years,
            "cibil_score": cibil_score,
            "residential_assets_value": residential_assets_value,
            "commercial_assets_value": commercial_assets_value,
            "luxury_assets_value": luxury_assets_value,
            "bank_asset_value": bank_asset_value,
            "loan_to_income_ratio": loan_to_income_ratio,
            "total_assets": total_assets,
            "assets_to_loan_ratio": assets_to_loan_ratio,
            "assets_to_income_ratio": assets_to_income_ratio,
            "debt_to_asset_ratio": debt_to_asset_ratio,
            "monthly_payment": monthly_payment,
            "payment_to_income_ratio": payment_to_income_ratio,
            "cibil_excellent": cibil_excellent,
            "cibil_good": cibil_good,
            "cibil_fair": cibil_fair,
            "cibil_poor": cibil_poor
        }
        
        return features
    
    def _encode_education(self, education: str) -> int:
        """Encode education level to match training data."""
        education = str(education).lower().strip()
        
        # Match training encoding: Graduate=0, Not Graduate=1
        if 'graduate' in education or 'post' in education or 'master' in education or \
           'bachelor' in education or 'degree' in education or education == 'graduated':
            return 0
        else:
            return 1
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction from features dictionary."""
        # Convert features dict to DataFrame with correct order
        df = pd.DataFrame([features])[self.feature_names]
        
        # Step 1: Normalize features (StandardScaler)
        if self.scaler is not None:
            df_normalized = pd.DataFrame(
                self.scaler.transform(df),
                columns=self.feature_names
            )
        else:
            logger.warning("Scaler not available, using raw features")
            df_normalized = df
        
        # Step 2: Apply PCA dimensionality reduction
        if self.pca is not None:
            df_pca = self.pca.transform(df_normalized)
            df_pca = pd.DataFrame(df_pca)
        else:
            logger.warning("PCA not available, using normalized features directly")
            df_pca = df_normalized
        
        # Step 3: Get detailed predictions from hybrid model
        result = self.model.predict_with_details(df_pca)
        
        prob = float(result['probability'][0])
        pred = int(result['prediction'][0])
        bnn_uncertainty = float(result['bnn_uncertainty'][0])
        risk_level = str(result['risk_level'][0])
        
        return {
            'probability': prob,
            'prediction': pred,
            'risk_level': risk_level,
            'confidence': max(prob, 1 - prob) * 100,
            'uncertainty': bnn_uncertainty,
            'threshold_used': self.OPTIMAL_THRESHOLD,
            'recommendation': self._get_recommendation(prob),
            'decision': "APPROVE" if pred == 1 else "REJECT"  # pred=1 means Approved (from training data)
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make batch predictions from list of features dictionaries."""
        results = []
        for features in features_list:
            results.append(self.predict(features))
        return results
    
    def explain(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Get prediction with explanation of key factors."""
        # Get basic prediction
        result = self.predict(features)
        
        # Determine key factors based on new features
        top_factors = []
        important_features = [
            'cibil_score', 'loan_to_income_ratio', 'total_assets',
            'payment_to_income_ratio', 'income_annum', 'loan_amount'
        ]
        
        for feat in important_features:
            if feat in features:
                importance = self._get_feature_importance(feat)
                top_factors.append({
                    'feature': feat,
                    'value': features[feat],
                    'importance': importance,
                    'explanation': self._explain_feature(feat, features[feat])
                })
        
        top_factors = sorted(top_factors, key=lambda x: x['importance'], reverse=True)[:5]
        
        result['top_factors'] = top_factors
        return result
    
    def _get_feature_importance(self, feature: str) -> float:
        """Get feature importance scores for new features."""
        # Based on training results and domain knowledge
        importance_map = {
            'cibil_score': 0.25,  # Most important
            'loan_to_income_ratio': 0.20,
            'total_assets': 0.15,
            'payment_to_income_ratio': 0.12,
            'income_annum': 0.10,
            'loan_amount': 0.08,
            'loan_term': 0.05,
            'education': 0.03,
            'no_of_dependents': 0.02,
        }
        return importance_map.get(feature, 0.01)
    
    def _explain_feature(self, feature: str, value: float) -> str:
        """Generate human-readable explanation for feature."""
        if feature == 'cibil_score':
            if value >= 750:
                return "Excellent credit score - very strong indicator of reliability."
            elif value >= 650:
                return "Good credit score - shows responsible credit management."
            elif value >= 550:
                return "Fair credit score - could be improved."
            else:
                return "Low credit score - this raises some concerns."
        elif feature == 'loan_to_income_ratio':
            if value < 2:
                return "Loan amount is very manageable for your income."
            elif value < 4:
                return "Loan amount is reasonable for your income level."
            elif value < 6:
                return "Loan amount is relatively high for your income."
            else:
                return "Loan amount is quite high compared to your income."
        elif feature == 'total_assets':
            if value > 5000000:
                return f"Strong asset base of LKR {value:,.0f} provides good security."
            elif value > 2000000:
                return f"Decent asset base of LKR {value:,.0f}."
            elif value > 500000:
                return f"Moderate asset base of LKR {value:,.0f}."
            else:
                return f"Limited asset base of LKR {value:,.0f}."
        elif feature == 'payment_to_income_ratio':
            if value < 0.3:
                return "Monthly payment is very comfortable for your income."
            elif value < 0.5:
                return "Monthly payment is manageable for your income."
            else:
                return "Monthly payment is high relative to your income."
        elif feature == 'income_annum':
            return f"Annual income: LKR {value:,.0f}"
        elif feature == 'loan_amount':
            return f"Requested loan: LKR {value:,.0f}"
        return f"{feature}: {value}"
    
    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level from probability.
        
        Note: In our model, probability close to 1 = likely APPROVED = low risk.
        So high probability = low risk, low probability = high risk.
        """
        if probability >= 0.8:
            return "Very Low"
        elif probability >= 0.6:
            return "Low"
        elif probability >= 0.4:
            return "Medium"
        elif probability >= 0.2:
            return "High"
        else:
            return "Very High"
    
    def _get_recommendation(self, probability: float) -> str:
        """Generate recommendation based on probability.
        
        Note: probability close to 1 = likely to be APPROVED = good applicant.
        So high probability = recommend approval, low probability = recommend rejection.
        """
        if probability >= 0.8:
            return "Excellent candidate. Very likely to be approved."
        elif probability >= 0.6:
            return "Good candidate with low risk."
        elif probability >= 0.4:
            return "Moderate risk. Additional verification recommended."
        elif probability >= 0.2:
            return "High risk. Consider smaller loan amount or longer term."
        else:
            return "Very high risk. Not recommended for approval."
    
    def get_feature_names(self) -> List[str]:
        """Get required feature names."""
        return self.feature_names.copy()
    
    def is_healthy(self) -> bool:
        """Check if model is loaded and ready."""
        return self.model is not None and self.model.is_fitted


# Singleton instance
_predictor: Optional[LoanPredictor] = None


def get_predictor(model_path: str = None) -> LoanPredictor:
    """Get or create predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = LoanPredictor(model_path)
    return _predictor


def predict(features: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for single prediction."""
    return get_predictor().predict(features)


def predict_batch(features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function for batch predictions."""
    return get_predictor().predict_batch(features_list)
