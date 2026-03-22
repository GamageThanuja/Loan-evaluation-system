-- Migration: Status Management Tables
-- Version: 008
-- Created: 2026-01-15
-- Description: Creates tables for eligibility statuses, application statuses, and status colors

BEGIN;

-- ============================================
-- 1. Eligibility Statuses Table
-- ============================================
CREATE TABLE IF NOT EXISTS eligibility_statuses (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE NOT NULL, -- 'eligible', 'not_eligible', 'not_checked'
  name VARCHAR(100) NOT NULL, -- 'Eligible', 'Not Eligible', 'Not Checked'
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default eligibility statuses
INSERT INTO eligibility_statuses (code, name, description, display_order) VALUES
  ('eligible', 'Eligible', 'Applicant is eligible for the loan', 1),
  ('not_eligible', 'Not Eligible', 'Applicant is not eligible for the loan', 2),
  ('not_checked', 'Not Checked', 'Eligibility has not been checked yet', 0)
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 2. Application Statuses Table
-- ============================================
CREATE TABLE IF NOT EXISTS application_statuses (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE NOT NULL, -- 'pending', 'under_review', 'rejected', 'approved'
  name VARCHAR(100) NOT NULL, -- 'Pending', 'Under Review', 'Rejected', 'Approved'
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add color_code and color_name columns if they don't exist
ALTER TABLE application_statuses 
  ADD COLUMN IF NOT EXISTS color_code VARCHAR(7),
  ADD COLUMN IF NOT EXISTS color_name VARCHAR(50);

-- Insert default application statuses (without colors first, then update with colors)
INSERT INTO application_statuses (code, name, description, display_order) VALUES
  ('pending', 'Pending', 'Application is pending initial review', 1),
  ('under_review', 'Under Review', 'Application is under review by manager', 2),
  ('rejected', 'Rejected', 'Application has been rejected', 3),
  ('approved', 'Approved', 'Application has been approved', 4)
ON CONFLICT (code) DO NOTHING;

-- Update existing records with color codes
UPDATE application_statuses SET 
  color_code = CASE code
    WHEN 'approved' THEN '#2e7d32'
    WHEN 'rejected' THEN '#d32f2f'
    WHEN 'under_review' THEN '#ed6c02'
    WHEN 'pending' THEN '#1976d2'
    ELSE '#757575'
  END,
  color_name = CASE code
    WHEN 'approved' THEN 'success'
    WHEN 'rejected' THEN 'error'
    WHEN 'under_review' THEN 'warning'
    WHEN 'pending' THEN 'info'
    ELSE 'default'
  END
WHERE color_code IS NULL;

-- ============================================
-- 3. Status Colors Table
-- ============================================
CREATE TABLE IF NOT EXISTS status_colors (
  id SERIAL PRIMARY KEY,
  status_id INTEGER NOT NULL REFERENCES application_statuses(id) ON DELETE CASCADE,
  color_code VARCHAR(7) NOT NULL, -- HEX color code (e.g., '#4caf50')
  color_name VARCHAR(50), -- 'success', 'error', 'warning', 'info'
  is_primary BOOLEAN DEFAULT TRUE, -- Primary color for this status
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(status_id, is_primary) -- Only one primary color per status
);

-- Insert default status colors (matching Material-UI color scheme)
-- Note: Colors are now also stored directly in application_statuses table
-- This table provides additional color variations if needed
INSERT INTO status_colors (status_id, color_code, color_name, is_primary)
SELECT 
  s.id,
  s.color_code,
  s.color_name,
  TRUE
FROM application_statuses s
WHERE s.color_code IS NOT NULL
ON CONFLICT (status_id, is_primary) DO NOTHING;

-- ============================================
-- 4. Update Applicants Table
-- ============================================
-- Add foreign key columns (keeping old columns for backward compatibility during migration)
ALTER TABLE applicants 
  ADD COLUMN IF NOT EXISTS eligibility_status_id INTEGER REFERENCES eligibility_statuses(id),
  ADD COLUMN IF NOT EXISTS application_status_id INTEGER REFERENCES application_statuses(id);

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_applicants_eligibility_status_id ON applicants(eligibility_status_id);
CREATE INDEX IF NOT EXISTS idx_applicants_application_status_id ON applicants(application_status_id);

-- Migrate existing data to use new foreign keys
-- Map existing eligibility_status values to IDs
UPDATE applicants a
SET eligibility_status_id = es.id
FROM eligibility_statuses es
WHERE LOWER(a.eligibility_status) = es.code
  AND a.eligibility_status_id IS NULL;

-- Map existing status enum values to IDs
UPDATE applicants a
SET application_status_id = s.id
FROM application_statuses s
WHERE LOWER(a.status::text) = s.code
  AND a.application_status_id IS NULL;

-- ============================================
-- 5. Create Update Trigger
-- ============================================
-- Create or replace the trigger function
CREATE OR REPLACE FUNCTION update_status_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing triggers if they exist, then create them
DROP TRIGGER IF EXISTS eligibility_statuses_updated_at ON eligibility_statuses;
CREATE TRIGGER eligibility_statuses_updated_at
  BEFORE UPDATE ON eligibility_statuses
  FOR EACH ROW
  EXECUTE FUNCTION update_status_updated_at();

DROP TRIGGER IF EXISTS application_statuses_updated_at ON application_statuses;
CREATE TRIGGER application_statuses_updated_at
  BEFORE UPDATE ON application_statuses
  FOR EACH ROW
  EXECUTE FUNCTION update_status_updated_at();

DROP TRIGGER IF EXISTS status_colors_updated_at ON status_colors;
CREATE TRIGGER status_colors_updated_at
  BEFORE UPDATE ON status_colors
  FOR EACH ROW
  EXECUTE FUNCTION update_status_updated_at();

-- ============================================
-- 6. Create Views for Easy Access
-- ============================================
-- Drop the view if it exists (to handle column structure changes)
DROP VIEW IF EXISTS v_application_statuses_with_colors;

-- Recreate the view with the correct structure
CREATE VIEW v_application_statuses_with_colors AS
SELECT 
  s.id,
  s.code,
  s.name,
  s.description,
  s.color_code,
  s.color_name,
  s.is_active,
  s.display_order,
  s.created_at,
  s.updated_at
FROM application_statuses s
WHERE s.is_active = TRUE
ORDER BY s.display_order;

-- Comments
COMMENT ON TABLE eligibility_statuses IS 'Manages eligibility status values with unique IDs';
COMMENT ON TABLE application_statuses IS 'Manages application status values with unique IDs and color codes';
COMMENT ON TABLE status_colors IS 'Maps application statuses to color codes for UI consistency (optional - colors can also be stored directly in application_statuses)';
COMMENT ON COLUMN application_statuses.color_code IS 'HEX color code for this status (e.g., #2e7d32)';
COMMENT ON COLUMN application_statuses.color_name IS 'Color name for Material-UI compatibility (e.g., success, error, warning, info)';
COMMENT ON COLUMN applicants.eligibility_status_id IS 'Foreign key to eligibility_statuses table';
COMMENT ON COLUMN applicants.application_status_id IS 'Foreign key to application_statuses table';

COMMIT;

