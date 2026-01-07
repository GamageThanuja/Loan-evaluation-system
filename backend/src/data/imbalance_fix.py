"""
Class Imbalance Handling
Multiple strategies to address the 92% vs 8% class imbalance problem
"""

import pandas as pd
import numpy as np
from pathlib import Path
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler, NearMiss
from imblearn.combine import SMOTEENN, SMOTETomek
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    precision_recall_curve, roc_auc_score
)
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImbalanceHandler:
    """Handle class imbalance with multiple strategies"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        
    def load_data(self):
        """Load train, validation, and test splits"""
        logger.info("Loading data splits...")
        
        train_df = pd.read_parquet(self.data_path / 'train_split.parquet')
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        
        # Separate features and target
        self.X_train = train_df.drop('TARGET', axis=1).values
        self.y_train = train_df['TARGET'].values
        
        self.X_val = val_df.drop('TARGET', axis=1).values
        self.y_val = val_df['TARGET'].values
        
        self.X_test = test_df.drop('TARGET', axis=1).values
        self.y_test = test_df['TARGET'].values
        
        # Print class distribution
        unique, counts = np.unique(self.y_train, return_counts=True)
        logger.info("Original class distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(self.y_train)*100:.2f}%)")
        
        return self.X_train, self.y_train
    
    def method_1_smote(self, sampling_strategy='auto'):
        """Method 1: Standard SMOTE oversampling"""
        logger.info("\n[Method 1] Applying SMOTE...")
        
        smote = SMOTE(sampling_strategy=sampling_strategy, random_state=42, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("SMOTE resampled distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def method_2_borderline_smote(self, sampling_strategy=0.5):
        """Method 2: Borderline SMOTE (focuses on borderline cases)"""
        logger.info("\n[Method 2] Applying Borderline SMOTE...")
        
        borderline_smote = BorderlineSMOTE(
            sampling_strategy=sampling_strategy,
            random_state=42,
            k_neighbors=5,
            kind='borderline-1'
        )
        X_resampled, y_resampled = borderline_smote.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("Borderline SMOTE distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def method_3_adasyn(self, sampling_strategy='auto'):
        """Method 3: ADASYN (Adaptive Synthetic Sampling)"""
        logger.info("\n[Method 3] Applying ADASYN...")
        
        adasyn = ADASYN(sampling_strategy=sampling_strategy, random_state=42, n_neighbors=5)
        X_resampled, y_resampled = adasyn.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("ADASYN distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def method_4_smoteenn(self, sampling_strategy=0.3):
        """Method 4: SMOTEENN (SMOTE + ENN cleaning) - RECOMMENDED"""
        logger.info("\n[Method 4] Applying SMOTEENN (SMOTE + ENN)...")
        
        smote_enn = SMOTEENN(sampling_strategy=sampling_strategy, random_state=42)
        X_resampled, y_resampled = smote_enn.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("SMOTEENN distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def method_5_smotetomek(self, sampling_strategy=0.5):
        """Method 5: SMOTETomek (SMOTE + Tomek links removal)"""
        logger.info("\n[Method 5] Applying SMOTETomek...")
        
        smote_tomek = SMOTETomek(sampling_strategy=sampling_strategy, random_state=42)
        X_resampled, y_resampled = smote_tomek.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("SMOTETomek distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def method_6_undersampling(self, sampling_strategy='auto'):
        """Method 6: Random Undersampling"""
        logger.info("\n[Method 6] Applying Random Undersampling...")
        
        rus = RandomUnderSampler(sampling_strategy=sampling_strategy, random_state=42)
        X_resampled, y_resampled = rus.fit_resample(self.X_train, self.y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("Undersampled distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def compute_class_weights(self):
        """Compute class weights for cost-sensitive learning"""
        logger.info("\n[Method 7] Computing class weights...")
        
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=np.unique(self.y_train),
            y=self.y_train
        )
        
        weight_dict = dict(zip(np.unique(self.y_train), class_weights))
        logger.info(f"Computed class weights: {weight_dict}")
        
        return class_weights
    
    def optimize_threshold(self, y_true, y_proba):
        """Find optimal classification threshold using precision-recall curve"""
        logger.info("\n[Method 8] Optimizing classification threshold...")
        
        # Compute precision-recall curve
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        
        # Find threshold that maximizes F1 score
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        optimal_idx = np.argmax(f1_scores)
        optimal_threshold = thresholds[optimal_idx]
        
        logger.info(f"Default threshold (0.5):")
        preds_default = (y_proba > 0.5).astype(int)
        logger.info(classification_report(y_true, preds_default, target_names=['No Default', 'Default']))
        
        logger.info(f"\nOptimal threshold ({optimal_threshold:.3f}):")
        preds_optimal = (y_proba > optimal_threshold).astype(int)
        logger.info(classification_report(y_true, preds_optimal, target_names=['No Default', 'Default']))
        
        return optimal_threshold
    
    def save_resampled_data(self, X_resampled, y_resampled, output_name='train_balanced.parquet'):
        """Save resampled data"""
        output_path = self.data_path / output_name
        
        # Convert to DataFrame
        df_resampled = pd.DataFrame(X_resampled)
        df_resampled['TARGET'] = y_resampled
        
        # Save
        df_resampled.to_parquet(output_path, index=False)
        logger.info(f"\nResampled data saved to: {output_path}")
        logger.info(f"Shape: {df_resampled.shape}")


def main():
    """Main execution function"""
    from src.config import Config
    
    # Initialize handler
    handler = ImbalanceHandler(data_path=str(Config.DATA_PROCESSED))
    
    # Load data
    handler.load_data()
    
    # Try different methods
    logger.info("\n" + "="*80)
    logger.info("TESTING DIFFERENT IMBALANCE HANDLING METHODS")
    logger.info("="*80)
    
    # Method 1: SMOTE
    X_smote, y_smote = handler.method_1_smote(sampling_strategy=0.5)
    
    # Method 2: Borderline SMOTE
    X_borderline, y_borderline = handler.method_2_borderline_smote(sampling_strategy=0.3)
    
    # Method 3: ADASYN
    # X_adasyn, y_adasyn = handler.method_3_adasyn(sampling_strategy=0.5)
    
    # Method 4: SMOTEENN (RECOMMENDED)
    X_smoteenn, y_smoteenn = handler.method_4_smoteenn(sampling_strategy=0.3)
    handler.save_resampled_data(X_smoteenn, y_smoteenn, 'train_balanced_smoteenn.parquet')
    
    # Method 5: SMOTETomek
    X_smotetomek, y_smotetomek = handler.method_5_smotetomek(sampling_strategy=0.4)
    
    # Method 7: Class weights
    class_weights = handler.compute_class_weights()
    
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)
    logger.info("1. Use SMOTEENN for balanced training data")
    logger.info("2. Apply class_weights in model training: [1.0, 8.0] or [1.0, 10.0]")
    logger.info("3. Use lower threshold (0.15-0.25) for higher recall")
    logger.info("4. Consider ensemble with cost-sensitive learning")
    logger.info("="*80)


if __name__ == "__main__":
    main()
