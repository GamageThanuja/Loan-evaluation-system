-- Expand credit_history and repayment_history tables to match rich history payloads
-- Version: 007
-- Created: 2026-01-21

-- Credit history updates
ALTER TABLE credit_history
  ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'open',
  ADD COLUMN IF NOT EXISTS account_number VARCHAR(50),
  ADD COLUMN IF NOT EXISTS balance DECIMAL(15, 2),
  ADD COLUMN IF NOT EXISTS original_amount DECIMAL(15, 2),
  ADD COLUMN IF NOT EXISTS last_payment_date DATE,
  ADD COLUMN IF NOT EXISTS payment_history_score INTEGER,
  ADD COLUMN IF NOT EXISTS on_time_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS late_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS missed_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS credit_utilization DECIMAL(5, 2),
  ADD COLUMN IF NOT EXISTS months_since_last_delinquency INTEGER,
  ADD COLUMN IF NOT EXISTS derogatory_marks INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS lender_name VARCHAR(255),
  ADD COLUMN IF NOT EXISTS notes TEXT,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

UPDATE credit_history
SET balance = current_balance
WHERE balance IS NULL AND current_balance IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_credit_history_account_status ON credit_history(account_status);
CREATE INDEX IF NOT EXISTS idx_credit_history_created_at ON credit_history(created_at DESC);

DROP TRIGGER IF EXISTS credit_history_updated_at ON credit_history;
CREATE TRIGGER credit_history_updated_at
  BEFORE UPDATE ON credit_history
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Repayment history updates
ALTER TABLE repayment_history
  ADD COLUMN IF NOT EXISTS loan_id VARCHAR(50),
  ADD COLUMN IF NOT EXISTS loan_status VARCHAR(50) DEFAULT 'active',
  ADD COLUMN IF NOT EXISTS interest_rate DECIMAL(5, 2),
  ADD COLUMN IF NOT EXISTS maturity_date DATE,
  ADD COLUMN IF NOT EXISTS next_due_date DATE,
  ADD COLUMN IF NOT EXISTS on_time_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS late_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS missed_payments INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS total_payments_made INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS recent_payments JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS average_days_late DECIMAL(5, 2) DEFAULT 0,
  ADD COLUMN IF NOT EXISTS largest_late_days INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS on_time_payment_percentage DECIMAL(5, 2),
  ADD COLUMN IF NOT EXISTS lender_name VARCHAR(255),
  ADD COLUMN IF NOT EXISTS notes TEXT,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_repayment_history_loan_status ON repayment_history(loan_status);
CREATE INDEX IF NOT EXISTS idx_repayment_history_created_at ON repayment_history(created_at DESC);

DROP TRIGGER IF EXISTS repayment_history_updated_at ON repayment_history;
CREATE TRIGGER repayment_history_updated_at
  BEFORE UPDATE ON repayment_history
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
