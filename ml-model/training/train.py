#!/usr/bin/env python3
"""
Main Training Pipeline
======================
Complete training pipeline for the Loan Approval Prediction System.
- Runs preprocessing
- Trains Bayesian Neural Network
- Trains Bayesian Network (Gradient Boosting)
- Trains Hybrid Model
- Generates comprehensive evaluation with figures
"""

import os
import sys
import json
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve, average_precision_score
)
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import SMOTE
from sklearn.decomposition import PCA

warnings.filterwarnings('ignore')

# Set style for plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Constants
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


class ModelEvaluator:
    """Comprehensive model evaluation with visualization."""
    
    def __init__(self, reports_dir: str):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
    
    def evaluate_model(self, model_name: str, y_true, y_proba, y_pred):
        """Compute all evaluation metrics for a model."""
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_proba),
            'average_precision': average_precision_score(y_true, y_proba)
        }
        
        self.results[model_name] = {
            'metrics': metrics,
            'y_true': y_true,
            'y_proba': y_proba,
            'y_pred': y_pred
        }
        
        return metrics
    
    def print_metrics(self, model_name: str, metrics: dict):
        """Print metrics in a formatted way."""
        print(f"\n  {model_name} Results:")
        print("-" * 50)
        print(f"  Accuracy:          {metrics['accuracy']*100:.2f}%")
        print(f"  Precision:         {metrics['precision']*100:.2f}%")
        print(f"  Recall:            {metrics['recall']*100:.2f}%")
        print(f"  F1-Score:          {metrics['f1_score']*100:.2f}%")
        print(f"  ROC-AUC:           {metrics['roc_auc']*100:.2f}%")
        print(f"  Avg Precision:     {metrics['average_precision']*100:.2f}%")
    
    def plot_confusion_matrix(self, model_name: str, y_true, y_pred, save: bool = True):
        """Plot and save confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=['Rejected', 'Approved'],
                    yticklabels=['Rejected', 'Approved'],
                    annot_kws={'size': 14})
        
        ax.set_xlabel('Predicted', fontsize=12)
        ax.set_ylabel('Actual', fontsize=12)
        ax.set_title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
        
        # Add accuracy text
        accuracy = (cm[0,0] + cm[1,1]) / cm.sum()
        plt.figtext(0.5, 0.02, f'Accuracy: {accuracy*100:.2f}%', ha='center', fontsize=11)
        
        plt.tight_layout()
        
        if save:
            filepath = self.reports_dir / f'confusion_matrix_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
        return cm
    
    def plot_roc_curve(self, save: bool = True):
        """Plot ROC curves for all models."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6', '#f39c12']
        
        for i, (model_name, data) in enumerate(self.results.items()):
            fpr, tpr, _ = roc_curve(data['y_true'], data['y_proba'])
            auc = data['metrics']['roc_auc']
            
            ax.plot(fpr, tpr, color=colors[i % len(colors)], lw=2,
                    label=f'{model_name} (AUC = {auc:.4f})')
        
        ax.plot([0, 1], [0, 1], 'k--', lw=1.5, alpha=0.7, label='Random Classifier')
        
        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title('ROC Curves - Model Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.02])
        
        plt.tight_layout()
        
        if save:
            filepath = self.reports_dir / 'roc_curves_comparison.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
    
    def plot_precision_recall_curve(self, save: bool = True):
        """Plot Precision-Recall curves for all models."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#9b59b6', '#f39c12']
        
        for i, (model_name, data) in enumerate(self.results.items()):
            precision, recall, _ = precision_recall_curve(data['y_true'], data['y_proba'])
            ap = data['metrics']['average_precision']
            
            ax.plot(recall, precision, color=colors[i % len(colors)], lw=2,
                    label=f'{model_name} (AP = {ap:.4f})')
        
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title('Precision-Recall Curves - Model Comparison', fontsize=14, fontweight='bold')
        ax.legend(loc='lower left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1.02])
        
        plt.tight_layout()
        
        if save:
            filepath = self.reports_dir / 'precision_recall_curves.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
    
    def plot_metrics_comparison(self, save: bool = True):
        """Plot bar chart comparing all metrics across models."""
        metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'Avg Precision']
        metrics_keys = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'average_precision']
        
        n_models = len(self.results)
        n_metrics = len(metrics_names)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(n_metrics)
        width = 0.25
        
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        
        for i, (model_name, data) in enumerate(self.results.items()):
            values = [data['metrics'][key] * 100 for key in metrics_keys]
            offset = (i - n_models/2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=model_name, color=colors[i % len(colors)])
            
            # Add value labels
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{val:.1f}%', ha='center', va='bottom', fontsize=8, rotation=0)
        
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score (%)', fontsize=12)
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_names, fontsize=10)
        ax.legend(loc='lower right', fontsize=10)
        ax.set_ylim(0, 110)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filepath = self.reports_dir / 'metrics_comparison.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
    
    def plot_training_history(self, history: dict, model_name: str, save: bool = True):
        """Plot training history (loss and validation metrics)."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss curve
        if 'train_loss' in history:
            axes[0].plot(history['train_loss'], 'b-', lw=2, label='Training Loss')
            axes[0].set_xlabel('Epoch', fontsize=11)
            axes[0].set_ylabel('Loss', fontsize=11)
            axes[0].set_title(f'{model_name} - Training Loss', fontsize=12, fontweight='bold')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # Validation metrics
        if 'val_auc' in history:
            axes[1].plot(history['val_auc'], 'g-', lw=2, label='Validation AUC')
        if 'val_f1' in history:
            axes[1].plot(history['val_f1'], 'r-', lw=2, label='Validation F1')
        
        axes[1].set_xlabel('Epoch', fontsize=11)
        axes[1].set_ylabel('Score', fontsize=11)
        axes[1].set_title(f'{model_name} - Validation Metrics', fontsize=12, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filepath = self.reports_dir / f'training_history_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
    
    def generate_summary_figure(self, save: bool = True):
        """Generate a comprehensive summary figure with all key visualizations."""
        fig = plt.figure(figsize=(20, 16))
        
        # Create grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        
        # 1. ROC Curves (top left, spans 2 columns)
        ax1 = fig.add_subplot(gs[0, :2])
        for i, (model_name, data) in enumerate(self.results.items()):
            fpr, tpr, _ = roc_curve(data['y_true'], data['y_proba'])
            auc = data['metrics']['roc_auc']
            ax1.plot(fpr, tpr, color=colors[i], lw=2, label=f'{model_name} (AUC={auc:.4f})')
        ax1.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.7)
        ax1.set_xlabel('False Positive Rate')
        ax1.set_ylabel('True Positive Rate')
        ax1.set_title('ROC Curves', fontsize=12, fontweight='bold')
        ax1.legend(loc='lower right')
        ax1.grid(True, alpha=0.3)
        
        # 2. Metrics Summary Box (top right)
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        
        # Find best model
        best_model = max(self.results.items(), key=lambda x: x[1]['metrics']['f1_score'])
        best_name, best_data = best_model
        best_metrics = best_data['metrics']
        
        summary_text = f"BEST MODEL: {best_name}\n\n"
        summary_text += f"Accuracy:     {best_metrics['accuracy']*100:.2f}%\n"
        summary_text += f"Precision:    {best_metrics['precision']*100:.2f}%\n"
        summary_text += f"Recall:       {best_metrics['recall']*100:.2f}%\n"
        summary_text += f"F1-Score:     {best_metrics['f1_score']*100:.2f}%\n"
        summary_text += f"ROC-AUC:      {best_metrics['roc_auc']*100:.2f}%\n"
        summary_text += f"Avg Precision:{best_metrics['average_precision']*100:.2f}%"
        
        ax2.text(0.5, 0.5, summary_text, transform=ax2.transAxes,
                fontsize=11, verticalalignment='center', horizontalalignment='center',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        ax2.set_title('Best Model Summary', fontsize=12, fontweight='bold')
        
        # 3-5. Confusion Matrices (middle row)
        for i, (model_name, data) in enumerate(self.results.items()):
            ax = fig.add_subplot(gs[1, i])
            cm = confusion_matrix(data['y_true'], data['y_pred'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                        xticklabels=['Rejected', 'Approved'],
                        yticklabels=['Rejected', 'Approved'],
                        annot_kws={'size': 12})
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            ax.set_title(f'{model_name}\nConfusion Matrix', fontsize=11, fontweight='bold')
        
        # 6. Metrics Comparison Bar Chart (bottom, spans all columns)
        ax6 = fig.add_subplot(gs[2, :])
        
        metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'Avg Precision']
        metrics_keys = ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'average_precision']
        
        x = np.arange(len(metrics_names))
        width = 0.25
        
        for i, (model_name, data) in enumerate(self.results.items()):
            values = [data['metrics'][key] * 100 for key in metrics_keys]
            offset = (i - len(self.results)/2 + 0.5) * width
            bars = ax6.bar(x + offset, values, width, label=model_name, color=colors[i])
            
            for bar, val in zip(bars, values):
                ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{val:.1f}%', ha='center', va='bottom', fontsize=8)
        
        ax6.set_xlabel('Metrics', fontsize=11)
        ax6.set_ylabel('Score (%)', fontsize=11)
        ax6.set_title('Model Performance Comparison', fontsize=12, fontweight='bold')
        ax6.set_xticks(x)
        ax6.set_xticklabels(metrics_names)
        ax6.legend(loc='lower right')
        ax6.set_ylim(0, 110)
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Overall title
        fig.suptitle('Loan Approval Prediction - Model Evaluation Summary',
                     fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        if save:
            filepath = self.reports_dir / 'evaluation_summary.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved: {filepath.name}")
        
        plt.close()
    
    def save_results_json(self):
        """Save all results to JSON file."""
        results_json = {}
        
        for model_name, data in self.results.items():
            results_json[model_name] = {
                'metrics': data['metrics'],
                'confusion_matrix': confusion_matrix(data['y_true'], data['y_pred']).tolist()
            }
        
        filepath = self.reports_dir / 'evaluation_results.json'
        with open(filepath, 'w') as f:
            json.dump(results_json, f, indent=2)
        
        print(f"  ✓ Saved: {filepath.name}")
    
    def generate_all_reports(self):
        """Generate all evaluation reports and figures."""
        print("\n" + "="*60)
        print("  GENERATING EVALUATION REPORTS")
        print("="*60)
        
        # Individual confusion matrices
        for model_name, data in self.results.items():
            self.plot_confusion_matrix(model_name, data['y_true'], data['y_pred'])
        
        # Comparison plots
        self.plot_roc_curve()
        self.plot_precision_recall_curve()
        self.plot_metrics_comparison()
        
        # Summary figure
        self.generate_summary_figure()
        
        # JSON results
        self.save_results_json()
        
        print(f"\n  All reports saved to: {self.reports_dir}")


def load_processed_data(processed_path: Path):
    """Load preprocessed data from disk."""
    X_train = pd.read_csv(processed_path / 'X_train.csv')
    X_val = pd.read_csv(processed_path / 'X_val.csv')
    X_test = pd.read_csv(processed_path / 'X_test.csv')
    
    y_train = pd.read_csv(processed_path / 'y_train.csv')['loan_status']
    y_val = pd.read_csv(processed_path / 'y_val.csv')['loan_status']
    y_test = pd.read_csv(processed_path / 'y_test.csv')['loan_status']
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def handle_class_imbalance(X_train, y_train):
    """Apply SMOTE-Tomek for class imbalance."""
    print("\n" + "="*60)
    print("  HANDLING CLASS IMBALANCE")
    print("="*60)
    
    print(f"\n  Original distribution:")
    print(f"    - Rejected (0): {(y_train == 0).sum()} ({(y_train == 0).mean()*100:.1f}%)")
    print(f"    - Approved (1): {(y_train == 1).sum()} ({(y_train == 1).mean()*100:.1f}%)")
    
    smote_tomek = SMOTETomek(
        sampling_strategy='auto',
        random_state=RANDOM_STATE,
        smote=SMOTE(k_neighbors=5, random_state=RANDOM_STATE)
    )
    
    X_resampled, y_resampled = smote_tomek.fit_resample(X_train.values, y_train.values)
    
    X_resampled = pd.DataFrame(X_resampled, columns=X_train.columns)
    y_resampled = pd.Series(y_resampled)
    
    print(f"\n  Resampled distribution:")
    print(f"    - Rejected (0): {(y_resampled == 0).sum()} ({(y_resampled == 0).mean()*100:.1f}%)")
    print(f"    - Approved (1): {(y_resampled == 1).sum()} ({(y_resampled == 1).mean()*100:.1f}%)")
    
    return X_resampled, y_resampled


def apply_pca(X_train, X_val, X_test, variance_threshold=0.95):
    """Apply PCA for dimensionality reduction."""
    print("\n" + "="*60)
    print("  APPLYING PCA")
    print("="*60)
    
    print(f"\n  Original features: {X_train.shape[1]}")
    
    pca = PCA(n_components=variance_threshold, random_state=RANDOM_STATE)
    
    X_train_pca = pca.fit_transform(X_train)
    X_val_pca = pca.transform(X_val)
    X_test_pca = pca.transform(X_test)
    
    print(f"  Components retained: {pca.n_components_}")
    print(f"  Explained variance: {pca.explained_variance_ratio_.sum()*100:.2f}%")
    
    return X_train_pca, X_val_pca, X_test_pca, pca


def main():
    """Main training pipeline."""
    print("\n" + "="*60)
    print("  LOAN APPROVAL PREDICTION - TRAINING PIPELINE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Paths
    base_path = Path(__file__).parent.parent
    raw_path = base_path / 'data' / 'raw' / 'loan_approval_dataset.csv'
    processed_path = base_path / 'data' / 'processed'
    models_path = base_path / 'models'
    reports_path = base_path / 'reports'
    
    # Create directories
    models_path.mkdir(parents=True, exist_ok=True)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # STEP 1: PREPROCESSING
    # ========================================================================
    print("\n" + "="*60)
    print("  STEP 1: PREPROCESSING")
    print("="*60)
    
    from training.preprocess import DataPreprocessor
    
    preprocessor = DataPreprocessor(str(raw_path), str(processed_path))
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.run()
    
    # ========================================================================
    # STEP 2: CLASS IMBALANCE & PCA
    # ========================================================================
    X_train_balanced, y_train_balanced = handle_class_imbalance(X_train, y_train)
    X_train_pca, X_val_pca, X_test_pca, pca = apply_pca(X_train_balanced, X_val, X_test)
    
    # Save PCA transformer for inference
    pca_path = processed_path / 'pca.joblib'
    joblib.dump(pca, pca_path)
    print(f"  ✓ PCA transformer saved to {pca_path}")
    
    input_dim = X_train_pca.shape[1]
    print(f"\n  Input dimension for models: {input_dim}")
    
    # Initialize evaluator
    evaluator = ModelEvaluator(str(reports_path))
    
    # ========================================================================
    # STEP 3: TRAIN BAYESIAN NEURAL NETWORK
    # ========================================================================
    print("\n" + "="*60)
    print("  STEP 3: TRAINING BAYESIAN NEURAL NETWORK")
    print("="*60)
    
    from training.bayesian_nn import BayesianNeuralNetwork, BayesianNNTrainer
    
    bnn_model = BayesianNeuralNetwork(input_dim=input_dim, hidden_dims=[128, 64, 32], dropout=0.3)
    bnn_trainer = BayesianNNTrainer(bnn_model, device='cpu')
    
    bnn_history = bnn_trainer.train(
        X_train_pca, y_train_balanced, X_val_pca, y_val,
        epochs=100, batch_size=32, lr=0.001, patience=15
    )
    
    # Save BNN
    bnn_trainer.save(str(models_path / 'bayesian_nn.joblib'))
    
    # Evaluate BNN
    bnn_proba = bnn_trainer.predict(X_test_pca, with_uncertainty=False)
    bnn_pred = (bnn_proba >= 0.5).astype(int)
    
    bnn_metrics = evaluator.evaluate_model('Bayesian NN', y_test.values, bnn_proba, bnn_pred)
    evaluator.print_metrics('Bayesian Neural Network', bnn_metrics)
    evaluator.plot_training_history(bnn_history, 'Bayesian NN')
    
    # ========================================================================
    # STEP 4: TRAIN BAYESIAN NETWORK (GRADIENT BOOSTING)
    # ========================================================================
    print("\n" + "="*60)
    print("  STEP 4: TRAINING BAYESIAN NETWORK")
    print("="*60)
    
    from training.bayesian_network import GradientBoostingBayesian
    
    gb_model = GradientBoostingBayesian(n_estimators=100, max_depth=5)
    gb_model.fit(X_train_pca, y_train_balanced)
    
    # Save GB
    gb_model.save(str(models_path / 'bayesian_network.joblib'))
    
    # Evaluate GB
    gb_proba = gb_model.predict_proba(X_test_pca)[:, 1]
    gb_pred = (gb_proba >= 0.5).astype(int)
    
    gb_metrics = evaluator.evaluate_model('Bayesian Network', y_test.values, gb_proba, gb_pred)
    evaluator.print_metrics('Bayesian Network (Gradient Boosting)', gb_metrics)
    
    # ========================================================================
    # STEP 5: TRAIN HYBRID MODEL
    # ========================================================================
    print("\n" + "="*60)
    print("  STEP 5: TRAINING HYBRID MODEL")
    print("="*60)
    
    from training.hybrid_model import HybridModel
    
    hybrid_model = HybridModel(
        input_dim=input_dim,
        bnn_hidden_dims=[128, 64, 32],
        bnn_dropout=0.3,
        gb_n_estimators=100,
        gb_max_depth=5,
        bnn_weight=0.6,
        device='cpu'
    )
    
    hybrid_model.fit(
        pd.DataFrame(X_train_pca), y_train_balanced,
        pd.DataFrame(X_val_pca), y_val,
        epochs=100, batch_size=32, lr=0.001, patience=15
    )
    
    # Save Hybrid
    hybrid_model.save(str(models_path / 'hybrid_model.joblib'))
    
    # Evaluate Hybrid
    hybrid_proba, _ = hybrid_model.predict_proba(pd.DataFrame(X_test_pca))
    hybrid_pred = (hybrid_proba >= 0.5).astype(int)
    
    hybrid_metrics = evaluator.evaluate_model('Hybrid Model', y_test.values, hybrid_proba, hybrid_pred)
    evaluator.print_metrics('Hybrid Model', hybrid_metrics)
    
    # ========================================================================
    # STEP 6: GENERATE ALL REPORTS
    # ========================================================================
    evaluator.generate_all_reports()
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "="*60)
    print("  TRAINING COMPLETE - FINAL SUMMARY")
    print("="*60)
    
    print("\n  Models saved:")
    print(f"    - {models_path / 'bayesian_nn.joblib'}")
    print(f"    - {models_path / 'bayesian_network.joblib'}")
    print(f"    - {models_path / 'hybrid_model.joblib'}")
    
    print("\n  Reports saved:")
    for f in reports_path.glob('*.png'):
        print(f"    - {f.name}")
    for f in reports_path.glob('*.json'):
        print(f"    - {f.name}")
    
    # Print comparison table
    print("\n" + "="*60)
    print("  MODEL COMPARISON")
    print("="*60)
    print(f"\n  {'Model':<20} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'ROC-AUC':<12}")
    print("-" * 80)
    
    for model_name, data in evaluator.results.items():
        m = data['metrics']
        print(f"  {model_name:<20} {m['accuracy']*100:>10.2f}% {m['precision']*100:>10.2f}% "
              f"{m['recall']*100:>10.2f}% {m['f1_score']*100:>10.2f}% {m['roc_auc']*100:>10.2f}%")
    
    # Best model
    best = max(evaluator.results.items(), key=lambda x: x[1]['metrics']['f1_score'])
    print(f"\n  ✓ BEST MODEL: {best[0]} (F1-Score: {best[1]['metrics']['f1_score']*100:.2f}%)")
    
    print("\n" + "="*60)
    print("  ✓ ALL TASKS COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return evaluator.results


if __name__ == "__main__":
    # Add parent to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))
    main()
