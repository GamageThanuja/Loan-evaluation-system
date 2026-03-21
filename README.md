# LoanWise - Intelligent Loan Evaluation System

A machine learning-powered loan evaluation system with explainable AI using a Hybrid Bayesian Model architecture.

## 🎯 Model Architecture

### Hybrid Bayesian Model (v2.0.0)

Our production model combines two powerful components:

#### 1. Bayesian Network (PGMPY)
- **Purpose**: Causal structure learning and probabilistic embeddings
- **Algorithm**: Hill Climb with BIC scoring
- **Structure**: Learned 17-21 causal edges from data
- **Output**: Risk embeddings for BNN input

#### 2. Bayesian Neural Network (PyTorch)
- **Architecture**: [256, 128, 64] hidden layers
- **Uncertainty**: MC-Dropout (0.2 rate, 50 forward passes)
- **Loss Function**: ELBO = BCE + KL Divergence
- **Class Weights**: {0: 0.544, 1: 6.194} for imbalance handling

### Performance Metrics
| Metric | Value |
|--------|-------|
| Accuracy | 85.39% |
| Precision | 24.95% |
| Recall | 40.31% |
| F1 Score | 30.83% |
| ROC-AUC | 76.01% |

### Key Features
- ✅ **Uncertainty Quantification**: Epistemic & aleatoric uncertainty
- ✅ **Explainable Predictions**: Causal factor analysis
- ✅ **Class Imbalance Handling**: Weighted loss function
- ✅ **Production Ready**: FastAPI backend integration

## 🏗️ Project Structure

```
Loan-evaluation-system/
├── backend/                    # FastAPI backend
│   ├── api.py                 # Main API entry point
│   ├── routers/               # API routes
│   │   ├── predictions.py     # ML prediction endpoints
│   │   ├── applicants.py      # Applicant CRUD
│   │   └── auth.py            # Authentication
│   └── src/
│       └── inference/
│           └── predictor.py   # Model inference module
├── frontend/                   # Next.js frontend
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   └── services/              # API services
├── ml-model/                   # ML model training
│   ├── training/
│   │   ├── bayesian_network.py    # BN implementation
│   │   ├── bayesian_nn.py         # BNN implementation
│   │   ├── hybrid_model.py        # Combined model
│   │   └── train_pipeline.py      # Training script
│   └── models/
│       └── hybrid/
│           └── hybrid_bayesian_model.joblib
├── database/                   # Supabase schemas
└── scripts/                    # Helper scripts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r ../requirements.txt  # Install from root requirements.txt
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

### Predictions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/predictions/predict` | POST | Basic prediction |
| `/api/predictions/predict/explain` | POST | Prediction with explanation |
| `/api/predictions/eligibility` | POST | Full eligibility check |

### Health

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health status |
| `/api/model/health` | GET | Model health status |

## 📊 Training the Model

```bash
cd ml-model
python -m training.train_pipeline \
    --data data/processed/home_credit_consolidated_preprocessed.csv \
    --output models/hybrid \
    --use-class-weights
```

### Training Options
- `--use-class-weights`: Apply sklearn class weights (recommended)
- `--use-focal`: Use focal loss instead of BCE
- `--use-smote`: Apply SMOTE oversampling

## 📈 Model Comparison Report

See [HYBRID_BAYESIAN_MODEL_FINAL_REPORT.md](HYBRID_BAYESIAN_MODEL_FINAL_REPORT.md) for detailed analysis.

## 🔐 Authentication

The API uses JWT authentication. Login to get a token:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

Use the token in subsequent requests:
```bash
curl http://localhost:8000/api/predictions/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"features": {...}}'
```

## 📝 License

This project is developed as part of a Final Year Project.

## 👥 Contributors

- Project Owner: Thanuja
