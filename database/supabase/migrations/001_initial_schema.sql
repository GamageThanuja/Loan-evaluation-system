-- Initial Schema Migration for Home Credit Loan Approval System
-- Version: 001
-- Created: 2026-01-07

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('loan_officer', 'bank_manager', 'admin');
CREATE TYPE applicant_status AS ENUM ('pending', 'approved', 'rejected', 'under_review');
CREATE TYPE prediction_decision AS ENUM ('APPROVE', 'REJECT', 'MANUAL_REVIEW');
CREATE TYPE loan_purpose AS ENUM (
  'purchase',
  'refinance',
  'home_improvement',
  'debt_consolidation',
  'business',
  'education',
  'medical',
  'other'
);

-- Users table (Authentication)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role NOT NULL DEFAULT 'loan_officer',
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Applicants table
CREATE TABLE applicants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  -- Personal Information
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50) NOT NULL,
  date_of_birth DATE NOT NULL,
  gender VARCHAR(20),
  marital_status VARCHAR(50),
  education_level VARCHAR(100),
  
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

-- Predictions table
CREATE TABLE predictions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
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

-- Audit Logs table
CREATE TABLE audit_logs (
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

-- Create indexes for audit logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Model Performance Metrics table
CREATE TABLE model_performance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_version VARCHAR(50) NOT NULL,
  metric_name VARCHAR(100) NOT NULL,
  metric_value DECIMAL(10, 6) NOT NULL,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for model performance
CREATE INDEX idx_model_performance_version ON model_performance(model_version);
CREATE INDEX idx_model_performance_date ON model_performance(date DESC);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at columns
CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER applicants_updated_at
  BEFORE UPDATE ON applicants
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
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

-- Comments for documentation
COMMENT ON TABLE users IS 'User authentication and authorization';
COMMENT ON TABLE applicants IS 'Loan applicant information';
COMMENT ON TABLE predictions IS 'ML model predictions with explainability';
COMMENT ON TABLE audit_logs IS 'Audit trail for all system actions';
COMMENT ON TABLE model_performance IS 'Model performance metrics over time';
