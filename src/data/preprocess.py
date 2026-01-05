"""
Preprocessing Pipeline for Home Credit Default Risk
Handles missing values, encoding, feature engineering
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HomeCreditPreprocessor:
    """Preprocess Home Credit consolidated data"""
    
    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load consolidated data"""
        logger.info("Loading consolidated data...")
        return pd.read_csv(self.input_path / 'home_credit_consolidated.csv')
    
    def handle_missing_values(self, df):
        """Handle missing values"""
        logger.info("Handling missing values...")
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Impute numeric columns with median
        num_imputer = SimpleImputer(strategy='median')
        df[numeric_cols] = num_imputer.fit_transform(df[numeric_cols])
        
        # Impute categorical columns with mode
        cat_imputer = SimpleImputer(strategy='most_frequent')
        df[categorical_cols] = cat_imputer.fit_transform(df[categorical_cols])
        
        return df
    
    def encode_categorical(self, df):
        """Encode categorical variables"""
        logger.info("Encoding categorical variables...")
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        return df
    
    def engineer_features(self, df):
        """Create engineered features"""
        logger.info("Engineering features...")
        
        # Credit to income ratio
        if 'AMT_CREDIT' in df.columns and 'AMT_INCOME_TOTAL' in df.columns:
            df['CREDIT_INCOME_RATIO'] = df['AMT_CREDIT'] / (df['AMT_INCOME_TOTAL'] + 1)
        
        # Annuity to income ratio
        if 'AMT_ANNUITY' in df.columns and 'AMT_INCOME_TOTAL' in df.columns:
            df['ANNUITY_INCOME_RATIO'] = df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] + 1)
        
        # Employment to age ratio
        if 'DAYS_EMPLOYED' in df.columns and 'DAYS_BIRTH' in df.columns:
            df['EMPLOYMENT_AGE_RATIO'] = df['DAYS_EMPLOYED'] / (df['DAYS_BIRTH'] + 1)
        
        # Age in years
        if 'DAYS_BIRTH' in df.columns:
            df['AGE_YEARS'] = -df['DAYS_BIRTH'] / 365
        
        # Employment in years
        if 'DAYS_EMPLOYED' in df.columns:
            df['EMPLOYMENT_YEARS'] = -df['DAYS_EMPLOYED'] / 365
        
        return df
    
    def scale_features(self, df):
        """Scale numerical features"""
        logger.info("Scaling features...")
        
        # Exclude target column if present
        exclude_cols = ['TARGET', 'SK_ID_CURR']
        numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col not in exclude_cols]
        
        df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        
        return df
    
    def preprocess(self):
        """Execute complete preprocessing pipeline"""
        logger.info("Starting preprocessing pipeline...")
        
        # Load data
        df = self.load_data()
        logger.info(f"Initial shape: {df.shape}")
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Engineer features
        df = self.engineer_features(df)
        logger.info(f"After feature engineering: {df.shape}")
        
        # Encode categorical variables
        df = self.encode_categorical(df)
        
        # Scale features
        df = self.scale_features(df)
        
        # Save preprocessed data
        output_file = self.output_path / 'home_credit_consolidated_preprocessed.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Preprocessed data saved to {output_file}")
        
        return df


def main():
    """Main execution function"""
    from src.config import Config
    
    preprocessor = HomeCreditPreprocessor(
        input_path=str(Config.DATA_PROCESSED),
        output_path=str(Config.DATA_PROCESSED)
    )
    
    df_preprocessed = preprocessor.preprocess()
    print(f"\nPreprocessing complete! Final dataset shape: {df_preprocessed.shape}")
    print(f"Columns: {df_preprocessed.shape[1]}")
    print(f"Rows: {df_preprocessed.shape[0]}")


if __name__ == "__main__":
    main()
