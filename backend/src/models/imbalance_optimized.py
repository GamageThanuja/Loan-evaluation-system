"""
Optimized Training Pipeline with Imbalance Handling
Best combination approach for maximizing recall on minority class
"""

import pandas as pd
import numpy as np
from pathlib import Path
from pytorch_tabnet.tab_model import TabNetClassifier
import torch
from imblearn.combine import SMOTEENN
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    precision_recall_curve, roc_auc_score, roc_curve,
    precision_score, recall_score, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImbalanceOptimizedTrainer:
    """Train TabNet with optimal imbalance handling strategy"""
    
    def __init__(self, data_path: str, model_path: str, use_smoteenn: bool = True):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.use_smoteenn = use_smoteenn
        self.model = None
        self.optimal_threshold = 0.5
        
    def load_data(self):
        """Load and prepare data"""
        logger.info("Loading data...")
        
        train_df = pd.read_parquet(self.data_path / 'train_split.parquet')
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        
        # Separate features and target
        X_train = train_df.drop('TARGET', axis=1).values
        y_train = train_df['TARGET'].values
        
        X_val = val_df.drop('TARGET', axis=1).values
        y_val = val_df['TARGET'].values
        
        X_test = test_df.drop('TARGET', axis=1).values
        y_test = test_df['TARGET'].values
        
        feature_names = train_df.drop('TARGET', axis=1).columns.tolist()
        
        # Log original distribution
        unique, counts = np.unique(y_train, return_counts=True)
        logger.info("Original training distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_train)*100:.2f}%)")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test), feature_names
    
    def apply_smoteenn(self, X_train, y_train):
        """Apply SMOTEENN for balanced training"""
        logger.info("\nApplying SMOTEENN resampling...")
        
        smote_enn = SMOTEENN(
            sampling_strategy=0.3,  # Conservative ratio
            random_state=42
        )
        
        X_resampled, y_resampled = smote_enn.fit_resample(X_train, y_train)
        
        unique, counts = np.unique(y_resampled, return_counts=True)
        logger.info("Resampled distribution:")
        for label, count in zip(unique, counts):
            logger.info(f"  Class {label}: {count} ({count/len(y_resampled)*100:.2f}%)")
        
        return X_resampled, y_resampled
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Train TabNet with class weights"""
        logger.info("\nTraining TabNet with class weights...")
        
        # Compute class weights (boost minority class)
        unique, counts = np.unique(y_train, return_counts=True)
        majority_count = counts[0]
        minority_count = counts[1]
        weight_ratio = majority_count / minority_count
        
        # Use aggressive weighting for minority class
        class_weights = [1.0, min(weight_ratio * 1.5, 10.0)]  # Cap at 10x
        logger.info(f"Using class weights: {class_weights}")
        
        # Create TabNet model
        self.model = TabNetClassifier(
            n_d=64,
            n_a=64,
            n_steps=7,
            gamma=1.5,
            lambda_sparse=1e-4,
            optimizer_fn=torch.optim.Adam,
            optimizer_params=dict(lr=0.02),
            scheduler_params={"step_size": 10, "gamma": 0.9},
            scheduler_fn=torch.optim.lr_scheduler.StepLR,
            mask_type="entmax",
            verbose=1,
            seed=42
        )
        
        # Compute sample weights
        sample_weights = np.ones(len(y_train))
        sample_weights[y_train == 1] = class_weights[1]
        
        # Train model
        self.model.fit(
            X_train=X_train,
            y_train=y_train,
            eval_set=[(X_val, y_val)],
            eval_metric=['auc', 'accuracy'],
            max_epochs=100,
            patience=20,
            batch_size=1024,
            virtual_batch_size=256,
            num_workers=0,
            weights=sample_weights,
            drop_last=False
        )
        
        logger.info("Training complete!")
        
        return self.model
    
    def find_optimal_threshold(self, X_val, y_val):
        """Find optimal classification threshold"""
        logger.info("\nFinding optimal threshold...")
        
        y_proba = self.model.predict_proba(X_val)[:, 1]
        
        # Compute precision-recall curve
        precision, recall, thresholds = precision_recall_curve(y_val, y_proba)
        
        # Strategy 1: Maximize F1 score
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        f1_optimal_idx = np.argmax(f1_scores)
        f1_optimal_threshold = thresholds[f1_optimal_idx]
        
        # Strategy 2: Target minimum recall (e.g., 0.7)
        target_recall = 0.70
        recall_indices = np.where(recall >= target_recall)[0]
        if len(recall_indices) > 0:
            # Among thresholds achieving target recall, pick one with best precision
            best_prec_idx = recall_indices[np.argmax(precision[recall_indices])]
            recall_optimal_threshold = thresholds[best_prec_idx]
        else:
            recall_optimal_threshold = f1_optimal_threshold
        
        # Strategy 3: Balance precision and recall (F-beta with beta=2, favor recall)
        fbeta = 5 * (precision * recall) / (4 * precision + recall + 1e-10)
        fbeta_optimal_idx = np.argmax(fbeta)
        fbeta_optimal_threshold = thresholds[fbeta_optimal_idx]
        
        logger.info("\nThreshold candidates:")
        logger.info(f"  F1-optimal: {f1_optimal_threshold:.3f}")
        logger.info(f"  Recall-focused (70%): {recall_optimal_threshold:.3f}")
        logger.info(f"  F2-optimal (favor recall): {fbeta_optimal_threshold:.3f}")
        
        # Use F2-optimal (favors recall)
        self.optimal_threshold = fbeta_optimal_threshold
        logger.info(f"\nSelected threshold: {self.optimal_threshold:.3f}")
        
        return self.optimal_threshold
    
    def evaluate(self, X_test, y_test):
        """Evaluate model with optimal threshold"""
        logger.info("\n" + "="*80)
        logger.info("EVALUATION RESULTS")
        logger.info("="*80)
        
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Evaluate with default threshold
        logger.info("\nResults with DEFAULT threshold (0.5):")
        y_pred_default = (y_proba > 0.5).astype(int)
        logger.info(classification_report(y_test, y_pred_default, 
                                         target_names=['No Default', 'Default'],
                                         digits=4))
        
        # Evaluate with optimal threshold
        logger.info(f"\nResults with OPTIMAL threshold ({self.optimal_threshold:.3f}):")
        y_pred_optimal = (y_proba > self.optimal_threshold).astype(int)
        logger.info(classification_report(y_test, y_pred_optimal,
                                         target_names=['No Default', 'Default'],
                                         digits=4))
        
        # Compute metrics
        auc = roc_auc_score(y_test, y_proba)
        
        # Save metrics
        metrics = {
            'auc': float(auc),
            'optimal_threshold': float(self.optimal_threshold),
            'default_threshold': {
                'precision': float(precision_score(y_test, y_pred_default)),
                'recall': float(recall_score(y_test, y_pred_default)),
                'f1': float(f1_score(y_test, y_pred_default))
            },
            'optimal_threshold_metrics': {
                'precision': float(precision_score(y_test, y_pred_optimal)),
                'recall': float(recall_score(y_test, y_pred_optimal)),
                'f1': float(f1_score(y_test, y_pred_optimal))
            }
        }
        
        # Confusion matrices
        logger.info("\nConfusion Matrix (Optimal Threshold):")
        cm = confusion_matrix(y_test, y_pred_optimal)
        logger.info(f"\n{cm}")
        logger.info(f"TN: {cm[0,0]}, FP: {cm[0,1]}")
        logger.info(f"FN: {cm[1,0]}, TP: {cm[1,1]}")
        
        return metrics
    
    def save_model(self):
        """Save trained model"""
        output_path = self.model_path / 'tabnet_imbalance_optimized.zip'
        self.model.save_model(str(output_path))
        logger.info(f"\nModel saved to: {output_path}")
        
        # Save threshold
        threshold_path = self.model_path / 'optimal_threshold.json'
        with open(threshold_path, 'w') as f:
            json.dump({'optimal_threshold': float(self.optimal_threshold)}, f, indent=2)
        logger.info(f"Optimal threshold saved to: {threshold_path}")
    
    def plot_precision_recall_curve(self, X_test, y_test):
        """Plot precision-recall curve"""
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
        
        plt.figure(figsize=(10, 6))
        plt.plot(recall, precision, linewidth=2)
        plt.axvline(x=0.7, color='r', linestyle='--', label='Target Recall (70%)')
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title('Precision-Recall Curve', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        output_path = self.model_path / 'precision_recall_curve.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Precision-Recall curve saved to: {output_path}")
        plt.close()


def main():
    """Main training pipeline"""
    
    logger.info("="*80)
    logger.info("IMBALANCE-OPTIMIZED TRAINING PIPELINE")
    logger.info("="*80)
    from src.config import Config
    
    # Initialize trainer
    trainer = ImbalanceOptimizedTrainer(
        data_path=str(Config.DATA_PROCESSED),
        model_path=str(Config.TABNET_DIR),
        use_smoteenn=True
    )
    
    # Load data
    (X_train, y_train), (X_val, y_val), (X_test, y_test), feature_names = trainer.load_data()
    
    # Apply SMOTEENN
    if trainer.use_smoteenn:
        X_train, y_train = trainer.apply_smoteenn(X_train, y_train)
    
    # Train model
    model = trainer.train_model(X_train, y_train, X_val, y_val)
    
    # Find optimal threshold
    trainer.find_optimal_threshold(X_val, y_val)
    
    # Evaluate
    metrics = trainer.evaluate(X_test, y_test)
    
    # Save model
    trainer.save_model()
    
    # Plot curves
    trainer.plot_precision_recall_curve(X_test, y_test)
    
    logger.info("\n" + "="*80)
    logger.info("✅ TRAINING COMPLETE!")
    logger.info("="*80)
    logger.info(f"Final AUC: {metrics['auc']:.4f}")
    logger.info(f"Optimal Recall: {metrics['optimal_threshold_metrics']['recall']:.4f}")
    logger.info(f"Optimal Precision: {metrics['optimal_threshold_metrics']['precision']:.4f}")
    logger.info(f"Optimal F1: {metrics['optimal_threshold_metrics']['f1']:.4f}")


if __name__ == "__main__":
    main()
