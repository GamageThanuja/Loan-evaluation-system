# 🚀 Quick Start Guide

Get the Home Credit Loan Approval System running in 5 minutes!

## Prerequisites Check

```bash
node --version    # Should be 18+
python --version  # Should be 3.8+
```

## Step 1: Setup Database (Choose One)

### Option A: Supabase Cloud (Recommended)
1. Go to [supabase.com](https://supabase.com) → New Project
2. Copy your credentials
3. Run migrations in SQL Editor:
   - Copy `database/supabase/migrations/001_initial_schema.sql` → Execute
   - Copy `database/supabase/migrations/002_rls_policies.sql` → Execute

### Option B: Local Supabase
```bash
brew install supabase/tap/supabase
cd database
supabase start
```

## Step 2: Start Backend (3 commands)

```bash
cd backend

# Install
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Supabase credentials

# Run
python api.py
```

Backend running at **http://localhost:8000** ✅

## Step 3: Start Frontend (2 commands)

```bash
cd frontend

# Install (if not done)
npm install

# Run
npm run dev
```

Frontend running at **http://localhost:3000** ✅

## Step 4: Login

Open http://localhost:3000

**Test Credentials:**
- Email: `officer@example.com`
- Password: `password123`
- Role: `Loan Officer`

## Step 5: Create Test User (If needed)

In Supabase SQL Editor:

```sql
INSERT INTO users (email, name, role, password_hash) VALUES
('officer@example.com', 'John Officer', 'loan_officer', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIhLU8kQ3G'),
('manager@example.com', 'Jane Manager', 'bank_manager',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIhLU8kQ3G');
```

## ✅ You're Done!

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Supabase: http://localhost:54323 (local) or your cloud dashboard

## Common Issues

**Backend won't start?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Frontend build error?**
```bash
rm -rf .next node_modules
npm install
```

**Can't login?**
- Check if backend is running: `curl http://localhost:8000/health`
- Check Supabase connection: Verify .env credentials
- Check if user exists: Go to Supabase → Table Editor → users

## Next Steps

1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
2. Read [PROJECT_README.md](PROJECT_README.md) for architecture
3. Read [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) for what's been done

## Need Help?

- API Documentation: http://localhost:8000/docs
- Backend logs: `backend/logs/app.log`
- Browser console: Check for errors
- Database: Check Supabase dashboard

---

**Happy coding! 🎉**
