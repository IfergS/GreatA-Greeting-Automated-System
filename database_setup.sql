-- GreetA Faculty Attendance System - XAMPP MySQL Database Setup Script
-- Run this script in phpMyAdmin or MySQL command line to create the database and tables
-- 
-- For XAMPP:
-- 1. Open phpMyAdmin: http://localhost/phpmyadmin
-- 2. Select SQL tab
-- 3. Paste and run this script
-- OR use MySQL command line from XAMPP

-- Create database
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

-- Create dedicated user (optional but recommended)
-- Uncomment and modify as needed:
-- CREATE USER IF NOT EXISTS 'greeta_user'@'localhost' IDENTIFIED BY 'your_secure_password';
-- GRANT ALL PRIVILEGES ON greeta_attendance.* TO 'greeta_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Show tables
SHOW TABLES;

-- Verify admin user
SELECT * FROM admins;

