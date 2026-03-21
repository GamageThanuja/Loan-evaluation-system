"""
Loan Approval Prediction - Training Module
==========================================

This module contains the complete implementation of the prediction models
for loan approval prediction.

Components:
-----------
1. DataPreprocessor (preprocess.py)
   - Data loading and cleaning
   - Feature engineering
   - Train/val/test splitting

2. BayesianNeuralNetwork (bayesian_nn.py)
   - Deep learning with MC-Dropout for uncertainty estimation
   - Focal Loss for class imbalance handling

3. BayesianNetwork (bayesian_network.py)
   - Gradient Boosting with calibrated probabilities
   - Feature importance analysis

4. HybridModel (hybrid_model.py)
   - Ensemble combining BNN + Bayesian Network
   - Optimized weighting for best predictions

5. train.py
   - Main training pipeline
   - Model evaluation and reporting

Usage:
------
    from training.preprocess import DataPreprocessor
    from training.bayesian_nn import BayesianNeuralNetwork, BayesianNNTrainer
    from training.bayesian_network import GradientBoostingBayesian
    from training.hybrid_model import HybridModel
    
    # Preprocess
    preprocessor = DataPreprocessor(raw_path, processed_path)
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.run()
    
    # Train models
    bnn = BayesianNeuralNetwork(input_dim=22)
    hybrid = HybridModel(input_dim=22)
"""

from training.preprocess import DataPreprocessor
from training.bayesian_nn import BayesianNeuralNetwork, BayesianNNTrainer, FocalLoss
from training.bayesian_network import BayesianNetwork, GradientBoostingBayesian
from training.hybrid_model import HybridModel

__all__ = [
    'DataPreprocessor',
    'BayesianNeuralNetwork',
    'BayesianNNTrainer',
    'FocalLoss',
    'BayesianNetwork',
    'GradientBoostingBayesian',
    'HybridModel'
]

__version__ = '2.0.0'
