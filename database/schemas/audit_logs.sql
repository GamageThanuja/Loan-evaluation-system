-- Audit Logs Table Schema
-- System audit trail for all actions

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id VARCHAR(100),  -- VARCHAR to support both UUID and integer IDs
  details JSONB,
  ip_address VARCHAR(50),
  user_agent TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Comments
COMMENT ON TABLE audit_logs IS 'Audit trail for all system actions';
COMMENT ON COLUMN audit_logs.action IS 'Action performed (e.g., CREATE_APPLICANT, APPROVE_APPLICATION)';
COMMENT ON COLUMN audit_logs.resource_type IS 'Type of resource affected (e.g., applicant, prediction)';
COMMENT ON COLUMN audit_logs.resource_id IS 'ID of affected resource (supports both UUID and integer)';
COMMENT ON COLUMN audit_logs.details IS 'Additional details about the action (JSON)';
