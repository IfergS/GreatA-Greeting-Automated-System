# 🎓 GreetA - Faculty Attendance System (Flutter Edition)

A modern Flutter application for faculty attendance management using AI-powered face recognition, voice assistance, and comprehensive admin controls.

## ✨ Features

### Core Features
- **Face Recognition**: AI-powered face detection and recognition for attendance marking
- **Voice Assistant**: Text-to-speech greetings and voice command support
- **Admin Panel**: Complete faculty management system with CRUD operations
- **Attendance Tracking**: Daily attendance records with CSV export
- **Real-time Camera**: Live face detection and recognition
- **Modern UI**: Beautiful dark theme with Material Design 3

### Advanced Features
- **Duplicate Prevention**: One attendance record per faculty per day
- **Time-based Greetings**: Contextual greetings based on time of day
- **Password Protection**: Secure admin access
- **Training Images**: Capture 100 images per faculty for accurate recognition
- **Statistics Dashboard**: View faculty count, attendance records, and more

## 📋 Requirements

- Flutter SDK >= 3.0.0
- Dart SDK >= 3.0.0
- Android Studio / VS Code with Flutter extensions
- Android device/emulator or iOS device/simulator
- Camera permissions

## 🚀 Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "GreatA Greeting Automated System"
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the application**
   ```bash
   flutter run
   ```

## 📱 Platform Setup

### Android
- Minimum SDK: 21 (Android 5.0)
- Add camera permissions in `android/app/src/main/AndroidManifest.xml`:
  ```xml
  <uses-permission android:name="android.permission.CAMERA" />
  <uses-permission android:name="android.permission.RECORD_AUDIO" />
  ```

### iOS
- Minimum iOS: 12.0
- Add camera permissions in `ios/Runner/Info.plist`:
  ```xml
  <key>NSCameraUsageDescription</key>
  <string>This app needs camera access for face recognition</string>
  <key>NSMicrophoneUsageDescription</key>
  <string>This app needs microphone access for voice commands</string>
  ```

## 🎯 Usage Guide

### First Time Setup

1. **Launch the app** - You'll see the home screen with voice assistant
2. **Access Admin Panel** - Click "⚙️ Admin Panel"
3. **Login** - Default credentials:
   - Username: `admin`
   - Password: `admin123`
4. **Add Faculty**:
   - Click "➕ Add Faculty" or navigate to Faculty Management
   - Enter Faculty ID and Name
   - Capture 100 training images using the camera
   - Click "Save Faculty"

### Taking Attendance

1. From home screen, click "▶ Take Attendance"
2. Position your face in front of the camera
3. Wait for face detection and recognition
4. System will automatically:
   - Detect your face
   - Recognize you (if registered)
   - Mark attendance
   - Greet you with voice message

### Voice Commands

Click "🎯 Start Listening" and say:
- "hello" or "hi" - Get a greeting
- "time" - Get current time
- "date" - Get current date
- "weather" - Weather information (placeholder)

## 📁 Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/
│   ├── faculty.dart          # Faculty data model
│   └── attendance.dart       # Attendance data model
├── screens/
│   ├── home_screen.dart      # Main home screen
│   ├── attendance_screen.dart # Face recognition attendance
│   ├── admin_panel_screen.dart # Admin dashboard
│   ├── admin_login_screen.dart # Admin authentication
│   ├── add_faculty_screen.dart # Add new faculty
│   ├── view_faculty_screen.dart # View all faculty
│   └── attendance_records_screen.dart # View attendance records
├── services/
│   ├── storage_service.dart  # CSV file management
│   ├── face_recognition_service.dart # Face detection & recognition
│   └── voice_service.dart    # TTS and speech recognition
└── utils/
    └── app_theme.dart        # App theme and colors
```

## 🔧 Configuration

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

Change password in Admin Panel → Settings → Change Password

### Training Images
- **Required**: 100 images per faculty member
- **Purpose**: Improve face recognition accuracy
- **Location**: Stored in app documents directory

## 📊 Data Storage

All data is stored locally in CSV format:
- **Faculty Details**: `FacultyDetails/FacultyDetails.csv`
- **Attendance Records**: `Attendance/Attendance_DD-MM-YYYY.csv`
- **Training Images**: `TrainingImage/User.{FacultyID}/`
- **Password**: `TrainingImageLabel/psd.txt`

## 🎨 UI Theme

The app uses a modern dark theme with:
- **Primary Color**: Deep Navy (#1a1a2e)
- **Secondary Color**: Darker Navy (#16213e)
- **Accent Color**: Blue (#2196F3)
- **Text Colors**: White, Light Gray, Muted Gray

## 🔐 Security Features

- Password-protected admin access
- Secure local data storage
- Face quality validation
- Duplicate attendance prevention

## 🐛 Troubleshooting

### Camera Not Working
- Check camera permissions in device settings
- Ensure camera is not being used by another app
- Restart the app

### Face Not Recognized
- Ensure good lighting
- Face the camera directly
- Make sure you've registered with 100 training images
- Try retraining with more images

### Voice Not Working
- Check microphone permissions
- Ensure device volume is up
- Check if TTS is enabled on device

### App Crashes
- Clear app data and restart
- Ensure all dependencies are installed: `flutter pub get`
- Check Flutter version compatibility

## 📝 Notes

- This Flutter version is a complete rebuild of the Python system
- Face recognition uses Google ML Kit for detection
- For production, consider using TensorFlow Lite models for better accuracy
- CSV storage can be migrated to SQLite for better performance

## 🔄 Migration from Python Version

If you have data from the Python version:
1. Copy CSV files to Flutter app's documents directory
2. Copy training images to `TrainingImage/User.{ID}/` structure
3. Update file paths in `StorageService` if needed

## 📄 License

See LICENSE file for details.

## 👥 Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Contact: greeta.support@email.com

## 🚧 Future Enhancements

- [ ] TensorFlow Lite model integration for better face recognition
- [ ] SQLite database migration
- [ ] Cloud backup and sync
- [ ] Multi-language support
- [ ] Advanced anti-spoofing detection
- [ ] Export to PDF/Excel
- [ ] Biometric authentication
- [ ] Push notifications

---

**Built with Flutter 💙 | Powered by AI 🤖**

