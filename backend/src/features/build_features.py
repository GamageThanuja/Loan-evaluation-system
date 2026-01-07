"""
Feature Engineering Module
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Build and engineer features for credit default prediction"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def create_aggregate_features(self, df):
        """Create aggregate features"""
        logger.info("Creating aggregate features...")
        
        # Ratios
        if 'AMT_CREDIT' in df.columns and 'AMT_INCOME_TOTAL' in df.columns:
            df['CREDIT_INCOME_RATIO'] = df['AMT_CREDIT'] / (df['AMT_INCOME_TOTAL'] + 1)
        
        if 'AMT_ANNUITY' in df.columns and 'AMT_INCOME_TOTAL' in df.columns:
            df['ANNUITY_INCOME_RATIO'] = df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] + 1)
        
        if 'AMT_GOODS_PRICE' in df.columns and 'AMT_CREDIT' in df.columns:
            df['GOODS_PRICE_CREDIT_RATIO'] = df['AMT_GOODS_PRICE'] / (df['AMT_CREDIT'] + 1)
        
        return df
    
    def create_temporal_features(self, df):
        """Create time-based features"""
        logger.info("Creating temporal features...")
        
        if 'DAYS_BIRTH' in df.columns:
            df['AGE_YEARS'] = -df['DAYS_BIRTH'] / 365
            df['AGE_GROUP'] = pd.cut(df['AGE_YEARS'], bins=[0, 25, 35, 45, 55, 100], 
                                     labels=['<25', '25-35', '35-45', '45-55', '55+'])
        
        if 'DAYS_EMPLOYED' in df.columns:
            df['EMPLOYMENT_YEARS'] = -df['DAYS_EMPLOYED'] / 365
            df['EMPLOYMENT_YEARS'] = df['EMPLOYMENT_YEARS'].clip(lower=0)
        
        return df
    
    def create_interaction_features(self, df):
        """Create interaction features"""
        logger.info("Creating interaction features...")
        
        # Income * Employment interaction
        if 'AMT_INCOME_TOTAL' in df.columns and 'EMPLOYMENT_YEARS' in df.columns:
            df['INCOME_EMPLOYMENT_INTERACTION'] = df['AMT_INCOME_TOTAL'] * df['EMPLOYMENT_YEARS']
        
        # Age * Credit interaction
        if 'AGE_YEARS' in df.columns and 'AMT_CREDIT' in df.columns:
            df['AGE_CREDIT_INTERACTION'] = df['AGE_YEARS'] * df['AMT_CREDIT']
        
        return df
    
    def engineer_all_features(self, df):
        """Execute all feature engineering"""
        df = self.create_aggregate_features(df)
        df = self.create_temporal_features(df)
        df = self.create_interaction_features(df)
        
        return df
