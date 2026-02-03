# 📱 Running App on Your Phone - Step by Step Guide

## 🔌 Step 1: Connect Your Phone

### **For Android Phone:**

1. **Enable Developer Options:**
   - Go to **Settings** → **About Phone**
   - Find **"Build Number"** (or **"Build Version"**)
   - Tap it **7 times** until you see "You are now a developer!"

2. **Enable USB Debugging:**
   - Go to **Settings** → **Developer Options**
   - Turn on **"USB Debugging"**
   - Accept the warning dialog

3. **Connect Phone to Computer:**
   - Use a **USB cable** to connect your phone
   - On your phone, when prompted, tap **"Allow USB debugging"**
   - Check **"Always allow from this computer"** (optional)
   - Tap **"Allow"**

4. **Verify Connection:**
   ```bash
   flutter devices
   ```
   You should see your phone listed!

---

## 🗄️ Step 2: Configure MySQL for Phone Connection

**Important:** Your phone cannot connect to `localhost` - it needs your **computer's IP address**.

### **Find Your Computer's IP Address:**

**Windows:**
1. Open **Command Prompt** or **PowerShell**
2. Run: `ipconfig`
3. Look for **"IPv4 Address"** under your active network adapter
   - Example: `192.168.1.100` or `192.168.0.5`

**Or use this command:**
```bash
ipconfig | findstr IPv4
```

### **Update Database Config:**

1. Open: `lib/config/database_config.dart`

2. Change the host from `localhost` to your computer's IP:
   ```dart
   static const String host = '192.168.1.100'; // Your computer's IP address
   ```

3. **Make sure:**
   - Phone and computer are on the **same Wi-Fi network**
   - XAMPP MySQL is running on your computer
   - Windows Firewall allows MySQL connections (port 3306)

---

## 🔥 Step 3: Configure Windows Firewall

**Allow MySQL through Firewall:**

1. Open **Windows Defender Firewall**
2. Click **"Advanced settings"**
3. Click **"Inbound Rules"** → **"New Rule"**
4. Select **"Port"** → **Next**
5. Select **"TCP"** → Enter port **3306** → **Next**
6. Select **"Allow the connection"** → **Next**
7. Check all profiles → **Next**
8. Name: **"MySQL XAMPP"** → **Finish**

**Or use Command Prompt (Admin):**
```bash
netsh advfirewall firewall add rule name="MySQL XAMPP" dir=in action=allow protocol=TCP localport=3306
```

---

## 🚀 Step 4: Run the App

1. **Check your phone is connected:**
   ```bash
   flutter devices
   ```

2. **Run on your phone:**
   ```bash
   flutter run
   ```
   Or specify Android:
   ```bash
   flutter run -d android
   ```

3. **The app will:**
   - Build and install on your phone
   - Connect to XAMPP MySQL on your computer
   - Show: `✅ XAMPP MySQL database connected`

---

## ✅ Step 5: Verify Connection

**Check Console Output:**
```
✅ Connected to MySQL database: mysql://root@192.168.1.100:3306/greeta_attendance
✅ Database tables initialized
✅ Default admin user created
```

**Test in App:**
- Open Admin Panel
- Login: `admin` / `admin123`
- Should connect successfully!

---

## 🐛 Troubleshooting

### **Phone Not Detected?**

1. **Check USB connection:**
   - Try different USB cable
   - Try different USB port
   - Make sure USB debugging is enabled

2. **Restart ADB:**
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

3. **Check phone:**
   - Unlock phone screen
   - Accept USB debugging prompt
   - Check "Always allow" if prompted

### **MySQL Connection Failed?**

1. **Check IP Address:**
   - Make sure phone and computer are on same Wi-Fi
   - Verify IP in `database_config.dart` is correct
   - Test: `ping 192.168.1.100` (your IP)

2. **Check XAMPP MySQL:**
   - XAMPP Control Panel → MySQL should be "Running" (green)
   - Test connection on computer first

3. **Check Firewall:**
   - Windows Firewall should allow port 3306
   - Try temporarily disabling firewall to test

4. **Check MySQL Binding:**
   - XAMPP MySQL might only bind to localhost
   - Edit: `C:\xampp\mysql\bin\my.ini`
   - Find: `bind-address = 127.0.0.1`
   - Change to: `bind-address = 0.0.0.0`
   - Restart MySQL in XAMPP

### **Build Errors?**

1. **Clean and rebuild:**
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

2. **Check Android SDK:**
   ```bash
   flutter doctor
   ```

---

## 📝 Quick Checklist

- [ ] Phone connected via USB
- [ ] USB debugging enabled
- [ ] Phone appears in `flutter devices`
- [ ] Computer IP address found
- [ ] Database config updated with IP
- [ ] Phone and computer on same Wi-Fi
- [ ] Windows Firewall allows port 3306
- [ ] XAMPP MySQL running
- [ ] App runs successfully
- [ ] MySQL connects from phone

---

## 🎯 Alternative: Use Same Wi-Fi Network

**For best results:**
- Connect phone and computer to **same Wi-Fi network**
- Use computer's **local IP address** (not localhost)
- Example: `192.168.1.100` instead of `localhost`

---

## 📱 Testing on Phone

Once connected:
1. App will install automatically
2. MySQL will connect to your computer's XAMPP
3. All features will work:
   - ✅ Face recognition
   - ✅ Voice commands
   - ✅ Admin panel
   - ✅ Database operations

---

**Ready to run!** Follow the steps above and your app will work on your phone! 🚀

