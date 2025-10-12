#!/usr/bin/env python3
"""
Database Setup Script for Attendance System
This script will create the database and tables for the attendance system.
Make sure XAMPP MySQL is running before executing this script.
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the attendance_system database and tables"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            print("Creating database 'attendance_system'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system")
            print("✓ Database 'attendance_system' created successfully")
            
            # Use the database
            cursor.execute("USE attendance_system")
            
            # Create tables
            tables = {
                'admins': """
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                
                'users': """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    department VARCHAR(50),
                    position VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                
                'tasks': """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    assigned_to VARCHAR(20),
                    assigned_by VARCHAR(50),
                    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE CASCADE
                )
                """,
                
                'attendance_records': """
                CREATE TABLE IF NOT EXISTS attendance_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(20),
                    date DATE NOT NULL,
                    time_in TIME,
                    time_out TIME,
                    status ENUM('present', 'absent', 'late', 'half_day') DEFAULT 'present',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
                """
            }
            
            # Create each table
            for table_name, table_sql in tables.items():
                print(f"Creating table '{table_name}'...")
                cursor.execute(table_sql)
                print(f"✓ Table '{table_name}' created successfully")
            
            # Insert default admin
            print("Creating default admin account...")
            cursor.execute("SELECT COUNT(*) FROM admins")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO admins (username, password, email) 
                    VALUES ('admin', 'admin123', 'admin@attendance.com')
                """)
                print("✓ Default admin created: username='admin', password='admin123'")
            else:
                print("✓ Admin account already exists")
            
            connection.commit()
            print("\n" + "="*50)
            print("DATABASE SETUP COMPLETED SUCCESSFULLY!")
            print("="*50)
            print("Database: attendance_system")
            print("Tables: admins, users, tasks, attendance_records")
            print("Default Admin: admin / admin123")
            print("="*50)
            
    except Error as e:
        print(f"Error: {e}")
        print("\n" + "="*60)
        print("SETUP FAILED - PLEASE CHECK:")
        print("="*60)
        print("1. XAMPP is installed and running")
        print("2. MySQL service is started in XAMPP Control Panel")
        print("3. MySQL is running on localhost:3306")
        print("4. Root user has no password (default XAMPP setup)")
        print("="*60)
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    print("Attendance System Database Setup")
    print("="*40)
    create_database()
    input("\nPress Enter to exit...")
