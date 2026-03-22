-- Full Database Recreation Script for Loan Evaluation System v4.0
-- RUN THIS IN SUPABASE SQL EDITOR TO FIX "MISSING COLUMN" ERRORS

-- 1. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Clean up existing tables (CASCADE drops dependent tables like predictions)
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS applicants CASCADE;
-- NOTE: We keep users table to preserve logins. If you want a full reset, uncomment the next line:
-- DROP TABLE IF EXISTS users CASCADE; 

-- 3. Create Users Table (if not exists)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL DEFAULT 'loan_officer',
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP WITH TIME ZONE,
  reset_token VARCHAR(255),
  reset_token_expires TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create Applicants Table (Updated with v4.0 columns)
CREATE TABLE applicants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_number SERIAL,
  
  -- Personal Information
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50) NOT NULL,
  nic VARCHAR(20) NOT NULL, -- Required by v4.0
  date_of_birth DATE NOT NULL,
  gender VARCHAR(20),
  marital_status VARCHAR(50),
  dependents INTEGER DEFAULT 0,
  education_level VARCHAR(100),
  
  -- Employment Information
  employment_status VARCHAR(100), -- Maps to employment_type
  occupation VARCHAR(200),        -- Maps to job_title
  employer_name VARCHAR(255),
  years_employed DECIMAL(5, 2),   -- Maps to employment_length
  monthly_income DECIMAL(15, 2) NOT NULL,
  annual_income DECIMAL(15, 2),
  
  -- Financial Information
  account_number VARCHAR(50),
  assets_value DECIMAL(15, 2) DEFAULT 0,
  monthly_expenses DECIMAL(15, 2) DEFAULT 0,
  credit_score INTEGER,
  existing_loans_count INTEGER DEFAULT 0,
  existing_debt_amount DECIMAL(15, 2) DEFAULT 0,
  
  -- Loan Application Details
  loan_amount DECIMAL(15, 2) NOT NULL,
  loan_purpose VARCHAR(100) NOT NULL,
  loan_term_months INTEGER NOT NULL,
  
  -- Address Information
  address_line1 VARCHAR(255), -- Maps to address
  address_line2 VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(100),         -- Maps to district
  postal_code VARCHAR(20),
  country VARCHAR(100) DEFAULT 'Sri Lanka',
  
  -- System Status & Metadata
  status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, under_review
  eligibility_status VARCHAR(50),       -- eligible, not_eligible
  risk_score DECIMAL(5, 4),             -- Cached risk score
  
  notes TEXT,
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP WITH TIME ZONE,
  rejected_by UUID REFERENCES users(id),
  rejected_at TIMESTAMP WITH TIME ZONE,
  rejection_reason TEXT,
  
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create Predictions Table
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
  risk_score DECIMAL(5, 4) NOT NULL,
  confidence DECIMAL(5, 4) NOT NULL,
  decision VARCHAR(50) NOT NULL, -- APPROVE, REJECT, MANUAL_REVIEW
  
  -- Explainability
  shap_explanation JSONB,
  bayesian_network JSONB,
  business_rules JSONB,
  input_features JSONB,
  
  model_version VARCHAR(50) NOT NULL,
  processing_time_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create Audit Logs Table (if not exists)
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id UUID,
  details JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Create Model Performance Table (if not exists)
CREATE TABLE IF NOT EXISTS model_performance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_version VARCHAR(50) NOT NULL,
  metric_name VARCHAR(100) NOT NULL,
  metric_value DECIMAL(10, 6) NOT NULL,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_applicants_nic ON applicants(nic);
CREATE INDEX IF NOT EXISTS idx_applicants_email ON applicants(email);
CREATE INDEX IF NOT EXISTS idx_predictions_applicant_id ON predictions(applicant_id);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS applicants_updated_at ON applicants;
CREATE TRIGGER applicants_updated_at
  BEFORE UPDATE ON applicants
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
