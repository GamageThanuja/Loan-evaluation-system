-- Applicants Table Schema
-- Loan applicant information with auto-incrementing integer IDs

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

-- Indexes
CREATE INDEX idx_applicants_email ON applicants(email);
CREATE INDEX idx_applicants_status ON applicants(status);
CREATE INDEX idx_applicants_created_by ON applicants(created_by);
CREATE INDEX idx_applicants_created_at ON applicants(created_at DESC);

-- Enums
CREATE TYPE applicant_status AS ENUM ('pending', 'approved', 'rejected', 'under_review');
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

-- Trigger
CREATE TRIGGER applicants_updated_at
  BEFORE UPDATE ON applicants
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE applicants IS 'Loan applicant information with auto-incrementing integer IDs';
COMMENT ON COLUMN applicants.id IS 'Auto-incrementing integer ID (changed from UUID in migration 005)';
COMMENT ON COLUMN applicants.status IS 'Application status: pending, approved, rejected, under_review';
COMMENT ON COLUMN applicants.eligibility_status IS 'ML model eligibility determination';
