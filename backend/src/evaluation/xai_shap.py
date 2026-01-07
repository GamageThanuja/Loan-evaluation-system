"""
SHAP Explainability Analysis
Generate SHAP plots for model interpretability
"""

import pickle
import shap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SHAPExplainer:
    """Generate SHAP explanations for TabNet model"""
    
    def __init__(self, model_path: str, data_path: str, output_path: str):
        self.model_path = Path(model_path)
        self.data_path = Path(data_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """Load test data and trained model"""
        logger.info("Loading test data...")
        
        test_df = pd.read_parquet(self.data_path / 'test_split.parquet')
        X_test = test_df.drop('TARGET', axis=1)
        y_test = test_df['TARGET']
        
        logger.info("Loading TabNet model...")
        from pytorch_tabnet.tab_model import TabNetClassifier
        self.model = TabNetClassifier()
        self.model.load_model(str(self.model_path / 'tabnet_model.zip'))
        
        self.feature_names = X_test.columns.tolist()
        
        return X_test.values, y_test.values
    
    def generate_shap_values(self, X_test, sample_size=100):
        """Generate SHAP values using KernelExplainer"""
        logger.info(f"Generating SHAP values for {sample_size} samples...")
        
        # Sample data for faster computation
        X_sample = X_test[:sample_size]
        
        # Create explainer
        def model_predict(X):
            return self.model.predict_proba(X)[:, 1]
        
        # Use a smaller background dataset for speed
        background = shap.sample(X_test, 50)
        explainer = shap.KernelExplainer(model_predict, background)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_sample)
        
        logger.info("SHAP values generated!")
        return shap_values, explainer.expected_value, X_sample
    
    def create_summary_plot(self, shap_values, X_sample):
        """Create SHAP summary plot"""
        logger.info("Creating SHAP summary plot...")
        
        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            shap_values, 
            X_sample, 
            feature_names=self.feature_names,
            max_display=20,
            show=False
        )
        
        output_file = self.output_path / 'shap_summary.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Summary plot saved to {output_file}")
    
    def create_waterfall_plot(self, shap_values, expected_value, X_sample, idx=0):
        """Create SHAP waterfall plot for a single prediction"""
        logger.info("Creating SHAP waterfall plot...")
        
        explanation = shap.Explanation(
            values=shap_values[idx],
            base_values=expected_value,
            data=X_sample[idx],
            feature_names=self.feature_names
        )
        
        plt.figure(figsize=(10, 8))
        shap.waterfall_plot(explanation, max_display=15, show=False)
        
        output_file = self.output_path / 'shap_waterfall.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Waterfall plot saved to {output_file}")
    
    def create_feature_importance(self, shap_values):
        """Create feature importance bar plot"""
        logger.info("Creating feature importance plot...")
        
        # Calculate mean absolute SHAP values
        feature_importance = np.abs(shap_values).mean(axis=0)
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': feature_importance
        }).sort_values('importance', ascending=False).head(20)
        
        # Plot
        plt.figure(figsize=(10, 8))
        plt.barh(importance_df['feature'], importance_df['importance'])
        plt.xlabel('Mean |SHAP value|')
        plt.title('Top 20 Feature Importance (SHAP)')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        output_file = self.output_path / 'feature_importance_shap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save to CSV
        importance_df.to_csv(self.output_path / 'feature_importance_shap.csv', index=False)
        logger.info(f"Feature importance saved to {output_file}")
    
    def run_analysis(self):
        """Run complete SHAP analysis"""
        logger.info("Starting SHAP analysis...")
        
        # Load data
        X_test, y_test = self.load_data()
        
        # Generate SHAP values
        shap_values, expected_value, X_sample = self.generate_shap_values(X_test)
        
        # Create visualizations
        self.create_summary_plot(shap_values, X_sample)
        self.create_waterfall_plot(shap_values, expected_value, X_sample, idx=0)
        self.create_feature_importance(shap_values)
        
        logger.info("✅ SHAP analysis complete!")


def main():
    """Main execution function"""
    project_root = Path(__file__).parent.parent.parent
    
    explainer = SHAPExplainer(
        model_path=str(project_root / 'models' / 'tabnet'),
        data_path=str(project_root / 'data' / 'processed'),
        output_path=str(project_root / 'reports' / 'figures')
    )
    
    explainer.run_analysis()
    
    print("\n" + "="*50)
    print("SHAP Analysis Complete!")
    print("="*50)
    print(f"Plots saved to: reports/figures/")
    print("  - shap_summary.png")
    print("  - shap_waterfall.png")
    print("  - feature_importance_shap.png")
    print("  - feature_importance_shap.csv")


if __name__ == "__main__":
    main()
