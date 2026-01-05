# Home Credit Default Risk - Hybrid Model

A hybrid machine learning system combining TabNet and Bayesian Networks for credit default prediction with **71% recall** and **0.702 AUC**.

## 📋 Project Overview

This project implements a hybrid ensemble model for predicting credit default risk using the Home Credit dataset. The system combines deep learning (TabNet) with probabilistic graphical models (Bayesian Networks) to achieve robust and interpretable predictions.

### Key Features
- ✅ **Class Imbalance Handling**: SMOTEENN + Class Weights (92% → 30% sampling)
- ✅ **Hyperparameter Optimization**: Optuna-based automated tuning
- ✅ **Explainable AI**: SHAP visualizations for model interpretability
- ✅ **Production API**: FastAPI with optimal threshold (0.309)
- ✅ **Centralized Config**: No hardcoded paths, clean maintainable code

## 🏗️ Project Structure

```
home-credit-default-risk/
│
├── 📁 data/                          # All datasets
│   ├── raw/                          # Original data files (307,511 train samples)
│   ├── processed/                    # Preprocessed splits (train/val/test)
│   └── external/                     # External datasets
│
├── 📁 models/                        # Trained models
│   ├── tabnet/                       # TabNet optimized (2.4MB)
│   ├── bayesian/                     # Bayesian Network (34KB)
│   └── hybrid/                       # Ensemble models
│
├── 📁 src/                           # Source code
│   ├── config.py                     # 🆕 Centralized configuration
│   ├── data/                         # Data pipelines
│   │   ├── imbalance_fix.py         # 6 resampling methods
│   │   ├── preprocess.py            # Feature engineering
│   │   └── merge_home_credit.py     # Data consolidation
│   ├── models/                       # Model training
│   │   ├── imbalance_optimized.py   # Best training pipeline (71% recall)
│   │   ├── hyperparameter_tuning.py # Optuna-based tuning
│   │   ├── tabnet_train.py          # TabNet training
│   │   └── bayesian_network.py      # BN training
│   ├── evaluation/                   # Metrics & validation
│   │   ├── final_evaluation.py      # Model comparison
│   │   └── xai_shap.py              # SHAP analysis
│   └── inference/                    # Production API
│       └── api.py                    # FastAPI (clean, single implementation)
│
├── 📁 reports/                       # Generated reports
│   └── figures/                      # SHAP visualizations (4 files, 880KB)
├── 📁 config/                        # YAML configuration files
├── 📁 docs/                          # Documentation
├── 📁 schemas/                       # Data validation
├── 📁 tests/                         # Unit tests
│
├── check_health.py                   # Codebase health verification
├── CLEANUP_SUMMARY.md                # Cleanup documentation
├── TRAINING_GUIDE.md                 # Model training guide
├── POSTMAN_GUIDE.md                  # API testing guide
└── requirements.txt                  # Python dependencies
```

## 🚀 Quick Start

### Installation

```bash
# Navigate to project
cd /Users/Thanuja/Desktop/FYP/home-credit-default-risk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Data Preparation

1. Place raw CSV files in `data/raw/`
2. Run data merging and preprocessing:

```bash
python src/data/merge_home_credit.py
python src/data/preprocess.py
python src/data/data_loader.py
```

### Model Training

### Training Models

Train with imbalance optimization (recommended):

```bash
# Train optimized TabNet with SMOTEENN + Class Weights
python src/models/imbalance_optimized.py

# Run hyperparameter tuning (optional)
python src/models/hyperparameter_tuning.py

# Evaluate all models
python src/evaluation/final_evaluation.py

# Generate SHAP explanations
python src/evaluation/xai_shap.py
```

### Running the API

```bash
# Start FastAPI server
uvicorn src.inference.api:app --host 0.0.0.0 --port 8000

# Test in browser
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"EXT_SOURCE_2": 0.6, "EXT_SOURCE_3": 0.4, "AGE_YEARS": 35}}'
```

See [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md) for Postman testing instructions.

## 📊 Models

### TabNet (Primary Model)
- Deep learning architecture with attention mechanism
- **71% recall** at optimal threshold (0.309)
- **0.702 AUC** on test set
- Handles class imbalance with SMOTEENN + Class Weights
- Trained on 99 engineered features

### Bayesian Network
- Probabilistic graphical model
- Captures dependencies between top 20 features
- Provides uncertainty quantification
- Trained with structure learning (Hill Climbing + BIC)

### Hybrid Ensemble
- Combines TabNet and Bayesian Network predictions
- Meta-learning approach with Logistic Regression
- **0.702 AUC** on test set

## 📈 Performance Metrics

Current best model (TabNet Imbalance-Optimized):

| Metric | Value |
|--------|-------|
| **Recall** | 0.71 (71% of defaults caught) |
| **AUC** | 0.702 |
| **Precision** | 0.13 |
| **Optimal Threshold** | 0.309 (vs 0.5 default) |
| **Class Balance** | SMOTEENN 30% + Weights [1.0, 5.16] |

Detailed metrics available in `reports/figures/`:
- SHAP summary plots
- Feature importance visualizations
- Precision-recall curves

## 🔧 Configuration

All paths are centralized in [src/config.py](src/config.py):
- `Config.DATA_PROCESSED` - Preprocessed data location
- `Config.TABNET_DIR` - TabNet models
- `Config.REPORTS_DIR` - Generated reports

Additional YAML configs in `config/`:
- `config.yaml` - Model hyperparameters
- `paths.yaml` - Legacy paths (deprecated)
- `logging.yaml` - Logging configuration

## ✅ Code Quality

Run health check:
```bash
python check_health.py
```

This verifies:
- All critical paths exist
- Models are properly saved
- Data splits are available
- SHAP outputs generated
- No hardcoded paths remain

## 🧪 Testing

Run tests:

```bash
pytest tests/
```

## 📝 Documentation

Detailed documentation is available in the `docs/` directory.

## 👥 Contributors

- Your Name

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Home Credit Dataset from Kaggle
- PyTorch TabNet implementation
- pgmpy for Bayesian Networks
