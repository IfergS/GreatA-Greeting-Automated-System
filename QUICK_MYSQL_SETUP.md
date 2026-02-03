# ⚡ Quick MySQL Setup Guide

## 🚀 5-Minute Setup

### **Step 1: Install MySQL** (if not installed)
- **Windows:** Download from https://dev.mysql.com/downloads/installer/
- **Mac:** `brew install mysql && brew services start mysql`
- **Linux:** `sudo apt install mysql-server && sudo systemctl start mysql`

### **Step 2: Create Database**
```bash
mysql -u root -p
```
Then run:
```sql
CREATE DATABASE greeta_attendance;
EXIT;
```

### **Step 3: Configure App**
Open `lib/config/database_config.dart` and set your MySQL password:
```dart
static const String password = 'your_mysql_password_here';
```

### **Step 4: Install Dependencies**
```bash
flutter pub get
```

### **Step 5: Run App**
```bash
flutter run
```

The app will automatically create tables on first connection!

---

## ✅ Default Login
- **Username:** `admin`
- **Password:** `admin123`

---

## 🔧 Configuration File
**Location:** `lib/config/database_config.dart`

**Update these values:**
- `host` - MySQL server address (default: localhost)
- `port` - MySQL port (default: 3306)
- `database` - Database name (default: greeta_attendance)
- `username` - MySQL username (default: root)
- `password` - **⚠️ SET YOUR MYSQL PASSWORD HERE**

---

## 🐛 Quick Troubleshooting

**"Can't connect"**
→ Check MySQL is running: `sudo systemctl status mysql`

**"Access denied"**
→ Check password in `database_config.dart`

**"Unknown database"**
→ Run: `CREATE DATABASE greeta_attendance;`

---

**That's it!** 🎉 See `MYSQL_SETUP.md` for detailed instructions.

