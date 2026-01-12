-- Database Functions and Triggers
-- Reusable functions and triggers

-- Updated At Trigger Function
-- Automatically updates the updated_at column on row updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column() IS 'Automatically updates updated_at timestamp on row update';

-- Usage:
-- CREATE TRIGGER table_name_updated_at
--   BEFORE UPDATE ON table_name
--   FOR EACH ROW
--   EXECUTE FUNCTION update_updated_at_column();
