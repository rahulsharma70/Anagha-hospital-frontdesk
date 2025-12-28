-- WhatsApp Integration Schema Updates
-- Run this in your Supabase SQL Editor or database

-- Add new appointment status (VISITED)
-- Note: If using enum, you may need to alter the enum type
-- For PostgreSQL:
-- ALTER TYPE appointmentstatus ADD VALUE 'visited';

-- Add visit_date and followup_date to appointments table
ALTER TABLE appointments
ADD COLUMN IF NOT EXISTS visit_date DATE,
ADD COLUMN IF NOT EXISTS followup_date DATE;

-- Add WhatsApp settings to hospitals table
ALTER TABLE hospitals
ADD COLUMN IF NOT EXISTS whatsapp_enabled VARCHAR(10) DEFAULT 'false',
ADD COLUMN IF NOT EXISTS whatsapp_confirmation_template VARCHAR(500),
ADD COLUMN IF NOT EXISTS whatsapp_followup_template VARCHAR(500),
ADD COLUMN IF NOT EXISTS whatsapp_reminder_template VARCHAR(500);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointments_followup_date ON appointments(followup_date);
CREATE INDEX IF NOT EXISTS idx_appointments_visit_date ON appointments(visit_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status_date ON appointments(status, date);

-- Update existing appointments to have default values
UPDATE appointments SET visit_date = NULL WHERE visit_date IS NULL;
UPDATE appointments SET followup_date = NULL WHERE followup_date IS NULL;
UPDATE hospitals SET whatsapp_enabled = 'false' WHERE whatsapp_enabled IS NULL;



