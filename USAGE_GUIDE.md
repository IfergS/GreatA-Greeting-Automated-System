# 🎓 GreatA - AI Attendance System Usage Guide

## 📱 Two Applications

### 1. **Main Attendance App** (`main_enhanced.py`)
For daily attendance taking by teachers/staff

### 2. **Admin Panel** (`admin_panel.py`)
For student registration and system management (Admin only)

---

## 🚀 Quick Start

### Running the Main Attendance App
```bash
python3 main_enhanced.py
```

### Running the Admin Panel
```bash
python3 admin_panel.py
```

Or click "🚀 Open Admin Panel" button in the main app.

---

## 🔐 Admin Panel

### Default Password
- **Password:** `admin123`
- **⚠️ Change this immediately after first login!**

### Admin Features

#### 📊 Dashboard
- View total students registered
- See training images count
- Check attendance days
- View recent students

#### ➕ Add Student
1. Enter Student ID
2. Enter Student Name
3. Click "📷 Capture Face Images"
4. Look at the camera (100 photos will be taken automatically)
5. Model trains automatically after capture

#### 📋 View Students
- See all registered students in a table
- Delete students if needed
- Refresh the list
- View serial numbers and IDs

#### 📈 Attendance Records
- Select date from dropdown
- View attendance for that day
- Export to CSV file
- See ID, Name, Date, and Time

#### ⚙️ Settings
- Change admin password
- View system information
- Check database locations

---

## 👤 Main Attendance App

### Features

#### 📸 Take Attendance
1. Click "▶ Take Attendance"
2. Face recognition starts
3. Voice greets recognized students
4. Press 'Q' to stop
5. Attendance saved automatically

#### 🎤 Voice Assistant
1. Click "🎤 Start Listening"
2. Say commands:
   - "Hello" - Get a greeting
   - "What time is it?" - Get current time
   - "What's the weather?" - Get weather info
   - "What's the date?" - Get current date
   - "Thank you" - Get appreciation response

#### 🔐 Admin Panel Access
- Click "🚀 Open Admin Panel" to launch admin interface
- Requires password authentication

---

## 📁 File Structure

```
GreatA-Greeting-Automated-System/
├── main_enhanced.py              # Main attendance application
├── admin_panel.py                # Admin panel for registration
├── FacultyDetails/
│   └── FacultyDetails.csv        # Faculty database
├── TrainingImage/                # Face images for training
├── TrainingImageLabel/
│   ├── Trainner.yml             # Trained model
│   └── psd.txt                  # Admin password
├── Attendance/
│   └── Attendance_DD-MM-YYYY.csv # Daily attendance records
└── haarcascade_frontalface_default.xml  # Face detection model
```

---

## 🔧 Troubleshooting

### Camera Not Working
- Check if camera is connected
- Close other apps using camera
- Grant camera permissions to Terminal/Python

### Face Not Recognized
- Ensure good lighting
- Look directly at camera
- Re-train the model with more images

### Admin Panel Won't Open
- Check password is correct (default: admin123)
- Run `python3 admin_panel.py` manually
- Check file permissions

### Voice Not Working
- Check microphone permissions
- Ensure speakers are on
- Test with "Hello" command

---

## 💡 Best Practices

### For Administrators
1. Change default password immediately
2. Take 100 clear face images per student
3. Ensure good lighting during capture
4. Backup StudentDetails.csv regularly
5. Export attendance records weekly

### For Users (Teachers/Staff)
1. Ensure good lighting for attendance
2. Students should look at camera
3. Wait for voice confirmation
4. Press 'Q' to stop attendance
5. Check attendance table for accuracy

---

## 🔒 Security

### Password Protection
- Admin panel requires password
- Change password in Settings
- Password stored in TrainingImageLabel/psd.txt

### Data Privacy
- Student data in StudentDetails.csv
- Face images in TrainingImage folder
- Attendance records in Attendance folder
- Keep these folders secure!

---

## 📊 Reports & Export

### Exporting Attendance
1. Open Admin Panel
2. Go to "📈 Attendance Records"
3. Select date
4. Click "💾 Export CSV"
5. File saved as `Exported_Attendance_DD-MM-YYYY.csv`

---

## 🆘 Support

For issues or questions:
- Email: greeta.support@email.com
- Check README.md for more details
- Review error messages in terminal

---

## 🎯 Tips for Best Results

### Photo Capture
- ✓ Good lighting
- ✓ Face camera directly
- ✓ Neutral expression
- ✓ No sunglasses/masks
- ✓ Take 100 photos minimum

### Daily Attendance
- ✓ Good lighting in room
- ✓ Students face camera one at a time
- ✓ Wait for voice confirmation
- ✓ Check attendance table
- ✓ Export records regularly

---

## 🔄 Version

**Current Version:** 2.0 Enhanced
**Features:** Modern UI, Voice Assistant, Admin Panel

---

## ✨ Quick Commands

```bash
# Start main app
python3 main_enhanced.py

# Start admin panel
python3 admin_panel.py

# Check Python version
python3 --version

# View attendance files
ls Attendance/

# View registered faculty
cat FacultyDetails/FacultyDetails.csv
```

---

**Enjoy using GreetA! 🎓✨**

