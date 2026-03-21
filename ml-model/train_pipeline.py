#!/usr/bin/env python3
"""
Training Pipeline — Main Entry Point
======================================
Orchestrates the complete model development lifecycle:

  1. Preprocessing + EDA
  2. Bayesian Network structure learning
  3. Phase 1 — Baseline models (ANN+BN, LSTM+BN, RNN+BN)
  4. Phase 2 — Tuned models   (ANN+BN, LSTM+BN, RNN+BN)
  5. Evaluation of all 6 models
  6. Automatic best model selection
  7. K-Fold Cross-Validation on best model
  8. Save best model + registry
  9. Result regeneration

Usage:
    python train_pipeline.py
"""

import sys
import json
import logging
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np

# Ensure the ml-model directory is on the path
ML_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ML_ROOT))

from src.configuration.config import Config
from src.preprocessing.preprocessor import DataPreprocessor
from src.bayesian_network.bayesian_network import BayesianNetworkModel
from src.hybrid_models.ann_bayesian_network.model import ANNBayesianHybrid
from src.hybrid_models.lstm_bayesian_network.model import LSTMBayesianHybrid
from src.hybrid_models.rnn_bayesian_network.model import RNNBayesianHybrid
from src.evaluation.evaluator import ModelEvaluator

warnings.filterwarnings("ignore")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

np.random.seed(Config.RANDOM_SEED)

# Model class lookup
MODEL_CLASSES = {
    "ann": ANNBayesianHybrid,
    "lstm": LSTMBayesianHybrid,
    "rnn": RNNBayesianHybrid,
}

MODEL_LABELS = {
    "ann":  "ANN + BN",
    "lstm": "LSTM + BN",
    "rnn":  "RNN + BN",
}


# ======================================================================
# Helper: build kwargs from config preset
# ======================================================================
def _build_kwargs(arch: str, preset: dict, input_dim: int) -> dict:
    """Translate a config preset dict into model constructor kwargs."""
    common = dict(
        learning_rate=preset["learning_rate"],
        batch_size=preset["batch_size"],
        epochs=preset["epochs"],
        patience=preset["patience"],
        device=Config.DEVICE,
    )

    if arch == "ann":
        return dict(
            input_dim=input_dim,
            hidden_dims=preset["hidden_dims"],
            dropout=preset["dropout"],
            **common,
        )
    else:  # lstm / rnn
        return dict(
            input_dim=input_dim,
            hidden_size=preset["hidden_size"],
            num_layers=preset["num_layers"],
            dropout=preset["dropout"],
            **common,
        )


