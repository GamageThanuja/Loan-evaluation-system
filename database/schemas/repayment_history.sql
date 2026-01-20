-- Repayment History Table Schema
-- Loan repayment history and schedules

CREATE TABLE repayment_history (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  loan_id VARCHAR(50),
  loan_type VARCHAR(50) NOT NULL,
  loan_status VARCHAR(50) DEFAULT 'active',
  original_amount DECIMAL(15, 2) NOT NULL,
  remaining_balance DECIMAL(15, 2) NOT NULL,
  monthly_payment DECIMAL(15, 2) NOT NULL,
  interest_rate DECIMAL(5, 2),
  payment_status VARCHAR(50) NOT NULL,
  days_past_due INTEGER DEFAULT 0,
  start_date DATE NOT NULL,
  end_date DATE,
  maturity_date DATE,
  next_due_date DATE,
  on_time_payments INTEGER DEFAULT 0,
  late_payments INTEGER DEFAULT 0,
  missed_payments INTEGER DEFAULT 0,
  total_payments_made INTEGER DEFAULT 0,
  recent_payments JSONB DEFAULT '[]'::jsonb,
  average_days_late DECIMAL(5, 2) DEFAULT 0,
  largest_late_days INTEGER DEFAULT 0,
  on_time_payment_percentage DECIMAL(5, 2),
  lender_name VARCHAR(255),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_repayment_history_applicant_id ON repayment_history(applicant_id);
CREATE INDEX idx_repayment_history_loan_status ON repayment_history(loan_status);
CREATE INDEX idx_repayment_history_created_at ON repayment_history(created_at DESC);

-- Comments
COMMENT ON TABLE repayment_history IS 'Loan repayment history records for applicants';
COMMENT ON COLUMN repayment_history.loan_type IS 'Type of loan (e.g., personal, auto, mortgage)';
COMMENT ON COLUMN repayment_history.loan_status IS 'Loan status (active, closed, defaulted, paid_off)';
COMMENT ON COLUMN repayment_history.payment_status IS 'Current payment status (e.g., current, late, defaulted)';
COMMENT ON COLUMN repayment_history.days_past_due IS 'Number of days payment is overdue (0 if current)';
