-- PostgreSQL Schema for OTP System
-- Database: otp_system

-- Create database (run separately)
-- CREATE DATABASE otp_system;

-- Connect to database
-- \c otp_system;

-- Drop tables if they exist (for testing)
DROP TABLE IF EXISTS sms_delivery_statuses CASCADE;
DROP TABLE IF EXISTS otps CASCADE;
DROP TABLE IF EXISTS sms_templates CASCADE;

-- OTPs Table
CREATE TABLE otps (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    is_expired BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP,
    attempts_remaining INTEGER NOT NULL DEFAULT 3
);

-- Indexes for OTPs
CREATE INDEX idx_otps_phone_number ON otps(phone_number);
CREATE INDEX idx_otps_expires_at ON otps(expires_at);
CREATE INDEX idx_otps_created_at ON otps(created_at DESC);

-- SMS Delivery Statuses Table
CREATE TABLE sms_delivery_statuses (
    id SERIAL PRIMARY KEY,
    otp_id INTEGER NOT NULL REFERENCES otps(id) ON DELETE CASCADE,
    message_id VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_at TIMESTAMP,
    error_message TEXT
);

-- Indexes for SMS Delivery Statuses
CREATE INDEX idx_sms_message_id ON sms_delivery_statuses(message_id);
CREATE INDEX idx_sms_otp_id ON sms_delivery_statuses(otp_id);
CREATE INDEX idx_sms_status ON sms_delivery_statuses(status);
CREATE INDEX idx_sms_created_at ON sms_delivery_statuses(created_at DESC);

-- SMS Templates Table
CREATE TABLE sms_templates (
    id SERIAL PRIMARY KEY,
    template_type VARCHAR(50) NOT NULL,
    template_content TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for SMS Templates
CREATE INDEX idx_template_type ON sms_templates(template_type);
CREATE INDEX idx_template_active ON sms_templates(is_active);

-- Insert seed data for SMS templates
INSERT INTO sms_templates (template_type, template_content, is_active) VALUES
('login', 'Your login OTP is {otp}. Valid for 5 minutes. Do not share this code.', TRUE),
('registration', 'Welcome! Your registration OTP is {otp}. This code expires in 5 minutes.', TRUE),
('password_reset', 'Password reset OTP: {otp}. Valid for 5 minutes. If you didn''t request this, ignore this message.', TRUE),
('transaction', 'Transaction verification code: {otp}. Valid for 5 minutes. Do not share with anyone.', TRUE);

-- Create a function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_sms_delivery_statuses_updated_at
    BEFORE UPDATE ON sms_delivery_statuses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sms_templates_updated_at
    BEFORE UPDATE ON sms_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Useful queries for testing

-- Check all OTPs for a phone number
-- SELECT * FROM otps WHERE phone_number = '+1234567890' ORDER BY created_at DESC;

-- Check SMS delivery status
-- SELECT s.*, o.phone_number, o.otp_code 
-- FROM sms_delivery_statuses s 
-- JOIN otps o ON s.otp_id = o.id 
-- ORDER BY s.created_at DESC;

-- Get active templates
-- SELECT * FROM sms_templates WHERE is_active = TRUE;

-- Check expired OTPs
-- SELECT * FROM otps WHERE expires_at < CURRENT_TIMESTAMP AND is_expired = FALSE;

-- SMS delivery statistics
-- SELECT status, COUNT(*) as count 
-- FROM sms_delivery_statuses 
-- GROUP BY status;