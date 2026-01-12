-- Database Views
-- Materialized and regular views for common queries

-- Recent Predictions View
-- Shows latest predictions with applicant details
CREATE VIEW recent_predictions AS
SELECT 
  p.id,
  p.applicant_id,
  a.name AS applicant_name,
  p.risk_score,
  p.confidence,
  p.decision,
  p.model_version,
  p.created_at
FROM predictions p
JOIN applicants a ON p.applicant_id = a.id
ORDER BY p.created_at DESC
LIMIT 100;

COMMENT ON VIEW recent_predictions IS 'Latest 100 predictions with applicant details';

-- Dashboard Stats View
-- Aggregated statistics for dashboard
CREATE VIEW dashboard_stats AS
SELECT
  COUNT(DISTINCT a.id) AS total_applicants,
  COUNT(DISTINCT CASE WHEN a.status = 'approved' THEN a.id END) AS approved_count,
  COUNT(DISTINCT CASE WHEN a.status = 'rejected' THEN a.id END) AS rejected_count,
  COUNT(DISTINCT CASE WHEN a.status = 'pending' THEN a.id END) AS pending_count,
  AVG(CASE WHEN p.decision = 'APPROVE' THEN 1 ELSE 0 END) AS approval_rate,
  AVG(p.risk_score) AS avg_risk_score,
  AVG(p.confidence) AS avg_confidence
FROM applicants a
LEFT JOIN predictions p ON a.id = p.applicant_id
WHERE a.created_at >= NOW() - INTERVAL '30 days';

COMMENT ON VIEW dashboard_stats IS 'Aggregated statistics for the last 30 days';
