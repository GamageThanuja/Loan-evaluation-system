#!/usr/bin/env python3
"""
Data Preprocessing Module
=========================
Handles all data preprocessing for the loan approval prediction system.
- Loads raw data
- Cleans and preprocesses
- Engineers features
- Saves processed data
"""

import os
import json
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

warnings.filterwarnings('ignore')

# Constants
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


class DataPreprocessor:
    """Handles all data preprocessing operations."""
    
    def __init__(self, raw_data_path: str, processed_data_path: str):
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path(processed_data_path)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.preprocessing_info = {}
        
    def load_data(self) -> pd.DataFrame:
        """Load raw data from CSV."""
        print("\n" + "="*60)
        print("STEP 1: LOADING RAW DATA")
        print("="*60)
        
        df = pd.read_csv(self.raw_data_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        print(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)}")
        
        self.preprocessing_info['initial_rows'] = len(df)
        self.preprocessing_info['initial_columns'] = len(df.columns)
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data: remove duplicates, handle missing values, outliers."""
        print("\n" + "="*60)
        print("STEP 2: DATA CLEANING")
        print("="*60)
        
        initial_rows = len(df)
        
        # 2.1 Remove duplicates
        print("\n[2.1] Removing duplicates...")
        df = df.drop_duplicates()
        duplicates_removed = initial_rows - len(df)
        print(f"  ✓ Removed {duplicates_removed:,} duplicates")
        
        # 2.2 Handle missing values
        print("\n[2.2] Checking missing values...")
        missing = df.isnull().sum()
        total_missing = missing.sum()
        
        if total_missing > 0:
            for col in missing[missing > 0].index:
                print(f"  - {col}: {missing[col]} missing ({missing[col]/len(df)*100:.2f}%)")
            
            # For numeric columns, fill with median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].median())
            
            # For categorical, fill with mode
            cat_cols = df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if df[col].isnull().any():
                    df[col] = df[col].fillna(df[col].mode().iloc[0])
            
            print(f"  ✓ Imputed {total_missing} missing values")
        else:
            print("  ✓ No missing values found")
        
        # 2.3 Handle outliers (IQR method - cap instead of remove)
        print("\n[2.3] Handling outliers (IQR capping)...")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = ['loan_id', 'loan_status']
        numeric_cols = [c for c in numeric_cols if c not in exclude_cols]
        
        outliers_capped = 0
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if outliers > 0:
                df[col] = df[col].clip(lower=lower, upper=upper)
                outliers_capped += outliers
        
        print(f"  ✓ Capped {outliers_capped} outlier values")
        
        self.preprocessing_info['duplicates_removed'] = duplicates_removed
        self.preprocessing_info['missing_imputed'] = total_missing
        self.preprocessing_info['outliers_capped'] = outliers_capped
        self.preprocessing_info['rows_after_cleaning'] = len(df)
        
        print(f"\n  Summary: {initial_rows:,} → {len(df):,} rows")
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create domain-specific engineered features."""
        print("\n" + "="*60)
        print("STEP 3: FEATURE ENGINEERING")
        print("="*60)
        
        initial_features = len(df.columns)
        new_features = 0
        
        # 3.1 Loan-to-income ratio
        if all(c in df.columns for c in ['loan_amount', 'income_annum']):
            df['loan_to_income_ratio'] = df['loan_amount'] / (df['income_annum'] + 1)
            print("  ✓ Created: loan_to_income_ratio")
            new_features += 1
        
        # 3.2 Total assets
        asset_cols = ['residential_assets_value', 'commercial_assets_value',
                      'luxury_assets_value', 'bank_asset_value']
        if all(c in df.columns for c in asset_cols):
            df['total_assets'] = df[asset_cols].sum(axis=1)
            df['assets_to_loan_ratio'] = df['total_assets'] / (df['loan_amount'] + 1)
            df['assets_to_income_ratio'] = df['total_assets'] / (df['income_annum'] + 1)
            print("  ✓ Created: total_assets, assets_to_loan_ratio, assets_to_income_ratio")
            new_features += 3
        
        # 3.3 Debt-to-asset ratio
        if all(c in df.columns for c in ['loan_amount', 'total_assets']):
            df['debt_to_asset_ratio'] = df['loan_amount'] / (df['total_assets'] + 1)
            print("  ✓ Created: debt_to_asset_ratio")
            new_features += 1
        
        # 3.4 Monthly payment estimate
        if all(c in df.columns for c in ['loan_amount', 'loan_term']):
            df['monthly_payment'] = df['loan_amount'] / (df['loan_term'] * 12 + 1)
            df['payment_to_income_ratio'] = df['monthly_payment'] / ((df['income_annum'] / 12) + 1)
            print("  ✓ Created: monthly_payment, payment_to_income_ratio")
            new_features += 2
        
        # 3.5 CIBIL score categories
        if 'cibil_score' in df.columns:
            df['cibil_excellent'] = (df['cibil_score'] >= 750).astype(int)
            df['cibil_good'] = ((df['cibil_score'] >= 650) & (df['cibil_score'] < 750)).astype(int)
            df['cibil_fair'] = ((df['cibil_score'] >= 550) & (df['cibil_score'] < 650)).astype(int)
            df['cibil_poor'] = (df['cibil_score'] < 550).astype(int)
            print("  ✓ Created: cibil_excellent, cibil_good, cibil_fair, cibil_poor")
            new_features += 4
        
        self.preprocessing_info['new_features'] = new_features
        print(f"\n  Total: {initial_features} → {len(df.columns)} features (+{new_features})")
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables."""
        print("\n" + "="*60)
        print("STEP 4: ENCODING CATEGORICAL VARIABLES")
        print("="*60)
        
        # Target encoding
        if 'loan_status' in df.columns:
            # Clean whitespace
            df['loan_status'] = df['loan_status'].str.strip()
            df['loan_status'] = df['loan_status'].map({'Approved': 1, 'Rejected': 0})
            print("  ✓ Encoded loan_status: Approved=1, Rejected=0")
        
        # Binary encoding for education
        if 'education' in df.columns:
            df['education'] = df['education'].str.strip()
            df['education'] = df['education'].map({'Graduate': 1, 'Not Graduate': 0})
            print("  ✓ Encoded education: Graduate=1, Not Graduate=0")
        
        # Binary encoding for self_employed
        if 'self_employed' in df.columns:
            df['self_employed'] = df['self_employed'].str.strip()
            df['self_employed'] = df['self_employed'].map({'Yes': 1, 'No': 0})
            print("  ✓ Encoded self_employed: Yes=1, No=0")
        
        # Handle any remaining NaN from encoding
        df = df.fillna(0)
        
        return df
    
    def prepare_splits(self, df: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.1):
        """Split data into train, validation, and test sets."""
        print("\n" + "="*60)
        print("STEP 5: PREPARING DATA SPLITS")
        print("="*60)
        
        # Separate features and target
        exclude_cols = ['loan_status', 'loan_id']
        feature_cols = [c for c in df.columns if c not in exclude_cols]
        
        X = df[feature_cols]
        y = df['loan_status']
        
        self.feature_names = feature_cols
        
        print(f"\n[5.1] Features: {len(feature_cols)}")
        print(f"  {feature_cols}")
        
        # Split
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
        )
        
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=RANDOM_STATE, stratify=y_temp
        )
        
        print(f"\n[5.2] Data splits:")
        print(f"  - Train: {len(X_train):,} ({len(X_train)/len(df)*100:.1f}%)")
        print(f"  - Val:   {len(X_val):,} ({len(X_val)/len(df)*100:.1f}%)")
        print(f"  - Test:  {len(X_test):,} ({len(X_test)/len(df)*100:.1f}%)")
        
        print(f"\n[5.3] Class distribution:")
        print(f"  - Train: Approved={y_train.sum()} ({y_train.mean()*100:.1f}%)")
        print(f"  - Val:   Approved={y_val.sum()} ({y_val.mean()*100:.1f}%)")
        print(f"  - Test:  Approved={y_test.sum()} ({y_test.mean()*100:.1f}%)")
        
        self.preprocessing_info['train_size'] = len(X_train)
        self.preprocessing_info['val_size'] = len(X_val)
        self.preprocessing_info['test_size'] = len(X_test)
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def normalize_data(self, X_train, X_val, X_test):
        """Normalize features using StandardScaler."""
        print("\n" + "="*60)
        print("STEP 6: NORMALIZING DATA")
        print("="*60)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrames
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=self.feature_names)
        X_val_scaled = pd.DataFrame(X_val_scaled, columns=self.feature_names)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=self.feature_names)
        
        print("  ✓ Applied StandardScaler normalization")
        
        return X_train_scaled, X_val_scaled, X_test_scaled
    
    def save_processed_data(self, X_train, X_val, X_test, y_train, y_val, y_test):
        """Save processed data to disk."""
        print("\n" + "="*60)
        print("STEP 7: SAVING PROCESSED DATA")
        print("="*60)
        
        # Create directory
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        # Save splits
        X_train.to_csv(self.processed_data_path / 'X_train.csv', index=False)
        X_val.to_csv(self.processed_data_path / 'X_val.csv', index=False)
        X_test.to_csv(self.processed_data_path / 'X_test.csv', index=False)
        
        y_train.to_csv(self.processed_data_path / 'y_train.csv', index=False, header=['loan_status'])
        y_val.to_csv(self.processed_data_path / 'y_val.csv', index=False, header=['loan_status'])
        y_test.to_csv(self.processed_data_path / 'y_test.csv', index=False, header=['loan_status'])
        
        print(f"  ✓ Saved X_train.csv, X_val.csv, X_test.csv")
        print(f"  ✓ Saved y_train.csv, y_val.csv, y_test.csv")
        
        # Save scaler
        import joblib
        joblib.dump(self.scaler, self.processed_data_path / 'scaler.joblib')
        print(f"  ✓ Saved scaler.joblib")
        
        # Save feature names
        with open(self.processed_data_path / 'feature_names.json', 'w') as f:
            json.dump(self.feature_names, f, indent=2)
        print(f"  ✓ Saved feature_names.json")
        
        # Save preprocessing info
        self.preprocessing_info['timestamp'] = datetime.now().isoformat()
        self.preprocessing_info['feature_count'] = len(self.feature_names)
        
        # Convert numpy types to Python types for JSON serialization
        info_json = {}
        for key, value in self.preprocessing_info.items():
            if hasattr(value, 'item'):  # numpy scalar
                info_json[key] = value.item()
            else:
                info_json[key] = value
        
        with open(self.processed_data_path / 'preprocessing_info.json', 'w') as f:
            json.dump(info_json, f, indent=2)
        print(f"  ✓ Saved preprocessing_info.json")
        
        print(f"\n  All files saved to: {self.processed_data_path}")
    
    def run(self):
        """Execute full preprocessing pipeline."""
        print("\n" + "="*60)
        print("  DATA PREPROCESSING PIPELINE")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("="*60)
        
        # Execute pipeline
        df = self.load_data()
        df = self.clean_data(df)
        df = self.engineer_features(df)
        df = self.encode_categorical(df)
        
        X_train, X_val, X_test, y_train, y_val, y_test = self.prepare_splits(df)
        X_train, X_val, X_test = self.normalize_data(X_train, X_val, X_test)
        
        self.save_processed_data(X_train, X_val, X_test, y_train, y_val, y_test)
        
        print("\n" + "="*60)
        print("  PREPROCESSING COMPLETE")
        print("="*60)
        
        return X_train, X_val, X_test, y_train, y_val, y_test


def main():
    """Run preprocessing as standalone script."""
    base_path = Path(__file__).parent.parent
    raw_path = base_path / 'data' / 'raw' / 'loan_approval_dataset.csv'
    processed_path = base_path / 'data' / 'processed'
    
    preprocessor = DataPreprocessor(str(raw_path), str(processed_path))
    preprocessor.run()


if __name__ == "__main__":
    main()
