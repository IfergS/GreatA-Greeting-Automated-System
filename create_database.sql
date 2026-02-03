-- ============================================
-- GreetA Attendance System - Database Creation
-- XAMPP MySQL Database Setup
-- ============================================
-- 
-- INSTRUCTIONS:
-- 1. Open phpMyAdmin: http://localhost/phpmyadmin
-- 2. Click on "SQL" tab at the top
-- 3. Copy and paste this entire script
-- 4. Click "Go" button
-- 5. ✅ Database and tables will be created automatically
-- ============================================

-- Create the database
CREATE DATABASE IF NOT EXISTS greeta_attendance 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use the database
USE greeta_attendance;

-- Create admins table
CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  fullName VARCHAR(100),
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  lastLogin DATETIME,
  isActive TINYINT(1) DEFAULT 1,
  INDEX idx_username (username),
  INDEX idx_isActive (isActive)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create login_logs table
CREATE TABLE IF NOT EXISTS login_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  loginTime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  success TINYINT(1) DEFAULT 0,
  ipAddress VARCHAR(45),
  deviceInfo TEXT,
  INDEX idx_username (username),
  INDEX idx_loginTime (loginTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default admin user
INSERT INTO admins (username, password, email, fullName, createdAt, isActive)
VALUES ('admin', 'admin123', 'admin@greeta.com', 'System Administrator', NOW(), 1)
ON DUPLICATE KEY UPDATE username=username;

-- Show confirmation
SELECT 'Database greeta_attendance created successfully!' AS Status;
SELECT 'Default admin user created: admin / admin123' AS LoginInfo;
SHOW TABLES;

