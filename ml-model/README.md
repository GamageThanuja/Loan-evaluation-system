# Hybrid Bayesian Model - Loan Default Prediction

## Overview

This is a research-driven **Hybrid Bayesian Model** combining:

1. **Bayesian Network (BN)** - For causal structure learning and probabilistic embeddings
2. **Bayesian Neural Network (BNN)** - For deep feature extraction with uncertainty quantification

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HYBRID BAYESIAN ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Raw Features                                                               │
│      │                                                                      │
│      ├──────────────────────────┐                                          │
│      │                          │                                          │
│      ▼                          ▼                                          │
│  ┌────────────────────┐   ┌─────────────────┐                              │
│  │  BAYESIAN NETWORK  │   │  StandardScaler │                              │
│  │      (PGMPY)       │   │                 │                              │
│  │                    │   └────────┬────────┘                              │
│  │  ├─ Hill Climb     │            │                                       │
│  │  ├─ BIC Score      │            │                                       │
│  │  └─ BayesianEst.   │            │                                       │
│  └─────────┬──────────┘            │                                       │
│            │                       │                                       │
│            ▼                       │                                       │
│  ┌────────────────────┐            │                                       │
│  │   Probabilistic    │            │                                       │
│  │    Embeddings      │            │                                       │
│  └─────────┬──────────┘            │                                       │
│            │                       │                                       │
│            └───────────┬───────────┘                                       │
│                        │                                                    │
│                        ▼                                                    │
│              ┌─────────────────┐                                           │
│              │    COMBINED     │                                           │
│              │  [Raw + Embed]  │                                           │
│              └────────┬────────┘                                           │
│                       │                                                     │
│                       ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │            BAYESIAN NEURAL NETWORK (PyTorch)                     │       │
│  ├─────────────────────────────────────────────────────────────────┤       │
│  │                                                                  │       │
│  │  ┌──────────────────────────────────────────────────────────┐   │       │
│  │  │  DEEP FEATURE EXTRACTOR                                   │   │       │
│  │  │  ├─ Linear(input, 128) + BatchNorm + ReLU + MC-Dropout    │   │       │
│  │  │  ├─ Linear(128, 64) + BatchNorm + ReLU + MC-Dropout       │   │       │
│  │  │  └─ Linear(64, 32) + BatchNorm + ReLU + MC-Dropout        │   │       │
│  │  └──────────────────────────────────────────────────────────┘   │       │
│  │                          │                                      │       │
│  │                          ▼                                      │       │
│  │  ┌──────────────────────────────────────────────────────────┐   │       │
│  │  │  BAYESIAN OUTPUT LAYER (Variational Inference)           │   │       │
│  │  │  ├─ Weight Mean (μ)                                      │   │       │
│  │  │  ├─ Weight Variance (σ²)                                  │   │       │
│  │  │  └─ Sample: W ~ N(μ, σ²)                                  │   │       │
│  │  └──────────────────────────────────────────────────────────┘   │       │
│  │                          │                                      │       │
│  └──────────────────────────┼──────────────────────────────────────┘       │
│                             │                                               │
│                             ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                     UNCERTAINTY OUTPUT                           │       │
│  ├─────────────────────────────────────────────────────────────────┤       │
│  │  • Probability of Default                                        │       │
│  │  • Epistemic Uncertainty (model uncertainty)                     │       │
│  │  • Aleatoric Uncertainty (data uncertainty)                      │       │
│  │  • Confidence Score                                              │       │
│  │  • Risk Recommendation                                           │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Bayesian Network (PGMPY)

**File:** `training/bayesian_network.py`

- **Causal Structure Learning:** Uses Hill Climb search with BIC scoring
- **Probabilistic Embeddings:** Generates embeddings based on learned causal relationships
- **Feature Dependencies:** Discovers and outputs interpretable feature relationships

### 2. Bayesian Neural Network (PyTorch)

**File:** `training/bayesian_nn.py`

- **MC-Dropout:** Active during both training and inference for epistemic uncertainty
- **Variational Inference (Bayes-by-Backprop):** Learns weight distributions, not point estimates
- **ELBO Loss:** Combines Binary Cross-Entropy + KL Divergence

