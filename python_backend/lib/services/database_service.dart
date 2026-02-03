import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:mysql1/mysql1.dart';
import '../models/admin.dart';
import 'mysql_service.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  final MySQLService _mysqlService = MySQLService();

  Future<MySqlConnection> get _connection async {
    return await _mysqlService.getConnection();
  }

  // Admin Management
  Future<int> createAdmin(Admin admin) async {
    try {
      final conn = await _connection;
      final result = await conn.query('''
        INSERT INTO admins (username, password, email, fullName, createdAt, isActive)
        VALUES (?, ?, ?, ?, ?, ?)
      ''', [
        admin.username.toLowerCase(),
        admin.password,
        admin.email,
        admin.fullName,
        admin.createdAt ?? DateTime.now(),
        admin.isActive ? 1 : 0,
      ]);
      
      return result.insertId?.toInt() ?? 0;
    } catch (e) {
      print('Error creating admin: $e');
      rethrow;
    }
  }

  Future<Admin?> getAdminByUsername(String username) async {
    try {
      final conn = await _connection;
      final results = await conn.query('''
        SELECT * FROM admins 
        WHERE username = ? AND isActive = 1
        LIMIT 1
      ''', [username.toLowerCase()]);

      if (results.isEmpty) return null;
      
      final row = results.first;
      return _mapRowToAdmin(row);
    } catch (e) {
      print('Error getting admin by username: $e');
      return null;
    }
  }

  Future<Admin?> getAdminById(int id) async {
    try {
      final conn = await _connection;
      final results = await conn.query('''
        SELECT * FROM admins 
        WHERE id = ?
        LIMIT 1
      ''', [id]);

      if (results.isEmpty) return null;
      
      final row = results.first;
      return _mapRowToAdmin(row);
    } catch (e) {
      print('Error getting admin by ID: $e');
      return null;
    }
  }

  Future<List<Admin>> getAllAdmins() async {
    try {
      final conn = await _connection;
      final results = await conn.query('''
        SELECT * FROM admins 
        ORDER BY createdAt DESC
      ''');

      return results.map((row) => _mapRowToAdmin(row)).toList();
    } catch (e) {
      print('Error getting all admins: $e');
      return [];
    }
  }

  Future<bool> updateAdmin(Admin admin) async {
    try {
      final conn = await _connection;
      final result = await conn.query('''
        UPDATE admins 
        SET username = ?, password = ?, email = ?, fullName = ?, 
            createdAt = ?, lastLogin = ?, isActive = ?
        WHERE id = ?
      ''', [
        admin.username.toLowerCase(),
        admin.password,
        admin.email,
        admin.fullName,
        admin.createdAt,
        admin.lastLogin,
        admin.isActive ? 1 : 0,
        admin.id,
      ]);
      
      return (result.affectedRows ?? 0) > 0;
    } catch (e) {
      print('Error updating admin: $e');
      return false;
    }
  }

  Future<bool> deleteAdmin(int id) async {
    try {
      final conn = await _connection;
      // Soft delete - set isActive to 0
      final result = await conn.query('''
        UPDATE admins 
        SET isActive = 0 
        WHERE id = ?
      ''', [id]);
      
      return (result.affectedRows ?? 0) > 0;
    } catch (e) {
      print('Error deleting admin: $e');
      return false;
    }
  }

  Future<bool> changePassword(String username, String oldPassword, String newPassword) async {
    final admin = await getAdminByUsername(username);
    if (admin == null || admin.password != oldPassword) {
      return false;
    }

    try {
      final conn = await _connection;
      final result = await conn.query('''
        UPDATE admins 
        SET password = ? 
        WHERE username = ? AND password = ?
      ''', [newPassword, username.toLowerCase(), oldPassword]);
      
      return (result.affectedRows ?? 0) > 0;
    } catch (e) {
      print('Error changing password: $e');
      return false;
    }
  }

  // Authentication
  Future<Admin?> authenticate(String username, String password) async {
    final admin = await getAdminByUsername(username);
    
    if (admin == null || admin.password != password) {
      // Log failed login attempt
      await logLoginAttempt(username, false);
      return null;
    }

    // Update last login time
    try {
      final conn = await _connection;
      await conn.query('''
        UPDATE admins 
        SET lastLogin = NOW() 
        WHERE id = ?
      ''', [admin.id]);
    } catch (e) {
      print('Error updating last login: $e');
    }
    
    // Log successful login
    await logLoginAttempt(username, true);
    
    // Get updated admin
    return await getAdminByUsername(username);
  }

  // Login Logging
  Future<void> logLoginAttempt(String username, bool success) async {
    try {
      final conn = await _connection;
      await conn.query('''
        INSERT INTO login_logs (username, loginTime, success)
        VALUES (?, NOW(), ?)
      ''', [username.toLowerCase(), success ? 1 : 0]);
    } catch (e) {
      print('Error logging login attempt: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getLoginLogs({int limit = 50}) async {
    try {
      final conn = await _connection;
      final results = await conn.query('''
        SELECT * FROM login_logs 
        ORDER BY loginTime DESC 
        LIMIT ?
      ''', [limit]);

      return results.map((row) => {
        'id': row['id'],
        'username': row['username'],
        'loginTime': row['loginTime']?.toString(),
        'success': row['success'],
        'ipAddress': row['ipAddress'],
        'deviceInfo': row['deviceInfo'],
      }).toList();
    } catch (e) {
      print('Error getting login logs: $e');
      return [];
    }
  }

  // Check if admin exists
  Future<bool> adminExists(String username) async {
    final admin = await getAdminByUsername(username);
    return admin != null;
  }

  // Helper method to map MySQL row to Admin model
  Admin _mapRowToAdmin(ResultRow row) {
    return Admin(
      id: row['id'] as int?,
      username: row['username'] as String,
      password: row['password'] as String,
      email: row['email'] as String?,
      fullName: row['fullName'] as String?,
      createdAt: row['createdAt'] as DateTime?,
      lastLogin: row['lastLogin'] as DateTime?,
      isActive: (row['isActive'] as int? ?? 1) == 1,
    );
  }

  // Test database connection
  Future<bool> testConnection() async {
    if (kIsWeb) {
      print('ℹ️ Database connection test skipped on web platform');
      return false;
    }
    return await _mysqlService.testConnection();
  }

  // Close database connection
  Future<void> close() async {
    await _mysqlService.close();
  }

  // Get database instance (for compatibility)
  Future<MySqlConnection> get database async {
    return await _connection;
  }
}
