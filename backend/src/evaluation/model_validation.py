"""
Model Validation Module
"""

from sklearn.model_selection import cross_val_score, StratifiedKFold
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelValidator:
    """Cross-validation and model validation"""
    
    def __init__(self, n_folds=5, random_state=42):
        self.n_folds = n_folds
        self.random_state = random_state
        self.cv_scores = None
        
    def cross_validate(self, model, X, y, scoring='roc_auc'):
        """Perform cross-validation"""
        logger.info(f"Performing {self.n_folds}-fold cross-validation...")
        
        cv = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)
        
        self.cv_scores = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        
        logger.info(f"CV Scores: {self.cv_scores}")
        logger.info(f"Mean CV Score: {self.cv_scores.mean():.4f} (+/- {self.cv_scores.std():.4f})")
        
        return self.cv_scores
    
    def get_cv_summary(self):
        """Get summary of cross-validation results"""
        if self.cv_scores is None:
            raise ValueError("Must run cross_validate first")
        
        return {
            'mean': self.cv_scores.mean(),
            'std': self.cv_scores.std(),
            'min': self.cv_scores.min(),
            'max': self.cv_scores.max(),
            'scores': self.cv_scores.tolist()
        }
