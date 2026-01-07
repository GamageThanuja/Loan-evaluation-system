# Changelog

All notable changes to the Loan Evaluation System will be documented in this file.

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
