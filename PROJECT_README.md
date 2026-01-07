# 🏦 Home Credit Loan Approval System

A full-stack, production-ready AI-powered loan approval system featuring explainable ML models, modern web interface, and secure database architecture.

## 🎯 Project Overview

This system combines:
- **Hybrid ML Model**: TabNet + Bayesian Network for accurate risk prediction
- **Explainable AI**: SHAP values, Bayesian causality, business rules
- **Modern Frontend**: Next.js 14 with Material UI and TypeScript
- **Secure Backend**: FastAPI with JWT authentication
- **Scalable Database**: Supabase (PostgreSQL) with Row Level Security
- **Clean Architecture**: Separated frontend, backend, database, middleware, and ML layers

## 📁 Project Structure

```
Loan-evaluation-system/
├── frontend/                    # Next.js 14 + Material UI + TypeScript
│   ├── app/                    # Next.js App Router pages
│   ├── components/             # React components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities and helpers
│   ├── layouts/                # Page layouts
│   ├── services/               # API services
│   ├── types/                  # TypeScript definitions
│   └── package.json
│
├── backend/                     # FastAPI Python backend
│   ├── src/                    # Source code
│   ├── config/                 # Configuration files
│   ├── scripts/                # Utility scripts
│   ├── tests/                  # Backend tests
│   ├── api.py                  # Main API server
│   ├── main.py                 # ML pipeline runner
│   └── requirements.txt
│
├── database/                    # Supabase database layer
│   ├── supabase/
│   │   └── migrations/         # Database migrations
│   ├── schemas/                # Table schemas
│   ├── client/                 # Python client
│   └── README.md
│
├── middleware/                  # API middleware
│   ├── auth.py                 # JWT authentication
│   ├── logging_middleware.py  # Request logging
│   ├── error_handler.py       # Error handling
│   └── README.md
│
├── ml-model/                    # ML models and data
│   ├── models/                 # Trained models
│   │   ├── tabnet/
│   │   ├── bayesian/
│   │   └── hybrid/
│   ├── data/                   # Training data
│   ├── schemas/                # Data schemas
│   └── reports/                # Model reports
│
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.8+ (for backend and ML)
- **PostgreSQL** or Supabase account
- **Git**

### 1. Clone Repository

```bash
cd Loan-evaluation-system
```

### 2. Setup Database (Supabase)

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Initialize and start local Supabase
cd database
supabase init
supabase start

# Apply migrations
supabase db reset
```

**OR** use Supabase Cloud:
1. Create project at [https://supabase.com](https://supabase.com)
2. Copy your project URL and API keys
3. Run migrations in SQL Editor

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Supabase credentials

# Run backend server
python api.py
# Server will start at http://localhost:8000
```

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local
# Edit NEXT_PUBLIC_API_URL to point to backend

# Run development server
npm run dev
# Frontend will start at http://localhost:3000
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Supabase Dashboard**: http://localhost:54323 (local)

## 🔑 Default Login Credentials

### For Development/Testing

Create users in Supabase or use these test accounts:

**Loan Officer:**
- Email: `officer@example.com`
- Password: `password123`
- Role: `loan_officer`

**Bank Manager:**
- Email: `manager@example.com`
- Password: `password123`
- Role: `bank_manager`

## 🏗️ Architecture

### Frontend (Next.js 14)

- **Framework**: Next.js 14 with App Router
- **UI Library**: Material UI 5
- **State Management**: 
  - Zustand (auth)
  - TanStack Query (API data)
- **Validation**: Zod schemas
- **Styling**: Tailwind CSS + Material UI

### Backend (FastAPI)

- **Framework**: FastAPI
- **Authentication**: JWT tokens with bcrypt
- **Database**: Supabase Python client
- **ML Integration**: TabNet + Bayesian models
- **Middleware**: Auth, logging, error handling

### Database (Supabase/PostgreSQL)

- **Tables**: Users, Applicants, Predictions, Audit Logs
- **Security**: Row Level Security (RLS) policies
- **Features**: Real-time, Auth, Storage
- **Migrations**: Version-controlled SQL migrations

### ML Model

- **Primary**: TabNet (PyTorch)
- **Secondary**: Bayesian Network (pgmpy)
- **Ensemble**: Weighted hybrid model
- **Explainability**: SHAP + Bayesian paths + Business rules

## 📊 Features

### ✅ Implemented

1. **User Management**
   - JWT-based authentication
   - Role-based access (Loan Officer, Bank Manager)
   - Secure password hashing

2. **Loan Application**
   - Comprehensive applicant forms
   - Real-time validation
   - Document upload support

3. **ML Predictions**
   - Hybrid TabNet + Bayesian model
   - Risk score (0-1 scale)
   - Decision: APPROVE/REJECT/MANUAL_REVIEW

4. **Explainable AI**
   - SHAP feature importance
   - Bayesian causal paths
   - Business rule triggers
   - Risk gauge visualization

5. **Dashboard & Reports**
   - Real-time statistics
   - Performance metrics
   - Decision distribution
   - Export to CSV/PDF

6. **Security & Audit**
   - Row-level security
   - Audit logs for all actions
   - IP tracking
   - User agent logging

### 🚧 Planned Enhancements

- [ ] Email notifications
- [ ] Document OCR and parsing
- [ ] Batch prediction uploads
- [ ] Advanced analytics dashboard
- [ ] Model retraining pipeline
- [ ] A/B testing framework

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
pylint src/
black src/

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### Database Migrations

```bash
cd database

# Create new migration
supabase migration new migration_name

# Apply migrations (local)
supabase db reset

# Apply migrations (production)
supabase db push
```

## 📦 Deployment

### Frontend (Vercel - Recommended)

```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Docker)

```bash
cd backend
docker build -t loan-approval-backend .
docker run -p 8000:8000 --env-file .env loan-approval-backend
```

### Database (Supabase Cloud)

1. Create project at [supabase.com](https://supabase.com)
2. Run migrations in SQL Editor
3. Enable RLS policies
4. Update backend .env with production credentials

## 🔒 Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use different keys for dev/prod
   - Rotate secrets regularly

2. **Authentication**
   - Use HTTPS in production
   - Implement rate limiting
   - Set appropriate token expiry

3. **Database**
   - Enable RLS on all tables
   - Use service role key only in backend
   - Regular backups

4. **API**
   - Validate all inputs
   - Sanitize user data
   - Log security events

## 📖 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/auth/login          # User login
GET    /api/applicants          # List applicants
POST   /api/applicants          # Create applicant
GET    /api/applicants/:id      # Get applicant details
POST   /api/predict             # Generate prediction
POST   /api/applicants/:id/approve  # Approve loan (Manager)
POST   /api/applicants/:id/reject   # Reject loan (Manager)
GET    /api/dashboard/stats     # Dashboard statistics
GET    /api/model/health        # Model health check
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is part of the Home Credit Default Risk prediction system.

## 👥 Team

- **Frontend**: Next.js 14 + Material UI + TypeScript
- **Backend**: FastAPI + Python 3.8+
- **Database**: Supabase (PostgreSQL)
- **ML Models**: TabNet + Bayesian Network
- **Architecture**: Clean, scalable, production-ready

## 📞 Support

For questions or issues:
1. Check documentation in each directory
2. Review API documentation at `/docs`
3. Check logs in `backend/logs/`
4. Create an issue in the repository

---

**Built with ❤️ using modern, production-ready technologies**

## 🔗 Useful Links

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Material UI Components](https://mui.com/material-ui/)
- [PyTorch TabNet](https://github.com/dreamquark-ai/tabnet)
