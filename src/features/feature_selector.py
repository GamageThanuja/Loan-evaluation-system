"""
Feature Selection Module
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.ensemble import RandomForestClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureSelector:
    """Select most important features for modeling"""
    
    def __init__(self, method='mutual_info', k=50):
        self.method = method
        self.k = k
        self.selected_features = None
        
    def select_by_statistical_test(self, X, y):
        """Select features using statistical tests"""
        logger.info(f"Selecting top {self.k} features using {self.method}...")
        
        if self.method == 'f_classif':
            selector = SelectKBest(f_classif, k=self.k)
        elif self.method == 'mutual_info':
            selector = SelectKBest(mutual_info_classif, k=self.k)
        else:
            raise ValueError(f"Unknown method: {self.method}")
        
        selector.fit(X, y)
        self.selected_features = X.columns[selector.get_support()].tolist()
        
        logger.info(f"Selected {len(self.selected_features)} features")
        
        return self.selected_features
    
    def select_by_importance(self, X, y, threshold=0.01):
        """Select features using Random Forest importance"""
        logger.info("Selecting features using Random Forest importance...")
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Get feature importances
        importances = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Select features above threshold
        self.selected_features = importances[importances['importance'] > threshold]['feature'].tolist()
        
        logger.info(f"Selected {len(self.selected_features)} features with importance > {threshold}")
        
        return self.selected_features, importances
