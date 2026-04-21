-- ============================================
-- Authentication System Migration
-- SAFE: No data deletion, no table drops
-- ============================================

USE personal_expense_tracker;

-- Add OTP columns to users table
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS otp_code VARCHAR(255) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS otp_expires_at DATETIME DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS otp_attempts INT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS otp_last_sent_at DATETIME DEFAULT NULL;

-- Add remember-me token columns
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS remember_token VARCHAR(255) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS remember_expires_at DATETIME DEFAULT NULL;

-- Add login attempt tracking columns
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS login_attempts INT DEFAULT 0,
    ADD COLUMN IF NOT EXISTS login_locked_until DATETIME DEFAULT NULL;

-- ============================================
-- ACCOUNT MIGRATION
-- Migrate dishita@exp.com → dishitabachudasama@gmail.com
-- Password: Dishitaba0!555# (bcrypt hashed)
-- ALL EXPENSE DATA REMAINS INTACT
-- ============================================

-- The bcrypt hash below is for: Dishitaba0!555#
-- Generated with PHP: password_hash('Dishitaba0!555#', PASSWORD_DEFAULT)
-- We'll use a PHP script to generate the correct hash - see migrate_account.php

-- For now, update email only (password will be updated via PHP for proper bcrypt):
UPDATE users 
SET email = 'dishitabachudasama@gmail.com',
    updated_at = NOW()
WHERE email = 'dishita@exp.com';

-- Verify migration (run this SELECT after to confirm):
-- SELECT id, username, email, created_at FROM users WHERE email = 'dishitabachudasama@gmail.com';
