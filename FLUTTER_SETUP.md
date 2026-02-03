# Flutter Setup Guide

## Quick Start

1. **Ensure Flutter is installed**
   ```bash
   flutter doctor
   ```

2. **Get dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

## Dependencies

All dependencies are listed in `pubspec.yaml`. Key packages:

- **camera**: Camera access for face capture
- **google_mlkit_face_detection**: Face detection
- **flutter_tts**: Text-to-speech
- **speech_to_text**: Speech recognition
- **path_provider**: File system access
- **csv**: CSV file handling

## Platform-Specific Setup

### Android

1. Open `android/app/src/main/AndroidManifest.xml`
2. Add permissions:
   ```xml
   <uses-permission android:name="android.permission.CAMERA" />
   <uses-permission android:name="android.permission.RECORD_AUDIO" />
   <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
   <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
   ```

### iOS

1. Open `ios/Runner/Info.plist`
2. Add permissions:
   ```xml
   <key>NSCameraUsageDescription</key>
   <string>This app needs camera access for face recognition</string>
   <key>NSMicrophoneUsageDescription</key>
   <string>This app needs microphone access for voice commands</string>
   ```

## Building for Release

### Android
```bash
flutter build apk --release
```

### iOS
```bash
flutter build ios --release
```

## Testing

Run tests:
```bash
flutter test
```

## Common Issues

### Camera Permission Denied
- Go to device Settings → Apps → GreetA → Permissions
- Enable Camera and Microphone

### Face Recognition Not Working
- Ensure training images are captured (100 per faculty)
- Check lighting conditions
- Face the camera directly

### Build Errors
- Run `flutter clean`
- Run `flutter pub get`
- Restart IDE

