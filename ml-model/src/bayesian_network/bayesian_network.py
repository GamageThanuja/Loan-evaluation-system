"""
Bayesian Network Module
========================
Structure learning, DAG fitting, AIC/BIC scoring,
DAG visualisation, and risk-embedding extraction for
the hybrid deep learning + Bayesian Network system.
"""

import json
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.estimators import HillClimbSearch, BIC, MaximumLikelihoodEstimator
from pgmpy.models import DiscreteBayesianNetwork as PgmpyBN
from pgmpy.inference import VariableElimination

from src.configuration.config import Config

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class BayesianNetworkModel:
    """Bayesian Network for causal structure learning and reasoning."""

    def __init__(self):
        self.model: PgmpyBN = None
        self.inference_engine = None
        self.feature_names: list = []
        self.discretised_data: pd.DataFrame = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: list):
        """Learn structure from data, fit CPDs, compute AIC/BIC.

        Parameters
        ----------
        X : np.ndarray  — scaled feature matrix (train set)
        y : np.ndarray  — binary target
        feature_names : list of str
        """
        self.feature_names = feature_names
        logger.info("  Learning Bayesian Network structure …")

        # Discretise continuous features into 3 bins (low, medium, high)
        df = pd.DataFrame(X, columns=feature_names)
        df[Config.TARGET_COLUMN] = y

        disc = df.copy()
        for col in feature_names:
            try:
                disc[col] = pd.qcut(df[col], q=3, labels=[0, 1, 2], duplicates="drop")
            except ValueError:
                disc[col] = pd.cut(df[col], bins=3, labels=[0, 1, 2])
        disc = disc.astype(int)
        self.discretised_data = disc

        # Structure learning — Hill Climb with BIC scoring
        hc = HillClimbSearch(disc)
        best_model = hc.estimate(
            scoring_method=BIC(disc),
            max_indegree=Config.BN_MAX_INDEGREE,
        )

        # Build Bayesian Network from learned edges
        self.model = PgmpyBN(best_model.edges())
        self.model.fit(disc, estimator=MaximumLikelihoodEstimator)
        self.inference_engine = VariableElimination(self.model)

        # Compute AIC / BIC
        aic, bic = self._compute_information_criteria(disc)

        logger.info(f"    Nodes : {len(self.model.nodes())}")
        logger.info(f"    Edges : {len(self.model.edges())}")
        logger.info(f"    AIC   : {aic:.2f}")
        logger.info(f"    BIC   : {bic:.2f}")

        return {"aic": aic, "bic": bic}

    # ------------------------------------------------------------------
    def get_risk_embeddings(self, X: np.ndarray) -> np.ndarray:
        """Compute Bayesian risk embeddings for each sample.

        For every row we query P(target | observed features) from the
        fitted BN and return the probability as an extra feature.
        """
        if self.model is None:
            raise RuntimeError("BN model not fitted yet.")

        df = pd.DataFrame(X, columns=self.feature_names)
        disc = df.copy()
        for col in self.feature_names:
            try:
                disc[col] = pd.qcut(df[col], q=3, labels=[0, 1, 2], duplicates="drop")
            except ValueError:
                disc[col] = pd.cut(df[col], bins=3, labels=[0, 1, 2])
        disc = disc.astype(int)

        embeddings = []
        target = Config.TARGET_COLUMN

        # Use a subset of the most connected parent features for inference
        parent_nodes = self._get_top_parents(target, max_parents=5)

        for _, row in disc.iterrows():
            evidence = {}
            for col in parent_nodes:
                if col in row.index and col != target:
                    evidence[col] = int(row[col])
            try:
                if evidence:
                    result = self.inference_engine.query([target], evidence=evidence)
                    prob = float(result.values[1])  # P(Approved=1)
                else:
                    prob = 0.5
            except Exception:
                prob = 0.5
            embeddings.append(prob)

        return np.array(embeddings).reshape(-1, 1)

    # ------------------------------------------------------------------
    def generate_dag_visualisation(self, tag: str = ""):
        """Save DAG as PNG."""
        if self.model is None:
            return

        out_dir = Config.DAG_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        G = nx.DiGraph(self.model.edges())
        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, k=2.5, seed=Config.RANDOM_SEED)

        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#4FC3F7", alpha=0.9)
        nx.draw_networkx_edges(G, pos, edge_color="#90A4AE", arrows=True,
                               arrowsize=20, width=2, connectionstyle="arc3,rad=0.1")
        labels = {n: n.replace("_", "\n") for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight="bold")

        title = f"Bayesian Network DAG{' — ' + tag if tag else ''}"
        plt.title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        filename = f"dag{'_' + tag if tag else ''}.png"
        plt.savefig(out_dir / filename, dpi=150, bbox_inches="tight")
        plt.close()

        logger.info(f"  ✓ DAG saved → {out_dir / filename}")

    # ------------------------------------------------------------------
    def get_bn_metrics(self) -> dict:
        """Return AIC, BIC, node/edge counts."""
        if self.model is None:
            return {}
        aic, bic = self._compute_information_criteria(self.discretised_data)
        return {
            "aic": aic,
            "bic": bic,
            "nodes": len(self.model.nodes()),
            "edges": len(self.model.edges()),
        }

    # ------------------------------------------------------------------
    def explain(self, features: dict) -> dict:
        """Return Bayesian reasoning for a single sample."""
        if self.model is None:
            return {"explanation": "BN not available"}

        target = Config.TARGET_COLUMN
        parent_nodes = self._get_top_parents(target, max_parents=5)

        # Discretise the input
        evidence = {}
        for col in parent_nodes:
            if col in features and col != target:
                val = features[col]
                # Simple 3-bin discretisation
                evidence[col] = int(min(max(round(val), 0), 2))

        try:
            if evidence:
                result = self.inference_engine.query([target], evidence=evidence)
                prob_approved = float(result.values[1])
            else:
                prob_approved = 0.5
        except Exception:
            prob_approved = 0.5

        return {
            "bn_probability": prob_approved,
            "evidence_used": evidence,
            "parent_features": parent_nodes,
        }

    # ------------------------------------------------------------------
    def save(self, path: Path = None):
        """Persist the BN model."""
        import joblib
        path = path or Config.MODELS_DIR / "bayesian_network.pkl"
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"  ✓ BN model saved → {path}")

    @classmethod
    def load(cls, path: Path = None) -> "BayesianNetworkModel":
        import joblib
        path = path or Config.MODELS_DIR / "bayesian_network.pkl"
        return joblib.load(path)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _compute_information_criteria(self, data: pd.DataFrame):
        """Compute AIC and BIC for the fitted BN."""
        n = len(data)
        log_likelihood = 0.0
        k = 0  # total parameters

        for cpd in self.model.get_cpds():
            k += cpd.values.size
            variable = cpd.variable
            parents = cpd.get_evidence()
            for _, row in data.iterrows():
                var_val = int(row[variable])
                if parents:
                    parent_vals = tuple(int(row[p]) for p in parents)
                    try:
                        prob = cpd.get_value(**{variable: var_val,
                                                **{p: v for p, v in zip(parents, parent_vals)}})
                    except Exception:
                        prob = 1e-10
                else:
                    try:
                        prob = cpd.values.flatten()[var_val]
                    except Exception:
                        prob = 1e-10
                log_likelihood += np.log(max(prob, 1e-10))

        aic = 2 * k - 2 * log_likelihood
        bic = k * np.log(n) - 2 * log_likelihood
        return aic, bic

    def _get_top_parents(self, target: str, max_parents: int = 5) -> list:
        """Return the parent nodes of the target, or the most-connected nodes."""
        if target in self.model.nodes():
            parents = list(self.model.get_parents(target))
            if parents:
                return parents[:max_parents]

        # Fallback: most connected nodes
        degree = dict(nx.DiGraph(self.model.edges()).degree())
        sorted_nodes = sorted(degree, key=degree.get, reverse=True)
        return [n for n in sorted_nodes if n != target][:max_parents]
