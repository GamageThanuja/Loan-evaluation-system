-- Transactions Table Schema
-- Loan-related transaction history for applicants

CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  loan_id VARCHAR(50),
  transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
  transaction_type VARCHAR(50) NOT NULL,
  amount DECIMAL(15, 2) NOT NULL,
  description TEXT,
  status VARCHAR(50) NOT NULL,
  payment_method VARCHAR(50),
  reference_number VARCHAR(100),
  balance DECIMAL(15, 2),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_transactions_applicant_id ON transactions(applicant_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date DESC);

-- Comments
COMMENT ON TABLE transactions IS 'Transaction history for applicant loans';
COMMENT ON COLUMN transactions.transaction_type IS 'payment, disbursement, fee, refund, adjustment, penalty';
