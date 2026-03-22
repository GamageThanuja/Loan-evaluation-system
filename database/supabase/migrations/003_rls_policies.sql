-- Row Level Security (RLS) Policies
-- Version: 002
-- Created: 2026-01-07

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE applicants ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_performance ENABLE ROW LEVEL SECURITY;

-- ============================================
-- USERS TABLE POLICIES
-- ============================================

-- Users can read their own profile
CREATE POLICY users_select_own
  ON users FOR SELECT
  USING (auth.uid() = id);

-- Admins can read all users
CREATE POLICY users_select_admin
  ON users FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Users can update their own profile (except role)
CREATE POLICY users_update_own
  ON users FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (
    auth.uid() = id AND
    role = (SELECT role FROM users WHERE id = auth.uid())
  );

-- Only admins can insert/delete users
CREATE POLICY users_insert_admin
  ON users FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY users_delete_admin
  ON users FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- ============================================
-- APPLICANTS TABLE POLICIES
-- ============================================

-- Loan officers can view their own applicants
CREATE POLICY applicants_select_own
  ON applicants FOR SELECT
  USING (
    created_by = auth.uid() OR
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
    )
  );

-- Loan officers and managers can create applicants
CREATE POLICY applicants_insert_authorized
  ON applicants FOR INSERT
  WITH CHECK (
    created_by = auth.uid() AND
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('loan_officer', 'bank_manager', 'admin')
    )
  );

-- Loan officers can update their own applicants (if pending)
CREATE POLICY applicants_update_own
  ON applicants FOR UPDATE
  USING (
    created_by = auth.uid() AND status = 'pending' OR
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
    )
  );

-- Only managers can approve/reject
CREATE POLICY applicants_approve_reject_manager
  ON applicants FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
    )
  );

-- Only admins can delete applicants
CREATE POLICY applicants_delete_admin
  ON applicants FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- ============================================
-- PREDICTIONS TABLE POLICIES
-- ============================================

-- Users can view predictions for applicants they have access to
CREATE POLICY predictions_select_authorized
  ON predictions FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM applicants a
      WHERE a.id = predictions.applicant_id
        AND (
          a.created_by = auth.uid() OR
          EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
          )
        )
    )
  );

-- Only system (service role) can insert predictions
-- This is handled at application level using service_role key
CREATE POLICY predictions_insert_system
  ON predictions FOR INSERT
  WITH CHECK (false); -- Disable direct inserts through RLS

-- Only admins can update predictions
CREATE POLICY predictions_update_admin
  ON predictions FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Only admins can delete predictions
CREATE POLICY predictions_delete_admin
  ON predictions FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- ============================================
-- AUDIT LOGS POLICIES
-- ============================================

-- Users can view their own audit logs
CREATE POLICY audit_logs_select_own
  ON audit_logs FOR SELECT
  USING (
    user_id = auth.uid() OR
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
    )
  );

-- System handles inserts (service role only)
CREATE POLICY audit_logs_insert_system
  ON audit_logs FOR INSERT
  WITH CHECK (false); -- Handled by service role

-- No updates or deletes allowed
CREATE POLICY audit_logs_no_update
  ON audit_logs FOR UPDATE
  USING (false);

CREATE POLICY audit_logs_no_delete
  ON audit_logs FOR DELETE
  USING (false);

-- ============================================
-- MODEL PERFORMANCE POLICIES
-- ============================================

-- Everyone can view model performance
CREATE POLICY model_performance_select_all
  ON model_performance FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid()
    )
  );

-- Only admins can insert/update/delete performance metrics
CREATE POLICY model_performance_admin_only
  ON model_performance FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to check if user is manager
CREATE OR REPLACE FUNCTION is_manager()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users
    WHERE id = auth.uid() AND role IN ('bank_manager', 'admin')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user owns applicant
CREATE OR REPLACE FUNCTION owns_applicant(applicant_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM applicants
    WHERE id = applicant_uuid AND created_by = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log actions (called from application)
CREATE OR REPLACE FUNCTION log_action(
  p_user_id UUID,
  p_action VARCHAR,
  p_resource_type VARCHAR,
  p_resource_id UUID DEFAULT NULL,
  p_details JSONB DEFAULT NULL,
  p_ip_address VARCHAR DEFAULT NULL,
  p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
  v_log_id UUID;
BEGIN
  INSERT INTO audit_logs (
    user_id, action, resource_type, resource_id,
    details, ip_address, user_agent
  )
  VALUES (
    p_user_id, p_action, p_resource_type, p_resource_id,
    p_details, p_ip_address, p_user_agent
  )
  RETURNING id INTO v_log_id;
  
  RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION is_manager() TO authenticated;
GRANT EXECUTE ON FUNCTION owns_applicant(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION log_action(UUID, VARCHAR, VARCHAR, UUID, JSONB, VARCHAR, TEXT) TO service_role;
