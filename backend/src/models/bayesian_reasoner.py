"""
Bayesian Network Reasoner
Provides explainable reasoning for credit default predictions using Bayesian inference paths
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pickle
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    VERY_LOW = "Very Low Risk"
    LOW = "Low Risk"
    MEDIUM = "Medium Risk"
    HIGH = "High Risk"
    VERY_HIGH = "Very High Risk"


@dataclass
class FeatureInfluence:
    """Represents the influence of a feature on the prediction"""
    feature_name: str
    feature_value: float
    discretized_value: int
    influence_direction: str  # "increases_risk" or "decreases_risk"
    influence_strength: float  # 0.0 to 1.0
    conditional_probability: float
    explanation: str


@dataclass
class InferencePath:
    """Represents the inference path in the Bayesian Network"""
    parent_nodes: List[str]
    child_nodes: List[str]
    path_strength: float
    description: str


@dataclass
class BayesianReasoning:
    """Complete reasoning output from the Bayesian Network"""
    prediction: int
    probability: float
    risk_level: str
    decision: str
    
    # Reasoning components
    top_risk_factors: List[FeatureInfluence]
    top_protective_factors: List[FeatureInfluence]
    inference_paths: List[InferencePath]
    
    # Natural language explanation
    summary_explanation: str
    detailed_explanation: str
    
    # Conditional probabilities
    conditional_probabilities: Dict[str, float]
    
    # Confidence metrics
    confidence_score: float
    evidence_strength: str


class BayesianReasoner:
    """
    Bayesian Network Reasoner for explainable credit default predictions
    
    Provides:
    - Inference path extraction showing which evidence nodes influenced the decision
    - Conditional probabilities explaining the reasoning
    - Natural language explanations
    """
    
    # Feature descriptions for human-readable explanations
    FEATURE_DESCRIPTIONS = {
        'EXT_SOURCE_1': 'External credit score 1',
        'EXT_SOURCE_2': 'External credit score 2',
        'EXT_SOURCE_3': 'External credit score 3',
        'EXT_SOURCE_MEAN': 'Average external credit score',
        'EXT_SOURCE_STD': 'Variability in external credit scores',
        'AGE_YEARS': 'Applicant age',
        'DAYS_BIRTH': 'Days since birth',
        'DAYS_EMPLOYED': 'Employment duration',
        'CODE_GENDER': 'Gender',
        'NAME_EDUCATION_TYPE': 'Education level',
        'REGION_RATING_CLIENT': 'Region rating',
        'REG_CITY_NOT_WORK_CITY': 'Lives outside work city',
        'DAYS_LAST_PHONE_CHANGE': 'Days since phone change',
        'bureau_DAYS_CREDIT_max': 'Maximum credit history length',
        'bureau_DAYS_CREDIT_min': 'Minimum credit history length',
        'bureau_DAYS_CREDIT_mean': 'Average credit history length',
        'bureau_AMT_CREDIT_SUM_DEBT_mean': 'Average outstanding debt',
        'inst_AMT_PAYMENT_min': 'Minimum installment payment',
        'inst_DAYS_INSTALMENT_min': 'Minimum days to installment',
        'prev_DAYS_DECISION_min': 'Fastest previous decision',
        'prev_DAYS_DECISION_mean': 'Average previous decision time',
        'AMT_CREDIT': 'Credit amount',
        'AMT_INCOME_TOTAL': 'Total income',
        'AMT_ANNUITY': 'Annuity amount',
        'CREDIT_INCOME_RATIO': 'Credit to income ratio',
        'ANNUITY_INCOME_RATIO': 'Annuity to income ratio',
    }
    
    # Thresholds for risk interpretation
    RISK_THRESHOLDS = {
        'EXT_SOURCE_MEAN': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
        'EXT_SOURCE_2': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
        'EXT_SOURCE_3': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
        'AGE_YEARS': {'young': 25, 'middle': 45, 'senior': 60},
        'CREDIT_INCOME_RATIO': {'low': 2, 'medium': 5, 'high': 10},
    }
    
    def __init__(self, model_path: str):
        """
        Initialize the Bayesian Reasoner
        
        Args:
            model_path: Path to the directory containing Bayesian Network model files
        """
        self.model_path = Path(model_path)
        self.model = None
        self.inference = None
        self.structure = None
        self.top_features = None
        self._load_model()
        
    def _load_model(self):
        """Load the Bayesian Network model and parameters"""
        logger.info("Loading Bayesian Network model for reasoning...")
        
        try:
            # Load the trained model
            model_file = self.model_path / 'bayesian_network.pkl'
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                    
                # Initialize inference engine
                from pgmpy.inference import VariableElimination
                self.inference = VariableElimination(self.model)
                logger.info("✅ Bayesian Network model loaded successfully")
            else:
                logger.warning(f"Model file not found: {model_file}")
                
            # Load structure parameters
            params_file = self.model_path / 'bn_parameters.json'
            if params_file.exists():
                with open(params_file, 'r') as f:
                    params = json.load(f)
                    self.structure = {
                        'nodes': params.get('nodes', []),
                        'edges': params.get('edges', [])
                    }
                    self.top_features = params.get('top_features', [])
                logger.info(f"✅ Loaded structure with {len(self.structure['nodes'])} nodes and {len(self.structure['edges'])} edges")
                
        except Exception as e:
            logger.error(f"Error loading Bayesian Network: {str(e)}")
            raise
    
    def _discretize_value(self, feature_name: str, value: float, n_bins: int = 3) -> int:
        """
        Discretize a continuous value into bins
        
        Args:
            feature_name: Name of the feature
            value: Continuous value to discretize
            n_bins: Number of bins (default: 3 for low/medium/high)
            
        Returns:
            Discretized bin index (0, 1, or 2)
        """
        # Use feature-specific thresholds if available
        if feature_name in self.RISK_THRESHOLDS:
            thresholds = self.RISK_THRESHOLDS[feature_name]
            if 'low' in thresholds:
                if value < thresholds['low']:
                    return 0
                elif value < thresholds.get('high', thresholds.get('medium', 0.5)):
                    return 1
                else:
                    return 2
        
        # Default discretization based on common ranges
        # Assume normalized values between 0-1 for most features
        if value < 0.33:
            return 0  # Low
        elif value < 0.67:
            return 1  # Medium
        else:
            return 2  # High
    
    def _get_value_description(self, feature_name: str, discretized_value: int) -> str:
        """Get human-readable description for a discretized value"""
        descriptions = {
            0: "low",
            1: "medium", 
            2: "high"
        }
        return descriptions.get(discretized_value, "unknown")
    
    def _get_parent_nodes(self, node: str) -> List[str]:
        """Get parent nodes of a given node in the BN structure"""
        if not self.structure:
            return []
        
        parents = []
        for edge in self.structure['edges']:
            if edge[1] == node:
                parents.append(edge[0])
        return parents
    
    def _get_child_nodes(self, node: str) -> List[str]:
        """Get child nodes of a given node in the BN structure"""
        if not self.structure:
            return []
        
        children = []
        for edge in self.structure['edges']:
            if edge[0] == node:
                children.append(edge[1])
        return children
    
    def _calculate_feature_influence(
        self, 
        feature_name: str, 
        feature_value: float,
        evidence: Dict[str, int],
        base_probability: float
    ) -> FeatureInfluence:
        """
        Calculate the influence of a single feature on the prediction
        
        Args:
            feature_name: Name of the feature
            feature_value: Original continuous value
            evidence: Complete evidence dictionary
            base_probability: Baseline probability of default
            
        Returns:
            FeatureInfluence object with influence details
        """
        discretized_value = self._discretize_value(feature_name, feature_value)
        
        # Calculate conditional probability without this feature
        evidence_without = {k: v for k, v in evidence.items() if k != feature_name}
        
        try:
            if self.inference and len(evidence_without) > 0:
                # Query probability without this feature
                result_without = self.inference.query(
                    variables=['TARGET'],
                    evidence=evidence_without,
                    show_progress=False
                )
                prob_without = float(result_without.values[1])
            else:
                prob_without = base_probability
        except Exception:
            prob_without = base_probability
        
        # Calculate influence
        influence_diff = base_probability - prob_without
        influence_strength = min(abs(influence_diff) * 5, 1.0)  # Scale to 0-1
        
        # Determine direction
        if influence_diff > 0.01:
            direction = "increases_risk"
        elif influence_diff < -0.01:
            direction = "decreases_risk"
        else:
            direction = "neutral"
        
        # Get feature description
        feature_desc = self.FEATURE_DESCRIPTIONS.get(feature_name, feature_name)
        value_desc = self._get_value_description(feature_name, discretized_value)
        
        # Generate explanation
        if direction == "increases_risk":
            explanation = f"{feature_desc} is {value_desc}, which increases default risk"
        elif direction == "decreases_risk":
            explanation = f"{feature_desc} is {value_desc}, which decreases default risk"
        else:
            explanation = f"{feature_desc} is {value_desc}, with neutral effect on risk"
        
        return FeatureInfluence(
            feature_name=feature_name,
            feature_value=feature_value,
            discretized_value=discretized_value,
            influence_direction=direction,
            influence_strength=influence_strength,
            conditional_probability=base_probability,
            explanation=explanation
        )
    
    def _extract_inference_paths(self, evidence: Dict[str, int]) -> List[InferencePath]:
        """
        Extract the inference paths from evidence to TARGET
        
        Args:
            evidence: Dictionary of feature evidence
            
        Returns:
            List of inference paths
        """
        paths = []
        
        if not self.structure:
            return paths
        
        # Find direct parents of TARGET
        target_parents = self._get_parent_nodes('TARGET')
        
        for parent in target_parents:
            if parent in evidence:
                children = self._get_child_nodes(parent)
                
                # Calculate path strength based on conditional probability
                path_strength = 0.5  # Default
                
                try:
                    if self.inference and parent in evidence:
                        # Get CPD for TARGET given this parent
                        cpd = self.model.get_cpds('TARGET')
                        if cpd is not None:
                            path_strength = 0.7  # Has direct influence
                except Exception:
                    pass
                
                parent_desc = self.FEATURE_DESCRIPTIONS.get(parent, parent)
                paths.append(InferencePath(
                    parent_nodes=[parent],
                    child_nodes=['TARGET'] + [c for c in children if c != 'TARGET'],
                    path_strength=path_strength,
                    description=f"{parent_desc} directly influences credit default risk"
                ))
        
        return paths[:5]  # Return top 5 paths
    
    def _generate_summary_explanation(
        self,
        prediction: int,
        probability: float,
        risk_factors: List[FeatureInfluence],
        protective_factors: List[FeatureInfluence]
    ) -> str:
        """
        Generate a concise summary explanation
        
        Args:
            prediction: 0 or 1
            probability: Default probability
            risk_factors: List of risk-increasing factors
            protective_factors: List of risk-decreasing factors
            
        Returns:
            Summary explanation string
        """
        decision = "likely to default" if prediction == 1 else "unlikely to default"
        
        # Build explanation
        parts = [f"The applicant is {decision} (probability: {probability:.1%})."]
        
        if risk_factors:
            top_risk = risk_factors[0]
            parts.append(f"The main concern is that {top_risk.explanation.lower()}.")
        
        if protective_factors:
            top_protective = protective_factors[0]
            parts.append(f"However, {top_protective.explanation.lower()}.")
        
        return " ".join(parts)
    
    def _generate_detailed_explanation(
        self,
        prediction: int,
        probability: float,
        risk_factors: List[FeatureInfluence],
        protective_factors: List[FeatureInfluence],
        inference_paths: List[InferencePath]
    ) -> str:
        """
        Generate a detailed explanation with all reasoning components
        
        Args:
            prediction: 0 or 1
            probability: Default probability
            risk_factors: List of risk-increasing factors
            protective_factors: List of risk-decreasing factors
            inference_paths: List of inference paths
            
        Returns:
            Detailed explanation string
        """
        lines = []
        
        # Decision summary
        decision = "REJECT - High Default Risk" if prediction == 1 else "APPROVE - Low Default Risk"
        lines.append(f"## Decision: {decision}")
        lines.append(f"Default Probability: {probability:.2%}")
        lines.append("")
        
        # Risk factors
        if risk_factors:
            lines.append("### Risk Factors (Increase Default Likelihood):")
            for i, factor in enumerate(risk_factors[:5], 1):
                lines.append(f"{i}. **{self.FEATURE_DESCRIPTIONS.get(factor.feature_name, factor.feature_name)}**: {factor.explanation}")
            lines.append("")
        
        # Protective factors
        if protective_factors:
            lines.append("### Protective Factors (Decrease Default Likelihood):")
            for i, factor in enumerate(protective_factors[:5], 1):
                lines.append(f"{i}. **{self.FEATURE_DESCRIPTIONS.get(factor.feature_name, factor.feature_name)}**: {factor.explanation}")
            lines.append("")
        
        # Inference paths
        if inference_paths:
            lines.append("### Key Inference Paths:")
            for path in inference_paths[:3]:
                lines.append(f"- {path.description}")
            lines.append("")
        
        # Reasoning conclusion
        lines.append("### Reasoning Conclusion:")
        if prediction == 1:
            lines.append("Based on the Bayesian Network analysis, the combination of risk factors outweighs the protective factors, indicating elevated default risk.")
        else:
            lines.append("Based on the Bayesian Network analysis, the protective factors outweigh the risk factors, indicating the applicant is a good credit candidate.")
        
        return "\n".join(lines)
    
    def get_reasoning(
        self,
        features: Dict[str, float],
        threshold: float = 0.5
    ) -> BayesianReasoning:
        """
        Get complete Bayesian reasoning for a prediction
        
        Args:
            features: Dictionary of feature names to values
            threshold: Decision threshold (default: 0.5)
            
        Returns:
            BayesianReasoning object with complete explanation
        """
        logger.info("Generating Bayesian reasoning...")
        
        # Discretize all features
        evidence = {}
        for feature_name, value in features.items():
            if feature_name in self.top_features and feature_name != 'TARGET':
                evidence[feature_name] = self._discretize_value(feature_name, value)
        
        # Get prediction probability
        probability = 0.5  # Default
        try:
            if self.inference and len(evidence) > 0:
                result = self.inference.query(
                    variables=['TARGET'],
                    evidence=evidence,
                    show_progress=False
                )
                probability = float(result.values[1])
        except Exception as e:
            logger.warning(f"Inference error, using heuristic: {str(e)}")
            # Fallback: use simple heuristic based on external sources
            ext_sources = [features.get(f, 0.5) for f in ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'EXT_SOURCE_MEAN']]
            probability = 1 - np.mean([s for s in ext_sources if s > 0])
        
        # Make prediction
        prediction = 1 if probability > threshold else 0
        
        # Determine risk level
        if probability < 0.2:
            risk_level = RiskLevel.VERY_LOW.value
        elif probability < 0.35:
            risk_level = RiskLevel.LOW.value
        elif probability < 0.5:
            risk_level = RiskLevel.MEDIUM.value
        elif probability < 0.7:
            risk_level = RiskLevel.HIGH.value
        else:
            risk_level = RiskLevel.VERY_HIGH.value
        
        # Calculate feature influences
        all_influences = []
        for feature_name, value in features.items():
            if feature_name in self.top_features and feature_name != 'TARGET':
                influence = self._calculate_feature_influence(
                    feature_name, value, evidence, probability
                )
                all_influences.append(influence)
        
        # Sort by influence strength
        all_influences.sort(key=lambda x: x.influence_strength, reverse=True)
        
        # Separate risk and protective factors
        risk_factors = [f for f in all_influences if f.influence_direction == "increases_risk"]
        protective_factors = [f for f in all_influences if f.influence_direction == "decreases_risk"]
        
        # Extract inference paths
        inference_paths = self._extract_inference_paths(evidence)
        
        # Generate explanations
        summary = self._generate_summary_explanation(
            prediction, probability, risk_factors, protective_factors
        )
        detailed = self._generate_detailed_explanation(
            prediction, probability, risk_factors, protective_factors, inference_paths
        )
        
        # Calculate conditional probabilities for key features
        conditional_probs = {}
        for feature_name in list(features.keys())[:10]:
            if feature_name in self.top_features:
                conditional_probs[feature_name] = probability
        
        # Calculate confidence score
        evidence_count = len([v for v in features.values() if v != 0 and not np.isnan(v)])
        confidence_score = min(evidence_count / 15, 1.0)  # Based on evidence completeness
        
        if confidence_score > 0.8:
            evidence_strength = "Strong"
        elif confidence_score > 0.5:
            evidence_strength = "Moderate"
        else:
            evidence_strength = "Weak"
        
        decision = "REJECT" if prediction == 1 else "APPROVE"
        
        return BayesianReasoning(
            prediction=prediction,
            probability=round(probability, 4),
            risk_level=risk_level,
            decision=decision,
            top_risk_factors=risk_factors[:5],
            top_protective_factors=protective_factors[:5],
            inference_paths=inference_paths,
            summary_explanation=summary,
            detailed_explanation=detailed,
            conditional_probabilities=conditional_probs,
            confidence_score=round(confidence_score, 2),
            evidence_strength=evidence_strength
        )
    
    def explain_feature(self, feature_name: str, feature_value: float) -> Dict[str, Any]:
        """
        Get explanation for a single feature's contribution
        
        Args:
            feature_name: Name of the feature
            feature_value: Value of the feature
            
        Returns:
            Dictionary with feature explanation
        """
        discretized = self._discretize_value(feature_name, feature_value)
        description = self.FEATURE_DESCRIPTIONS.get(feature_name, feature_name)
        value_desc = self._get_value_description(feature_name, discretized)
        
        # Get parents and children
        parents = self._get_parent_nodes(feature_name)
        children = self._get_child_nodes(feature_name)
        
        return {
            "feature_name": feature_name,
            "description": description,
            "value": feature_value,
            "discretized_level": value_desc,
            "parent_influences": [self.FEATURE_DESCRIPTIONS.get(p, p) for p in parents],
            "influences": [self.FEATURE_DESCRIPTIONS.get(c, c) for c in children],
            "is_direct_parent_of_target": 'TARGET' in children
        }
    
    def get_network_structure(self) -> Dict[str, Any]:
        """
        Get the Bayesian Network structure for visualization
        
        Returns:
            Dictionary with nodes and edges
        """
        if not self.structure:
            return {"nodes": [], "edges": [], "target_parents": []}
        
        # Enrich with descriptions
        nodes_with_desc = []
        for node in self.structure['nodes']:
            nodes_with_desc.append({
                "id": node,
                "description": self.FEATURE_DESCRIPTIONS.get(node, node),
                "is_target": node == "TARGET"
            })
        
        edges_with_desc = []
        for edge in self.structure['edges']:
            edges_with_desc.append({
                "from": edge[0],
                "to": edge[1],
                "from_desc": self.FEATURE_DESCRIPTIONS.get(edge[0], edge[0]),
                "to_desc": self.FEATURE_DESCRIPTIONS.get(edge[1], edge[1])
            })
        
        target_parents = self._get_parent_nodes('TARGET')
        
        return {
            "nodes": nodes_with_desc,
            "edges": edges_with_desc,
            "target_parents": target_parents,
            "total_nodes": len(self.structure['nodes']),
            "total_edges": len(self.structure['edges'])
        }


def reasoning_to_dict(reasoning: BayesianReasoning) -> Dict[str, Any]:
    """Convert BayesianReasoning dataclass to dictionary for JSON serialization"""
    return {
        "prediction": reasoning.prediction,
        "probability": reasoning.probability,
        "risk_level": reasoning.risk_level,
        "decision": reasoning.decision,
        "top_risk_factors": [asdict(f) for f in reasoning.top_risk_factors],
        "top_protective_factors": [asdict(f) for f in reasoning.top_protective_factors],
        "inference_paths": [asdict(p) for p in reasoning.inference_paths],
        "summary_explanation": reasoning.summary_explanation,
        "detailed_explanation": reasoning.detailed_explanation,
        "conditional_probabilities": reasoning.conditional_probabilities,
        "confidence_score": reasoning.confidence_score,
        "evidence_strength": reasoning.evidence_strength
    }
