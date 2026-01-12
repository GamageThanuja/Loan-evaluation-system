-- Predictions Table Schema
-- ML model predictions with explainability (SHAP, Bayesian networks)

CREATE TABLE predictions (
  id SERIAL PRIMARY KEY,
  applicant_id INTEGER NOT NULL REFERENCES applicants(id) ON DELETE CASCADE,
  
  -- Model Outputs
  risk_score DECIMAL(5, 4) NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
  confidence DECIMAL(5, 4) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  decision prediction_decision NOT NULL,
  
  -- Explainability Data (JSON)
  shap_explanation JSONB,
  bayesian_network JSONB,
  business_rules JSONB,
  
  -- Feature Values Used (for audit)
  input_features JSONB NOT NULL,
  
  -- Model Metadata
  model_version VARCHAR(50) NOT NULL,
  model_type VARCHAR(50) DEFAULT 'hybrid_tabnet_bayesian',
  processing_time_ms INTEGER,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_predictions_applicant_id ON predictions(applicant_id);
CREATE INDEX idx_predictions_decision ON predictions(decision);
CREATE INDEX idx_predictions_risk_score ON predictions(risk_score);
CREATE INDEX idx_predictions_created_at ON predictions(created_at DESC);

-- Enum
CREATE TYPE prediction_decision AS ENUM ('APPROVE', 'REJECT', 'MANUAL_REVIEW');

-- Comments
COMMENT ON TABLE predictions IS 'ML model predictions with explainability';
COMMENT ON COLUMN predictions.risk_score IS 'Risk score between 0 and 1 (0 = low risk, 1 = high risk)';
COMMENT ON COLUMN predictions.confidence IS 'Model confidence in the prediction (0-1)';
COMMENT ON COLUMN predictions.shap_explanation IS 'SHAP values for feature importance';
COMMENT ON COLUMN predictions.bayesian_network IS 'Bayesian network causal relationships';
COMMENT ON COLUMN predictions.business_rules IS 'Business rules evaluation results';
COMMENT ON COLUMN predictions.input_features IS 'Feature values used for prediction (audit trail)';
