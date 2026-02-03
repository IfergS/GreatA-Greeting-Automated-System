-- ============================================
-- GreetA Attendance System - Full PHP Schema
-- MySQL (XAMPP / MariaDB)
-- ============================================

CREATE DATABASE IF NOT EXISTS greeta_attendance
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE greeta_attendance;

-- Admins
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

-- Login logs
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

-- Faculty
CREATE TABLE IF NOT EXISTS faculty (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100),
  phone VARCHAR(30),
  registrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Attendance (one record per faculty per day)
CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  facultyId VARCHAR(50) NOT NULL,
  facultyName VARCHAR(100) NOT NULL,
  date DATE NOT NULL,
  time TIME NOT NULL,
  status VARCHAR(20) DEFAULT 'present',
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_faculty_date (facultyId, date),
  INDEX idx_date (date),
  INDEX idx_facultyId (facultyId),
  FOREIGN KEY (facultyId) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Default admin: run install.php once to create admin (username: admin, password: admin123)

SELECT 'Database greeta_attendance ready for PHP app.' AS Status;
