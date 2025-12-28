-- ============================================
-- Hospital Booking System - Supabase Tables
-- Copy and paste this entire script into Supabase SQL Editor
-- ============================================

-- Create hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  mobile TEXT NOT NULL,
  address_line1 TEXT,
  address_line2 TEXT,
  address_line3 TEXT,
  city TEXT,
  state TEXT,
  pincode TEXT,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  approved_date TIMESTAMP,
  plan TEXT,
  expiry_date DATE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  hospital_id INTEGER REFERENCES hospitals(id),
  name TEXT NOT NULL,
  mobile TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('patient', 'pharma', 'doctor')),
  password_hash TEXT NOT NULL,
  address_line1 TEXT,
  address_line2 TEXT,
  address_line3 TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Pharma Professional fields
  company_name TEXT,
  product1 TEXT,
  product2 TEXT,
  product3 TEXT,
  product4 TEXT,
  
  -- Doctor fields
  degree TEXT,
  institute_name TEXT,
  experience1 TEXT,
  experience2 TEXT,
  experience3 TEXT,
  experience4 TEXT
);

-- Create appointment table
CREATE TABLE IF NOT EXISTS appointment (
  id SERIAL PRIMARY KEY,
  hospital_id INTEGER REFERENCES hospitals(id),
  user_id INTEGER REFERENCES users(id),
  doctor_id INTEGER REFERENCES users(id),
  date DATE NOT NULL,
  time_slot TEXT NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create operation table
CREATE TABLE IF NOT EXISTS operation (
  id SERIAL PRIMARY KEY,
  hospital_id INTEGER REFERENCES hospitals(id),
  patient_id INTEGER REFERENCES users(id),
  doctor_id INTEGER REFERENCES users(id),
  specialty TEXT NOT NULL CHECK (specialty IN ('ortho', 'gyn', 'surgery')),
  date DATE NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_hospital_id ON users(hospital_id);
CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_appointment_hospital_id ON appointment(hospital_id);
CREATE INDEX IF NOT EXISTS idx_appointment_user_id ON appointment(user_id);
CREATE INDEX IF NOT EXISTS idx_appointment_doctor_id ON appointment(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointment_date ON appointment(date);
CREATE INDEX IF NOT EXISTS idx_operation_hospital_id ON operation(hospital_id);
CREATE INDEX IF NOT EXISTS idx_operation_patient_id ON operation(patient_id);
CREATE INDEX IF NOT EXISTS idx_operation_doctor_id ON operation(doctor_id);
CREATE INDEX IF NOT EXISTS idx_operation_date ON operation(date);
CREATE INDEX IF NOT EXISTS idx_hospitals_status ON hospitals(status);
CREATE INDEX IF NOT EXISTS idx_hospitals_email ON hospitals(email);

-- ============================================
-- Tables created successfully!
-- ============================================

