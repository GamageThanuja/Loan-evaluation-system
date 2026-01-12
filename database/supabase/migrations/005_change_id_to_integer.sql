-- Migration: Change Applicant ID from UUID to Auto-Incrementing Integer
-- Version: 005
-- Created: 2026-01-12

-- This migration changes the applicants table ID from UUID to SERIAL (auto-incrementing integer)
-- WARNING: This will drop and recreate the applicants table and related data

BEGIN;

-- Step 1: Drop dependent tables and views
DROP VIEW IF EXISTS recent_predictions CASCADE;
DROP VIEW IF EXISTS dashboard_stats CASCADE;

-- Step 2: Drop tables with foreign key dependencies (in reverse order)
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS repayment_history CASCADE;
DROP TABLE IF EXISTS credit_history CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;

-- Step 3: Drop and recreate applicants table with integer ID
DROP TABLE IF EXISTS applicants CASCADE;

CREATE TABLE applicants (
  id SERIAL PRIMARY KEY,
  -- Personal Information
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50) NOT NULL,
  date_of_birth DATE NOT NULL,
  gender VARCHAR(20),
  marital_status VARCHAR(50),
  education_level VARCHAR(100),
  nic VARCHAR(50),
  
  -- Employment Information
  employment_status VARCHAR(100),
  occupation VARCHAR(200),
  employer_name VARCHAR(255),
  years_employed DECIMAL(5, 2),
  monthly_income DECIMAL(15, 2) NOT NULL,
  
  -- Financial Information
  credit_score INTEGER CHECK (credit_score BETWEEN 300 AND 850),
  existing_loans_count INTEGER DEFAULT 0,
  existing_debt_amount DECIMAL(15, 2) DEFAULT 0,
  assets_value DECIMAL(15, 2) DEFAULT 0,
  
  -- Loan Information
  loan_amount DECIMAL(15, 2) NOT NULL,
  loan_purpose loan_purpose NOT NULL,
  loan_term_months INTEGER NOT NULL,
  
  -- Address
  address_line1 VARCHAR(255),
  address_line2 VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(100),
  postal_code VARCHAR(20),
  country VARCHAR(100) DEFAULT 'USA',
  
  -- Status
  status applicant_status DEFAULT 'pending',
  eligibility_status VARCHAR(50),
  notes TEXT,
  approved_by UUID REFERENCES users(id),
  approved_at TIMESTAMP WITH TIME ZONE,
  rejected_by UUID REFERENCES users(id),
  rejected_at TIMESTAMP WITH TIME ZONE,
  rejection_reason TEXT,
  
  -- Metadata
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for applicants
CREATE INDEX idx_applicants_email ON applicants(email);
CREATE INDEX idx_applicants_status ON applicants(status);
CREATE INDEX idx_applicants_created_by ON applicants(created_by);
CREATE INDEX idx_applicants_created_at ON applicants(created_at DESC);

-- Step 4: Recreate predictions table with integer applicant_id
CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
  -- Model Outputs
  risk_score DECIMAL(5, 4) NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
  confidence DECIMAL(5, 4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  decision prediction_decision NOT NULL,
  
  -- Explainability Data (JSON)
  shap_explanation JSONB,
  bayesian_network JSONB,
  business_rules JSONB,
  
  -- Feature Values Used (for audit)
  input_features JSONB NOT NULL,
  
  -- Model Metadata
  model_version VARCHAR(50) NOT NULL,
  model_type VARCHAR(50) DEFAULT 'hybrid_tabnet_bayesian',
  processing_time_ms INTEGER,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for predictions
CREATE INDEX idx_predictions_applicant_id ON predictions(applicant_id);
CREATE INDEX idx_predictions_decision ON predictions(decision);
CREATE INDEX idx_predictions_risk_score ON predictions(risk_score);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- Step 5: Recreate credit_history table with integer applicant_id
CREATE TABLE IF NOT EXISTS credit_history (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  account_type VARCHAR(50) NOT NULL,
  credit_limit DECIMAL(15, 2),
  current_balance DECIMAL(15, 2),
  payment_status VARCHAR(50),
  opened_date DATE,
  closed_date DATE,
  months_reviewed INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_credit_history_applicant_id ON credit_history(applicant_id);

-- Step 6: Recreate repayment_history table with integer applicant_id
CREATE TABLE IF NOT EXISTS repayment_history (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  loan_type VARCHAR(50) NOT NULL,
  original_amount DECIMAL(15, 2) NOT NULL,
  remaining_balance DECIMAL(15, 2) NOT NULL,
  monthly_payment DECIMAL(15, 2) NOT NULL,
  payment_status VARCHAR(50) NOT NULL,
  days_past_due INTEGER DEFAULT 0,
  start_date DATE NOT NULL,
  end_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_repayment_history_applicant_id ON repayment_history(applicant_id);

-- Step 7: Recreate audit_logs table with integer resource_id support
DROP TABLE IF EXISTS audit_logs CASCADE;

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id VARCHAR(100),  -- Changed to VARCHAR to support both UUID and integer
  details JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for audit logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Step 8: Add trigger for updated_at on applicants
CREATE TRIGGER applicants_updated_at
  BEFORE UPDATE ON applicants
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Step 9: Recreate views
CREATE VIEW recent_predictions AS
SELECT 
  p.id,
  p.applicant_id,
  a.name AS applicant_name,
  p.risk_score,
  p.confidence,
  p.decision,
  p.model_version,
  p.created_at
FROM predictions p
JOIN applicants a ON p.applicant_id = a.id
ORDER BY p.created_at DESC
LIMIT 100;

CREATE VIEW dashboard_stats AS
SELECT
  COUNT(DISTINCT a.id) AS total_applicants,
  COUNT(DISTINCT CASE WHEN a.status = 'approved' THEN a.id END) AS approved_count,
  COUNT(DISTINCT CASE WHEN a.status = 'rejected' THEN a.id END) AS rejected_count,
  COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN a.id END) AS pending_count,
  AVG(CASE WHEN p.decision = 'APPROVE' THEN 1 ELSE 0 END) AS approval_rate,
  AVG(p.risk_score) AS avg_risk_score,
  AVG(p.confidence) AS avg_confidence
FROM applicants a
LEFT JOIN predictions p ON a.id = p.applicant_id
WHERE a.created_at >= NOW() - INTERVAL '30 days';

-- Comments
COMMENT ON TABLE applicants IS 'Loan applicant information with auto-incrementing integer IDs';
COMMENT ON TABLE predictions IS 'ML model predictions with explainability';
COMMENT ON TABLE credit_history IS 'Credit history records for applicants';
COMMENT ON TABLE repayment_history IS 'Repayment history records for applicants';

COMMIT;
