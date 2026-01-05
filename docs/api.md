# API Documentation

## Overview

This document provides API reference for the Home Credit Hybrid Model.

## Data Loading API

### DataLoader

```python
from src.data.data_loader import DataLoader

loader = DataLoader(data_path='data/processed')
df = loader.load_preprocessed_data()
train, val, test = loader.split_data(df)
```

**Methods:**
- `load_preprocessed_data(filename)`: Load preprocessed data
- `split_data(df, target_col, test_size, val_size)`: Split data into train/val/test
- `save_splits(train_data, val_data, test_data, output_path)`: Save splits to disk

## Model Training API

### TabNetTrainer

```python
from src.models.tabnet_train import TabNetTrainer

trainer = TabNetTrainer(
    data_path='data/processed',
    model_path='models/tabnet'
)
metrics = trainer.train_pipeline()
```

**Methods:**
- `load_data()`: Load train/val/test splits
- `create_model()`: Initialize TabNet model
- `train(train_data, val_data)`: Train the model
- `evaluate(test_data)`: Evaluate on test set
- `save_model()`: Save trained model

### BayesianNetworkModel

```python
from src.models.bayesian_network import BayesianNetworkModel

bn = BayesianNetworkModel(
    data_path='data/processed',
    model_path='models/bayesian'
)
metrics = bn.train_pipeline()
```

**Methods:**
- `learn_structure(df)`: Learn Bayesian network structure
- `train_model(df, structure)`: Train with MLE
- `predict(df)`: Make predictions
- `evaluate(test_df)`: Evaluate model

### HybridEnsemble

```python
from src.models.hybrid_ensemble import HybridEnsemble

ensemble = HybridEnsemble(
    data_path='data/processed',
    tabnet_path='models/tabnet',
    bn_path='models/bayesian',
    output_path='models/hybrid'
)
metrics = ensemble.train_pipeline()
```

## Prediction API

### CreditDefaultPredictor

```python
from src.inference.predict import CreditDefaultPredictor

predictor = CreditDefaultPredictor(
    tabnet_path='models/tabnet',
    hybrid_path='models/hybrid'
)
predictor.load_models()

predictions, probabilities = predictor.predict(df)
```

**Methods:**
- `load_models()`: Load trained models
- `predict(df, return_proba)`: Make predictions
- `predict_from_file(input_file, output_file)`: Predict from CSV

## Feature Engineering API

### FeatureEngineer

```python
from src.features.build_features import FeatureEngineer

engineer = FeatureEngineer()
df_engineered = engineer.engineer_all_features(df)
```

## Evaluation API

### ModelEvaluator

```python
from src.evaluation.metrics import ModelEvaluator

evaluator = ModelEvaluator()
metrics = evaluator.calculate_metrics(y_true, y_pred, y_proba)
evaluator.print_metrics()
```

**Methods:**
- `calculate_metrics(y_true, y_pred, y_proba)`: Calculate all metrics
- `print_metrics()`: Display metrics
- `plot_roc_curve(y_true, y_proba)`: Plot ROC curve
- `plot_confusion_matrix(y_true, y_pred)`: Plot confusion matrix
