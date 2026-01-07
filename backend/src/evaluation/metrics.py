"""
Evaluation Metrics Module
"""

import numpy as np
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, classification_report, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation"""
    
    def __init__(self):
        self.metrics = {}
        
    def calculate_metrics(self, y_true, y_pred, y_proba=None):
        """Calculate all classification metrics"""
        logger.info("Calculating evaluation metrics...")
        
        self.metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }
        
        if y_proba is not None:
            self.metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
        
        return self.metrics
    
    def print_metrics(self):
        """Print metrics in formatted way"""
        print("\n" + "="*50)
        print("Model Evaluation Metrics")
        print("="*50)
        
        for key, value in self.metrics.items():
            if key != 'confusion_matrix':
                print(f"{key.upper()}: {value:.4f}")
        
        print("\nConfusion Matrix:")
        print(np.array(self.metrics['confusion_matrix']))
        print("="*50 + "\n")
    
    def plot_roc_curve(self, y_true, y_proba, save_path=None):
        """Plot ROC curve"""
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.4f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"ROC curve saved to {save_path}")
        
        plt.show()
    
    def plot_confusion_matrix(self, y_true, y_pred, save_path=None):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Confusion Matrix')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to {save_path}")
        
        plt.show()
