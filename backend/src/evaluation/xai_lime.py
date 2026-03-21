"""
Automated XAI Visual Reports using LIME
=======================================
Generates sophisticated, human-readable reports (HTML/JSON) with visual summaries
and personalized explanations for loan decisions.

Key Features:
- Personalized, Applicant-Specific Explanations
- Visual Weights (Red=Risk, Green=Favor)
- Business & Regulatory Compliance Reports
"""

import sys
import os
import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# Add parent directories to path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

try:
    import lime
    import lime.lime_tabular
except ImportError:
    logging.warning("LIME not installed. Run 'pip install lime'")

logger = logging.getLogger(__name__)

class LimeReportGenerator:
    """
    Generates automated LIME-based XAI reports for loan applicants.
    """
    
    def __init__(self, model_predictor, train_data_path: str = None):
        """
        Initialize LIME explainer with training data statistics.
        
        Args:
            model_predictor: The LoanPredictor instance (must have .predict_proba method)
            train_data_path: Path to X_train.npy (optional, auto-detected if None)
        """
        self.predictor = model_predictor
        self.explainer = None
        self.feature_names = model_predictor.feature_names
        self.class_names = ['Rejected', 'Approved']
        
        # Load training data for initialization
        if train_data_path:
            self.train_data_path = Path(train_data_path)
        else:
            # Try to find it in standard location
            self.train_data_path = project_root / "ml-model" / "dataset" / "processed_data" / "X_train.npy"
            
        self._initialize_explainer()
        
    def _initialize_explainer(self):
        """Initialize LimeTabularExplainer with training data summary"""
        try:
            if not self.train_data_path.exists():
                logger.warning(f"Training data not found at {self.train_data_path}. LIME explainer not initialized.")
                return

            # Load training data (using a sample for efficiency)
            X_train = np.load(self.train_data_path)
            
            # Use a representative sample (e.g., 5000 rows) to initialize explainer
            sample_size = min(5000, X_train.shape[0])
            X_sample = X_train[np.random.choice(X_train.shape[0], sample_size, replace=False)]
            
            self.explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data=X_sample,
                feature_names=self.feature_names,
                class_names=self.class_names,
                mode='classification',
                discretize_continuous=True,
                random_state=42
            )
            logger.info("✅ LIME Explainer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LIME explainer: {e}")
            self.explainer = None

    def generate_report(self, applicant_features: np.ndarray, applicant_id: str = "Unknown") -> Dict[str, Any]:
        """
        Generate a comprehensive XAI report for a single applicant.
        
        Args:
            applicant_features: 1D numpy array of scaled features
            applicant_id: Identifier for the report
            
        Returns:
            Dict containing HTML report, JSON summary, and visual weights
        """
        if self.explainer is None:
            return {"error": "Explainer not initialized"}
            
        try:
            # Define prediction function wrapper for LIME
            # LIME passes a 2D array (n_samples, n_features)
            # We need to return (n_samples, 2) probabilities
            predict_fn = lambda x: self.predictor.dl_model.predict_proba(x)
            
            # Generate explanation
            # num_features=10 to show top 10 most impactful factors
            exp = self.explainer.explain_instance(
                data_row=applicant_features,
                predict_fn=predict_fn,
                num_features=10,
                top_labels=1
            )
            
            # Extract weights
            weights = exp.as_list()
            
            # Separate into Risk (Red) and Favor (Green) factors
            # In LIME for binary classification (Rejected=0, Approved=1):
            # Positive weight for class 1 = Supports Approval (Green)
            # Negative weight for class 1 = Supports Rejection (Red)
            # Note: LIME weights are relative to the prediction.
            
            risk_factors = []
            favor_factors = []
            
            for feature, weight in weights:
                # Format weight for display
                impact = abs(weight)
                
                factor_data = {
                    "feature": feature,
                    "weight": weight,
                    "impact_score": round(impact * 100, 2), # Scaled for readability
                    "description": self._generate_natural_language_description(feature, weight)
                }
                
                if weight < 0:
                    risk_factors.append(factor_data)
                else:
                    favor_factors.append(factor_data)
            
            # Generate HTML Report
            html_report = self._create_html_report(exp, applicant_id, risk_factors, favor_factors)
            
            return {
                "applicant_id": applicant_id,
                "summary_json": {
                    "risk_factors": risk_factors,
                    "favor_factors": favor_factors,
                    "prediction_probability": exp.predict_proba[1]
                },
                "html_report": html_report,
                "visual_weights": {
                    "red_factors": [f["feature"] for f in risk_factors],
                    "green_factors": [f["feature"] for f in favor_factors]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating LIME report: {e}")
            return {"error": str(e)}

    def _generate_natural_language_description(self, feature_condition: str, weight: float) -> str:
        """Convert LIME condition (e.g., 'Income <= 5000') into business language."""
        # Simple heuristic for demo purposes
        if weight < 0:
            return f"The condition '{feature_condition}' increases credit risk."
        else:
            return f"The condition '{feature_condition}' supports loan approval."

    def _create_html_report(self, exp, applicant_id: str, risks: List[Dict], favors: List[Dict]) -> str:
        """Create a sophisticated HTML report."""
        
        # Get LIME's visualization as HTML string
        lime_html = exp.as_html()
        
        # Determine overall decision based on probability
        prob_approved = exp.predict_proba[1]
        decision = "APPROVED" if prob_approved >= self.predictor.OPTIMAL_THRESHOLD else "REJECTED"
        color = "#2ecc71" if decision == "APPROVED" else "#e74c3c"
        
        custom_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa; }}
                .report-container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-radius: 8px; }}
                .header {{ border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
                .title {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                .meta {{ color: #7f8c8d; font-size: 14px; }}
                .decision-badge {{ padding: 10px 20px; border-radius: 5px; color: white; font-weight: bold; background-color: {color}; }}
                .section {{ margin-bottom: 30px; }}
                .factors-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .factor-card {{ padding: 15px; border-radius: 6px; border-left: 4px solid; }}
                .risk {{ background-color: #fdeaea; border-color: #e74c3c; }}
                .favor {{ background-color: #eafaf1; border-color: #2ecc71; }}
                .lime-viz {{ margin-top: 30px; border: 1px solid #eee; padding: 10px; }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <div class="header">
                    <div>
                        <div class="title">Automated Risk Assessment Report</div>
                        <div class="meta">Applicant ID: {applicant_id} | Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}</div>
                    </div>
                    <div class="decision-badge">{decision}</div>
                </div>
                
                <div class="section">
                    <h3>Executive Summary</h3>
                    <p>The system has assessed this application with a <strong>{prob_approved*100:.1f}% probability of approval</strong>.</p>
                </div>
                
                <div class="section">
                    <h3>Key Decision Factors</h3>
                    <div class="factors-grid">
                        <div>
                            <h4 style="color: #e74c3c;">⚠️ Risk Factors (Negative Impact)</h4>
                            {''.join([f'<div class="factor-card risk"><strong>{f["feature"]}</strong><br><small>{f["description"]}</small></div>' for f in risks])}
                        </div>
                        <div>
                            <h4 style="color: #2ecc71;">✅ Supporting Factors (Positive Impact)</h4>
                            {''.join([f'<div class="factor-card favor"><strong>{f["feature"]}</strong><br><small>{f["description"]}</small></div>' for f in favors])}
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h3>Detailed LIME Analysis</h3>
                    <div class="lime-viz">
                        {lime_html}
                    </div>
                </div>
                
                <div class="section">
                    <p style="font-size: 12px; color: #95a5a6; text-align: center;">
                        Generated by LoanWise v4.0 Automated XAI System. Compliant with regulatory "Right to Explanation" standards.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return custom_html
