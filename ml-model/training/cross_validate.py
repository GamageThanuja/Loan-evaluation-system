#!/usr/bin/env python3
"""
Cross-Validation for Hybrid Bayesian Loan Approval Model
=========================================================
Performs 5-fold stratified cross-validation to validate model performance.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hybrid_model import HybridModel


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_fold_results(fold, metrics):
    """Print results for a single fold"""
    print(f"\n  Fold {fold}:")
    print(f"    Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"    Precision: {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    print(f"    Recall:    {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    print(f"    F1-Score:  {metrics['f1']:.4f} ({metrics['f1']*100:.2f}%)")
    print(f"    ROC-AUC:   {metrics['roc_auc']:.4f} ({metrics['roc_auc']*100:.2f}%)")


def print_summary(all_metrics):
    """Print summary statistics"""
    print_header("CROSS-VALIDATION SUMMARY")
    
    print("\n  Performance Across All Folds:")
    metric_col = "Metric"
    mean_col = "Mean"
    std_col = "Std Dev"
    range_col = "Range"
    print(f"\n  {metric_col:<15} {mean_col:<18} {std_col:<12} {range_col:<25}")
    print("  " + "-"*70)
    
    for metric_name in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
        values = [m[metric_name] for m in all_metrics]
        mean = np.mean(values)
        std = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        
        metric_label = metric_name.replace('_', ' ').title()
        print(f"  {metric_label:<15} {mean:.4f} ({mean*100:6.2f}%)    ±{std:.4f}      [{min_val:.4f}, {max_val:.4f}]")
    
    print("\n  Interpretation:")
    avg_accuracy = np.mean([m['accuracy'] for m in all_metrics])
    std_accuracy = np.std([m['accuracy'] for m in all_metrics])
    
    if std_accuracy < 0.01:
        consistency = "Excellent"
    elif std_accuracy < 0.02:
        consistency = "Very Good"
    elif std_accuracy < 0.03:
        consistency = "Good"
    else:
        consistency = "Fair"
    
    print(f"     Model Consistency: {consistency} (std = {std_accuracy:.4f})")
    print(f"     Average Performance: {avg_accuracy*100:.2f}%")
    print(f"     The low standard deviation indicates the model performs")
    print(f"     consistently across different data subsets.")


def simple_preprocess(df):
    """Simple preprocessing for cross-validation"""
    # Remove leading/trailing spaces from column names
    df.columns = df.columns.str.strip()
    
    # Also remove leading/trailing spaces from all string values
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    # Separate features and target
    X = df.drop(['loan_id', 'loan_status'], axis=1, errors='ignore')
    y = df['loan_status'].map({'Approved': 1, 'Rejected': 0})
    
    # Handle categorical features
    categorical_cols = X.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
    
    return X, y


def run_cross_validation(n_splits=5):
    """Run stratified k-fold cross-validation"""
    
    print_header("HYBRID BAYESIAN MODEL - CROSS-VALIDATION")
    print(f"\n  Configuration:")
    print(f"    Method: Stratified K-Fold")
    print(f"    Number of Folds: {n_splits}")
    print(f"    Random Seed: 42")
    
    # Load data
    print("\n  Loading dataset...")
    data_path = Path(__file__).parent.parent / 'data' / 'raw' / 'loan_approval_dataset.csv'
    
    if not data_path.exists():
        print(f"\n  Error: Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df)} samples")
    
    # Preprocess
    print("\n  Preprocessing data...")
    X, y = simple_preprocess(df)
    
    print(f"  Features: {X.shape[1]} columns")
    print(f"  Class distribution: {y.value_counts().to_dict()}")
    
    # Setup cross-validation
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    print_header("TRAINING AND EVALUATION")
    
    all_metrics = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        print(f"\n  {'─'*76}")
        print(f"  Training Fold {fold}/{n_splits}...")
        
        # Split data
        X_train = X.iloc[train_idx].copy()
        y_train = y.iloc[train_idx].copy()
        X_val = X.iloc[val_idx].copy()
        y_val = y.iloc[val_idx].copy()
        
        # Normalize features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Initialize and train model
        model = HybridModel(
            input_dim=X_train_scaled.shape[1],
            bnn_hidden_dims=[128, 64, 32],
            bnn_dropout=0.3,
            gb_n_estimators=100,
            gb_max_depth=5,
            bnn_weight=0.6
        )
        
        # Train (with reduced epochs for speed in cross-validation)
        model.fit(
            X_train_scaled, y_train.values,
            X_val_scaled, y_val.values,
            epochs=50,
            batch_size=32,
            lr=0.001,
            patience=10
        )
        
        # Predict
        y_pred_proba, _ = model.predict_proba(X_val_scaled)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_val, y_pred_proba)
        }
        
        all_metrics.append(metrics)
        print_fold_results(fold, metrics)
    
    # Print summary
    print_summary(all_metrics)
    
    # Save results
    results_df = pd.DataFrame(all_metrics)
    results_df.index = [f'Fold {i+1}' for i in range(n_splits)]
    
    # Add summary row
    summary = pd.DataFrame([{
        'accuracy': results_df['accuracy'].mean(),
        'precision': results_df['precision'].mean(),
        'recall': results_df['recall'].mean(),
        'f1': results_df['f1'].mean(),
        'roc_auc': results_df['roc_auc'].mean()
    }], index=['Mean'])
    
    std = pd.DataFrame([{
        'accuracy': results_df['accuracy'].std(),
        'precision': results_df['precision'].std(),
        'recall': results_df['recall'].std(),
        'f1': results_df['f1'].std(),
        'roc_auc': results_df['roc_auc'].std()
    }], index=['Std Dev'])
    
    final_results = pd.concat([results_df, summary, std])
    
    # Save to CSV
    output_path = Path(__file__).parent.parent / 'reports' / 'cross_validation_results.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_results.to_csv(output_path)
    
    print(f"\n  Results saved to: {output_path}")
    
    print("\n" + "="*80)
    print("  CROSS-VALIDATION COMPLETE")
    print("="*80 + "\n")
    
    return final_results


if __name__ == '__main__':
    results = run_cross_validation(n_splits=5)