# ======================================================================
# Main pipeline
# ======================================================================
def main():
    start_time = datetime.now()
    logger.info("=" * 64)
    logger.info("  LOAN APPROVAL HYBRID DL + BN — TRAINING PIPELINE")
    logger.info(f"  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 64)

    Config.ensure_directories()
    Config.ensure_raw_data()

    # ------------------------------------------------------------------
    # Clear old results
    # ------------------------------------------------------------------
    ModelEvaluator.clear_previous_results()

    # ------------------------------------------------------------------
    # STEP 1 — Preprocessing + EDA
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 1: PREPROCESSING & EDA")
    logger.info("=" * 64)

    preprocessor = DataPreprocessor()
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.run()
    feature_names = preprocessor.feature_names

    # ------------------------------------------------------------------
    # STEP 2 — Bayesian Network
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 2: BAYESIAN NETWORK")
    logger.info("=" * 64)

    bn_model = BayesianNetworkModel()
    bn_metrics = bn_model.fit(X_train, y_train, feature_names)
    bn_model.generate_dag_visualisation(tag="structure")

    # Risk embeddings
    logger.info("  Computing Bayesian risk embeddings …")
    emb_train = bn_model.get_risk_embeddings(X_train)
    emb_val   = bn_model.get_risk_embeddings(X_val)
    emb_test  = bn_model.get_risk_embeddings(X_test)

    X_train_aug = np.hstack([X_train, emb_train])
    X_val_aug   = np.hstack([X_val,   emb_val])
    X_test_aug  = np.hstack([X_test,  emb_test])

    input_dim = X_train_aug.shape[1]
    logger.info(f"  Augmented input dimension: {input_dim}")

    # Save BN model
    bn_model.save()

    # ------------------------------------------------------------------
    # STEP 3 — Phase 1: Baseline Models
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 3 — PHASE 1: BASELINE MODELS (default params)")
    logger.info("=" * 64)

    baseline_evaluator = ModelEvaluator()
    baseline_models = {}

    for arch in ["ann", "lstm", "rnn"]:
        label = f"{MODEL_LABELS[arch]} Baseline"
        logger.info(f"\n  Training {label} …")

        kwargs = _build_kwargs(arch, Config.BASELINE[arch], input_dim)
        model = MODEL_CLASSES[arch](**kwargs)
        history = model.train(X_train_aug, y_train, X_val_aug, y_val)

        y_proba = model.predict_proba(X_test_aug)
        y_pred  = (y_proba >= 0.5).astype(int)

        metrics = baseline_evaluator.evaluate_model(
            label, y_test, y_proba, y_pred, history=history, bn_metrics=bn_metrics,
        )
        _print_metrics(label, metrics)

        # Save baseline model
        save_path = Config.BASELINE_DIR / f"{arch}_bn_baseline.pth"
        model.save(str(save_path))
        baseline_models[arch] = model

    baseline_evaluator.generate_all_reports(phase_label="baseline")

    # ------------------------------------------------------------------
    # STEP 4 — Phase 2: Tuned Models
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 4 — PHASE 2: TUNED MODELS (optimised params)")
    logger.info("=" * 64)

    tuned_evaluator = ModelEvaluator()
    tuned_models = {}

    for arch in ["ann", "lstm", "rnn"]:
        label = f"{MODEL_LABELS[arch]} Tuned"
        logger.info(f"\n  Training {label} …")

        kwargs = _build_kwargs(arch, Config.TUNED[arch], input_dim)
        model = MODEL_CLASSES[arch](**kwargs)
        history = model.train(X_train_aug, y_train, X_val_aug, y_val)

        y_proba = model.predict_proba(X_test_aug)
        y_pred  = (y_proba >= 0.5).astype(int)

        metrics = tuned_evaluator.evaluate_model(
            label, y_test, y_proba, y_pred, history=history, bn_metrics=bn_metrics,
        )
        _print_metrics(label, metrics)

        save_path = Config.TUNED_DIR / f"{arch}_bn_tuned.pth"
        model.save(str(save_path))
        tuned_models[arch] = model

    tuned_evaluator.generate_all_reports(phase_label="tuned")

    # ------------------------------------------------------------------
    # STEP 5 — Full Comparison (all 6 models)
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 5: MODEL COMPARISON")
    logger.info("=" * 64)

    combined_evaluator = ModelEvaluator()
    combined_evaluator.results.update(baseline_evaluator.results)
    combined_evaluator.results.update(tuned_evaluator.results)

    comp_table = combined_evaluator.generate_comparison_table()
    logger.info(f"\n{comp_table.to_string()}\n")

    combined_evaluator.plot_roc_curves(Config.COMPARISON_DIR)
    combined_evaluator.plot_comparison_bar_chart(Config.COMPARISON_DIR)

    # Save full comparison
    comp_table.to_csv(Config.COMPARISON_DIR / "full_comparison.csv")
    with open(Config.COMPARISON_DIR / "full_comparison.json", "w") as f:
        metrics_all = {n: d["metrics"] for n, d in combined_evaluator.results.items()}
        json.dump(metrics_all, f, indent=2)

    # ------------------------------------------------------------------
    # STEP 6 — Automatic Best Model Selection
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 6: AUTOMATIC BEST MODEL SELECTION")
    logger.info("=" * 64)

    best_label = combined_evaluator.select_best_model()
    best_metrics = combined_evaluator.results[best_label]["metrics"]

    # Determine architecture and phase from the label
    best_arch = None
    best_phase = None
    for arch in ["ann", "lstm", "rnn"]:
        if MODEL_LABELS[arch].lower() in best_label.lower():
            best_arch = arch
            best_phase = "tuned" if "tuned" in best_label.lower() else "baseline"
            break

    # Get the actual model object
    if best_phase == "tuned":
        best_model = tuned_models[best_arch]
    else:
        best_model = baseline_models[best_arch]

    # ------------------------------------------------------------------
    # STEP 7 — Cross-Validation on Best Model
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 7: K-FOLD CROSS-VALIDATION")
    logger.info("=" * 64)
    logger.info(f"  Selected model: {best_label}")

    preset = Config.TUNED[best_arch] if best_phase == "tuned" else Config.BASELINE[best_arch]
    cv_kwargs = _build_kwargs(best_arch, preset, input_dim)

    # Combine train + val for CV (test stays held out)
    X_cv = np.vstack([X_train_aug, X_val_aug])
    y_cv = np.concatenate([y_train, y_val])

    cv_results = ModelEvaluator.cross_validate(
        model_cls=MODEL_CLASSES[best_arch],
        model_kwargs=cv_kwargs,
        X=X_cv, y=y_cv,
        k=Config.CV_FOLDS,
    )

    # Save CV results
    with open(Config.EVAL_METRICS_DIR / "cross_validation_results.json", "w") as f:
        json.dump(cv_results, f, indent=2)

    # ------------------------------------------------------------------
    # STEP 8 — Save Best Model + Registry
    # ------------------------------------------------------------------
    logger.info("\n" + "=" * 64)
    logger.info("  STEP 8: SAVING BEST MODEL")
    logger.info("=" * 64)

    best_model_path = Config.MODELS_DIR / "best_model.pth"
    best_model.save(str(best_model_path))

    registry = {
        "best_model": {
            "name": best_label,
            "architecture": best_arch.upper(),
            "phase": best_phase,
            "path": "best_model.pth",
            "bayesian_network_path": "bayesian_network.pkl",
            "metrics": best_metrics,
            "cross_validation": cv_results,
            "selection_weights": Config.SELECTION_WEIGHTS,
            "feature_names": feature_names + ["bn_risk_embedding"],
            "input_dim": input_dim,
            "hyperparameters": preset,
            "created_at": datetime.now().isoformat(),
        },
        "all_models": {n: d["metrics"] for n, d in combined_evaluator.results.items()},
        "bayesian_network": bn_metrics,
    }

    with open(Config.MODELS_DIR / "model_registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    # Also save feature_names for the backend to load
    with open(Config.PROCESSED_DIR / "feature_names.json", "w") as f:
        json.dump(feature_names, f, indent=2)

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    elapsed = datetime.now() - start_time
    logger.info("\n" + "=" * 64)
    logger.info("  PIPELINE COMPLETE")
    logger.info("=" * 64)
    logger.info(f"  Best model     : {best_label}")
    logger.info(f"  F1 Score       : {best_metrics['f1']:.4f}")
    logger.info(f"  ROC-AUC        : {best_metrics['roc_auc']:.4f}")
    logger.info(f"  Accuracy       : {best_metrics['accuracy']:.4f}")
    logger.info(f"  CV Mean F1     : {cv_results['f1_mean']:.4f} ± {cv_results['f1_std']:.4f}")
    logger.info(f"  Elapsed time   : {elapsed}")
    logger.info("=" * 64)


# ======================================================================
# Utilities
# ======================================================================
def _print_metrics(label: str, metrics: dict):
    logger.info(f"  {label} Results:")
    logger.info(f"    Accuracy  : {metrics['accuracy']*100:.2f}%")
    logger.info(f"    Precision : {metrics['precision']*100:.2f}%")
    logger.info(f"    Recall    : {metrics['recall']*100:.2f}%")
    logger.info(f"    F1 Score  : {metrics['f1']*100:.2f}%")
    logger.info(f"    ROC-AUC   : {metrics['roc_auc']*100:.2f}%")
    logger.info(f"    MSE       : {metrics['mse']:.4f}")
    logger.info(f"    RMSE      : {metrics['rmse']:.4f}")


if __name__ == "__main__":
    main()
