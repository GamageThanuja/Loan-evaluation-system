"""
Data Loading Utilities
Handles loading and splitting of preprocessed data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and split Home Credit data"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        
    def load_preprocessed_data(self, filename: str = 'home_credit_consolidated_preprocessed.csv'):
        """Load preprocessed data"""
        logger.info(f"Loading {filename}...")
        df = pd.read_csv(self.data_path / filename)
        return df
    
    def split_data(self, df, target_col: str = 'TARGET', test_size: float = 0.2, 
                   val_size: float = 0.1, random_state: int = 42):
        """Split data into train, validation, and test sets"""
        logger.info("Splitting data...")
        
        # Separate features and target
        X = df.drop(columns=[target_col, 'SK_ID_CURR'], errors='ignore')
        y = df[target_col]
        
        # First split: train+val and test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: train and val
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_ratio, random_state=random_state, stratify=y_temp
        )
        
        logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
    
    def save_splits(self, train_data, val_data, test_data, output_path: str):
        """Save data splits to parquet files"""
        output_path = Path(output_path)
        
        # Unpack data
        X_train, y_train = train_data
        X_val, y_val = val_data
        X_test, y_test = test_data
        
        # Combine features and target
        train_df = X_train.copy()
        train_df['TARGET'] = y_train.values
        
        val_df = X_val.copy()
        val_df['TARGET'] = y_val.values
        
        test_df = X_test.copy()
        test_df['TARGET'] = y_test.values
        
        # Save to parquet
        train_df.to_parquet(output_path / 'train_split.parquet', index=False)
        val_df.to_parquet(output_path / 'val_split.parquet', index=False)
        test_df.to_parquet(output_path / 'test_split.parquet', index=False)
        
        logger.info(f"Splits saved to {output_path}")


def main():
    """Main execution function"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    loader = DataLoader(data_path=str(project_root / 'data' / 'processed'))
    
    # Load data
    df = loader.load_preprocessed_data()
    
    # Split data
    train_data, val_data, test_data = loader.split_data(df)
    
    # Save splits
    loader.save_splits(train_data, val_data, test_data, output_path=str(project_root / 'data' / 'processed'))
    
    print("Data loading and splitting complete!")


if __name__ == "__main__":
    main()
