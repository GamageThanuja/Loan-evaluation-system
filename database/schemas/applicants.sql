-- Migration to add missing columns to applicants table for v4.0 model

-- 1. Add address_line1 if it doesn't exist (or rename address if it exists)
DO $$
BEGIN
    -- Check if 'address' column exists
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'address') THEN
        ALTER TABLE applicants RENAME COLUMN address TO address_line1;
    -- Check if 'address_line1' does NOT exist
    ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'address_line1') THEN
        ALTER TABLE applicants ADD COLUMN address_line1 VARCHAR(255);
    END IF;
END $$;

-- 2. Add education_level column
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'education_level') THEN
        ALTER TABLE applicants ADD COLUMN education_level VARCHAR(100);
    END IF;
END $$;

-- 3. Add assets_value column
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'assets_value') THEN
        ALTER TABLE applicants ADD COLUMN assets_value DECIMAL(15, 2) DEFAULT 0;
    END IF;
END $$;

-- 4. Ensure other potentially missing columns from recent updates exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'address_line2') THEN
        ALTER TABLE applicants ADD COLUMN address_line2 VARCHAR(255);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'state') THEN
        ALTER TABLE applicants ADD COLUMN state VARCHAR(100);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'city') THEN
        ALTER TABLE applicants ADD COLUMN city VARCHAR(100);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'postal_code') THEN
        ALTER TABLE applicants ADD COLUMN postal_code VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'applicants' AND column_name = 'country') THEN
        ALTER TABLE applicants ADD COLUMN country VARCHAR(100) DEFAULT 'Sri Lanka';
    END IF;
END $$;
