# ⚡ Quick Database Setup - XAMPP MySQL

## 🎯 Automatic Database Creation (Recommended)

The app will **automatically create the database** when you run it!

### **Steps:**

1. **Start XAMPP MySQL:**
   - Open XAMPP Control Panel
   - Click **"Start"** next to MySQL
   - Wait for green "Running" status ✅

2. **Run Flutter App:**
   ```bash
   flutter run
   ```

3. **Watch Console:**
   - You'll see: `🔄 Attempting to create database automatically...`
   - Then: `✅ Database "greeta_attendance" created successfully`
   - Then: `✅ Database tables initialized`
   - Then: `✅ Default admin user created`

**That's it!** The database is created automatically! 🎉

---

## 📋 Manual Database Creation (If Needed)

If automatic creation fails, create it manually:

### **Method 1: Using phpMyAdmin (Easiest)**

1. **Open phpMyAdmin:**
   - XAMPP Control Panel → Click **"Admin"** next to MySQL
   - OR: http://localhost/phpmyadmin

2. **Create Database:**
   - Click **"New"** in left sidebar
   - Database name: `greeta_attendance`
   - Collation: `utf8mb4_unicode_ci`
   - Click **"Create"**

3. **Run SQL Script:**
   - Click **"SQL"** tab
   - Open `create_database.sql` from project folder
   - Copy ALL SQL code
   - Paste and click **"Go"**

✅ Done!

---

### **Method 2: Using SQL Script Only**

1. **Open phpMyAdmin:** http://localhost/phpmyadmin

2. **Click "SQL" tab**

3. **Copy this SQL:**
   ```sql
   CREATE DATABASE IF NOT EXISTS greeta_attendance 
   CHARACTER SET utf8mb4 
   COLLATE utf8mb4_unicode_ci;
   
   USE greeta_attendance;
   ```

4. **Paste and click "Go"**

✅ Database created! Tables will be created automatically when you run the app.

---

## ✅ Verification

After database is created (automatically or manually):

1. **Check in phpMyAdmin:**
   - Left sidebar → See `greeta_attendance` database ✅
   - Click it → See `admins` and `login_logs` tables ✅

2. **Run Flutter App:**
   ```bash
   flutter run
   ```
   - Should see: `✅ XAMPP MySQL database connected`
   - No errors ✅

3. **Test Login:**
   - Username: `admin`
   - Password: `admin123`

---

## 🐛 Troubleshooting

### **"Database doesn't exist" Error**

**Solution:**
- Make sure XAMPP MySQL is running (green)
- Try manual creation method above
- Check database name matches: `greeta_attendance`

### **"Access denied" Error**

**Solution:**
- XAMPP default: username=`root`, password=(empty)
- If you set a password, update `lib/config/database_config.dart`

### **"Cannot connect" Error**

**Solution:**
- Start MySQL in XAMPP Control Panel
- Check port 3306 is not in use
- Restart XAMPP if needed

---

## 📝 Files Reference

- **SQL Script:** `create_database.sql` - Full database + tables setup
- **Instructions:** `CREATE_DATABASE_INSTRUCTIONS.md` - Detailed guide
- **Config:** `lib/config/database_config.dart` - Database settings

---

**Database setup complete!** ✅

