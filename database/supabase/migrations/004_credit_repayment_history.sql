-- Credit and Repayment History Tables Migration
-- Version: 004
-- Created: 2026-01-10

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types for credit and repayment history
CREATE TYPE account_type AS ENUM ('credit_card', 'personal_loan', 'mortgage', 'auto_loan', 'student_loan', 'other');
CREATE TYPE account_status AS ENUM ('open', 'closed', 'charged_off', 'in_collections');
CREATE TYPE loan_status AS ENUM ('active', 'closed', 'defaulted', 'paid_off');

-- Credit History table
CREATE TABLE credit_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
  -- Account Information
  account_type account_type NOT NULL,
  account_status account_status NOT NULL DEFAULT 'open',
  account_number VARCHAR(50),
  
  -- Financial Details
  balance DECIMAL(15, 2) DEFAULT 0,
  credit_limit DECIMAL(15, 2),
  original_amount DECIMAL(15, 2),
  
  -- Dates
  opened_date DATE NOT NULL,
  closed_date DATE,
  last_payment_date DATE,
  
  -- Payment History
  payment_history_score INTEGER CHECK (payment_history_score BETWEEN 0 AND 100),
  on_time_payments INTEGER DEFAULT 0,
  late_payments INTEGER DEFAULT 0,
  missed_payments INTEGER DEFAULT 0,
  
  -- Credit Metrics
  credit_utilization DECIMAL(5, 2) CHECK (credit_utilization BETWEEN 0 AND 100),
  months_since_last_delinquency INTEGER,
  derogatory_marks INTEGER DEFAULT 0,
  
  -- Additional Info
  lender_name VARCHAR(255),
  notes TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for credit_history
CREATE INDEX idx_credit_history_applicant_id ON credit_history(applicant_id);
CREATE INDEX idx_credit_history_account_type ON credit_history(account_type);
CREATE INDEX idx_credit_history_account_status ON credit_history(account_status);
CREATE INDEX idx_credit_history_created_at ON credit_history(created_at DESC);

-- Repayment History table
CREATE TABLE repayment_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  applicant_id UUID NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
  -- Loan Information
  loan_id VARCHAR(50) UNIQUE,
  loan_type account_type NOT NULL,
  loan_status loan_status NOT NULL DEFAULT 'active',
  
  -- Financial Details
  original_amount DECIMAL(15, 2) NOT NULL,
  remaining_balance DECIMAL(15, 2) DEFAULT 0,
  monthly_payment DECIMAL(15, 2),
  interest_rate DECIMAL(5, 2),
  
  -- Dates
  start_date DATE NOT NULL,
  end_date DATE,
  maturity_date DATE,
  next_due_date DATE,
  
  -- Payment Performance
  on_time_payments INTEGER DEFAULT 0,
  late_payments INTEGER DEFAULT 0,
  missed_payments INTEGER DEFAULT 0,
  total_payments_made INTEGER DEFAULT 0,
  
  -- Payment Details (JSON array of recent payments)
  recent_payments JSONB DEFAULT '[]'::jsonb,
  
  -- Metrics
  average_days_late DECIMAL(5, 2) DEFAULT 0,
  largest_late_days INTEGER DEFAULT 0,
  on_time_payment_percentage DECIMAL(5, 2) CHECK (on_time_payment_percentage BETWEEN 0 AND 100),
  
  -- Additional Info
  lender_name VARCHAR(255),
  notes TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for repayment_history
CREATE INDEX idx_repayment_history_applicant_id ON repayment_history(applicant_id);
CREATE INDEX idx_repayment_history_loan_type ON repayment_history(loan_type);
CREATE INDEX idx_repayment_history_loan_status ON repayment_history(loan_status);
CREATE INDEX idx_repayment_history_created_at ON repayment_history(created_at DESC);

-- Add triggers for updated_at columns
CREATE TRIGGER credit_history_updated_at
  BEFORE UPDATE ON credit_history
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER repayment_history_updated_at
  BEFORE UPDATE ON repayment_history
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create view for applicant financial summary
CREATE VIEW applicant_financial_summary AS
SELECT 
  a.id AS applicant_id,
  a.name AS applicant_name,
  a.credit_score,
  COUNT(DISTINCT ch.id) AS total_credit_accounts,
  COUNT(DISTINCT CASE WHEN ch.account_status = 'open' THEN ch.id END) AS open_accounts,
  SUM(CASE WHEN ch.account_status = 'open' THEN ch.balance ELSE 0 END) AS total_credit_balance,
  SUM(CASE WHEN ch.account_status = 'open' THEN ch.credit_limit ELSE 0 END) AS total_credit_limit,
  AVG(ch.credit_utilization) AS avg_credit_utilization,
  COUNT(DISTINCT rh.id) AS total_loans,
  COUNT(DISTINCT CASE WHEN rh.loan_status = 'active' THEN rh.id END) AS active_loans,
  SUM(CASE WHEN rh.loan_status = 'active' THEN rh.remaining_balance ELSE 0 END) AS total_loan_balance,
  AVG(rh.on_time_payment_percentage) AS avg_on_time_payment_pct
FROM applicants a
LEFT JOIN credit_history ch ON a.id = ch.applicant_id
LEFT JOIN repayment_history rh ON a.id = rh.applicant_id
GROUP BY a.id, a.name, a.credit_score;

-- Comments for documentation
COMMENT ON TABLE credit_history IS 'Credit account history for loan applicants';
COMMENT ON TABLE repayment_history IS 'Loan repayment history for applicants';
COMMENT ON VIEW applicant_financial_summary IS 'Aggregated financial metrics per applicant';
