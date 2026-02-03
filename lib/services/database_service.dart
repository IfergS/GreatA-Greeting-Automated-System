import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/admin.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  static Database? _database;
  static const String _databaseName = 'greeta_attendance.db';
  static const int _databaseVersion = 1;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _databaseName);

    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Create admins table
    await db.execute('''
      CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        fullName TEXT,
        createdAt TEXT,
        lastLogin TEXT,
        isActive INTEGER DEFAULT 1
      )
    ''');

    // Create login_logs table
    await db.execute('''
      CREATE TABLE login_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        loginTime TEXT NOT NULL,
        success INTEGER DEFAULT 0,
        ipAddress TEXT,
        deviceInfo TEXT
      )
    ''');

    // Create indexes
    await db.execute('CREATE INDEX idx_username ON admins(username)');
    await db.execute('CREATE INDEX idx_isActive ON admins(isActive)');
    await db.execute('CREATE INDEX idx_loginTime ON login_logs(loginTime)');

    // Insert default admin user
    await db.insert('admins', {
      'username': 'admin',
      'password': 'admin123',
      'email': 'admin@greeta.com',
      'fullName': 'System Administrator',
      'createdAt': DateTime.now().toIso8601String(),
      'isActive': 1,
    });

    print('✅ SQLite database initialized');
    print('✅ Default admin user created: admin / admin123');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // Handle database migrations here if needed
  }

  // Admin Management
  Future<int> createAdmin(Admin admin) async {
    try {
      final db = await database;
      return await db.insert('admins', {
        'username': admin.username.toLowerCase(),
        'password': admin.password,
        'email': admin.email,
        'fullName': admin.fullName,
        'createdAt': (admin.createdAt ?? DateTime.now()).toIso8601String(),
        'isActive': admin.isActive ? 1 : 0,
      });
    } catch (e) {
      print('Error creating admin: $e');
      rethrow;
    }
  }

  Future<Admin?> getAdminByUsername(String username) async {
    try {
      final db = await database;
      final results = await db.query(
        'admins',
        where: 'username = ? AND isActive = ?',
        whereArgs: [username.toLowerCase(), 1],
        limit: 1,
      );

      if (results.isEmpty) return null;
      return _mapRowToAdmin(results.first);
    } catch (e) {
      print('Error getting admin by username: $e');
      return null;
    }
  }

  Future<Admin?> getAdminById(int id) async {
    try {
      final db = await database;
      final results = await db.query(
        'admins',
        where: 'id = ?',
        whereArgs: [id],
        limit: 1,
      );

      if (results.isEmpty) return null;
      return _mapRowToAdmin(results.first);
    } catch (e) {
      print('Error getting admin by ID: $e');
      return null;
    }
  }

  Future<List<Admin>> getAllAdmins() async {
    try {
      final db = await database;
      final results = await db.query(
        'admins',
        orderBy: 'createdAt DESC',
      );

      return results.map((row) => _mapRowToAdmin(row)).toList();
    } catch (e) {
      print('Error getting all admins: $e');
      return [];
    }
  }

  Future<bool> updateAdmin(Admin admin) async {
    try {
      final db = await database;
      final count = await db.update(
        'admins',
        {
          'username': admin.username.toLowerCase(),
          'password': admin.password,
          'email': admin.email,
          'fullName': admin.fullName,
          'createdAt': admin.createdAt?.toIso8601String(),
          'lastLogin': admin.lastLogin?.toIso8601String(),
          'isActive': admin.isActive ? 1 : 0,
        },
        where: 'id = ?',
        whereArgs: [admin.id],
      );
      return count > 0;
    } catch (e) {
      print('Error updating admin: $e');
      return false;
    }
  }

  Future<bool> deleteAdmin(int id) async {
    try {
      final db = await database;
      // Soft delete - set isActive to 0
      final count = await db.update(
        'admins',
        {'isActive': 0},
        where: 'id = ?',
        whereArgs: [id],
      );
      return count > 0;
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
      final db = await database;
      final count = await db.update(
        'admins',
        {'password': newPassword},
        where: 'username = ? AND password = ?',
        whereArgs: [username.toLowerCase(), oldPassword],
      );
      return count > 0;
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
      final db = await database;
      await db.update(
        'admins',
        {'lastLogin': DateTime.now().toIso8601String()},
        where: 'id = ?',
        whereArgs: [admin.id],
      );
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
      final db = await database;
      await db.insert('login_logs', {
        'username': username.toLowerCase(),
        'loginTime': DateTime.now().toIso8601String(),
        'success': success ? 1 : 0,
      });
    } catch (e) {
      print('Error logging login attempt: $e');
    }
  }

  Future<List<Map<String, dynamic>>> getLoginLogs({int limit = 50}) async {
    try {
      final db = await database;
      final results = await db.query(
        'login_logs',
        orderBy: 'loginTime DESC',
        limit: limit,
      );

      return results;
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

  // Helper method to map database row to Admin model
  Admin _mapRowToAdmin(Map<String, dynamic> row) {
    return Admin(
      id: row['id'] as int?,
      username: row['username'] as String,
      password: row['password'] as String,
      email: row['email'] as String?,
      fullName: row['fullName'] as String?,
      createdAt: row['createdAt'] != null
          ? DateTime.parse(row['createdAt'] as String)
          : null,
      lastLogin: row['lastLogin'] != null
          ? DateTime.parse(row['lastLogin'] as String)
          : null,
      isActive: (row['isActive'] as int? ?? 1) == 1,
    );
  }

  // Test database connection
  Future<bool> testConnection() async {
    try {
      final db = await database;
      await db.rawQuery('SELECT 1');
      return true;
    } catch (e) {
      print('Database connection test failed: $e');
      return false;
    }
  }

  // Close database connection
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
      print('✅ SQLite database closed');
    }
  }
}
