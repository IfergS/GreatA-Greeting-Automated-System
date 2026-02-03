# 📱 Quick Setup: Run on Your Phone

## 🎯 Your Computer's IP Address: `192.168.1.10`

---

## ⚡ Quick Steps (5 minutes)

### **1. Connect Your Phone**

**Android:**
- Enable **Developer Options** (tap Build Number 7 times)
- Enable **USB Debugging** in Developer Options
- Connect phone via USB cable
- Accept "Allow USB debugging" prompt

**Check connection:**
```bash
flutter devices
```
Should show your phone!

---

### **2. Update Database Config for Phone**

**Open:** `lib/config/database_config.dart`

**Change line 12 from:**
```dart
static const String host = 'localhost';
```

**To:**
```dart
static const String host = '192.168.1.10'; // Your computer's IP
```

**Or uncomment line 17:**
```dart
static const String host = '192.168.1.10'; // Your computer's IP address
```

---

### **3. Configure Windows Firewall**

**Allow MySQL port 3306:**

Run in **Command Prompt (Admin):**
```bash
netsh advfirewall firewall add rule name="MySQL XAMPP" dir=in action=allow protocol=TCP localport=3306
```

**Or manually:**
- Windows Defender Firewall → Advanced Settings
- Inbound Rules → New Rule → Port → TCP → 3306 → Allow

---

### **4. Make Sure:**
- ✅ XAMPP MySQL is running (green in Control Panel)
- ✅ Phone and computer on **same Wi-Fi network**
- ✅ Database config updated with IP: `192.168.1.10`

---

### **5. Run on Phone:**
```bash
flutter run
```

**Or:**
```bash
flutter run -d android
```

---

## ✅ Success Indicators

**Console should show:**
```
✅ Connected to MySQL database: mysql://root@192.168.1.10:3306/greeta_attendance
✅ Database tables initialized
```

**App will:**
- Install on your phone
- Connect to XAMPP MySQL on your computer
- All features working!

---

## 🐛 Troubleshooting

**Phone not detected?**
```bash
adb kill-server
adb start-server
adb devices
```

**MySQL connection failed?**
- Check phone and computer on same Wi-Fi
- Verify IP: `192.168.1.10` in config
- Check XAMPP MySQL is running
- Check Windows Firewall allows port 3306

**Still not working?**
- See detailed guide: `RUN_ON_PHONE.md`

---

**Ready! Connect phone and run!** 🚀

