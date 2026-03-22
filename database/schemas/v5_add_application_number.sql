-- Run this script in the Supabase SQL editor to add an auto-incrementing application number
ALTER TABLE applicants ADD COLUMN IF NOT EXISTS application_number SERIAL;
