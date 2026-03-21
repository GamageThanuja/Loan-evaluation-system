"""
Data Preprocessing Pipeline
============================
Handles the complete data preprocessing workflow:
  1. Load raw CSV
  2. EDA report generation
  3. Data cleaning (missing values, duplicates, outliers)
  4. Feature engineering
  5. Encoding categorical variables
  6. Feature scaling
  7. Train / validation / test split
  8. Class imbalance handling (SMOTE)
  9. Save processed artefacts
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
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from imblearn.over_sampling import SMOTE

from src.configuration.config import Config

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """End-to-end data preprocessing for the loan approval dataset."""

    def __init__(self):
        Config.ensure_directories()
        Config.ensure_raw_data()
        self.scaler = StandardScaler()
        self.label_encoders: dict = {}
        self.feature_names: list = []

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def run(self):
        """Execute the full preprocessing pipeline.

        Returns
        -------
        X_train, X_val, X_test, y_train, y_val, y_test : np.ndarray
        """
        logger.info("=" * 60)
        logger.info("  DATA PREPROCESSING PIPELINE")
        logger.info("=" * 60)

        # 1. Load
        df = self._load_data()

        # 2. EDA
        self._generate_eda_report(df)

        # 3. Clean
        df = self._clean_data(df)

        # 4. Feature engineering
        df = self._engineer_features(df)

        # 5. Encode categoricals
        df = self._encode_categoricals(df)

        # 6. Separate features / target
        X = df.drop(columns=[Config.TARGET_COLUMN])
        y = df[Config.TARGET_COLUMN].values

        self.feature_names = X.columns.tolist()

        # 7. Split
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=Config.TEST_SIZE + Config.VAL_SIZE,
            random_state=Config.RANDOM_SEED,
            stratify=y,
        )
        relative_val = Config.VAL_SIZE / (Config.TEST_SIZE + Config.VAL_SIZE)
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=1 - relative_val,
            random_state=Config.RANDOM_SEED,
            stratify=y_temp,
        )

        # 8. Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled   = self.scaler.transform(X_val)
        X_test_scaled  = self.scaler.transform(X_test)

        # 9. SMOTE (only on training set)
        smote = SMOTE(random_state=Config.RANDOM_SEED)
        X_train_bal, y_train_bal = smote.fit_resample(X_train_scaled, y_train)

        logger.info(f"  Train (after SMOTE): {X_train_bal.shape}")
        logger.info(f"  Validation:          {X_val_scaled.shape}")
        logger.info(f"  Test:                {X_test_scaled.shape}")

        # 10. Save artefacts
        self._save_artefacts(
            X_train_bal, X_val_scaled, X_test_scaled,
            y_train_bal, y_val, y_test,
        )
        self._generate_preprocessing_report(
            df, X_train_bal, y_train_bal, X_val_scaled, X_test_scaled,
        )

        logger.info("  ✓ Preprocessing complete")
        return (
            X_train_bal, X_val_scaled, X_test_scaled,
            y_train_bal, y_val, y_test,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_data(self) -> pd.DataFrame:
        logger.info("  Loading raw data …")
        df = pd.read_csv(Config.RAW_CSV)
        # Strip whitespace from column names and string columns
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()
        logger.info(f"  Loaded {df.shape[0]} rows × {df.shape[1]} columns")
        return df

    # ------------------------------------------------------------------
    def _generate_eda_report(self, df: pd.DataFrame):
        """Create EDA visualisations and save to reports/eda_report/."""
        out = Config.EDA_REPORT_DIR
        out.mkdir(parents=True, exist_ok=True)

        logger.info("  Generating EDA report …")

        # --- Dataset overview ---
        overview = {
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "dtypes": {c: str(d) for c, d in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": int(df.duplicated().sum()),
            "target_distribution": df[Config.TARGET_COLUMN].value_counts().to_dict(),
        }
        with open(out / "dataset_overview.json", "w") as f:
            json.dump(overview, f, indent=2, default=str)

        # --- Numerical distributions (histograms) ---
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if Config.ID_COLUMN in num_cols:
            num_cols.remove(Config.ID_COLUMN)

        n = len(num_cols)
        fig, axes = plt.subplots(
            nrows=(n + 2) // 3, ncols=3, figsize=(15, 4 * ((n + 2) // 3))
        )
        axes = axes.flatten()
        for i, col in enumerate(num_cols):
            axes[i].hist(df[col].dropna(), bins=30, edgecolor="black", alpha=0.7)
            axes[i].set_title(col, fontsize=10)
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        plt.savefig(out / "numerical_distributions.png", dpi=150)
        plt.close()

        # --- Boxplots ---
        fig, axes = plt.subplots(
            nrows=(n + 2) // 3, ncols=3, figsize=(15, 4 * ((n + 2) // 3))
        )
        axes = axes.flatten()
        for i, col in enumerate(num_cols):
            axes[i].boxplot(df[col].dropna(), vert=True)
            axes[i].set_title(col, fontsize=10)
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        plt.savefig(out / "boxplots.png", dpi=150)
        plt.close()

        # --- Categorical countplots ---
        cat_cols = df.select_dtypes(include="object").columns.tolist()
        if Config.TARGET_COLUMN in cat_cols:
            cat_cols.remove(Config.TARGET_COLUMN)
        if cat_cols:
            fig, axes = plt.subplots(1, len(cat_cols), figsize=(6 * len(cat_cols), 5))
            if len(cat_cols) == 1:
                axes = [axes]
            for ax, col in zip(axes, cat_cols):
                df[col].value_counts().plot.bar(ax=ax, edgecolor="black")
                ax.set_title(col)
            plt.tight_layout()
            plt.savefig(out / "categorical_distributions.png", dpi=150)
            plt.close()

        # --- Correlation heatmap ---
        corr = df[num_cols].corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", square=True)
        plt.title("Feature Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(out / "correlation_heatmap.png", dpi=150)
        plt.close()

        # --- Class distribution ---
        plt.figure(figsize=(6, 4))
        df[Config.TARGET_COLUMN].value_counts().plot.bar(edgecolor="black")
        plt.title("Target Class Distribution")
        plt.xlabel(Config.TARGET_COLUMN)
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(out / "class_distribution.png", dpi=150)
        plt.close()

        logger.info(f"  ✓ EDA report saved to {out}")

    # ------------------------------------------------------------------
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("  Cleaning data …")

        # Drop ID column
        if Config.ID_COLUMN in df.columns:
            df = df.drop(columns=[Config.ID_COLUMN])

        # Drop duplicates
        before = len(df)
        df = df.drop_duplicates()
        logger.info(f"    Duplicates removed: {before - len(df)}")

        # Handle missing values — impute numerical with median, categorical with mode
        for col in df.select_dtypes(include=np.number).columns:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        for col in df.select_dtypes(include="object").columns:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].mode()[0], inplace=True)

        # Outlier treatment — IQR capping for numerical columns
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        for col in num_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            df[col] = df[col].clip(lower, upper)

        logger.info(f"    Final shape after cleaning: {df.shape}")
        return df

    # ------------------------------------------------------------------
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("  Engineering features …")

        # Derived ratios
        df["loan_to_income_ratio"] = df["loan_amount"] / (df["income_annum"] + 1)
        df["total_assets"] = (
            df["residential_assets_value"]
            + df["commercial_assets_value"]
            + df["luxury_assets_value"]
            + df["bank_asset_value"]
        )
        df["assets_to_loan_ratio"] = df["total_assets"] / (df["loan_amount"] + 1)
        df["assets_to_income_ratio"] = df["total_assets"] / (df["income_annum"] + 1)
        df["debt_to_asset_ratio"] = df["loan_amount"] / (df["total_assets"] + 1)
        df["monthly_payment"] = df["loan_amount"] / (df["loan_term"] * 12 + 1)
        df["payment_to_income_ratio"] = df["monthly_payment"] / (
            df["income_annum"] / 12 + 1
        )

        # CIBIL score categories (one-hot)
        df["cibil_excellent"] = (df["cibil_score"] >= 750).astype(int)
        df["cibil_good"] = ((df["cibil_score"] >= 650) & (df["cibil_score"] < 750)).astype(int)
        df["cibil_fair"] = ((df["cibil_score"] >= 550) & (df["cibil_score"] < 650)).astype(int)
        df["cibil_poor"] = (df["cibil_score"] < 550).astype(int)

        # Encode target: Approved → 1, Rejected → 0
        if Config.TARGET_COLUMN in df.columns:
            df[Config.TARGET_COLUMN] = df[Config.TARGET_COLUMN].replace({"Approved": 1, "Rejected": 0}).astype(int)

        logger.info(f"    Features after engineering: {df.shape[1]}")
        return df

    # ------------------------------------------------------------------
    def _encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("  Encoding categorical variables …")
        for col in Config.CATEGORICAL_COLS:
            if col in df.columns:
                # Force to string in case it's object or categorical
                df[col] = df[col].astype(str)
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.label_encoders[col] = le
                logger.info(f"    {col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")
        return df

    # ------------------------------------------------------------------
    def _save_artefacts(self, X_train, X_val, X_test, y_train, y_val, y_test):
        """Persist processed data, scaler, and feature names."""
        import joblib

        out = Config.PROCESSED_DIR
        out.mkdir(parents=True, exist_ok=True)

        np.save(out / "X_train.npy", X_train)
        np.save(out / "X_val.npy",   X_val)
        np.save(out / "X_test.npy",  X_test)
        np.save(out / "y_train.npy", y_train)
        np.save(out / "y_val.npy",   y_val)
        np.save(out / "y_test.npy",  y_test)

        joblib.dump(self.scaler, out / "scaler.joblib")

        with open(out / "feature_names.json", "w") as f:
            json.dump(self.feature_names, f, indent=2)

        # Save label encoders
        if self.label_encoders:
            joblib.dump(self.label_encoders, out / "label_encoders.joblib")

        logger.info(f"  ✓ Artefacts saved to {out}")

    # ------------------------------------------------------------------
    def _generate_preprocessing_report(
        self, df, X_train, y_train, X_val, X_test
    ):
        out = Config.PREPROCESS_REPORT_DIR
        out.mkdir(parents=True, exist_ok=True)

        report = {
            "original_shape": list(df.shape),
            "train_shape": list(X_train.shape),
            "val_shape": list(X_val.shape),
            "test_shape": list(X_test.shape),
            "train_class_distribution": {
                "approved": int((y_train == 1).sum()),
                "rejected": int((y_train == 0).sum()),
            },
            "features": self.feature_names,
            "num_features": len(self.feature_names),
            "scaler": "StandardScaler",
            "imbalance_method": "SMOTE",
        }
        with open(out / "preprocessing_summary.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"  ✓ Preprocessing report saved to {out}")
