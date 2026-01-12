#!/bin/bash
# Database Migration Helper Script
# This script helps you run the migration to change applicant IDs from UUID to auto-incrementing integers

set -e  # Exit on error

echo "========================================="
echo "Applicant ID Migration Helper"
echo "========================================="
echo ""
echo "This script will help you migrate applicant IDs from UUID to auto-incrementing integers."
echo ""
echo "⚠️  WARNING: This migration will:"
echo "   - Drop all existing applicant data"
echo "   - Drop all related predictions, credit history, and repayment history"
echo "   - Recreate tables with integer IDs"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

echo ""
echo "Please provide your Supabase connection details:"
echo "(You can find these in your Supabase project settings)"
echo ""

# Get Supabase connection details
read -p "Supabase Project URL (e.g., https://xxx.supabase.co): " SUPABASE_URL
read -p "Supabase Database Password: " -s SUPABASE_PASSWORD
echo ""

# Extract project ID from URL
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/https:\/\///' | sed 's/.supabase.co//')

# Construct connection string
DB_HOST="db.${PROJECT_ID}.supabase.co"
DB_PORT="5432"
DB_NAME="postgres"
DB_USER="postgres"

echo ""
echo "Connecting to database..."
echo "Host: $DB_HOST"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ Error: psql (PostgreSQL client) is not installed."
    echo "Please install PostgreSQL client tools:"
    echo "  - macOS: brew install postgresql"
    echo "  - Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  - Windows: Download from https://www.postgresql.org/download/windows/"
    exit 1
fi

# Run the migration
echo "Running migration..."
PGPASSWORD=$SUPABASE_PASSWORD psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -f database/supabase/migrations/005_change_id_to_integer.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Run the seed script to populate data with new integer IDs:"
    echo "   cd backend && python scripts/seed_applicants.py"
    echo ""
    echo "2. Test the backend API:"
    echo "   cd backend && uvicorn api:app --reload"
    echo ""
    echo "3. Test the frontend:"
    echo "   cd frontend && npm run dev"
else
    echo ""
    echo "❌ Migration failed. Please check the error messages above."
    exit 1
fi
