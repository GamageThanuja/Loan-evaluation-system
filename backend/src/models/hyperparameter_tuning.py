"""
Automated Hyperparameter Tuning for TabNet
Uses Optuna for efficient hyperparameter optimization
"""

import optuna
from pytorch_tabnet.tab_model import TabNetClassifier
import torch
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score, make_scorer
import pickle
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TabNetTuner:
    """Hyperparameter tuning for TabNet using Optuna"""
    
    def __init__(self, data_path: str, model_path: str, n_trials: int = 50):
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)
        self.n_trials = n_trials
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.best_params = None
        
    def load_data(self):
        """Load training and validation data"""
        logger.info("Loading data splits...")
        
        train_df = pd.read_parquet(self.data_path / 'train_split.parquet')
        val_df = pd.read_parquet(self.data_path / 'val_split.parquet')
        
        # Separate features and target
        self.X_train = train_df.drop('TARGET', axis=1).values
        self.y_train = train_df['TARGET'].values
        
        self.X_val = val_df.drop('TARGET', axis=1).values
        self.y_val = val_df['TARGET'].values
        
        logger.info(f"Train: {self.X_train.shape}, Val: {self.X_val.shape}")
        
    def objective(self, trial):
        """Optuna objective function"""
        
        # Hyperparameters to tune
        n_d = trial.suggest_int('n_d', 8, 128)
        n_a = trial.suggest_int('n_a', 8, 128)
        n_steps = trial.suggest_int('n_steps', 3, 10)
        lr = trial.suggest_float('lr', 0.005, 0.1, log=True)
        gamma = trial.suggest_float('gamma', 1.0, 2.0)
        lambda_sparse = trial.suggest_float('lambda_sparse', 1e-6, 1e-3, log=True)
        batch_size = trial.suggest_categorical('batch_size', [256, 512, 1024, 2048])
        virtual_batch_size = trial.suggest_categorical('virtual_batch_size', [128, 256, 512])
        
        try:
            # Create TabNet model with suggested parameters
            model = TabNetClassifier(
                n_d=n_d,
                n_a=n_a,
                n_steps=n_steps,
                gamma=gamma,
                lambda_sparse=lambda_sparse,
                optimizer_fn=torch.optim.Adam,
                optimizer_params=dict(lr=lr),
                scheduler_params={"step_size": 10, "gamma": 0.9},
                scheduler_fn=torch.optim.lr_scheduler.StepLR,
                mask_type="entmax",
                verbose=0,
                seed=42
            )
            
            # Train model
            model.fit(
                X_train=self.X_train,
                y_train=self.y_train,
                eval_set=[(self.X_val, self.y_val)],
                eval_metric=['auc'],
                max_epochs=50,
                patience=10,
                batch_size=batch_size,
                virtual_batch_size=virtual_batch_size,
                num_workers=0,
                drop_last=False
            )
            
            # Evaluate on validation set
            y_pred_proba = model.predict_proba(self.X_val)[:, 1]
            auc_score = roc_auc_score(self.y_val, y_pred_proba)
            
            logger.info(f"Trial {trial.number}: AUC = {auc_score:.4f}")
            
            return auc_score
            
        except Exception as e:
            logger.warning(f"Trial {trial.number} failed: {str(e)}")
            return 0.0
    
    def optimize(self):
        """Run Optuna optimization"""
        logger.info(f"Starting hyperparameter optimization with {self.n_trials} trials...")
        
        # Create Optuna study
        study = optuna.create_study(
            direction='maximize',
            study_name='tabnet_optimization',
            pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=10)
        )
        
        # Run optimization
        study.optimize(self.objective, n_trials=self.n_trials, show_progress_bar=True)
        
        # Save best parameters
        self.best_params = study.best_params
        
        logger.info("=" * 60)
        logger.info("Optimization Complete!")
        logger.info("=" * 60)
        logger.info(f"Best AUC: {study.best_value:.4f}")
        logger.info(f"Best parameters:")
        for param, value in self.best_params.items():
            logger.info(f"  {param}: {value}")
        
        # Save results
        results = {
            'best_params': self.best_params,
            'best_auc': study.best_value,
            'n_trials': self.n_trials,
            'all_trials': [
                {
                    'number': trial.number,
                    'params': trial.params,
                    'value': trial.value
                }
                for trial in study.trials
            ]
        }
        
        output_path = self.model_path / 'hyperparameter_tuning_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nResults saved to: {output_path}")
        
        return study
    
    def train_best_model(self):
        """Train final model with best parameters"""
        logger.info("\nTraining final model with best parameters...")
        
        if self.best_params is None:
            raise ValueError("No best parameters found. Run optimize() first.")
        
        # Create model with best parameters
        model = TabNetClassifier(
            n_d=self.best_params['n_d'],
            n_a=self.best_params['n_a'],
            n_steps=self.best_params['n_steps'],
            gamma=self.best_params['gamma'],
            lambda_sparse=self.best_params['lambda_sparse'],
            optimizer_fn=torch.optim.Adam,
            optimizer_params=dict(lr=self.best_params['lr']),
            scheduler_params={"step_size": 10, "gamma": 0.9},
            scheduler_fn=torch.optim.lr_scheduler.StepLR,
            mask_type="entmax",
            verbose=1,
            seed=42
        )
        
        # Train on full training data
        model.fit(
            X_train=self.X_train,
            y_train=self.y_train,
            eval_set=[(self.X_val, self.y_val)],
            eval_metric=['auc', 'accuracy'],
            max_epochs=100,
            patience=20,
            batch_size=self.best_params['batch_size'],
            virtual_batch_size=self.best_params['virtual_batch_size'],
            num_workers=0,
            drop_last=False
        )
        
        # Save optimized model
        output_path = self.model_path / 'tabnet_optimized.zip'
        model.save_model(str(output_path))
        logger.info(f"Optimized model saved to: {output_path}")
        
        # Evaluate
        y_pred_proba = model.predict_proba(self.X_val)[:, 1]
        final_auc = roc_auc_score(self.y_val, y_pred_proba)
        logger.info(f"Final Validation AUC: {final_auc:.4f}")
        
        return model


def main():
    """Main execution function"""
    from src.config import Config
    
    # Configuration
    data_path = Config.DATA_PROCESSED
    model_path = Config.TABNET_DIR
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize tuner
    tuner = TabNetTuner(
        data_path=str(data_path),
        model_path=str(model_path),
        n_trials=50  # Adjust based on computational resources
    )
    
    # Load data
    tuner.load_data()
    
    # Run optimization
    study = tuner.optimize()
    
    # Train final model with best parameters
    best_model = tuner.train_best_model()
    
    logger.info("\n✅ Hyperparameter tuning complete!")


if __name__ == "__main__":
    main()
