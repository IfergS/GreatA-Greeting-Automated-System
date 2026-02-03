# 🗄️ MySQL Database Setup Guide - GreetA System

## Overview

The GreetA Faculty Attendance System now uses **MySQL** instead of SQLite for better scalability, performance, and multi-user support.

---

## 📋 Prerequisites

1. **MySQL Server** installed and running
2. **MySQL Client** (optional, for management)
3. **Network access** to MySQL server (if remote)

---

## 🚀 Setup Instructions

### **Step 1: Install MySQL Server**

#### **Windows:**
1. Download MySQL from: https://dev.mysql.com/downloads/installer/
2. Run the installer
3. Choose "Developer Default" or "Server only"
4. Set root password during installation
5. Start MySQL service

#### **Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo mysql_secure_installation
```

#### **macOS:**
```bash
brew install mysql
brew services start mysql
```

---

### **Step 2: Create Database**

1. **Open MySQL Command Line** or **MySQL Workbench**

2. **Login as root:**
```sql
mysql -u root -p
```

3. **Create Database:**
```sql
CREATE DATABASE greeta_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **Create User (Optional but Recommended):**
```sql
CREATE USER 'greeta_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON greeta_attendance.* TO 'greeta_user'@'localhost';
FLUSH PRIVILEGES;
```

---

### **Step 3: Configure Flutter App**

1. **Open:** `lib/config/database_config.dart`

2. **Update Configuration:**
```dart
static const String host = 'localhost';        // MySQL server address
static const int port = 3306;                  // MySQL port (default: 3306)
static const String database = 'greeta_attendance';
static const String username = 'root';         // or 'greeta_user'
static const String password = 'your_password'; // Your MySQL password
```

3. **For Remote MySQL Server:**
```dart
static const String host = '192.168.1.100';    // Server IP address
static const int port = 3306;
static const String database = 'greeta_attendance';
static const String username = 'greeta_user';
static const String password = 'your_password';
```

---

### **Step 4: Install Dependencies**

Run in your project directory:
```bash
flutter pub get
```

This will install the `mysql1` package.

---

### **Step 5: Test Connection**

1. **Start MySQL Server** (if not running)
2. **Run the Flutter app**
3. **Check console** for connection messages:
   - ✅ `Connected to MySQL database` = Success
   - ❌ `MySQL connection error` = Check configuration

---

## 📊 Database Schema

The app will automatically create these tables on first connection:

### **admins Table**
```sql
CREATE TABLE admins (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### **login_logs Table**
```sql
CREATE TABLE login_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  loginTime DATETIME NOT NULL,
  success TINYINT(1) DEFAULT 0,
  ipAddress VARCHAR(45),
  deviceInfo TEXT,
  INDEX idx_username (username),
  INDEX idx_loginTime (loginTime)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 🔐 Default Admin User

The system automatically creates a default admin user:

- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@greeta.com`

**⚠️ Change this password immediately after first login!**

---

## 🔧 Configuration Options

### **Local Development:**
```dart
static const String host = 'localhost';
static const int port = 3306;
static const String database = 'greeta_attendance';
static const String username = 'root';
static const String password = 'your_root_password';
```

### **Remote Server:**
```dart
static const String host = 'your-server-ip';
static const int port = 3306;
static const String database = 'greeta_attendance';
static const String username = 'greeta_user';
static const String password = 'secure_password';
```

### **Connection Pool Settings:**
```dart
static const int maxConnections = 5;
static const int connectionTimeout = 30; // seconds
```

---

## 🛠️ Troubleshooting

### **Issue: "Can't connect to MySQL server"**

**Solutions:**
1. Check MySQL service is running:
   ```bash
   # Windows
   services.msc → MySQL
   
   # Linux
   sudo systemctl status mysql
   
   # macOS
   brew services list
   ```

2. Verify host and port:
   - Default port: 3306
   - Check firewall settings

3. Test connection manually:
   ```bash
   mysql -h localhost -u root -p
   ```

### **Issue: "Access denied for user"**

**Solutions:**
1. Check username and password in `database_config.dart`
2. Verify user has privileges:
   ```sql
   GRANT ALL PRIVILEGES ON greeta_attendance.* TO 'username'@'localhost';
   FLUSH PRIVILEGES;
   ```

### **Issue: "Unknown database"**

**Solutions:**
1. Create the database:
   ```sql
   CREATE DATABASE greeta_attendance;
   ```

2. Check database name in config matches

### **Issue: "Connection timeout"**

**Solutions:**
1. Check network connectivity
2. Verify MySQL server is accessible
3. Check firewall rules
4. Increase timeout in config

---

## 🔒 Security Best Practices

### **1. Use Strong Passwords**
- Minimum 12 characters
- Mix of letters, numbers, symbols
- Don't use default passwords

### **2. Create Dedicated User**
```sql
CREATE USER 'greeta_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON greeta_attendance.* TO 'greeta_user'@'localhost';
FLUSH PRIVILEGES;
```

### **3. Restrict Remote Access**
- Only allow connections from trusted IPs
- Use firewall rules
- Consider SSH tunneling for remote access

### **4. Enable SSL (Production)**
- Configure MySQL SSL certificates
- Update connection settings to use SSL

### **5. Regular Backups**
```bash
mysqldump -u root -p greeta_attendance > backup.sql
```

---

## 📈 Performance Tips

1. **Indexes:** Already created on frequently queried columns
2. **Connection Pooling:** Configured for efficient connections
3. **Query Optimization:** Use prepared statements (already implemented)
4. **Regular Maintenance:** Run `OPTIMIZE TABLE` periodically

---

## 🔄 Migration from SQLite

If you have existing SQLite data:

1. **Export SQLite data:**
   ```bash
   sqlite3 greeta_database.db .dump > export.sql
   ```

2. **Convert to MySQL format:**
   - Replace `INTEGER PRIMARY KEY AUTOINCREMENT` with `INT AUTO_INCREMENT PRIMARY KEY`
   - Replace `TEXT` with `VARCHAR` or `TEXT`
   - Update date formats

3. **Import to MySQL:**
   ```bash
   mysql -u root -p greeta_attendance < converted_export.sql
   ```

---

## 📝 Testing

### **Test Connection:**
```dart
final dbService = DatabaseService();
final connected = await dbService.testConnection();
print(connected ? 'Connected!' : 'Failed!');
```

### **Test Admin Login:**
1. Run app
2. Go to Admin Panel
3. Login with: `admin` / `admin123`
4. Should connect to MySQL and authenticate

---

## 🌐 Network Configuration

### **For Remote MySQL Access:**

1. **Update MySQL Config** (`my.cnf` or `my.ini`):
   ```ini
   bind-address = 0.0.0.0  # Allow remote connections
   ```

2. **Update Flutter Config:**
   ```dart
   static const String host = 'your-server-ip';
   ```

3. **Firewall Rules:**
   ```bash
   # Allow MySQL port
   sudo ufw allow 3306/tcp
   ```

4. **MySQL User:**
   ```sql
   CREATE USER 'greeta_user'@'%' IDENTIFIED BY 'password';
   GRANT ALL PRIVILEGES ON greeta_attendance.* TO 'greeta_user'@'%';
   ```

---

## ✅ Verification Checklist

- [ ] MySQL server installed and running
- [ ] Database `greeta_attendance` created
- [ ] User created with proper privileges
- [ ] Configuration updated in `database_config.dart`
- [ ] Dependencies installed (`flutter pub get`)
- [ ] Connection test successful
- [ ] Default admin user created
- [ ] Login test successful

---

## 📚 Additional Resources

- **MySQL Documentation:** https://dev.mysql.com/doc/
- **mysql1 Package:** https://pub.dev/packages/mysql1
- **MySQL Workbench:** https://dev.mysql.com/downloads/workbench/

---

**MySQL database is ready!** 🎉

Make sure your MySQL server is running before starting the app.

