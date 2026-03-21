#!/usr/bin/env python3
"""
Bayesian Network Model (Traditional Probabilistic)
===================================================
Uses probabilistic graphical model approach for loan approval prediction.
Implemented using sklearn's Gaussian Naive Bayes with calibration.
"""

import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, f1_score
import joblib


class BayesianNetwork:
    """
    Bayesian Network model using Gaussian Naive Bayes with probability calibration.
    This provides a probabilistic model that estimates P(Y|X).
    """
    
    VERSION = "1.0.0"
    MODEL_NAME = "BayesianNetwork"
    
    def __init__(self, var_smoothing: float = 1e-9, cv: int = 5):
        self.var_smoothing = var_smoothing
        self.cv = cv
        
        # Base Naive Bayes model
        self.base_model = GaussianNB(var_smoothing=var_smoothing)
        
        # Calibrated model for better probability estimates
        self.model = CalibratedClassifierCV(
            self.base_model,
            method='isotonic',
            cv=cv
        )
        
        self.is_fitted = False
        self.feature_names = None
        self.class_priors = None
    
    def fit(self, X, y):
        """Fit the Bayesian Network model."""
        print(f"\n  Training {self.MODEL_NAME}...")
        print("-" * 60)
        
        # Store feature names
        self.feature_names = X.columns.tolist() if hasattr(X, 'columns') else None
        
        # Calculate class priors
        unique, counts = np.unique(y, return_counts=True)
        self.class_priors = dict(zip(unique, counts / len(y)))
        print(f"  Class priors: {self.class_priors}")
        
        # Convert to numpy
        X_np = X.values if hasattr(X, 'values') else X
        y_np = y.values if hasattr(y, 'values') else y
        
        # Fit calibrated model
        self.model.fit(X_np, y_np)
        self.is_fitted = True
        
        print(f"  ✓ Model fitted with {len(X):,} samples")
        
        return self
    
    def predict_proba(self, X):
        """Predict probabilities."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_np = X.values if hasattr(X, 'values') else X
        return self.model.predict_proba(X_np)
    
    def predict(self, X, threshold: float = 0.5):
        """Predict class labels."""
        proba = self.predict_proba(X)[:, 1]
        return (proba >= threshold).astype(int)
    
    def evaluate(self, X, y):
        """Evaluate model performance."""
        X_np = X.values if hasattr(X, 'values') else X
        y_np = y.values if hasattr(y, 'values') else y
        
        proba = self.predict_proba(X_np)[:, 1]
        preds = (proba >= 0.5).astype(int)
        
        metrics = {
            'roc_auc': roc_auc_score(y_np, proba),
            'f1': f1_score(y_np, preds)
        }
        
        return metrics
    
    def get_config(self):
        """Return model configuration."""
        return {
            'model_name': self.MODEL_NAME,
            'version': self.VERSION,
            'var_smoothing': self.var_smoothing,
            'cv': self.cv,
            'class_priors': self.class_priors,
            'feature_count': len(self.feature_names) if self.feature_names else None
        }
    
    def save(self, path: str):
        """Save model to disk."""
        model_data = {
            'model': self.model,
            'config': self.get_config(),
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, path)
        print(f"  ✓ Saved to {path}")
    
    @classmethod
    def load(cls, path: str):
        """Load model from disk."""
        model_data = joblib.load(path)
        
        instance = cls()
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        instance.is_fitted = True
        
        config = model_data['config']
        instance.var_smoothing = config['var_smoothing']
        instance.cv = config['cv']
        instance.class_priors = config['class_priors']
        
        return instance


class GradientBoostingBayesian:
    """
    Gradient Boosting with Bayesian-like probability calibration.
    Provides more accurate probability estimates than standard GB.
    """
    
    VERSION = "1.0.0"
    MODEL_NAME = "GradientBoostingBayesian"
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 5,
                 learning_rate: float = 0.1, cv: int = 5):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.cv = cv
        
        self.base_model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42
        )
        
        self.model = CalibratedClassifierCV(
            self.base_model,
            method='isotonic',
            cv=cv
        )
        
        self.is_fitted = False
        self.feature_names = None
        self.feature_importance = None
    
    def fit(self, X, y):
        """Fit the model."""
        print(f"\n  Training {self.MODEL_NAME}...")
        print("-" * 60)
        
        self.feature_names = X.columns.tolist() if hasattr(X, 'columns') else None
        
        X_np = X.values if hasattr(X, 'values') else X
        y_np = y.values if hasattr(y, 'values') else y
        
        # Fit base model first to get feature importance
        self.base_model.fit(X_np, y_np)
        self.feature_importance = self.base_model.feature_importances_
        
        # Now fit calibrated model
        self.model.fit(X_np, y_np)
        self.is_fitted = True
        
        print(f"  ✓ Model fitted with {len(X):,} samples")
        
        # Show top features
        if self.feature_names:
            importance_idx = np.argsort(self.feature_importance)[::-1][:5]
            print(f"  Top 5 features:")
            for idx in importance_idx:
                print(f"    - {self.feature_names[idx]}: {self.feature_importance[idx]:.4f}")
        
        return self
    
    def predict_proba(self, X):
        """Predict probabilities."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_np = X.values if hasattr(X, 'values') else X
        return self.model.predict_proba(X_np)
    
    def predict(self, X, threshold: float = 0.5):
        """Predict class labels."""
        proba = self.predict_proba(X)[:, 1]
        return (proba >= threshold).astype(int)
    
    def evaluate(self, X, y):
        """Evaluate model performance."""
        X_np = X.values if hasattr(X, 'values') else X
        y_np = y.values if hasattr(y, 'values') else y
        
        proba = self.predict_proba(X_np)[:, 1]
        preds = (proba >= 0.5).astype(int)
        
        return {
            'roc_auc': roc_auc_score(y_np, proba),
            'f1': f1_score(y_np, preds)
        }
    
    def get_config(self):
        """Return model configuration."""
        return {
            'model_name': self.MODEL_NAME,
            'version': self.VERSION,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'cv': self.cv
        }
    
    def save(self, path: str):
        """Save model to disk."""
        model_data = {
            'model': self.model,
            'base_model': self.base_model,
            'config': self.get_config(),
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, path)
        print(f"  ✓ Saved to {path}")
    
    @classmethod
    def load(cls, path: str):
        """Load model from disk."""
        model_data = joblib.load(path)
        
        config = model_data['config']
        instance = cls(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            learning_rate=config['learning_rate'],
            cv=config['cv']
        )
        instance.model = model_data['model']
        instance.base_model = model_data['base_model']
        instance.feature_names = model_data['feature_names']
        instance.feature_importance = model_data['feature_importance']
        instance.is_fitted = True
        
        return instance
