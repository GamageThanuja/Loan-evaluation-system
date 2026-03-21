"""
Configuration Module
====================
Centralised paths, hyperparameters, and constants for the
Hybrid Deep Learning + Bayesian Network loan evaluation system.
"""

import os
import torch
from pathlib import Path

# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # ml-model/
BACKEND_ROOT = PROJECT_ROOT.parent / "backend"

class Config:
    """Single source of truth for every configurable value."""

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    PROJECT_ROOT = PROJECT_ROOT

    # Dataset
    RAW_DATA_DIR   = PROJECT_ROOT / "dataset" / "raw_data"
    PROCESSED_DIR  = PROJECT_ROOT / "dataset" / "processed_data"
    RAW_CSV        = RAW_DATA_DIR / "loan_approval_dataset.csv"

    # Legacy data dir (copy raw CSV here if it only exists under data/)
    LEGACY_RAW_DIR = PROJECT_ROOT / "data" / "raw"

    # Models
    MODELS_DIR     = PROJECT_ROOT / "models"

    # Results
    RESULTS_DIR          = PROJECT_ROOT / "results"
    BASELINE_DIR         = RESULTS_DIR / "baseline_models"
    TUNED_DIR            = RESULTS_DIR / "tuned_models"
    DAG_DIR              = RESULTS_DIR / "dag_visualizations"
    EVAL_METRICS_DIR     = RESULTS_DIR / "evaluation_metrics"
    COMPARISON_DIR       = RESULTS_DIR / "model_comparison"

    # Reports
    REPORTS_DIR          = PROJECT_ROOT / "reports"
    EDA_REPORT_DIR       = REPORTS_DIR / "eda_report"
    PREPROCESS_REPORT_DIR = REPORTS_DIR / "preprocessing_report"
    HYBRID_ANALYSIS_DIR  = REPORTS_DIR / "hybrid_model_analysis"

    # ------------------------------------------------------------------
    # Random seed & device
    # ------------------------------------------------------------------
    RANDOM_SEED = 42
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # ------------------------------------------------------------------
    # Dataset
    # ------------------------------------------------------------------
    TARGET_COLUMN = "loan_status"
    ID_COLUMN = "loan_id"
    TEST_SIZE = 0.15
    VAL_SIZE  = 0.15  # from remaining after test split

    # ------------------------------------------------------------------
    # Feature engineering
    # ------------------------------------------------------------------
    CATEGORICAL_COLS = ["education", "self_employed"]
    NUMERICAL_COLS = [
        "no_of_dependents", "income_annum", "loan_amount", "loan_term",
        "cibil_score", "residential_assets_value", "commercial_assets_value",
        "luxury_assets_value", "bank_asset_value",
    ]

    # ------------------------------------------------------------------
    # Baseline hyperparameters (Phase 1 — no tuning)
    # ------------------------------------------------------------------
    BASELINE = {
        "ann": {
            "hidden_dims": [64, 32],
            "dropout": 0.3,
            "learning_rate": 1e-3,
            "batch_size": 64,
            "epochs": 100,
            "optimizer": "adam",
            "patience": 15,
        },
        "lstm": {
            "hidden_size": 64,
            "num_layers": 2,
            "dropout": 0.3,
            "learning_rate": 1e-3,
            "batch_size": 64,
            "epochs": 100,
            "optimizer": "adam",
            "patience": 15,
        },
        "rnn": {
            "hidden_size": 64,
            "num_layers": 2,
            "dropout": 0.3,
            "learning_rate": 1e-3,
            "batch_size": 64,
            "epochs": 100,
            "optimizer": "adam",
            "patience": 15,
        },
    }

    # ------------------------------------------------------------------
    # Tuned hyperparameters (Phase 2 — after grid/manual tuning)
    # ------------------------------------------------------------------
    TUNED = {
        "ann": {
            "hidden_dims": [128, 64, 32],
            "dropout": 0.4,
            "learning_rate": 5e-4,
            "batch_size": 32,
            "epochs": 150,
            "optimizer": "adam",
            "patience": 20,
        },
        "lstm": {
            "hidden_size": 128,
            "num_layers": 3,
            "dropout": 0.4,
            "learning_rate": 5e-4,
            "batch_size": 32,
            "epochs": 150,
            "optimizer": "adam",
            "patience": 20,
        },
        "rnn": {
            "hidden_size": 128,
            "num_layers": 3,
            "dropout": 0.4,
            "learning_rate": 5e-4,
            "batch_size": 32,
            "epochs": 150,
            "optimizer": "adam",
            "patience": 20,
        },
    }

    # ------------------------------------------------------------------
    # Bayesian Network
    # ------------------------------------------------------------------
    BN_MAX_INDEGREE = 3
    BN_SCORING_METHOD = "bicscore"

    # ------------------------------------------------------------------
    # Cross-validation
    # ------------------------------------------------------------------
    CV_FOLDS = 5

    # ------------------------------------------------------------------
    # Best model selection weights
    # ------------------------------------------------------------------
    SELECTION_WEIGHTS = {
        "f1": 0.40,
        "roc_auc": 0.30,
        "accuracy": 0.20,
        "rmse_inv": 0.10,  # 1 - RMSE
    }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @classmethod
    def ensure_directories(cls):
        """Create every directory in the layout if it does not exist."""
        for attr in dir(cls):
            val = getattr(cls, attr)
            if isinstance(val, Path) and attr.endswith("_DIR"):
                val.mkdir(parents=True, exist_ok=True)
        # Also create the models directory
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def ensure_raw_data(cls):
        """Copy raw CSV to the canonical location if it is elsewhere."""
        if not cls.RAW_CSV.exists():
            legacy = cls.LEGACY_RAW_DIR / "loan_approval_dataset.csv"
            if legacy.exists():
                cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(legacy, cls.RAW_CSV)
