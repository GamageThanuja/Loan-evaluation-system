# Supabase# Database Structure

This directory contains the database configuration, migrations, and client code for the Loan Evaluation System.

## Directory Structure

```
database/
├── README.md              # This file
├── schemas/               # Current table definitions (reference documentation)
│   ├── users.sql
│   ├── applicants.sql
│   ├── predictions.sql
│   ├── credit_history.sql
│   ├── repayment_history.sql
│   ├── audit_logs.sql
│   ├── views.sql
│   └── functions.sql
├── supabase/
│   ├── migrations/        # Database migrations (historical changes)
│   │   ├── 001_create_users_table.sql
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_rls_policies.sql
│   │   ├── 003_add_password_reset.sql
│   │   ├── 004_credit_repayment_history.sql
│   │   └── 005_change_id_to_integer.sql
│   └── config/            # Supabase configuration files
└── client/
    └── __init__.py        # Supabase client initialization
```

### Schemas vs Migrations

- **`schemas/`** - Current state of database tables (reference documentation)
  - Clean, documented table definitions
  - Shows what tables look like NOW
  - Useful for understanding and onboarding
  - NOT executed - just for reference

- **`supabase/migrations/`** - Historical changes to database
  - Shows how database evolved over time
  - Must be run in order
  - Actually executed to create/modify tables
  - Includes all ALTER, DROP, CREATE statements


## Database Schema

The system uses **Supabase (PostgreSQL)** with the following main tables:

### Core Tables
- **users** - User authentication and roles (loan_officer, manager)
- **applicants** - Loan applicant information with auto-incrementing integer IDs
- **predictions** - ML model predictions with SHAP explanations and Bayesian networks
- **audit_logs** - Audit trail for all system actions

### History Tables
- **credit_history** - Credit account history for applicants
- **repayment_history** - Loan repayment history and schedules

### Views
- **recent_predictions** - Latest predictions with applicant details
- **dashboard_stats** - Aggregated statistics for dashboard

## Migrations

All database migrations are in `supabase/migrations/` and should be run in order:

1. **001_create_users_table.sql** - Creates users table with authentication
2. **001_initial_schema.sql** - Creates core tables (applicants, predictions, audit_logs)
3. **002_rls_policies.sql** - Row Level Security policies
4. **003_add_password_reset.sql** - Password reset functionality
5. **004_credit_repayment_history.sql** - Credit and repayment history tables
6. **005_change_id_to_integer.sql** - Migrates applicant IDs from UUID to auto-incrementing integers

### Running Migrations

**Option 1: Supabase Dashboard (Recommended)**
1. Go to https://app.supabase.com
2. Select your project
3. Navigate to SQL Editor
4. Copy and paste the migration file contents
5. Click Run

**Option 2: Using psql (if direct access is enabled)**
```bash
psql -h db.YOUR_PROJECT.supabase.co \
     -p 5432 \
     -U postgres \
     -d postgres \
     -f database/supabase/migrations/001_initial_schema.sql
```

## Database Client

The Python database client is located in `client/__init__.py` and provides:

- Connection management (Supabase singleton client)
- CRUD operations for all tables
- Query helpers with proper error handling
- Type conversions between Python and PostgreSQL

### Usage

```python
from database.client import db

# Get applicants
applicants = db.get_applicants(user_id="...", page=1, page_size=10)

# Get single applicant
applicant = db.get_applicant_by_id(applicant_id=1)

# Create prediction
prediction = db.create_prediction(prediction_data)
```

## Environment Variables

