"""
TabNet Model Training Pipeline
Train TabNet model for credit default prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report
import torch
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TabNetTrainer:
    """Train and evaluate TabNet model"""
    
    def __init__(self, data_path: str, model_path: str):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.model = None
        self.feature_names = None
        
    def load_data(self):
        """Load train, validation, and test splits"""
        logger.info("Loading data splits...")
        
        train_df = pd.read_parquet(self.data_path / 'train_split.parquet')
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        
        # Separate features and target
        X_train = train_df.drop('TARGET', axis=1)
        y_train = train_df['TARGET'].values
        
        X_val = val_df.drop('TARGET', axis=1)
        y_val = val_df['TARGET'].values
        
        X_test = test_df.drop('TARGET', axis=1)
        y_test = test_df['TARGET'].values
        
        self.feature_names = X_train.columns.tolist()
        
        logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        return (X_train.values, y_train), (X_val.values, y_val), (X_test.values, y_test)
    
    def create_model(self):
        """Initialize TabNet model"""
        logger.info("Creating TabNet model...")
        
        self.model = TabNetClassifier(
            n_d=64,
            n_a=64,
            n_steps=5,
            gamma=1.5,
            n_independent=2,
            n_shared=2,
            lambda_sparse=1e-4,
            optimizer_fn=torch.optim.Adam,
            optimizer_params=dict(lr=2e-2),
            mask_type='entmax',
            scheduler_params={"step_size": 50, "gamma": 0.9},
            scheduler_fn=torch.optim.lr_scheduler.StepLR,
            verbose=1,
            seed=42
        )
        
        return self.model
    
    def train(self, train_data, val_data, max_epochs=200, patience=50):
        """Train TabNet model"""
        logger.info("Training TabNet model...")
        
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        # Train model
        self.model.fit(
            X_train=X_train,
            y_train=y_train,
            eval_set=[(X_val, y_val)],
            eval_name=['validation'],
            eval_metric=['auc', 'accuracy'],
            max_epochs=max_epochs,
            patience=patience,
            batch_size=1024,
            virtual_batch_size=128,
            num_workers=0,
            drop_last=False
        )
        
        # Save training history
        history = {
            'train_loss': self.model.history['loss'],
            'val_auc': self.model.history['validation_auc'],
            'val_accuracy': self.model.history['validation_accuracy']
        }
        
        with open(self.model_path / 'training_history.json', 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info("Training complete!")
        
        return history
    
    def evaluate(self, test_data):
        """Evaluate model on test set"""
        logger.info("Evaluating model...")
        
        X_test, y_test = test_data
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        auc_score = roc_auc_score(y_test, y_proba)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Test AUC: {auc_score:.4f}")
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        report = classification_report(y_test, y_pred)
        print("\nClassification Report:")
        print(report)
        
        return {
            'auc': auc_score,
            'accuracy': accuracy,
            'report': report
        }
    
    def save_model(self):
        """Save trained model"""
        logger.info("Saving model...")
        
        # Save model
        self.model.save_model(str(self.model_path / 'tabnet_model'))
        
        # Save feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        feature_importance.to_csv(
            self.model_path / 'feature_importance.csv', 
            index=False
        )
        
        logger.info(f"Model saved to {self.model_path}")
    
    def train_pipeline(self):
        """Execute complete training pipeline"""
        # Load data
        train_data, val_data, test_data = self.load_data()
        
        # Create model
        self.create_model()
        
        # Train model
        history = self.train(train_data, val_data)
        
        # Evaluate model
        metrics = self.evaluate(test_data)
        
        # Save model
        self.save_model()
        
        return metrics


def main():
    """Main execution function"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    trainer = TabNetTrainer(
        data_path=str(project_root / 'data' / 'processed'),
        model_path=str(project_root / 'models' / 'tabnet')
    )
    
    metrics = trainer.train_pipeline()
    
    print("\n" + "="*50)
    print("TabNet Training Complete!")
    print("="*50)
    print(f"Test AUC: {metrics['auc']:.4f}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
