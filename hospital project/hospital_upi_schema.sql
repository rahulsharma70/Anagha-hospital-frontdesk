-- ============================================
-- Add UPI ID Columns to Hospital Table
-- Run this in your Supabase SQL Editor
-- ============================================

-- Add UPI ID columns to hospital table
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS upi_id text;
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS gpay_upi_id text;
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS phonepay_upi_id text;
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS paytm_upi_id text;
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS bhim_upi_id text;

-- Add comments for documentation
COMMENT ON COLUMN hospital.upi_id IS 'Default/Universal UPI ID for payments';
COMMENT ON COLUMN hospital.gpay_upi_id IS 'Google Pay specific UPI ID';
COMMENT ON COLUMN hospital.phonepay_upi_id IS 'PhonePe specific UPI ID';
COMMENT ON COLUMN hospital.paytm_upi_id IS 'Paytm specific UPI ID';
COMMENT ON COLUMN hospital.bhim_upi_id IS 'BHIM UPI specific UPI ID';