Required environment variables (set in `.env`):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key
```

## Data Types

### Applicant ID Format
- **Before migration 005**: UUID (e.g., `c5ee79d4-aa0e-42c2-a7b9-b1dcf211c936`)
- **After migration 005**: Auto-incrementing integer (e.g., `1`, `2`, `3`)

### Status Enums
- **applicant_status**: `pending`, `approved`, `rejected`, `under_review`
- **prediction_decision**: `APPROVE`, `REJECT`, `MANUAL_REVIEW`
- **user_role**: `loan_officer`, `bank_manager`, `admin`

## Seeding Data

To populate the database with sample applicants:

```bash
cd backend
python scripts/seed_applicants.py
```

This will create sample applicants with predictions, credit history, and repayment data.

## Backup and Recovery

### Backup
Supabase provides automatic backups. You can also export data:
1. Go to Database → Backups in Supabase dashboard
2. Download backup or create manual backup

### Recovery
1. Restore from Supabase backup
2. Or re-run migrations and seed script

## Troubleshooting

### Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in `.env`
- Check if IP is allowed in Supabase Network Restrictions
- Ensure Supabase project is active

### Migration Errors
- Run migrations in order (001, 002, 003, etc.)
- Check for existing tables before running migrations
- Review error messages in Supabase SQL Editor

### Data Not Showing
- Verify migrations have been run
- Check if seed script completed successfully
- Verify authentication tokens are valid


### Predictions Table
```sql
- id: UUID (primary key)
- applicant_id: UUID (foreign key -> applicants)
- confidence: DECIMAL
- decision: ENUM ('APPROVE', 'REJECT', 'MANUAL_REVIEW')
- shap_explanation: JSONB
- bayesian_network: JSONB
- business_rules: JSONB
- model_version: VARCHAR
- created_at: TIMESTAMP
```

### Audit Logs Table
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key -> users)
- action: VARCHAR
- resource_type: VARCHAR
- resource_id: UUID
- details: JSONB
- ip_address: VARCHAR
- created_at: TIMESTAMP
```

## Row Level Security (RLS)

Supabase uses PostgreSQL Row Level Security for fine-grained access control:

### Users Table
- Users can only read their own profile
- Only admins can create/update/delete users

### Applicants Table
- Loan officers can create and read applicants
- Bank managers can approve/reject applicants
- Users can only see applicants they created (unless manager)

### Predictions Table
- Read-only access based on applicant permissions
- System-only writes (through service role)

## API Integration

The backend Python application uses the Supabase Python client:

```python
from supabase import create_client, Client

supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_SERVICE_KEY")
)

# Query example
response = supabase.table("applicants").select("*").execute()
```

## Migrations

### Creating a New Migration
```bash
supabase migration new migration_name
```

### Applying Migrations (Local)
```bash
supabase db reset
```

### Applying Migrations (Production)
```bash
supabase db push
```

## Backup & Recovery

### Manual Backup
```bash
supabase db dump > backup_$(date +%Y%m%d).sql
```

### Restore from Backup
```bash
psql $DATABASE_URL < backup_20260107.sql
```

## Testing

Run database tests:
```bash
python -m pytest backend/tests/test_database.py
```

## Production Deployment

1. Create Supabase project at [https://supabase.com](https://supabase.com)
2. Get your project URL and API keys
3. Update environment variables
4. Run migrations: `supabase db push`
5. Enable RLS policies
6. Configure backups in Supabase dashboard

## Security Best Practices

1. **Never commit `.env` files** - Always use `.env.example` as template
2. **Use Service Role Key only in backend** - Never expose in frontend
3. **Enable RLS on all tables** - Ensure proper access control
4. **Audit logs for all actions** - Track who did what
5. **Regular backups** - Automated daily backups
6. **Connection pooling** - Use PgBouncer for production
7. **SSL/TLS required** - Enforce encrypted connections

## Useful Commands

```bash
# Start local Supabase
supabase start

# Stop local Supabase
supabase stop

# View local dashboard
open http://localhost:54323

# Generate TypeScript types
supabase gen types typescript --local > types/database.ts

# Check migration status
supabase migration list

# View logs
supabase logs

# Reset database
supabase db reset
```

## Support

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Issues: Create a ticket in the project repo
