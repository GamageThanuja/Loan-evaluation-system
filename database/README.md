# Supabase Database Configuration

## Overview
This directory contains Supabase database configuration, migrations, and schemas for the Home Credit Loan Approval System.

## Structure
```
database/
├── README.md               # This file
├── .env.example           # Example environment variables
├── supabase/
│   ├── config.toml        # Supabase configuration
│   ├── migrations/        # Database migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_auth_tables.sql
│   │   └── 003_prediction_tables.sql
│   └── seed.sql           # Seed data
├── schemas/
│   ├── users.sql          # Users table schema
│   ├── applicants.sql     # Applicants table schema
│   ├── predictions.sql    # Predictions table schema
│   └── audit_logs.sql     # Audit logs schema
└── client/
    ├── __init__.py        # Supabase client initialization
    └── queries.py         # Common database queries
```

## Setup

### 1. Install Supabase CLI
```bash
brew install supabase/tap/supabase
```

### 2. Initialize Supabase
```bash
cd database
supabase init
```

### 3. Start Local Development
```bash
supabase start
```

### 4. Apply Migrations
```bash
supabase db reset
```

## Environment Variables

Create a `.env` file in the `backend/` directory with:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
DATABASE_URL=postgresql://postgres:[password]@db.[project_ref].supabase.co:5432/postgres
```

## Database Schema

### Users Table
```sql
- id: UUID (primary key)
- email: VARCHAR (unique)
- name: VARCHAR
- role: ENUM ('loan_officer', 'bank_manager')
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Applicants Table
```sql
- id: UUID (primary key)
- name: VARCHAR
- email: VARCHAR (unique)
- phone: VARCHAR
- income: DECIMAL
- credit_score: INTEGER
- loan_amount: DECIMAL
- loan_purpose: VARCHAR
- status: ENUM ('pending', 'approved', 'rejected')
- created_by: UUID (foreign key -> users)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Predictions Table
```sql
- id: UUID (primary key)
- applicant_id: UUID (foreign key -> applicants)
- risk_score: DECIMAL
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
