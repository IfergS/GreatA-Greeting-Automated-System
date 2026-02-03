import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:mysql1/mysql1.dart';
import '../config/database_config.dart';
import '../models/admin.dart';

class MySQLService {
  static final MySQLService _instance = MySQLService._internal();
  factory MySQLService() => _instance;
  MySQLService._internal();

  MySqlConnection? _connection;
  bool _isConnected = false;

  Future<MySqlConnection> getConnection() async {
    if (_connection != null && _isConnected) {
      return _connection!;
    }

    return await connect();
  }

  Future<MySqlConnection> connect() async {
    // Check if running on web platform
    if (kIsWeb) {
      throw UnsupportedError(
        'Direct MySQL connections are not supported on web platforms.\n'
        'MySQL requires native socket support which browsers do not provide.\n'
        'Please run the app on Android, iOS, Windows, macOS, or Linux for MySQL support.\n'
        'For web, you would need a REST API backend (PHP/Node.js) to connect to MySQL.'
      );
    }

    try {
      // Note: XAMPP MySQL default password is empty (blank), which is fine for local development
      if (!DatabaseConfig.isPasswordSet()) {
        print('ℹ️ Using XAMPP MySQL default (empty password) - OK for local development');
      }

      // First, try to connect to the database
      final settings = ConnectionSettings(
        host: DatabaseConfig.host,
        port: DatabaseConfig.port,
        user: DatabaseConfig.username,
        password: DatabaseConfig.password,
        db: DatabaseConfig.database,
        timeout: Duration(seconds: DatabaseConfig.connectionTimeout),
      );

      try {
        _connection = await MySqlConnection.connect(settings);
        _isConnected = true;
        
        print('✅ Connected to MySQL database: ${DatabaseConfig.getConnectionInfo()}');
        
        // Initialize database schema
        await _initializeDatabase();
        
        return _connection!;
      } on MySqlException catch (e) {
        // If database doesn't exist (error 1049), create it
        if (e.errorNumber == 1049) {
          print('⚠️ Database "${DatabaseConfig.database}" does not exist');
          print('🔄 Attempting to create database automatically...');
          
          // Connect without specifying database
          final tempSettings = ConnectionSettings(
            host: DatabaseConfig.host,
            port: DatabaseConfig.port,
            user: DatabaseConfig.username,
            password: DatabaseConfig.password,
            timeout: Duration(seconds: DatabaseConfig.connectionTimeout),
          );
          
          final tempConn = await MySqlConnection.connect(tempSettings);
          
          // Create database
          await tempConn.query(
            'CREATE DATABASE IF NOT EXISTS `${DatabaseConfig.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'
          );
          
          print('✅ Database "${DatabaseConfig.database}" created successfully');
          
          // Close temporary connection
          await tempConn.close();
          
          // Now connect to the newly created database
          _connection = await MySqlConnection.connect(settings);
          _isConnected = true;
          
          print('✅ Connected to MySQL database: ${DatabaseConfig.getConnectionInfo()}');
          
          // Initialize database schema
          await _initializeDatabase();
          
          return _connection!;
        } else {
          rethrow;
        }
      }
    } on MySqlException catch (e) {
      _isConnected = false;
      print('❌ MySQL connection error: ${e.message}');
      print('❌ Error code: ${e.errorNumber}');
      if (e.errorNumber == 1045) {
        print('⚠️ Access denied - Check username and password in database_config.dart');
        print('⚠️ XAMPP default: username=root, password=(empty)');
      } else if (e.errorNumber == 1049) {
        print('⚠️ Could not create database automatically');
        print('⚠️ Please create database manually:');
        print('   1. Open phpMyAdmin: http://localhost/phpmyadmin');
        print('   2. Click "New" → Database name: ${DatabaseConfig.database} → "Create"');
        print('   3. Or run: CREATE DATABASE ${DatabaseConfig.database};');
      } else if (e.errorNumber == 2003) {
        print('⚠️ Cannot connect to MySQL server');
        print('⚠️ Make sure XAMPP MySQL is running (green in XAMPP Control Panel)');
        print('⚠️ Start MySQL in XAMPP Control Panel');
      }
      rethrow;
    } catch (e) {
      _isConnected = false;
      print('❌ MySQL connection error: $e');
      rethrow;
    }
  }

  Future<void> _initializeDatabase() async {
    try {
      final conn = await getConnection();
      
      // Create admins table
      await conn.query('''
        CREATE TABLE IF NOT EXISTS admins (
          id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(50) UNIQUE NOT NULL,
          password VARCHAR(255) NOT NULL,
          email VARCHAR(100),
          fullName VARCHAR(100),
          createdAt DATETIME,
          lastLogin DATETIME,
          isActive TINYINT(1) DEFAULT 1,
          INDEX idx_username (username),
          INDEX idx_isActive (isActive)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
      ''');

      // Create login_logs table
      await conn.query('''
        CREATE TABLE IF NOT EXISTS login_logs (
          id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(50) NOT NULL,
          loginTime DATETIME NOT NULL,
          success TINYINT(1) DEFAULT 0,
          ipAddress VARCHAR(45),
          deviceInfo TEXT,
          INDEX idx_username (username),
          INDEX idx_loginTime (loginTime)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
      ''');

      // Check if default admin exists
      final adminCheck = await conn.query(
        'SELECT COUNT(*) as count FROM admins WHERE username = ?',
        ['admin'],
      );
      
      final count = adminCheck.first.fields['count'] as int;
      if (count == 0) {
        // Insert default admin
        await conn.query('''
          INSERT INTO admins (username, password, email, fullName, createdAt, isActive)
          VALUES (?, ?, ?, ?, NOW(), 1)
        ''', ['admin', 'admin123', 'admin@greeta.com', 'System Administrator']);
        
        print('✅ Default admin user created');
      }

      print('✅ Database tables initialized');
    } catch (e) {
      print('❌ Database initialization error: $e');
      rethrow;
    }
  }

  Future<void> close() async {
    if (_connection != null) {
      await _connection!.close();
      _isConnected = false;
      _connection = null;
      print('✅ MySQL connection closed');
    }
  }

  // Test connection
  Future<bool> testConnection() async {
    // Check if running on web platform
    if (kIsWeb) {
      print('⚠️ MySQL connection test skipped on web platform');
      print('ℹ️ Direct MySQL connections are not supported in browsers');
      print('ℹ️ Run the app on Android, iOS, Windows, macOS, or Linux for MySQL support');
      return false;
    }

    try {
      final conn = await getConnection();
      await conn.query('SELECT 1');
      return true;
    } catch (e) {
      print('Connection test failed: $e');
      return false;
    }
  }
}

