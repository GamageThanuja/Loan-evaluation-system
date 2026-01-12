-- Credit History Table Schema
-- Credit account history for applicants

CREATE TABLE credit_history (
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

-- Indexes
CREATE INDEX idx_credit_history_applicant_id ON credit_history(applicant_id);

-- Comments
COMMENT ON TABLE credit_history IS 'Credit account history for applicants';
COMMENT ON COLUMN credit_history.account_type IS 'Type of credit account (e.g., credit card, mortgage, auto loan)';
COMMENT ON COLUMN credit_history.payment_status IS 'Payment status (e.g., current, late, defaulted)';
COMMENT ON COLUMN credit_history.months_reviewed IS 'Number of months of history reviewed';
