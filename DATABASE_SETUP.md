# 🗄️ Database Setup - Admin Login System

## Overview

A SQLite database has been implemented to manage admin credentials and login functionality for the GreetA Faculty Attendance System.

---

## 📁 Files Created

### 1. **`lib/models/admin.dart`**
- Admin model class with all necessary fields
- JSON serialization/deserialization
- CopyWith method for updates

### 2. **`lib/services/database_service.dart`**
- Complete database service using SQLite (sqflite)
- Admin management (CRUD operations)
- Authentication system
- Login logging
- Password change functionality

---

## 🗃️ Database Schema

### **admins Table**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| username | TEXT | Unique username (case-insensitive) |
| password | TEXT | Password (plain text - should be hashed in production) |
| email | TEXT | Admin email (optional) |
| fullName | TEXT | Full name (optional) |
| createdAt | TEXT | ISO8601 timestamp |
| lastLogin | TEXT | ISO8601 timestamp |
| isActive | INTEGER | 1 = active, 0 = inactive |

### **login_logs Table**
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| username | TEXT | Username that attempted login |
| loginTime | TEXT | ISO8601 timestamp |
| success | INTEGER | 1 = success, 0 = failed |
| ipAddress | TEXT | IP address (for future use) |
| deviceInfo | TEXT | Device information (for future use) |

---

## 🔐 Default Admin Credentials

**Username:** `admin`  
**Password:** `admin123`

The default admin user is automatically created when the database is first initialized.

---

## ✨ Features Implemented

### 1. **Database Initialization**
- ✅ Automatically creates database on first run
- ✅ Creates tables (admins, login_logs)
- ✅ Inserts default admin user
- ✅ Initialized in `main.dart` on app start

### 2. **Admin Authentication**
- ✅ Login with username and password
- ✅ Case-insensitive username matching
- ✅ Failed attempt tracking
- ✅ Login logging (success/failure)
- ✅ Last login timestamp update

### 3. **Admin Management**
- ✅ Create new admin users
- ✅ Get admin by username/ID
- ✅ Get all admins
- ✅ Update admin information
- ✅ Soft delete (deactivate) admins
- ✅ Change password

### 4. **Login Logging**
- ✅ Tracks all login attempts
- ✅ Records success/failure
- ✅ Stores timestamp
- ✅ Can retrieve login history

### 5. **Security Features**
- ✅ Failed attempt counter (5 max)
- ✅ Password validation (min 4 characters)
- ✅ Remember me functionality
- ✅ Secure password change

---

## 🔄 How It Works

### **On App Start:**
1. Database is initialized in `main.dart`
2. Tables are created if they don't exist
3. Default admin user is inserted if not present

### **On Admin Panel Access:**
1. User clicks "Admin Panel" from home screen
2. `AdminPanelScreen` initializes database
3. Shows `AdminLoginScreen`
4. User enters credentials
5. Database authenticates user
6. On success: Opens admin panel
7. On failure: Shows error with attempt count

### **Login Process:**
```dart
// 1. User enters credentials
final admin = await _databaseService.authenticate(username, password);

// 2. Database checks:
//    - Admin exists?
//    - Password matches?
//    - Admin is active?

// 3. If valid:
//    - Updates lastLogin timestamp
//    - Logs successful login
//    - Returns admin object

// 4. If invalid:
//    - Logs failed login
//    - Returns null
```

---

## 📝 Usage Examples

### **Authenticate Admin:**
```dart
final databaseService = DatabaseService();
final admin = await databaseService.authenticate('admin', 'admin123');

if (admin != null) {
  // Login successful
} else {
  // Login failed
}
```

### **Create New Admin:**
```dart
final newAdmin = Admin(
  username: 'newadmin',
  password: 'password123',
  email: 'admin@example.com',
  fullName: 'New Administrator',
  createdAt: DateTime.now(),
);

await databaseService.createAdmin(newAdmin);
```

### **Change Password:**
```dart
final success = await databaseService.changePassword(
  'admin',
  'oldpassword',
  'newpassword',
);
```

### **Get Login Logs:**
```dart
final logs = await databaseService.getLoginLogs(limit: 50);
```

---

## 🔒 Security Notes

### **Current Implementation:**
- Passwords stored in **plain text** (for development)
- Username is case-insensitive
- Failed attempt tracking (5 max)
- Login logging enabled

### **Production Recommendations:**
1. **Hash passwords** using bcrypt or similar
2. **Add password complexity** requirements
3. **Implement account lockout** after failed attempts
4. **Add session management** with tokens
5. **Encrypt sensitive data** in database
6. **Add rate limiting** for login attempts
7. **Implement 2FA** (two-factor authentication)

---

## 🛠️ Database Location

**Android:** `/data/data/com.greeta.attendance/databases/greeta_database.db`  
**iOS:** App Documents Directory `/greeta_database.db`

---

## 📊 Database Service Methods

### **Admin Management:**
- `createAdmin(Admin)` - Create new admin
- `getAdminByUsername(String)` - Get admin by username
- `getAdminById(int)` - Get admin by ID
- `getAllAdmins()` - Get all admins
- `updateAdmin(Admin)` - Update admin
- `deleteAdmin(int)` - Soft delete admin
- `adminExists(String)` - Check if admin exists

### **Authentication:**
- `authenticate(String username, String password)` - Authenticate user
- `changePassword(String username, String oldPassword, String newPassword)` - Change password

### **Logging:**
- `logLoginAttempt(String username, bool success)` - Log login attempt
- `getLoginLogs({int limit})` - Get login history

---

## ✅ Testing

### **Test Login:**
1. Run the app
2. Click "Admin Panel"
3. Enter: `admin` / `admin123`
4. Should successfully login

### **Test Failed Login:**
1. Enter wrong password
2. Should show error with attempt count
3. After 5 failed attempts, login is blocked

### **Test Password Change:**
1. Login to admin panel
2. Go to Settings tab
3. Click "Change Password"
4. Enter old and new password
5. Should update successfully

---

## 🎯 Next Steps

1. **Add password hashing** (bcrypt)
2. **Implement session tokens**
3. **Add admin user management UI**
4. **View login logs in admin panel**
5. **Add password reset functionality**
6. **Implement account lockout**

---

**Database is ready to use!** 🎉

The system will automatically create the database and default admin user on first run.