### 3. Hybrid Model

**File:** `training/hybrid_model.py`

- Combines BN embeddings with raw features
- Trains BNN with uncertainty quantification
- Provides predictions with confidence intervals

## Loss Function

**ELBO (Evidence Lower Bound):**

$$\mathcal{L}_{ELBO} = \mathcal{L}_{BCE} + \beta \cdot D_{KL}(q(w|\theta) \| p(w))$$

Where:
- $\mathcal{L}_{BCE}$ = Binary Cross-Entropy loss
- $D_{KL}$ = KL Divergence between variational posterior and prior
- $\beta$ = KL annealing factor (increases from 0 to 1 during training)

## Uncertainty Quantification

### Epistemic Uncertainty (Reducible)
- Model uncertainty due to limited training data
- Captured via MC-Dropout and weight variance
- Can be reduced with more data

### Aleatoric Uncertainty (Irreducible)
- Inherent noise in the data
- Captured via output variance
- Cannot be reduced with more data

### Total Uncertainty
$$\sigma_{total}^2 = \sigma_{epistemic}^2 + \sigma_{aleatoric}^2$$

## Installation

```bash
cd ml-model
pip install -r requirements.txt
```

## Training

```bash
python -m training.train_pipeline --data data/processed/train.csv --epochs 50
```

### Training Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--data` | `data/processed/train.csv` | Path to training data |
| `--target` | `loan_status` | Target column name |
| `--epochs` | `50` | Number of training epochs |
| `--batch-size` | `256` | Batch size |
| `--hidden-dims` | `128,64,32` | Hidden layer dimensions |
| `--output` | `models/hybrid` | Output directory |

## Usage

### Python API

```python
from training.hybrid_model import HybridBayesianModel

# Load trained model
model = HybridBayesianModel.load('models/hybrid/hybrid_bayesian_model.joblib')

# Make prediction with uncertainty
result = model.predict_with_uncertainty(X_new)

print(f"Probability: {result['probability']}")
print(f"Prediction: {result['prediction']}")
print(f"Epistemic Uncertainty: {result['epistemic_uncertainty']}")
print(f"Aleatoric Uncertainty: {result['aleatoric_uncertainty']}")
print(f"Confidence: {result['confidence']}")

# Get detailed explanation
explanation = model.explain(X_new)
print(f"Risk Level: {explanation['risk_level']}")
print(f"Recommendation: {explanation['recommendation']}")
```

### Backend API

```python
from src.inference import predict

result = predict({
    'feature1': value1,
    'feature2': value2,
    # ... other features
})
```

## Output Format

```json
{
    "probability": 0.2345,
    "prediction": 0,
    "prediction_label": "REPAYMENT_LIKELY",
    "risk_level": "MEDIUM",
    "epistemic_uncertainty": 0.0532,
    "aleatoric_uncertainty": 0.0789,
    "total_uncertainty": 0.0951,
    "confidence": 90.5,
    "recommendation": "APPROVE_WITH_CONDITIONS",
    "bn_risk_posterior": 0.2234,
    "causal_dependencies": {
        "income": ["loan_amount", "credit_score"],
        "credit_score": ["loan_status"]
    }
}
```

## Files Structure

```
ml-model/
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── training/
│   ├── __init__.py
│   ├── bayesian_network.py   # PGMPY BN implementation
│   ├── bayesian_nn.py        # PyTorch BNN implementation
│   ├── hybrid_model.py       # Main hybrid model
│   └── train_pipeline.py     # Training script
├── models/
│   └── hybrid/
│       └── hybrid_bayesian_model.joblib
└── data/
    ├── raw/
    └── processed/
```

## Requirements

- Python 3.8+
- PyTorch 2.0+
- PGMPY 0.1.23+
- scikit-learn
- pandas
- numpy

## References

1. Bayesian Networks: Pearl, J. (1988). Probabilistic reasoning in intelligent systems
2. MC-Dropout: Gal, Y. & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation
3. Variational Inference: Blundell et al. (2015). Weight Uncertainty in Neural Networks
4. ELBO: Kingma, D.P. & Welling, M. (2014). Auto-Encoding Variational Bayes
