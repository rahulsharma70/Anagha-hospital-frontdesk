-- ============================================
-- Payment Tables for Hospital Booking System
-- Add these to your Supabase database
-- ============================================

-- Add UPI ID column to hospitals table (if not exists)
ALTER TABLE hospital ADD COLUMN IF NOT EXISTS upi_id text;

-- Add payment-related columns to appointment table
ALTER TABLE appointment ADD COLUMN IF NOT EXISTS amount text;
ALTER TABLE appointment ADD COLUMN IF NOT EXISTS payment_required text DEFAULT 'false';

-- Add payment-related columns to operation table
ALTER TABLE operation ADD COLUMN IF NOT EXISTS amount text;
ALTER TABLE operation ADD COLUMN IF NOT EXISTS payment_required text DEFAULT 'false';

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
  id serial primary key,
  appointment_id int references appointment(id),
  operation_id int references operation(id),
  user_id int references users(id) NOT NULL,
  hospital_id int references hospital(id) NOT NULL,
  amount text NOT NULL,
  payment_method text,
  status text DEFAULT 'pending',
  transaction_id text,
  upi_transaction_id text,
  payment_date timestamp,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_appointment_id ON payments(appointment_id);
CREATE INDEX IF NOT EXISTS idx_payments_operation_id ON payments(operation_id);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);



