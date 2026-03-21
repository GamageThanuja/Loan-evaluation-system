#!/usr/bin/env python3
"""
Hybrid Model
============
Combines Bayesian Neural Network and Bayesian Network (Gradient Boosting)
for enhanced prediction with uncertainty estimation.
"""

import numpy as np
import torch
import joblib
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score

try:
    from .bayesian_nn import BayesianNeuralNetwork, BayesianNNTrainer
    from .bayesian_network import GradientBoostingBayesian
except ImportError:
    from bayesian_nn import BayesianNeuralNetwork, BayesianNNTrainer
    from bayesian_network import GradientBoostingBayesian


class HybridModel:
    """
    Hybrid model that combines:
    1. Bayesian Neural Network (deep learning with uncertainty)
    2. Gradient Boosting Bayesian (ensemble with calibration)
    
    Uses weighted averaging of predictions for final output.
    """
    
    VERSION = "1.0.0"
    MODEL_NAME = "HybridModel"
    
    def __init__(self, input_dim: int, 
                 bnn_hidden_dims: list = [128, 64, 32],
                 bnn_dropout: float = 0.3,
                 gb_n_estimators: int = 100,
                 gb_max_depth: int = 5,
                 bnn_weight: float = 0.6,
                 device: str = 'cpu'):
        
        self.input_dim = input_dim
        self.bnn_weight = bnn_weight
        self.gb_weight = 1.0 - bnn_weight
        self.device = device
        
        # Initialize component models
        self.bnn_model = BayesianNeuralNetwork(
            input_dim=input_dim,
            hidden_dims=bnn_hidden_dims,
            dropout=bnn_dropout
        )
        self.bnn_trainer = BayesianNNTrainer(self.bnn_model, device)
        
        self.gb_model = GradientBoostingBayesian(
            n_estimators=gb_n_estimators,
            max_depth=gb_max_depth
        )
        
        self.is_fitted = False
        self.feature_names = None
        self.training_history = {}
    
    def fit(self, X_train, y_train, X_val, y_val,
            epochs: int = 100, batch_size: int = 32,
            lr: float = 0.001, patience: int = 15):
        """
        Train both component models.
        First trains BNN, then GB, then optimizes weights.
        """
        print("\n" + "="*60)
        print(f"  Training {self.MODEL_NAME}")
        print("="*60)
        
        self.feature_names = X_train.columns.tolist() if hasattr(X_train, 'columns') else None
        
        # 1. Train Bayesian Neural Network
        print("\n[1/3] Training Bayesian Neural Network...")
        bnn_history = self.bnn_trainer.train(
            X_train, y_train, X_val, y_val,
            epochs=epochs, batch_size=batch_size,
            lr=lr, patience=patience
        )
        self.training_history['bnn'] = bnn_history
        
        # 2. Train Gradient Boosting Bayesian
        print("\n[2/3] Training Gradient Boosting Bayesian...")
        self.gb_model.fit(X_train, y_train)
        
        # Evaluate GB on validation
        gb_metrics = self.gb_model.evaluate(X_val, y_val)
        print(f"  ✓ Validation AUC: {gb_metrics['roc_auc']:.4f}, F1: {gb_metrics['f1']:.4f}")
        self.training_history['gb'] = gb_metrics
        
        # 3. Optimize weights
        print("\n[3/3] Optimizing ensemble weights...")
        self._optimize_weights(X_val, y_val)
        
        self.is_fitted = True
        
        print("\n" + "="*60)
        print(f"  ✓ {self.MODEL_NAME} Training Complete")
        print(f"  Final weights: BNN={self.bnn_weight:.2f}, GB={self.gb_weight:.2f}")
        print("="*60)
        
        return self
    
    def _optimize_weights(self, X_val, y_val):
        """Optimize ensemble weights using validation set."""
        # Get predictions from both models
        bnn_pred, _ = self.bnn_trainer.predict(X_val, with_uncertainty=True)
        gb_pred = self.gb_model.predict_proba(X_val)[:, 1]
        
        y_val_np = y_val.values if hasattr(y_val, 'values') else y_val
        
        # Grid search for optimal weights
        best_auc = 0
        best_weight = 0.5
        
        for w in np.arange(0.1, 1.0, 0.1):
            combined = w * bnn_pred + (1 - w) * gb_pred
            auc = roc_auc_score(y_val_np, combined)
            
            if auc > best_auc:
                best_auc = auc
                best_weight = w
        
        self.bnn_weight = best_weight
        self.gb_weight = 1.0 - best_weight
        
        print(f"  ✓ Optimal weights: BNN={best_weight:.2f}, GB={1-best_weight:.2f}")
        print(f"  ✓ Best validation AUC: {best_auc:.4f}")
    
    def predict_proba(self, X):
        """Get probability predictions from hybrid model."""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # BNN predictions
        bnn_pred, bnn_uncertainty = self.bnn_trainer.predict(X, with_uncertainty=True)
        
        # GB predictions
        gb_pred = self.gb_model.predict_proba(X)[:, 1]
        
        # Weighted combination
        combined = self.bnn_weight * bnn_pred + self.gb_weight * gb_pred
        
        return combined, bnn_uncertainty
    
    def predict(self, X, threshold: float = 0.5):
        """Get class predictions."""
        proba, _ = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def predict_with_details(self, X):
        """
        Get detailed predictions including:
        - Combined probability
        - BNN probability and uncertainty
        - GB probability
        - Risk level
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        bnn_pred, bnn_uncertainty = self.bnn_trainer.predict(X, with_uncertainty=True)
        gb_pred = self.gb_model.predict_proba(X)[:, 1]
        combined = self.bnn_weight * bnn_pred + self.gb_weight * gb_pred
        
        # Calculate risk levels
        risk_levels = []
        for prob, unc in zip(combined, bnn_uncertainty):
            if prob >= 0.8 and unc < 0.1:
                risk_levels.append('Very Low')
            elif prob >= 0.6:
                risk_levels.append('Low')
            elif prob >= 0.4:
                risk_levels.append('Medium')
            elif prob >= 0.2:
                risk_levels.append('High')
            else:
                risk_levels.append('Very High')
        
        return {
            'probability': combined,
            'prediction': (combined >= 0.5).astype(int),
            'bnn_probability': bnn_pred,
            'bnn_uncertainty': bnn_uncertainty,
            'gb_probability': gb_pred,
            'risk_level': np.array(risk_levels)
        }
    
    def evaluate(self, X, y):
        """Evaluate hybrid model performance."""
        proba, uncertainty = self.predict_proba(X)
        preds = (proba >= 0.5).astype(int)
        
        y_np = y.values if hasattr(y, 'values') else y
        
        return {
            'roc_auc': roc_auc_score(y_np, proba),
            'f1': f1_score(y_np, preds),
            'accuracy': accuracy_score(y_np, preds),
            'mean_uncertainty': float(np.mean(uncertainty))
        }
    
    def get_config(self):
        """Return model configuration."""
        return {
            'model_name': self.MODEL_NAME,
            'version': self.VERSION,
            'input_dim': self.input_dim,
            'bnn_config': self.bnn_model.get_config(),
            'gb_config': self.gb_model.get_config(),
            'bnn_weight': self.bnn_weight,
            'gb_weight': self.gb_weight
        }
    
    def save(self, path: str):
        """Save hybrid model to disk."""
        model_data = {
            'bnn_state_dict': self.bnn_model.state_dict(),
            'bnn_config': self.bnn_model.get_config(),
            'bnn_history': self.bnn_trainer.history,
            'gb_model': self.gb_model.model,
            'gb_base_model': self.gb_model.base_model,
            'gb_config': self.gb_model.get_config(),
            'gb_feature_importance': self.gb_model.feature_importance,
            'hybrid_config': self.get_config(),
            'feature_names': self.feature_names,
            'training_history': self.training_history
        }
        joblib.dump(model_data, path)
        print(f"  ✓ Saved to {path}")
    
    @classmethod
    def load(cls, path: str, device: str = 'cpu'):
        """Load hybrid model from disk."""
        model_data = joblib.load(path)
        
        config = model_data['hybrid_config']
        bnn_config = model_data['bnn_config']
        
        instance = cls(
            input_dim=config['input_dim'],
            bnn_hidden_dims=bnn_config['hidden_dims'],
            bnn_dropout=bnn_config['dropout_rate'],
            bnn_weight=config['bnn_weight'],
            device=device
        )
        
        # Load BNN
        instance.bnn_model.load_state_dict(model_data['bnn_state_dict'])
        instance.bnn_trainer.history = model_data['bnn_history']
        
        # Load GB
        instance.gb_model.model = model_data['gb_model']
        instance.gb_model.base_model = model_data['gb_base_model']
        instance.gb_model.feature_importance = model_data['gb_feature_importance']
        instance.gb_model.is_fitted = True
        
        instance.feature_names = model_data['feature_names']
        instance.training_history = model_data['training_history']
        instance.is_fitted = True
        
        return instance
