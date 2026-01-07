# 🚀 Setup and Deployment Guide

This document provides step-by-step instructions for setting up and deploying the Home Credit Loan Approval System.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup (Supabase)](#database-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Testing the Integration](#testing)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Git**
- **PostgreSQL** (local) or **Supabase** account (recommended)

### Installation

```bash
# macOS
brew install node python@3.8 postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install nodejs npm python3.8 python3-pip postgresql

# Windows (use Chocolatey)
choco install nodejs python postgresql
```

## Environment Setup

### 1. Clone and Navigate

```bash
cd /Users/Thanuja/Desktop/FYP/Loan-evaluation-system
```

### 2. Verify Structure

```bash
ls -la
# Should see: frontend/, backend/, database/, middleware/, ml-model/
```

## Database Setup (Supabase)

### Option A: Supabase Cloud (Recommended for Production)

1. **Create Supabase Project**
   - Go to [https://supabase.com](https://supabase.com)
   - Click "New Project"
   - Choose organization and region
   - Set database password (save it!)

2. **Get Credentials**
   - Go to Settings → API
   - Copy:
     - `Project URL` (SUPABASE_URL)
     - `anon/public key` (SUPABASE_ANON_KEY)
     - `service_role key` (SUPABASE_SERVICE_KEY)

3. **Run Migrations**
   - Go to SQL Editor in Supabase Dashboard
   - Copy content from `database/supabase/migrations/001_initial_schema.sql`
   - Execute
   - Copy content from `database/supabase/migrations/002_rls_policies.sql`
   - Execute

4. **Verify Tables**
   - Go to Table Editor
   - Should see: users, applicants, predictions, audit_logs, model_performance

### Option B: Local Supabase (Development)

```bash
# Install Supabase CLI
brew install supabase/tap/supabase

# Initialize Supabase
cd database
supabase init

# Start local Supabase
supabase start
# This will output your local credentials

# Apply migrations
supabase db reset

# Access local dashboard
open http://localhost:54323
```

### 3. Create Test Users

Run in SQL Editor:

```sql
-- Insert test users (passwords are hashed 'password123')
INSERT INTO users (email, name, role, password_hash) VALUES
('officer@example.com', 'John Officer', 'loan_officer', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIhLU8kQ3G'),
('manager@example.com', 'Jane Manager', 'bank_manager', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIhLU8kQ3G');
```

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI, Uvicorn (API server)
- Supabase Python client
- PyJWT, bcrypt (authentication)
- TabNet, PyTorch (ML model)
- And all other dependencies

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

Update with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres

API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

SECRET_KEY=your-random-secret-key-here
CORS_ORIGINS=http://localhost:3000

MODEL_VERSION=2.0.0
MODEL_PATH=../ml-model/models
DATA_PATH=../ml-model/data

LOG_LEVEL=INFO
```

### 4. Verify ML Models

```bash
# Check if models exist
ls -la ../ml-model/models/

# Should see directories:
# - tabnet/
# - bayesian/
# - hybrid/
```

### 5. Start Backend Server

```bash
# Make sure venv is activated
python api.py

# Or use uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Backend will start at **http://localhost:8000**

### 6. Verify Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This installs:
- Next.js 14
- Material UI 5
- TanStack Query
- Zod validation
- All React dependencies

### 2. Configure Environment

```bash
# .env.local should already exist, verify it:
cat .env.local
```

Should contain:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="Home Credit Loan Approval"
NEXT_PUBLIC_RISK_THRESHOLD_LOW=0.15
NEXT_PUBLIC_RISK_THRESHOLD_MEDIUM=0.30
NEXT_PUBLIC_RISK_THRESHOLD_HIGH=0.50
```

### 3. Start Frontend

```bash
npm run dev
```

Frontend will start at **http://localhost:3000**

### 4. Verify Frontend

Open browser to `http://localhost:3000`
- Should see login page
- No console errors
- Dark/light mode toggle works

## Testing the Integration

### 1. Test Authentication

```bash
# Terminal: Test login API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "officer@example.com",
    "password": "password123"
  }'

# Should return: {"success": true, "token": "...", "user": {...}}
```

### 2. Test Frontend Login

1. Open `http://localhost:3000`
2. Enter:
   - Email: `officer@example.com`
   - Password: `password123`
   - Role: `Loan Officer`
3. Click "Sign In"
4. Should redirect to dashboard

### 3. Test Applicant Creation

1. Click "New Applicant" in sidebar
2. Fill out form:
   - Name: `Test Applicant`
   - Email: `test@example.com`
   - Phone: `+1234567890`
   - Date of Birth: `1990-01-01`
   - Income: `50000`
   - Credit Score: `720`
   - Loan Amount: `100000`
   - Loan Purpose: `purchase`
   - Loan Term: `360` months
3. Click "Submit Application"
4. Should create applicant and show in list

### 4. Test Prediction

The prediction should automatically trigger when applicant is created.
Check:
- Dashboard shows updated stats
- Applicant detail page shows risk gauge
- SHAP explanation visible
- Bayesian network displayed

### 5. Test Manager Actions

1. Logout
2. Login as manager:
   - Email: `manager@example.com`
   - Password: `password123`
   - Role: `Bank Manager`
3. Go to applicant detail page
4. Should see "Approve" and "Reject" buttons
5. Test approval workflow

## Production Deployment

### Frontend (Vercel)

```bash
cd frontend

# Build production version
npm run build

# Test production build locally
npm run start

# Deploy to Vercel
npm install -g vercel
vercel login
vercel deploy --prod
```

### Backend (Docker + Cloud Run / AWS / Azure)

```bash
cd backend

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build image
docker build -t loan-approval-backend .

# Test locally
docker run -p 8000:8000 --env-file .env loan-approval-backend

# Push to registry
docker tag loan-approval-backend gcr.io/your-project/loan-approval-backend
docker push gcr.io/your-project/loan-approval-backend

# Deploy to Cloud Run
gcloud run deploy loan-approval-backend \
  --image gcr.io/your-project/loan-approval-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Database (Supabase Production)

1. Use Supabase Cloud (already production-ready)
2. Enable backups in dashboard
3. Set up monitoring and alerts
4. Review and enable all RLS policies

### Environment Variables (Production)

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL`: Your backend URL

**Backend:**
- `SUPABASE_URL`: Production Supabase URL
- `SUPABASE_SERVICE_KEY`: Production service key
- `SECRET_KEY`: Strong random key (use `openssl rand -hex 32`)
- `CORS_ORIGINS`: Your production frontend URL
- `API_DEBUG=False`

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check if port is in use
lsof -i :8000
# If occupied, kill process or use different port

# Check dependencies
pip list | grep fastapi

# Check logs
cat backend/logs/app.log
```

### Frontend Build Errors

```bash
# Clear cache
rm -rf .next node_modules package-lock.json

# Reinstall
npm install

# Check Node version
node --version  # Should be 18+

# Check TypeScript errors
npm run type-check
```

### Database Connection Errors

```bash
# Test Supabase connection
python << EOF
from database.client import db
print(db.client)
EOF

# Check environment variables
env | grep SUPABASE

# Test direct PostgreSQL connection
psql $DATABASE_URL -c "SELECT version();"
```

### CORS Errors

Update `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

Restart backend server.

### Authentication Errors

1. Check JWT secret key matches between requests
2. Verify token expiry settings
3. Check browser console for token in localStorage
4. Test login endpoint directly with curl

## Next Steps

1. **Add More Test Data**: Create multiple applicants with different profiles
2. **Train Models**: If models don't exist, run `python main.py --train`
3. **Set Up Monitoring**: Add logging aggregation (e.g., Datadog, LogRocket)
4. **Performance Testing**: Load test with tools like k6 or Apache Bench
5. **Security Audit**: Review RLS policies and API endpoints
6. **Documentation**: Update API documentation with actual endpoints

## Support

- Check logs in `backend/logs/app.log`
- Review Supabase dashboard for database errors
- Check browser console for frontend errors
- Review API docs at `http://localhost:8000/docs`

---

**🎉 Congratulations! Your system is now fully integrated and ready to use!**
