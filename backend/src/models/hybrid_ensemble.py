"""
Hybrid Ensemble Model
Combines TabNet and Bayesian Network predictions
"""

import pandas as pd
import numpy as np
from pathlib import Path
from pytorch_tabnet.tab_model import TabNetClassifier
import pickle
import json
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HybridEnsemble:
    """Ensemble model combining TabNet and Bayesian Network"""
    
    def __init__(self, data_path: str, tabnet_path: str, bn_path: str, output_path: str):
        self.data_path = Path(data_path)
        self.tabnet_path = Path(tabnet_path)
        self.bn_path = Path(bn_path)
        self.output_path = Path(output_path)
        
        self.tabnet_model = None
        self.bn_model = None
        self.meta_model = None
        self.weights = None
        
    def load_models(self):
        """Load trained TabNet and Bayesian Network models"""
        logger.info("Loading pre-trained models...")
        
        # Load TabNet
        self.tabnet_model = TabNetClassifier()
        self.tabnet_model.load_model(str(self.tabnet_path / 'tabnet_model.zip'))
        logger.info("TabNet model loaded")
        
        # Load Bayesian Network
        with open(self.bn_path / 'bayesian_network.pkl', 'rb') as f:
            self.bn_model = pickle.load(f)
        logger.info("Bayesian Network model loaded")
        
    def load_data(self):
        """Load validation and test data"""
        logger.info("Loading data...")
        
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        
        return val_df, test_df
    
    def get_tabnet_predictions(self, X):
        """Get predictions from TabNet"""
        predictions = self.tabnet_model.predict_proba(X.values)[:, 1]
        return predictions
    
    def get_bn_predictions(self, df):
        """Get predictions from Bayesian Network"""
        # Load BN parameters to get top features
        with open(self.bn_path / 'bn_parameters.json', 'r') as f:
            bn_params = json.load(f)
        
        top_features = bn_params['top_features']
        df_subset = df[top_features]
        
        # Simple prediction using BN (placeholder - requires proper inference)
        # In practice, you would use VariableElimination here
        predictions = np.random.rand(len(df)) * 0.3 + 0.35  # Placeholder
        
        return predictions
    
    def train_meta_model(self, val_df):
        """Train meta-model for ensemble"""
        logger.info("Training meta-model...")
        
        # Separate features and target
        X_val = val_df.drop('TARGET', axis=1)
        y_val = val_df['TARGET'].values
        
        # Get base model predictions
        tabnet_preds = self.get_tabnet_predictions(X_val)
        bn_preds = self.get_bn_predictions(val_df)
        
        # Stack predictions
        meta_features = np.column_stack([tabnet_preds, bn_preds])
        
        # Train logistic regression meta-model
        self.meta_model = LogisticRegression()
        self.meta_model.fit(meta_features, y_val)
        
        # Extract weights
        self.weights = {
            'tabnet': float(self.meta_model.coef_[0][0]),
            'bayesian': float(self.meta_model.coef_[0][1]),
            'intercept': float(self.meta_model.intercept_[0])
        }
        
        logger.info(f"Meta-model weights: TabNet={self.weights['tabnet']:.4f}, "
                   f"Bayesian={self.weights['bayesian']:.4f}")
        
        return self.meta_model
    
    def predict(self, df):
        """Make ensemble predictions"""
        X = df.drop('TARGET', axis=1) if 'TARGET' in df.columns else df
        
        # Get base model predictions
        tabnet_preds = self.get_tabnet_predictions(X)
        bn_preds = self.get_bn_predictions(df)
        
        # Stack predictions
        meta_features = np.column_stack([tabnet_preds, bn_preds])
        
        # Get meta-model predictions
        ensemble_proba = self.meta_model.predict_proba(meta_features)[:, 1]
        ensemble_preds = self.meta_model.predict(meta_features)
        
        return ensemble_preds, ensemble_proba
    
    def evaluate(self, test_df):
        """Evaluate ensemble model"""
        logger.info("Evaluating ensemble model...")
        
        y_test = test_df['TARGET'].values
        
        # Make predictions
        y_pred, y_proba = self.predict(test_df)
        
        # Calculate metrics
        auc_score = roc_auc_score(y_test, y_proba)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Ensemble Test AUC: {auc_score:.4f}")
        logger.info(f"Ensemble Test Accuracy: {accuracy:.4f}")
        
        # Classification report
        report = classification_report(y_test, y_pred)
        print("\nEnsemble Classification Report:")
        print(report)
        
        return {
            'auc': auc_score,
            'accuracy': accuracy,
            'report': report
        }
    
    def save_model(self):
        """Save ensemble model"""
        logger.info("Saving ensemble model...")
        
        # Save meta-model
        with open(self.output_path / 'hybrid_model.pkl', 'wb') as f:
            pickle.dump(self.meta_model, f)
        
        # Save weights
        with open(self.output_path / 'ensemble_weights.json', 'w') as f:
            json.dump(self.weights, f, indent=2)
        
        logger.info(f"Ensemble model saved to {self.output_path}")
    
    def train_pipeline(self):
        """Execute complete ensemble training pipeline"""
        # Load models
        self.load_models()
        
        # Load data
        val_df, test_df = self.load_data()
        
        # Train meta-model
        self.train_meta_model(val_df)
        
        # Evaluate
        metrics = self.evaluate(test_df)
        
        # Save model
        self.save_model()
        
        return metrics


def main():
    """Main execution function"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    ensemble = HybridEnsemble(
        data_path=str(project_root / 'data' / 'processed'),
        tabnet_path=str(project_root / 'models' / 'tabnet'),
        bn_path=str(project_root / 'models' / 'bayesian'),
        output_path=str(project_root / 'models' / 'hybrid')
    )
    
    metrics = ensemble.train_pipeline()
    
    print("\n" + "="*50)
    print("Hybrid Ensemble Training Complete!")
    print("="*50)
    print(f"Ensemble Test AUC: {metrics['auc']:.4f}")
    print(f"Ensemble Test Accuracy: {metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
