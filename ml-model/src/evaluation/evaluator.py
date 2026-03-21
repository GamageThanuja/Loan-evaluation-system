"""
Model Evaluation Module
========================
Comprehensive evaluation, comparison, automatic best-model selection,
K-Fold cross-validation, and result regeneration.
"""

import json
import shutil
import logging
import warnings
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_squared_error, confusion_matrix,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold

from src.configuration.config import Config

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate, compare, and select the best hybrid model."""

    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Core metrics
    # ------------------------------------------------------------------
    def evaluate_model(
        self, model_name: str, y_true: np.ndarray,
        y_proba: np.ndarray, y_pred: np.ndarray,
        history: dict = None, bn_metrics: dict = None,
    ) -> dict:
        """Compute all metrics for a single model."""

        rmse = float(np.sqrt(mean_squared_error(y_true, y_proba)))
        metrics = {
            "accuracy":  float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall":    float(recall_score(y_true, y_pred, zero_division=0)),
            "f1":        float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc":   float(roc_auc_score(y_true, y_proba)),
            "mse":       float(mean_squared_error(y_true, y_proba)),
            "rmse":      rmse,
        }

        if bn_metrics:
            metrics["aic"] = bn_metrics.get("aic", 0.0)
            metrics["bic"] = bn_metrics.get("bic", 0.0)

        self.results[model_name] = {
            "metrics": metrics,
            "y_true": y_true,
            "y_proba": y_proba,
            "y_pred": y_pred,
            "history": history or {},
        }

        return metrics

    # ------------------------------------------------------------------
    # Visualisations
    # ------------------------------------------------------------------
    def plot_confusion_matrix(self, model_name: str, out_dir: Path):
        """Save confusion matrix PNG."""
        data = self.results[model_name]
        cm = confusion_matrix(data["y_true"], data["y_pred"])

        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["Rejected", "Approved"],
                    yticklabels=["Rejected", "Approved"], annot_kws={"size": 14})
        ax.set_xlabel("Predicted", fontsize=12)
        ax.set_ylabel("Actual", fontsize=12)
        ax.set_title(f"Confusion Matrix — {model_name}", fontsize=13, fontweight="bold")
        plt.tight_layout()

        fname = f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
        plt.savefig(out_dir / fname, dpi=150, bbox_inches="tight")
        plt.close()

    def plot_roc_curves(self, out_dir: Path):
        """Overlay ROC curves of all evaluated models."""
        fig, ax = plt.subplots(figsize=(10, 7))
        colours = plt.cm.tab10.colors

        for i, (name, data) in enumerate(self.results.items()):
            fpr, tpr, _ = roc_curve(data["y_true"], data["y_proba"])
            auc = data["metrics"]["roc_auc"]
            ax.plot(fpr, tpr, lw=2, color=colours[i % len(colours)],
                    label=f"{name} (AUC={auc:.4f})")

        ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6)
        ax.set_xlabel("False Positive Rate", fontsize=12)
        ax.set_ylabel("True Positive Rate", fontsize=12)
        ax.set_title("ROC Curves — Model Comparison", fontsize=14, fontweight="bold")
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / "roc_curves_comparison.png", dpi=150, bbox_inches="tight")
        plt.close()

    def plot_loss_curves(self, model_name: str, out_dir: Path):
        """Plot training and validation loss curves."""
        history = self.results.get(model_name, {}).get("history", {})
        if not history.get("train_loss"):
            return
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        axes[0].plot(history["train_loss"], "b-", lw=2, label="Train Loss")
        if "val_loss" in history:
            axes[0].plot(history["val_loss"], "r--", lw=2, label="Val Loss")
        axes[0].set_xlabel("Epoch")
        axes[0].set_ylabel("Loss")
        axes[0].set_title(f"{model_name} — Loss Curves", fontweight="bold")
        axes[0].legend()
        axes[0].grid(alpha=0.3)

        if "val_auc" in history:
            axes[1].plot(history["val_auc"], "g-", lw=2, label="Val AUC")
        axes[1].set_xlabel("Epoch")
        axes[1].set_ylabel("Score")
        axes[1].set_title(f"{model_name} — Validation AUC", fontweight="bold")
        axes[1].legend()
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        fname = f"loss_curves_{model_name.lower().replace(' ', '_')}.png"
        plt.savefig(out_dir / fname, dpi=150, bbox_inches="tight")
        plt.close()

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------
    def generate_comparison_table(self) -> pd.DataFrame:
        """Return a DataFrame comparing all models."""
        rows = []
        for name, data in self.results.items():
            row = {"Model": name}
            row.update(data["metrics"])
            rows.append(row)
        return pd.DataFrame(rows).set_index("Model")

    def plot_comparison_bar_chart(self, out_dir: Path):
        """Bar chart comparing key metrics across models."""
        comp = self.generate_comparison_table()
        metric_cols = ["accuracy", "precision", "recall", "f1", "roc_auc"]
        present = [c for c in metric_cols if c in comp.columns]

        fig, ax = plt.subplots(figsize=(14, 7))
        comp[present].plot(kind="bar", ax=ax, edgecolor="black", width=0.8)

        ax.set_ylabel("Score", fontsize=12)
        ax.set_title("Model Performance Comparison", fontsize=14, fontweight="bold")
        ax.set_ylim(0, 1.1)
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(alpha=0.3, axis="y")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(out_dir / "comparison_bar_chart.png", dpi=150, bbox_inches="tight")
        plt.close()

    # ------------------------------------------------------------------
    # Best model selection
    # ------------------------------------------------------------------
    def select_best_model(self) -> str:
        """Programmatically select the best model based on weighted score."""
        weights = Config.SELECTION_WEIGHTS
        scores = {}

        for name, data in self.results.items():
            m = data["metrics"]
            weighted = (
                weights["f1"]       * m["f1"]
                + weights["roc_auc"]  * m["roc_auc"]
                + weights["accuracy"] * m["accuracy"]
                + weights["rmse_inv"] * (1.0 - m["rmse"])
            )
            scores[name] = weighted

        best = max(scores, key=scores.get)
        logger.info(f"  ✓ Best model: {best}  (score={scores[best]:.4f})")

        # Log all scores
        for name, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"    {name:30s} → {score:.4f}")

        return best

    # ------------------------------------------------------------------
    # K-Fold Cross-Validation
    # ------------------------------------------------------------------
    @staticmethod
    def cross_validate(model_cls, model_kwargs: dict,
                       X: np.ndarray, y: np.ndarray,
                       bn_model=None, feature_names=None,
                       k: int = None) -> dict:
        """Run stratified K-Fold CV on the best model class.

        Returns dict with mean and std of key metrics.
        """
        k = k or Config.CV_FOLDS
        kfold = StratifiedKFold(n_splits=k, shuffle=True, random_state=Config.RANDOM_SEED)
        fold_metrics = []

        logger.info(f"  Running {k}-Fold Cross Validation …")

        for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
            X_train_f, X_val_f = X[train_idx], X[val_idx]
            y_train_f, y_val_f = y[train_idx], y[val_idx]

            # Add BN embeddings if available
            if bn_model is not None:
                emb_train = bn_model.get_risk_embeddings(X_train_f)
                emb_val   = bn_model.get_risk_embeddings(X_val_f)
                X_train_f = np.hstack([X_train_f, emb_train])
                X_val_f   = np.hstack([X_val_f, emb_val])
                # Update input_dim in kwargs
                model_kwargs = {**model_kwargs, "input_dim": X_train_f.shape[1]}

            model = model_cls(**model_kwargs)
            model.train(X_train_f, y_train_f, X_val_f, y_val_f)

            y_proba = model.predict_proba(X_val_f)
            y_pred  = (y_proba >= 0.5).astype(int)

            fold_metrics.append({
                "accuracy":  accuracy_score(y_val_f, y_pred),
                "precision": precision_score(y_val_f, y_pred, zero_division=0),
                "recall":    recall_score(y_val_f, y_pred, zero_division=0),
                "f1":        f1_score(y_val_f, y_pred, zero_division=0),
                "roc_auc":   roc_auc_score(y_val_f, y_proba),
            })
            logger.info(f"    Fold {fold+1}/{k}: F1={fold_metrics[-1]['f1']:.4f}  AUC={fold_metrics[-1]['roc_auc']:.4f}")

        # Aggregate
        df = pd.DataFrame(fold_metrics)
        result = {}
        for col in df.columns:
            result[f"{col}_mean"] = float(df[col].mean())
            result[f"{col}_std"]  = float(df[col].std())

        logger.info(f"  ✓ CV complete — Mean F1: {result['f1_mean']:.4f} ± {result['f1_std']:.4f}")
        return result

    # ------------------------------------------------------------------
    # Result regeneration
    # ------------------------------------------------------------------
    @staticmethod
    def clear_previous_results():
        """Delete all previous result/report files before regenerating."""
        dirs_to_clear = [
            Config.BASELINE_DIR,
            Config.TUNED_DIR,
            Config.DAG_DIR,
            Config.EVAL_METRICS_DIR,
            Config.COMPARISON_DIR,
            Config.HYBRID_ANALYSIS_DIR,
        ]
        for d in dirs_to_clear:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)
        logger.info("  ✓ Previous results cleared")

    # ------------------------------------------------------------------
    # Generate all outputs
    # ------------------------------------------------------------------
    def generate_all_reports(self, phase_label: str = ""):
        """Generate every visualisation and save metrics JSON."""
        if "baseline" in phase_label.lower():
            out = Config.BASELINE_DIR
        elif "tuned" in phase_label.lower():
            out = Config.TUNED_DIR
        else:
            out = Config.EVAL_METRICS_DIR
        out.mkdir(parents=True, exist_ok=True)

        logger.info(f"  Generating reports → {out}")

        # Individual confusion matrices + loss curves
        for name in self.results:
            self.plot_confusion_matrix(name, out)
            self.plot_loss_curves(name, out)

        # ROC curves
        self.plot_roc_curves(out)

        # Bar chart comparison
        self.plot_comparison_bar_chart(out)

        # Metrics JSON
        metrics_dict = {}
        for name, data in self.results.items():
            metrics_dict[name] = data["metrics"]

        with open(out / "evaluation_metrics.json", "w") as f:
            json.dump(metrics_dict, f, indent=2)

        # Comparison CSV
        comp = self.generate_comparison_table()
        comp.to_csv(out / "comparison_table.csv")

        # Also save to comparison dir
        Config.COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
        comp.to_csv(Config.COMPARISON_DIR / f"comparison_{phase_label or 'all'}.csv")
        with open(Config.COMPARISON_DIR / f"metrics_{phase_label or 'all'}.json", "w") as f:
            json.dump(metrics_dict, f, indent=2)

        logger.info(f"  ✓ Reports saved to {out}")
