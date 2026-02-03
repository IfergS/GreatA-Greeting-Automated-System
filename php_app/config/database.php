<?php
/**
 * Database configuration - GreetA Faculty Attendance System
 * Uses MySQL (XAMPP default: root, no password)
 */

define('DB_HOST', getenv('GREETA_DB_HOST') ?: 'localhost');
define('DB_NAME', getenv('GREETA_DB_NAME') ?: 'greeta_attendance');
define('DB_USER', getenv('GREETA_DB_USER') ?: 'root');
define('DB_PASS', getenv('GREETA_DB_PASS') ?: '');
define('DB_CHARSET', 'utf8mb4');
