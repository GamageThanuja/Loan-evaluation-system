-- Credit History Table Schema
-- Credit account history for applicants

CREATE TABLE credit_history (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  account_type VARCHAR(50) NOT NULL,
  account_status VARCHAR(50) DEFAULT 'open',
  account_number VARCHAR(50),
  balance DECIMAL(15, 2),
  credit_limit DECIMAL(15, 2),
  original_amount DECIMAL(15, 2),
  current_balance DECIMAL(15, 2),
  payment_status VARCHAR(50),
  opened_date DATE,
  closed_date DATE,
  last_payment_date DATE,
  payment_history_score INTEGER,
  on_time_payments INTEGER DEFAULT 0,
  late_payments INTEGER DEFAULT 0,
  missed_payments INTEGER DEFAULT 0,
  credit_utilization DECIMAL(5, 2),
  months_since_last_delinquency INTEGER,
  derogatory_marks INTEGER DEFAULT 0,
  lender_name VARCHAR(255),
  notes TEXT,
  months_reviewed INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_credit_history_applicant_id ON credit_history(applicant_id);
CREATE INDEX idx_credit_history_account_status ON credit_history(account_status);
CREATE INDEX idx_credit_history_created_at ON credit_history(created_at DESC);

-- Comments
COMMENT ON TABLE credit_history IS 'Credit account history for applicants';
COMMENT ON COLUMN credit_history.account_type IS 'Type of credit account (e.g., credit card, mortgage, auto loan)';
COMMENT ON COLUMN credit_history.account_status IS 'Account status (open, closed, charged_off)';
COMMENT ON COLUMN credit_history.payment_status IS 'Payment status (e.g., current, late, defaulted)';
COMMENT ON COLUMN credit_history.months_reviewed IS 'Number of months of history reviewed';
