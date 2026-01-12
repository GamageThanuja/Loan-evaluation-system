# Migration Instructions: Running via Supabase Dashboard

Since direct PostgreSQL connections are timing out, you should run the migration through the Supabase SQL Editor instead.

## Steps to Run Migration

### 1. Open Supabase SQL Editor

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project: `heoagebaztzfwzhpwere`
3. Click on **SQL Editor** in the left sidebar

### 2. Run the Migration

1. Click **New Query** button
2. Copy the entire contents of the migration file:
   - File: `database/supabase/migrations/005_change_id_to_integer.sql`
3. Paste into the SQL Editor
4. Click **Run** button (or press Cmd/Ctrl + Enter)

### 3. Verify Migration Success

After running, you should see:
- ✅ "Success. No rows returned" (this is expected)
- Check the **Table Editor** to verify:
  - `applicants` table exists with `id` column type as `int4` (integer)
  - `predictions`, `credit_history`, `repayment_history` tables have `applicant_id` as `int4`

### 4. Reseed the Database

Once migration is successful, run the seed script:

```bash
cd backend
python scripts/seed_applicants.py
```

### 5. Verify Data

In Supabase Table Editor:
- Open `applicants` table
- Verify you see records with IDs: 1, 2, 3, etc. (not UUIDs)

---

## Alternative: Enable Direct Database Access

If you prefer using `psql`, you need to enable direct database access in Supabase:

1. Go to **Project Settings** → **Database**
2. Scroll to **Connection Pooling**
3. Enable **Direct Connection** (not Pooler)
4. Use the connection string provided there
5. Make sure your IP is allowed in **Database Settings** → **Network Restrictions**

However, using the SQL Editor is simpler and recommended for migrations.

---

## Troubleshooting

If the migration fails in SQL Editor:
- Check error message carefully
- Ensure you're running the complete SQL file
- Verify no syntax errors in the migration file
- Check that the `users` table exists (required for foreign keys)

If you see "relation already exists" errors:
- Some tables might already exist
- You may need to manually drop tables first or modify the migration
