# Database Schemas - Reference Documentation

This directory contains **reference documentation** for the current state of all database tables, views, and functions.

## Purpose

These schema files show what your database looks like **right now**, after all migrations have been applied. They are:

- ✅ **For reference and documentation**
- ✅ **Helpful for onboarding new developers**
- ✅ **Easy to understand current structure**
- ❌ **NOT executed** - just for reading

## Files

- **`users.sql`** - User authentication and roles
- **`applicants.sql`** - Loan applicant information (with integer IDs)
- **`predictions.sql`** - ML predictions with explainability
- **`credit_history.sql`** - Credit account history
- **`repayment_history.sql`** - Loan repayment records
- **`audit_logs.sql`** - System audit trail
- **`views.sql`** - Database views (recent_predictions, dashboard_stats)
- **`functions.sql`** - Database functions and triggers

## Key Changes

### Applicant ID Migration
After migration `005_change_id_to_integer.sql`:
- **Before**: `id UUID PRIMARY KEY DEFAULT uuid_generate_v4()`
- **After**: `id SERIAL PRIMARY KEY` (auto-incrementing integers: 1, 2, 3...)

## How to Use

1. **Want to know current table structure?** → Read the schema file
2. **Want to see how it evolved?** → Check `supabase/migrations/`
3. **Want to create the database?** → Run migrations in order

## Updating Schema Files

When you create a new migration that changes table structure:
1. Run the migration
2. Update the corresponding schema file to reflect the new structure
3. Keep schemas in sync with actual database state
