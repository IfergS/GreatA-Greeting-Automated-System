# 🗄️ Create Database in XAMPP MySQL - Step by Step

## 📋 Quick Instructions

### **Method 1: Using phpMyAdmin (Easiest)**

1. **Start XAMPP MySQL:**
   - Open XAMPP Control Panel
   - Click **"Start"** next to MySQL
   - Wait for green "Running" status ✅

2. **Open phpMyAdmin:**
   - Click **"Admin"** button next to MySQL in XAMPP Control Panel
   - OR open browser: http://localhost/phpmyadmin

3. **Run SQL Script:**
   - Click **"SQL"** tab at the top
   - Open file: `create_database.sql` in this project
   - Copy **ALL** the SQL code
   - Paste into the SQL text area
   - Click **"Go"** button
   - ✅ Database created!

4. **Verify:**
   - You should see: `Database greeta_attendance created successfully!`
   - Check left sidebar - `greeta_attendance` database should appear
   - Click on it to see tables: `admins` and `login_logs`

---

### **Method 2: Using phpMyAdmin GUI (No SQL)**

1. **Start XAMPP MySQL** (same as above)

2. **Open phpMyAdmin:**
   - http://localhost/phpmyadmin

3. **Create Database:**
   - Click **"New"** in left sidebar
   - Database name: `greeta_attendance`
   - Collation: `utf8mb4_unicode_ci`
   - Click **"Create"**

4. **Select Database:**
   - Click on `greeta_attendance` in left sidebar

5. **Create Tables:**
   - Click **"SQL"** tab
   - Copy SQL from `create_database.sql` (skip the CREATE DATABASE line)
   - Paste and click **"Go"**

---

### **Method 3: Using MySQL Command Line**

1. **Open MySQL Command Line:**
   - XAMPP Control Panel → Click **"Shell"**
   - OR open: `C:\xampp\mysql\bin\mysql.exe`

2. **Run Commands:**
   ```bash
   mysql -u root
   ```
   (Press Enter - no password needed for XAMPP default)

3. **Execute SQL:**
   ```sql
   source C:\Users\USER\OneDrive\Desktop\Capstone Project 2025\GreatA Greeting Automated System\create_database.sql
   ```
   OR copy-paste the SQL commands from `create_database.sql`

---

## ✅ Verification Steps

After creating the database, verify it's set up correctly:

1. **Check Database Exists:**
   - phpMyAdmin → Left sidebar → See `greeta_attendance` ✅

2. **Check Tables:**
   - Click `greeta_attendance` → See `admins` and `login_logs` tables ✅

3. **Check Default Admin:**
   - Click `admins` table → Browse → See admin user ✅
   - Username: `admin`
   - Password: `admin123`

4. **Test Flutter App:**
   ```bash
   flutter run
   ```
   - Should see: `✅ XAMPP MySQL database connected`
   - No connection errors ✅

---

## 🐛 Troubleshooting

### **Issue: "Unknown database 'greeta_attendance'"**

**Solution:**
- Database doesn't exist yet
- Follow Method 1 or 2 above to create it

### **Issue: "Access denied"**

**Solution:**
- Check XAMPP MySQL is running (green)
- Default XAMPP: username=`root`, password=(empty)
- If you set a password, update `lib/config/database_config.dart`

### **Issue: "Table already exists"**

**Solution:**
- This is OK - tables already created
- Just verify they exist in phpMyAdmin

### **Issue: Can't open phpMyAdmin**

**Solution:**
- Make sure Apache is also running in XAMPP
- phpMyAdmin needs Apache to run
- Start Apache in XAMPP Control Panel

---

## 📊 Database Structure

After creation, you should have:

**Database:** `greeta_attendance`

**Tables:**
1. **admins** - Admin user accounts
   - id, username, password, email, fullName, createdAt, lastLogin, isActive

2. **login_logs** - Login attempt history
   - id, username, loginTime, success, ipAddress, deviceInfo

**Default Admin:**
- Username: `admin`
- Password: `admin123`

---

## 🎯 Quick Checklist

- [ ] XAMPP MySQL is running (green)
- [ ] phpMyAdmin opens: http://localhost/phpmyadmin
- [ ] Database `greeta_attendance` created
- [ ] Tables `admins` and `login_logs` exist
- [ ] Default admin user exists
- [ ] Flutter app connects successfully

---

## 📝 Next Steps

After database is created:

1. **Run Flutter App:**
   ```bash
   flutter run
   ```

2. **Test Connection:**
   - Check console for: `✅ XAMPP MySQL database connected`

3. **Login to Admin Panel:**
   - Username: `admin`
   - Password: `admin123`

4. **Change Default Password:**
   - Login → Settings → Change Password
   - ⚠️ Important for security!

---

**Database creation complete!** ✅

