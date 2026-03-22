-- Migration: Add password reset functionality to users table
-- Version: 003
-- Created: 2026-01-07

-- Add password reset columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone VARCHAR(50);

-- Update user_role ENUM to match new roles (manager, loan_officer)
ALTER TYPE user_role RENAME TO user_role_old;
CREATE TYPE user_role AS ENUM ('manager', 'loan_officer', 'admin');

-- Update existing users table to use new role type
ALTER TABLE users 
ALTER COLUMN role TYPE user_role USING 
  CASE role::text
    WHEN 'bank_manager' THEN 'manager'::user_role
    WHEN 'loan_officer' THEN 'loan_officer'::user_role
    WHEN 'admin' THEN 'admin'::user_role
    ELSE 'loan_officer'::user_role
  END;

-- Drop old enum
DROP TYPE user_role_old;

-- Create index on reset_token for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token) WHERE reset_token IS NOT NULL;

-- Add updated_at trigger function if not exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
  BEFORE UPDATE ON users 
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON COLUMN users.reset_token IS 'Hashed password reset token';
COMMENT ON COLUMN users.reset_token_expires IS 'Reset token expiration timestamp';
COMMENT ON COLUMN users.phone IS 'User phone number for contact';
