# Loan Evaluation System
## Personal Loan Assessment for Sri Lankan Banks

---

## Project Structure

```
project/
├── backend/          → API & business logic
│   ├── routers/      → API endpoints
│   └── src/models/   → reasoning.py (credit score logic)
├── frontend/         → UI (Next.js)
├── ml-model/         
│   ├── models/       → tabnet.pkl (ONLY model file)
│   └── data/         → Training data
├── database/         → DB client & schemas
├── config/           → app_config.yaml (ALL settings)
├── scripts/          → train.py, evaluate.py, run_*.sh
├── reports/          → Generated outputs (images, CSVs)
├── docs/             → PROJECT_GUIDE.md
└── logs/             → Runtime logs
```

---

## Quick Start

### 1. Start Backend
```bash
./scripts/run_backend.sh
# Or manually:
cd project && source backend/venv/bin/activate
PYTHONPATH="$(pwd):$(pwd)/backend" python backend/api.py
```

### 2. Start Frontend
```bash
./scripts/run_frontend.sh
```

### 3. Train Model (20 epochs max)
```bash
python scripts/train.py --epochs 20 --sample 0.2
```

### 4. Evaluate Model
```bash
python scripts/evaluate.py
```

---

## Configuration

Single config file: `config/app_config.yaml`

### Training
| Setting | Value |
|---------|-------|
| Max Epochs | 20 |
| Early Stopping | 10 |
| Batch Size | 1024 |
| Sample Rate | 0.2 (20%) |

### Credit Score Classification (Mandatory)
| Score Range | Rating |
|-------------|--------|
| < 580 | Poor |
| 580-669 | Fair |
| 670-739 | Good |
| 740-799 | Very Good |
| 800+ | Exceptional |

### Business Rules
| Rule | Value |
|------|-------|
| Max Loan | LKR 1,000,000 |
| Min Loan | LKR 50,000 |
| Max DTI | 40% |
| Interest | 12% p.a. |

---

## Model

- **Type**: TabNet (Deep Learning for Tabular Data)
- **File**: `ml-model/models/tabnet.pkl` (single file)
- **Threshold**: 0.309 (optimized for F1)
- **Performance**:
  - AUC: 0.702
  - Recall: 71%
  - F1: 0.627

---

## Reasoning Module

The system provides multi-factor explanations:

```python
from backend.src.models.reasoning import evaluate_loan_application

result = evaluate_loan_application(
    model_probability=0.45,
    loan_amount=500000,
    monthly_income=50000,
    loan_term_months=36,
    credit_score=620
)

# Returns:
# - decision: APPROVE/REJECT
# - risk_factors: [{factor_name, severity, impact}]
# - suggestions: [{action, reason, expected_improvement}]
# - alternative_offer: {amount, term}
# - credit_score: {score, rating, description}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/predictions/eligibility` | POST | Loan prediction |
| `/api/applicants` | GET | List applicants |
| `/api/auth/login` | POST | User login |

---

## Reports Folder

All generated artifacts go to `/reports`:
- Confusion matrices (PNG)
- ROC curves (PNG)
- Model comparison (CSV)
- SHAP analysis
- Training logs
