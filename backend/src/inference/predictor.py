"""
============================================================================
INFERENCE MODULE - Hybrid DL + Bayesian Network Predictor (v4.0)
============================================================================
Production inference using the automatically selected best hybrid model
(ANN+BN, LSTM+BN, or RNN+BN) combined with Bayesian Network reasoning.

Model loads:
  - best_model.pth   : PyTorch checkpoint of the winning hybrid model
  - bayesian_network.pkl : Fitted pgmpy BN for reasoning / risk embeddings
  - scaler.joblib    : StandardScaler from preprocessing
  - feature_names.json : Ordered feature list

Pipeline:
  raw features → scale → BN risk embedding → augment → DL predict
============================================================================
"""

import os
import sys
import json
import joblib
import logging

import numpy as np
import pandas as pd
import torch
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Add ml-model to path for imports
ML_MODEL_PATH = Path(__file__).parent.parent.parent.parent / "ml-model"
sys.path.insert(0, str(ML_MODEL_PATH))

# Fix namespace collision: backend and ml-model both use 'src' directory
try:
    import src
    ml_src_path = str(ML_MODEL_PATH / "src")
    if hasattr(src, "__path__"):
        if isinstance(src.__path__, list):
            if ml_src_path not in src.__path__:
                src.__path__.append(ml_src_path)
        else:
            if ml_src_path not in getattr(src.__path__, "_path", []):
                src.__path__._path.append(ml_src_path)
    else:
        src.__path__ = [ml_src_path]
except Exception as e:
    logger.warning(f"Failed to merge src namespace path: {e}")


