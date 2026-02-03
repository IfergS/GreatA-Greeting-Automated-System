# 🗄️ XAMPP MySQL Setup Guide - GreetA System

## Overview

This guide will help you set up the GreetA Faculty Attendance System to use **XAMPP MySQL** database.

---

## 📥 Step 1: Install XAMPP

1. **Download XAMPP:**
   - Visit: https://www.apachefriends.org/
   - Download XAMPP for Windows
   - Run the installer

2. **Install XAMPP:**
   - Choose installation directory (default: `C:\xampp`)
   - Select components: **MySQL** (required)
   - Complete installation

---

## 🚀 Step 2: Start MySQL in XAMPP

1. **Open XAMPP Control Panel:**
   - Launch "XAMPP Control Panel" from Start Menu
   - Or navigate to: `C:\xampp\xampp-control.exe`

2. **Start MySQL:**
   - Click **"Start"** button next to MySQL
   - Wait for MySQL to start (green indicator)
   - ✅ MySQL is now running on `localhost:3306`

---

## 🗃️ Step 3: Create Database

### **Option A: Using phpMyAdmin (Recommended)**

1. **Open phpMyAdmin:**
   - In XAMPP Control Panel, click **"Admin"** next to MySQL
   - Or open browser: http://localhost/phpmyadmin

2. **Create Database:**
   - Click **"New"** in left sidebar
   - Database name: `greeta_attendance`
   - Collation: `utf8mb4_unicode_ci`
   - Click **"Create"**

### **Option B: Using MySQL Command Line**

1. **Open MySQL Command Line:**
   - In XAMPP Control Panel, click **"Shell"**
   - Or open: `C:\xampp\mysql\bin\mysql.exe`

2. **Create Database:**
   ```sql
   CREATE DATABASE greeta_attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

---

## ⚙️ Step 4: Configure Flutter App

The app is **already configured** for XAMPP MySQL with default settings:

**File:** `lib/config/database_config.dart`

```dart
static const String host = 'localhost';     // ✅ XAMPP default
static const int port = 3306;               // ✅ XAMPP default
static const String database = 'greeta_attendance';
static const String username = 'root';      // ✅ XAMPP default
static const String password = '';           // ✅ XAMPP default (empty)
```

**⚠️ If you set a MySQL password in XAMPP:**
- Update `password` in `database_config.dart` with your password

---

## ✅ Step 5: Verify Setup

### **Test MySQL Connection:**

1. **Check MySQL is Running:**
   - XAMPP Control Panel → MySQL should show "Running" (green)

2. **Test in phpMyAdmin:**
   - Open: http://localhost/phpmyadmin
   - You should see `greeta_attendance` database

3. **Run Flutter App:**
   ```bash
   flutter run
   ```
   - Check console for: `✅ MySQL database connected`

---

## 🔧 XAMPP MySQL Default Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Host | `localhost` | Local server |
| Port | `3306` | Default MySQL port |
| Username | `root` | Default admin user |
| Password | `` (empty) | Default is blank |
| Data Directory | `C:\xampp\mysql\data` | Database files location |

---

## 🛠️ Troubleshooting

### **Issue: "Can't connect to MySQL server"**

**Solutions:**
1. **Check XAMPP Control Panel:**
   - MySQL must be "Running" (green)
   - If not, click "Start"

2. **Check Port 3306:**
   - Make sure no other MySQL instance is using port 3306
   - XAMPP Control Panel → Config → Check Ports

3. **Restart MySQL:**
   - Click "Stop" then "Start" in XAMPP Control Panel

### **Issue: "Access denied for user 'root'"**

**Solutions:**
1. **Check password:**
   - If you set a password, update it in `database_config.dart`
   - Default XAMPP password is empty (blank)

2. **Reset MySQL password:**
   - XAMPP Control Panel → MySQL → Config → my.ini
   - Or use phpMyAdmin to change password

### **Issue: "Unknown database 'greeta_attendance'"**

**Solutions:**
1. **Create database:**
   - Open phpMyAdmin
   - Create database: `greeta_attendance`

2. **Check database name:**
   - Verify name matches in `database_config.dart`

### **Issue: MySQL won't start**

**Solutions:**
1. **Check port conflict:**
   - Another MySQL service might be running
   - Stop other MySQL services

2. **Check XAMPP logs:**
   - XAMPP Control Panel → MySQL → Logs
   - Look for error messages

3. **Reinstall XAMPP:**
   - If issues persist, reinstall XAMPP

---

## 📊 Database Location

**XAMPP MySQL Data:**
- **Location:** `C:\xampp\mysql\data\`
- **Database Files:** `C:\xampp\mysql\data\greeta_attendance\`

**Backup Location:**
- XAMPP Control Panel → MySQL → Backup
- Or manually copy `C:\xampp\mysql\data\greeta_attendance\`

---

## 🔐 Security Notes

### **For Development (Current Setup):**
- ✅ Empty password is fine for local development
- ✅ Only accessible from localhost
- ✅ Not exposed to internet

### **For Production:**
- ⚠️ **Set a strong MySQL password**
- ⚠️ **Create dedicated database user** (not root)
- ⚠️ **Restrict remote access**
- ⚠️ **Enable firewall rules**

---

## 📝 Quick Setup Checklist

- [ ] XAMPP installed
- [ ] MySQL started in XAMPP Control Panel
- [ ] Database `greeta_attendance` created
- [ ] Flutter app configured (already done ✅)
- [ ] Test connection successful
- [ ] App runs without errors

---

## 🎯 Testing the Connection

1. **Start XAMPP MySQL:**
   - XAMPP Control Panel → Start MySQL

2. **Run Flutter App:**
   ```bash
   flutter run
   ```

3. **Check Console Output:**
   ```
   ✅ MySQL database connected on app start
   ✅ Connected to MySQL database: mysql://root@localhost:3306/greeta_attendance
   ✅ Database tables initialized
   ✅ Default admin user created
   ```

4. **Test Login:**
   - Open Admin Panel
   - Login with: `admin` / `admin123`
   - Should connect successfully

---

## 📚 XAMPP Useful Links

- **XAMPP Download:** https://www.apachefriends.org/
- **phpMyAdmin:** http://localhost/phpmyadmin
- **MySQL Documentation:** https://dev.mysql.com/doc/

---

## 🔄 Database Management

### **View Data:**
- Open phpMyAdmin: http://localhost/phpmyadmin
- Select `greeta_attendance` database
- Browse tables: `admins`, `login_logs`

### **Backup Database:**
1. phpMyAdmin → Select database → Export
2. Or use XAMPP Control Panel → MySQL → Backup

### **Restore Database:**
1. phpMyAdmin → Import
2. Select SQL file → Go

---

## ✅ Default Admin Credentials

After first run, default admin is created:
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Change this password immediately after first login!**

---

## 🎉 Setup Complete!

Your XAMPP MySQL database is now configured and ready to use!

**Next Steps:**
1. Start XAMPP MySQL
2. Run the Flutter app
3. Login to Admin Panel
4. Start using the system!

---

**Need Help?** Check the troubleshooting section or see `MYSQL_SETUP.md` for more details.

