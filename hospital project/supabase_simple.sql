-- ============================================
-- Simple Hospital Booking System - Supabase Tables
-- Copy and paste this into Supabase SQL Editor
-- ============================================

create table hospital (
  id serial primary key,
  name text,
  plan text,
  expiry_date date,
  is_active boolean default true
);

create table users (
  id serial primary key,
  hospital_id int references hospital(id),
  name text,
  mobile text unique,
  role text,
  password_hash text,
  is_active boolean default true
);

create table appointment (
  id serial primary key,
  hospital_id int,
  patient_id int,
  doctor_id int,
  date date,
  time_slot text,
  status text
);

create table operation (
  id serial primary key,
  hospital_id int,
  patient_id int,
  doctor_id int,
  specialty text,
  date date,
  status text
);

