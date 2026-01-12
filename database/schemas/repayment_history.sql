-- Repayment History Table Schema
-- Loan repayment history and schedules

CREATE TABLE repayment_history (
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

-- Indexes
CREATE INDEX idx_repayment_history_applicant_id ON repayment_history(applicant_id);

-- Comments
COMMENT ON TABLE repayment_history IS 'Loan repayment history records for applicants';
COMMENT ON COLUMN repayment_history.loan_type IS 'Type of loan (e.g., personal, auto, mortgage)';
COMMENT ON COLUMN repayment_history.payment_status IS 'Current payment status (e.g., current, late, defaulted)';
COMMENT ON COLUMN repayment_history.days_past_due IS 'Number of days payment is overdue (0 if current)';
