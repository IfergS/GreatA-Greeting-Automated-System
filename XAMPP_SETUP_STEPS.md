# 📋 XAMPP MySQL Setup - Step by Step

## ✅ Complete Setup Checklist

### **Step 1: Install XAMPP** ✅
- [ ] Download XAMPP from https://www.apachefriends.org/
- [ ] Install XAMPP (default location: `C:\xampp`)
- [ ] Make sure MySQL component is selected during installation

### **Step 2: Start MySQL** ✅
- [ ] Open XAMPP Control Panel
- [ ] Click **"Start"** button next to MySQL
- [ ] Wait for green "Running" status
- [ ] ✅ MySQL is now active on `localhost:3306`

### **Step 3: Create Database** ✅
- [ ] Open phpMyAdmin: http://localhost/phpmyadmin
- [ ] Click **"New"** in left sidebar
- [ ] Enter database name: `greeta_attendance`
- [ ] Collation: `utf8mb4_unicode_ci`
- [ ] Click **"Create"**
- [ ] ✅ Database created

### **Step 4: Verify Configuration** ✅
- [ ] Open: `lib/config/database_config.dart`
- [ ] Verify settings:
  ```dart
  host = 'localhost'      ✅
  port = 3306            ✅
  username = 'root'      ✅
  password = ''          ✅ (empty - XAMPP default)
  database = 'greeta_attendance' ✅
  ```

### **Step 5: Test Connection** ✅
- [ ] Run: `flutter run`
- [ ] Check console for: `✅ MySQL database connected`
- [ ] Tables should be created automatically
- [ ] Default admin user should be created

### **Step 6: Test Login** ✅
- [ ] Open Admin Panel in app
- [ ] Login with: `admin` / `admin123`
- [ ] ✅ Should connect successfully

---

## 🎯 Quick Reference

### **XAMPP Control Panel:**
- **Location:** Start Menu → XAMPP → XAMPP Control Panel
- **MySQL Start:** Click "Start" button
- **phpMyAdmin:** Click "Admin" button next to MySQL

### **phpMyAdmin:**
- **URL:** http://localhost/phpmyadmin
- **Default Login:** root / (no password)

### **Database Info:**
- **Name:** `greeta_attendance`
- **Location:** `C:\xampp\mysql\data\greeta_attendance\`

---

## 🔧 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| MySQL won't start | Check port 3306, restart XAMPP |
| Can't connect | Verify MySQL is running (green) |
| Unknown database | Create `greeta_attendance` in phpMyAdmin |
| Access denied | Check password in `database_config.dart` |

---

**Setup complete when all checkboxes are checked!** ✅