class LoanPredictor:
    """
    Loan Approval Predictor using the best Hybrid DL + Bayesian Network model.

    Loads the auto-selected best model from train_pipeline.py and provides
    the same predict() / explain() / prepare_features_from_applicant() API
    consumed by the predictions router.
    """

    MODEL_VERSION = "4.0.0"
    OPTIMAL_THRESHOLD = 0.80

    def __init__(self, model_path: str = None):
        self.dl_model = None
        self.bn_model = None
        self.scaler = None
        self.feature_names: list = []
        self.registry: dict = {}
        self.model_arch: str = ""
        self.input_dim: int = 0
        self._load_all(model_path)
        logger.info(
            f"✅ LoanPredictor v{self.MODEL_VERSION} — "
            f"arch={self.model_arch}, features={len(self.feature_names)}"
        )

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def _load_all(self, model_path: str = None):
        """Load best DL model, BN model, scaler, and feature names."""

        # 1. Registry
        registry_path = ML_MODEL_PATH / "models" / "model_registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                self.registry = json.load(f)
        else:
            raise FileNotFoundError(f"Model registry not found: {registry_path}")

        best_info = self.registry.get("best_model", {})
        self.model_arch = best_info.get("architecture", "ANN").lower()
        self.input_dim = best_info.get("input_dim", 0)
        hyperparams = best_info.get("hyperparameters", {})

        # 2. DL model
        dl_path = Path(model_path) if model_path else ML_MODEL_PATH / "models" / "best_model.pth"
        if not dl_path.exists():
            raise FileNotFoundError(f"Best model not found: {dl_path}")

        self.dl_model = self._instantiate_model(self.model_arch, hyperparams, self.input_dim)
        ckpt = torch.load(str(dl_path), map_location="cpu", weights_only=False)
        self.dl_model.network.load_state_dict(ckpt["state_dict"])
        self.dl_model.is_fitted = True
        logger.info(f"✅ Loaded DL model from {dl_path}")

        # 3. Bayesian Network
        bn_path = ML_MODEL_PATH / "models" / "bayesian_network.pkl"
        if bn_path.exists():
            self.bn_model = joblib.load(bn_path)
            logger.info("✅ Loaded Bayesian Network")
        else:
            logger.warning(f"BN model not found: {bn_path}")

        # 4. Scaler
        scaler_path = ML_MODEL_PATH / "dataset" / "processed_data" / "scaler.joblib"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            logger.info("✅ Loaded scaler")
        else:
            logger.warning(f"Scaler not found: {scaler_path}")

        # 5. Feature names
        fn_path = ML_MODEL_PATH / "dataset" / "processed_data" / "feature_names.json"
        if fn_path.exists():
            with open(fn_path) as f:
                self.feature_names = json.load(f)
            logger.info(f"✅ Loaded {len(self.feature_names)} feature names")
        else:
            self.feature_names = self._fallback_feature_names()

    def _instantiate_model(self, arch: str, hp: dict, input_dim: int):
        """Create the correct model class instance."""
        from src.hybrid_models.ann_bayesian_network.model import ANNBayesianHybrid
        from src.hybrid_models.lstm_bayesian_network.model import LSTMBayesianHybrid
        from src.hybrid_models.rnn_bayesian_network.model import RNNBayesianHybrid

        if arch == "ann":
            return ANNBayesianHybrid(
                input_dim=input_dim,
                hidden_dims=hp.get("hidden_dims", [128, 64, 32]),
                dropout=hp.get("dropout", 0.3),
                device="cpu",
            )
        elif arch == "lstm":
            return LSTMBayesianHybrid(
                input_dim=input_dim,
                hidden_size=hp.get("hidden_size", 128),
                num_layers=hp.get("num_layers", 3),
                dropout=hp.get("dropout", 0.3),
                device="cpu",
            )
        else:  # rnn
            return RNNBayesianHybrid(
                input_dim=input_dim,
                hidden_size=hp.get("hidden_size", 128),
                num_layers=hp.get("num_layers", 3),
                dropout=hp.get("dropout", 0.3),
                device="cpu",
            )

    @staticmethod
    def _fallback_feature_names():
        return [
            "no_of_dependents", "education", "self_employed", "income_annum",
            "loan_amount", "loan_term", "cibil_score", "residential_assets_value",
            "commercial_assets_value", "luxury_assets_value", "bank_asset_value",
            "loan_to_income_ratio", "total_assets", "assets_to_loan_ratio",
            "assets_to_income_ratio", "debt_to_asset_ratio", "monthly_payment",
            "payment_to_income_ratio", "cibil_excellent", "cibil_good",
            "cibil_fair", "cibil_poor",
        ]

    # ------------------------------------------------------------------
    # Feature preparation
    # ------------------------------------------------------------------
    def prepare_features_from_applicant(
        self, applicant: Dict, loan_amount: float, loan_term_years: int
    ) -> Dict[str, float]:
        """
        Map database applicant record → model feature dict.

        Mirrors the feature engineering done in preprocessing.
        """
        no_of_dependents = applicant.get("no_of_dependents", 0)
        education = self._encode_education(applicant.get("education_level", "Graduate"))
        employment_status = str(applicant.get("employment_status", "Employed")).lower()
        self_employed = 1 if "self" in employment_status else 0

        monthly_income = applicant.get("monthly_income", 50000)
        income_annum = monthly_income * 12
        cibil_score = applicant.get("credit_score", 650)

        total_assets_db = applicant.get("assets_value", 0)
        if "residential_assets_value" in applicant:
            res = applicant.get("residential_assets_value", 0)
            com = applicant.get("commercial_assets_value", 0)
            lux = applicant.get("luxury_assets_value", 0)
            bnk = applicant.get("bank_asset_value", 0)
        else:
            res = total_assets_db * 0.7
            com = 0
            lux = 0
            bnk = total_assets_db * 0.3

        total_assets = res + com + lux + bnk
        loan_to_income_ratio = loan_amount / (income_annum + 1)
        assets_to_loan_ratio = total_assets / (loan_amount + 1)
        assets_to_income_ratio = total_assets / (income_annum + 1)
        debt_to_asset_ratio = loan_amount / (total_assets + 1)
        monthly_payment = loan_amount / (loan_term_years * 12 + 1)
        payment_to_income_ratio = monthly_payment / (monthly_income + 1)

        return {
            "no_of_dependents": no_of_dependents,
            "education": education,
            "self_employed": self_employed,
            "income_annum": income_annum,
            "loan_amount": loan_amount,
            "loan_term": loan_term_years,
            "cibil_score": cibil_score,
            "residential_assets_value": res,
            "commercial_assets_value": com,
            "luxury_assets_value": lux,
            "bank_asset_value": bnk,
            "loan_to_income_ratio": loan_to_income_ratio,
            "total_assets": total_assets,
            "assets_to_loan_ratio": assets_to_loan_ratio,
            "assets_to_income_ratio": assets_to_income_ratio,
            "debt_to_asset_ratio": debt_to_asset_ratio,
            "monthly_payment": monthly_payment,
            "payment_to_income_ratio": payment_to_income_ratio,
            "cibil_excellent": 1 if cibil_score >= 750 else 0,
            "cibil_good": 1 if 650 <= cibil_score < 750 else 0,
            "cibil_fair": 1 if 550 <= cibil_score < 650 else 0,
            "cibil_poor": 1 if cibil_score < 550 else 0,
        }

    def _encode_education(self, education: str) -> int:
        education = str(education).lower().strip()
        if any(k in education for k in ("graduate", "post", "master", "bachelor", "degree")):
            return 0
        return 1

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Single-sample prediction with confidence and risk level."""
        x = self._features_to_array(features)
        prob = float(self.dl_model.predict_proba(x)[0])
        pred = int(prob >= self.OPTIMAL_THRESHOLD)

        return {
            "probability": prob,
            "prediction": pred,
            "risk_level": self._risk_level(prob),
            "confidence": max(prob, 1 - prob) * 100,
            "threshold_used": self.OPTIMAL_THRESHOLD,
            "recommendation": self._recommendation(prob),
            "decision": "APPROVE" if pred == 1 else "REJECT",
            "message": self._recommendation(prob),
        }

    def explain(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Prediction with top-factor explanations + BN reasoning."""
        result = self.predict(features)

        # Feature-importance factors
        important = [
            "cibil_score", "loan_to_income_ratio", "total_assets",
            "payment_to_income_ratio", "income_annum", "loan_amount",
        ]
        top_factors = []
        for feat in important:
            if feat in features:
                top_factors.append({
                    "feature": feat,
                    "value": features[feat],
                    "importance": self._feature_importance(feat),
                    "explanation": self._explain_feature(feat, features[feat]),
                })
        top_factors.sort(key=lambda x: x["importance"], reverse=True)
        result["top_factors"] = top_factors[:5]

        # BN reasoning
        if self.bn_model:
            try:
                bn_info = self.bn_model.explain(features)
                result["bn_reasoning"] = bn_info
            except Exception as e:
                logger.warning(f"BN reasoning failed: {e}")

        return result

    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.predict(f) for f in features_list]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _features_to_array(self, features: dict) -> np.ndarray:
        """Convert feature dict → scaled + BN-augmented numpy array."""
        df = pd.DataFrame([features])[self.feature_names]

        # Scale
        if self.scaler is not None:
            x_scaled = self.scaler.transform(df)
        else:
            x_scaled = df.values

        # BN risk embedding
        if self.bn_model is not None:
            try:
                emb = self.bn_model.get_risk_embeddings(x_scaled)
                x_aug = np.hstack([x_scaled, emb])
            except Exception:
                x_aug = np.hstack([x_scaled, np.array([[0.5]])])
        else:
            x_aug = np.hstack([x_scaled, np.array([[0.5]])])

        return x_aug

    @staticmethod
    def _risk_level(prob: float) -> str:
        if prob >= 0.8:
            return "Very Low Risk"
        elif prob >= 0.65:
            return "Low Risk"
        elif prob >= 0.5:
            return "Medium Risk"
        elif prob >= 0.35:
            return "High Risk"
        return "Very High Risk"

    @staticmethod
    def _recommendation(prob: float) -> str:
        if prob >= 0.8:
            return "Excellent candidate. Very likely to be approved."
        elif prob >= 0.6:
            return "Good candidate with low risk."
        elif prob >= 0.4:
            return "Moderate risk. Additional verification recommended."
        elif prob >= 0.2:
            return "High risk. Consider smaller loan amount or longer term."
        return "Very high risk. Not recommended for approval."

    @staticmethod
    def _feature_importance(feature: str) -> float:
        importance_map = {
            "cibil_score": 0.25,
            "loan_to_income_ratio": 0.20,
            "total_assets": 0.15,
            "payment_to_income_ratio": 0.12,
            "income_annum": 0.10,
            "loan_amount": 0.08,
            "loan_term": 0.05,
            "education": 0.03,
            "no_of_dependents": 0.02,
        }
        return importance_map.get(feature, 0.01)

    @staticmethod
    def _explain_feature(feature: str, value: float) -> str:
        if feature == "cibil_score":
            if value >= 750: return "Excellent credit score — very strong indicator of reliability."
            if value >= 650: return "Good credit score — shows responsible credit management."
            if value >= 550: return "Fair credit score — could be improved."
            return "Low credit score — this raises some concerns."
        if feature == "loan_to_income_ratio":
            if value < 2: return "Loan amount is very manageable for your income."
            if value < 4: return "Loan amount is reasonable for your income level."
            if value < 6: return "Loan amount is relatively high for your income."
            return "Loan amount is quite high compared to your income."
        if feature == "total_assets":
            if value > 5_000_000: return f"Strong asset base of LKR {value:,.0f} provides good security."
            if value > 2_000_000: return f"Decent asset base of LKR {value:,.0f}."
            if value > 500_000: return f"Moderate asset base of LKR {value:,.0f}."
            return f"Limited asset base of LKR {value:,.0f}."
        if feature == "payment_to_income_ratio":
            if value < 0.3: return "Monthly payment is very comfortable for your income."
            if value < 0.5: return "Monthly payment is manageable for your income."
            return "Monthly payment is high relative to your income."
        if feature == "income_annum":
            return f"Annual income: LKR {value:,.0f}"
        if feature == "loan_amount":
            return f"Requested loan: LKR {value:,.0f}"
        return f"{feature}: {value}"

    def get_feature_names(self) -> List[str]:
        return self.feature_names.copy()

    def is_healthy(self) -> bool:
        return self.dl_model is not None and self.dl_model.is_fitted

    def generate_lime_report(self, features: Dict[str, Any], applicant_id: str) -> Dict[str, Any]:
        """Generate automated LIME XAI report for an applicant."""
        try:
            from src.evaluation.xai_lime import LimeReportGenerator
            
            # Lazy initialization of LIME generator (it loads training data)
            if not hasattr(self, '_lime_generator') or self._lime_generator is None:
                self._lime_generator = LimeReportGenerator(self)
                
            # Prepare features as array
            x_array = self._features_to_array(features)
            
            # Generate report
            # Pass 1D array (x_array is 2D: (1, n_features))
            report = self._lime_generator.generate_report(x_array[0], applicant_id)
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate LIME report: {e}")
            return {"error": str(e)}


# Singleton
_predictor: Optional[LoanPredictor] = None


def get_predictor(model_path: str = None) -> LoanPredictor:
    global _predictor
    if _predictor is None:
        _predictor = LoanPredictor(model_path)
    return _predictor


def predict(features: Dict[str, Any]) -> Dict[str, Any]:
    return get_predictor().predict(features)


def predict_batch(features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return get_predictor().predict_batch(features_list)
