-- Update Credit Score for Saman Perera
-- Replace '750' with the actual CIBIL score you want to assign
-- Replace 'saman.perera@example.com' with the specific applicant's email

UPDATE applicants
SET credit_score = 750,
    updated_at = NOW()
WHERE email = 'saman.perera@example.com';

-- Verify the update
SELECT name, email, credit_score 
FROM applicants 
WHERE email = 'saman.perera@example.com';
