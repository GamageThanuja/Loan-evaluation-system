"""
Bayesian Network Model
Learn probabilistic graphical model for credit default prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.estimators import HillClimbSearch, BIC
from pgmpy.inference import VariableElimination
from sklearn.metrics import roc_auc_score, accuracy_score
import pickle
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BayesianNetworkModel:
    """Bayesian Network for credit default prediction"""
    
    def __init__(self, data_path: str, model_path: str):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.model = None
        self.inference = None
        
    def load_data(self):
        """Load and discretize data for Bayesian Network"""
        logger.info("Loading data...")
        
        train_df = pd.read_parquet(self.data_path / 'train_split.parquet')
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        
        # Combine train and val for structure learning
        train_full = pd.concat([train_df, val_df], axis=0).reset_index(drop=True)
        
        return train_full, test_df
    
    def discretize_features(self, df, n_bins=3):
        """Discretize continuous features for Bayesian Network"""
        logger.info("Discretizing features...")
        
        df_discrete = df.copy()
        
        for col in df.columns:
            if col != 'TARGET' and df[col].nunique() > 10:
                df_discrete[col] = pd.qcut(
                    df[col], 
                    q=n_bins, 
                    labels=False, 
                    duplicates='drop'
                )
        
        return df_discrete
    
    def learn_structure(self, df, max_features=20):
        """Learn Bayesian Network structure using Hill Climbing"""
        logger.info("Learning network structure...")
        
        # Select top features by correlation with target
        correlations = df.corr()['TARGET'].abs().sort_values(ascending=False)
        top_features = correlations.head(max_features + 1).index.tolist()
        
        df_subset = df[top_features]
        
        # Learn structure
        hc = HillClimbSearch(df_subset)
        best_model = hc.estimate(scoring_method=BIC(df_subset))
        
        logger.info(f"Learned structure with {len(best_model.edges())} edges")
        
        return best_model, top_features
    
    def train_model(self, df, structure):
        """Train Bayesian Network with Maximum Likelihood Estimation"""
        logger.info("Training Bayesian Network...")
        
        self.model = DiscreteBayesianNetwork(structure.edges())
        
        # Estimate parameters
        self.model.fit(
            df,
            estimator=MaximumLikelihoodEstimator
        )
        
        # Initialize inference
        self.inference = VariableElimination(self.model)
        
        logger.info("Training complete!")
        
        return self.model
    
    def predict(self, df):
        """Make predictions using Bayesian inference"""
        logger.info("Making predictions...")
        
        predictions = []
        probabilities = []
        
        for idx, row in df.iterrows():
            try:
                # Create evidence dictionary
                evidence = row.drop('TARGET').to_dict()
                
                # Query for TARGET
                result = self.inference.query(
                    variables=['TARGET'],
                    evidence=evidence
                )
                
                # Get probability of default (TARGET=1)
                prob_default = result.values[1]
                pred = 1 if prob_default > 0.5 else 0
                
                predictions.append(pred)
                probabilities.append(prob_default)
                
            except Exception as e:
                # Fallback to majority class
                predictions.append(0)
                probabilities.append(0.5)
        
        return np.array(predictions), np.array(probabilities)
    
    def evaluate(self, test_df):
        """Evaluate model on test set"""
        logger.info("Evaluating model...")
        
        y_test = test_df['TARGET'].values
        X_test = test_df.drop('TARGET', axis=1)
        
        # Make predictions
        y_pred, y_proba = self.predict(test_df)
        
        # Calculate metrics
        auc_score = roc_auc_score(y_test, y_proba)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Test AUC: {auc_score:.4f}")
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        
        return {
            'auc': auc_score,
            'accuracy': accuracy
        }
    
    def save_model(self, structure, top_features):
        """Save Bayesian Network model"""
        logger.info("Saving model...")
        
        # Save model
        with open(self.model_path / 'bayesian_network.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save structure
        structure_dict = {
            'nodes': list(self.model.nodes()),
            'edges': list(self.model.edges()),
            'top_features': top_features
        }
        
        with open(self.model_path / 'bn_parameters.json', 'w') as f:
            json.dump(structure_dict, f, indent=2)
        
        # Save structure as DOT file
        with open(self.model_path / 'bn_structure.dot', 'w') as f:
            f.write("digraph BayesianNetwork {\n")
            for edge in self.model.edges():
                f.write(f'  "{edge[0]}" -> "{edge[1]}";\n')
            f.write("}\n")
        
        logger.info(f"Model saved to {self.model_path}")
    
    def train_pipeline(self):
        """Execute complete training pipeline"""
        # Load data
        train_df, test_df = self.load_data()
        
        # Discretize features
        train_discrete = self.discretize_features(train_df)
        test_discrete = self.discretize_features(test_df)
        
        # Learn structure
        structure, top_features = self.learn_structure(train_discrete)
        
        # Train model
        train_subset = train_discrete[top_features]
        self.train_model(train_subset, structure)
        
        # Evaluate
        test_subset = test_discrete[top_features]
        metrics = self.evaluate(test_subset)
        
        # Save model
        self.save_model(structure, top_features)
        
        return metrics


def main():
    """Main execution function"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    bn_model = BayesianNetworkModel(
        data_path=str(project_root / 'data' / 'processed'),
        model_path=str(project_root / 'models' / 'bayesian')
    )
    
    metrics = bn_model.train_pipeline()
    
    print("\n" + "="*50)
    print("Bayesian Network Training Complete!")
    print("="*50)
    print(f"Test AUC: {metrics['auc']:.4f}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
