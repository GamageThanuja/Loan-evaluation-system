# Changelog

All notable changes to the Loan Evaluation System will be documented in this file.

## [2026-01-07] - Frontend Registration & Branding Update

### Added
- **Registration/Signup Page** (`frontend/app/register/page.tsx`)
  - Complete user registration form with validation
  - Password strength requirements (8+ chars, uppercase, lowercase, number)
  - Phone number field (optional)
  - Role selection (Manager or Loan Officer)
  - Password confirmation matching
  - Success message and auto-redirect to login
  - Link to login page for existing users

### Changed
- **System Rebranding: "Home Credit Loan Approval System" → "LoanWise"**
  - Backend API title updated to "LoanWise API"
  - Frontend AuthLayout: "LoanWise - Smart Loan Evaluation"
  - Frontend MainLayout sidebar: "LoanWise"
  - Login page messaging updated
  - All user-facing text updated to reflect new brand
- Login page now includes "Sign Up" link to registration page
- Updated routing to include `/register` as public route
- Enhanced login page with better getting started instructions

---

## [2026-01-07] - Authentication System Cleanup & Fixes

### Added
- **Frontend Authentication Service** (`frontend/lib/auth/authService.ts`)
  - Complete auth API integration with backend
  - Methods: register, login, logout, forgotPassword, resetPassword, verifyToken
  
### Fixed
- Removed duplicate login endpoint from `backend/api.py`
- All authentication endpoints now exclusively in `backend/routers/auth.py`
- Fixed module import paths for middleware and database client
- Installed missing dependencies (email-validator, pyjwt, bcrypt, passlib)
- Resolved Pydantic v2 compatibility issues

### Changed
- Centralized authentication to dedicated router only
- Cleaned up API structure to avoid endpoint duplication
- Backend API now only includes auth router mount, not duplicate endpoints
- Removed version prefix from auth endpoints (changed from `/api/v1/auth/*` to `/api/auth/*`)
- **Frontend fully integrated with backend authentication**
  - Updated `useAuth` hook to use real API calls instead of mock authentication
  - Added token management and persistence in localStorage
  - Updated API client to automatically inject JWT tokens
  - Updated User type to match backend response (role: 'manager' | 'loan_officer')
  - Enhanced error handling with backend error messages
  - Login page now connects to `/api/auth/login` endpoint

### Technical Details
- Authentication endpoints available at `/api/auth/*` prefix
- Login endpoint: `/api/auth/login`
- All auth endpoints use consistent response models
- Backend successfully running on port 8000
- Frontend running on port 3000
- JWT tokens stored in localStorage via zustand persist
- Automatic token injection in API requests via axios interceptor

---

## [2026-01-07] - Role-Based Authentication System

### Added
- **Authentication Router** (`backend/routers/auth.py`)
  - POST `/api/v1/auth/register` - User registration with role selection
  - POST `/api/v1/auth/login` - User login with JWT token generation
  - POST `/api/v1/auth/logout` - User logout
  - POST `/api/v1/auth/forgot-password` - Password reset request
  - POST `/api/v1/auth/reset-password` - Password reset with token
  - GET `/api/v1/auth/verify-token` - JWT token verification

- **User Roles**
  - `manager` - Bank managers with full access
  - `loan_officer` - Loan officers with standard access

- **Database Migration** (`database/supabase/migrations/003_add_password_reset.sql`)
  - Added `reset_token` column to users table
  - Added `reset_token_expires` column for token expiration
  - Added `phone` column for user contact
  - Updated user roles enum (manager, loan_officer, admin)

- **Database Client Methods**
  - `update_user_last_login()` - Track user login times
  - `update_user_reset_token()` - Store password reset tokens
  - `get_user_by_reset_token()` - Retrieve user by reset token
  - `update_user_password()` - Update password and clear reset token

- **Environment Variables**
  - `NEXT_PUBLIC_SUPABASE_URL` - Frontend Supabase URL
  - `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` - Frontend Supabase key

### Changed
- Integrated auth router into main API (`backend/api.py`)
- Updated middleware to support role-based access control
- Enhanced security with password reset token hashing

### Security Features
- JWT-based authentication with configurable expiration
- Password hashing using bcrypt
- Secure password reset tokens with SHA-256 hashing
- Token expiration (1 hour for reset tokens, 24 hours for access tokens)
- Role-based access control middleware

---

## [2026-01-07] - Environment Configuration Consolidation

### Added
- Created centralized `.env` file at project root with all environment variables
- Created `.env.example` as a template for environment configuration
- Added comprehensive environment variable documentation in README.md

### Changed
- Consolidated all environment variables into single `.env` file
- Backend now loads environment variables from root `.env` file
- Frontend now loads environment variables from root `.env` file

### Removed
- Removed `my-loan-approval-frontend/.env.local` (consolidated into root `.env`)
- Removed duplicate `my-loan-approval-frontend/` directory (kept `frontend/` with full features)
- Removed redundant documentation files:
  - `ENV_SETUP.md`
  - `COMPLETION_SUMMARY.md`
  - `PROJECT_README.md`
  - `SETUP_GUIDE.md`
  - `QUICKSTART.md`

### Environment Variables
All configuration is now in `.env`:
- **Database**: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
- **Backend**: API_HOST, API_PORT, API_DEBUG, CORS_ORIGINS, LOG_LEVEL, SECRET_KEY, MODEL_VERSION
- **Frontend**: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_NAME, NEXT_PUBLIC_RISK_THRESHOLD_*

### Notes
- Single source of truth for environment configuration
- Better maintainability and reduced confusion
- Cleaner project structure

---

## Future Changes
All future changes will be documented here chronologically.
