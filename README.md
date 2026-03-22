# 🏦 LoanWise - Loan Evaluation System

LoanWise is a comprehensive, AI-powered system designed for evaluating loan applications, predicting default risks, and managing the overall loan lifecycle. The platform leverages a modern web stack for its user interface and an advanced **Hybrid Bayesian deep Learning Architecture** for highly interpretable and uncertainty-aware risk prediction.

## 🌟 Key Features

*   **Intelligent Risk Assessment:** Uses a Hybrid Model approach combining a Bayesian Network (BN) with various deep learning architectures (ANN, LSTM, RNN) to calculate the probability of default.
*   **Uncertainty Quantification:** Quantifies both Epistemic (model) and Aleatoric (data) uncertainty to assign confidence scores and risk recommendations.
*   **Explainable AI (XAI):** Interrogates model decisions using LIME to ensure transparency and fairness in predictions.
*   **Modern Interactive Dashboard:** Built with Next.js and Material UI to track applications, view statuses, and visualize evaluation metrics.
*   **Secure & Robust:** Employs JWT-based authentication, role-based access control, and PostgreSQL database management (via Supabase).

## 🏗️ Architecture & Tech Stack

This project is a monorepo split into four core domains:

### 1. Frontend (`/frontend`)
*   **Framework:** [Next.js](https://nextjs.org/) 14 (React 18)
*   **Language:** TypeScript
*   **Styling:** Tailwind CSS + Material UI (MUI)
*   **State Management & Fetching:** Zustand, React Query, Axios

### 2. Backend API (`/backend`)
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Language:** Python 3
*   **Security:** JWT, Passlib, Bcrypt setup for user authentication.
*   **Role:** Acts as the principal gateway integrating the ML inference engine with the PostgreSQL database and providing a RESTful API to the frontend.

### 3. Machine Learning Model (`/ml-model`)
*   **Core Libraries:** PyTorch, Scikit-learn, Pandas, NumPy, pgmpy, LIME.
*   **Model Type:** Hybrid Deep Learning & Bayesian Architecture.
    *   *Bayesian Network (BN)*: Learns causal structures and generates probabilistic embeddings.
    *   *Deep Learning Models (ANN / LSTM / RNN)*: Extracts deep features from both raw data and BN embeddings to evaluate risk.
*   **Explainability:** Incorporates XAI (LIME) for local interpretable model-agnostic explanations.

### 4. Database (`/database`)
*   **Provider:** [Supabase](https://supabase.com/) (PostgreSQL)
*   **Migrations:** Structured SQL migrations (users, schemas, RLS policies, status management).

## 📂 Project Structure

```text
├── backend/            # FastAPI source code, routers, middleware, and inference endpoints
├── database/           # SQL schemas and Supabase migration scripts
├── frontend/           # Next.js web application
├── ml-model/           # Machine learning training pipelines, models, data, and Jupyter notebooks
├── logs/               # Application-level logs
├── start.sh            # Global startup script bridging frontend and backend
└── stop.sh             # Global teardown script
```

## 🚀 Getting Started

### Prerequisites
*   **Node.js** (v18 or higher recommended) & npm/pnpm
*   **Python** 3.9+
*   **LSOF & Bash** (for running the management scripts)
*   Supabase Account/Instance (set up your environment variables based on the database schema)

### 🛠️ One-Click Setup & Run

We provide a convenient bash script that automatically manages virtual environments, installs Python/Node dependencies, and maps them correctly.

To run both the backend API and frontend simultaneously:

```bash
chmod +x start.sh
./start.sh
```

**What this does:**
1. Checks for available ports (8000 and 3000).
2. Creates and activates a Python virtual environment in `backend/venv`.
3. Installs backend requirements from `REQUIREMENTS.txt`.
4. Installs frontend `node_modules`.
5. Starts the FastAPI backend and Next.js frontend in parallel.

### 🛑 Stopping the Application

To gracefully terminate the running backend and frontend processes:

```bash
chmod +x stop.sh
./stop.sh
```

## ⚙️ Manual Setup (Optional)

If you prefer to run the components independently:

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📊 Deep Learning Pipeline

The complete training and inference pipeline is located in the `/ml-model` directory.
*   `train_pipeline.py` orchestrates the model's data preprocessing, scaling, baseline training, and final hybrid model tuning.
*   The Bayesian network (`pgmpy`) generates probabilistic embeddings that are fed with standard scaled features into the `PyTorch`-based Bayesian Neural Output layer.
*   To retrain: Ensure your raw data is placed in `ml-model/data/raw/` or `ml-model/dataset/raw_data/` and execute `python train_pipeline.py`.

## 📜 Database Initialization

All schema migrations reside in `database/supabase/migrations/`. You can execute these sequentially on your running PostgreSQL instance or via the Supabase CLI:

```bash
cd database
supabase start       # If using local supabase
supabase db push     # Upgrades Remote/Local database with migrations
```
