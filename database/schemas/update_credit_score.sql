-- Update Credit Score for an Existing Applicant
-- Usage: Replace the email and score as needed.

-- Example 1: Set a good credit score (750)
UPDATE applicants
SET credit_score = 750,
    updated_at = NOW()
WHERE email = 'applicant@example.com';  -- Replace with actual email

-- Example 2: Set a poor credit score (500)
-- UPDATE applicants
-- SET credit_score = 500,
--     updated_at = NOW()
-- WHERE email = 'another.applicant@example.com';

-- Verify the update
SELECT name, email, credit_score 
FROM applicants 
WHERE email = 'applicant@example.com';
