# Python Backend - GreetA Faculty Attendance System

This folder contains the original Python-based implementation of the GreetA Faculty Attendance System.

## 📁 Contents

### Core Application Files
- `main.py` - Main attendance application with GUI
- `admin_panel.py` - Admin panel for faculty management
- `backup.py` - Backup utility
- `setup_database.py` - Database setup script
- `test_recognizer.py` - Face recognition testing
- `test.py` - General testing script
- `requirements.txt` - Python dependencies

### Data Directories
- `Attendance/` - Daily attendance CSV files
- `FacultyDetails/` - Faculty database (CSV)
- `TrainingImage/` - Face training images
- `TrainingImageLabel/` - Trained models and configuration
- `Training_data/` - Additional training data
- `StudentDetails/` - Legacy student details (if any)
- `dataset/` - Dataset files
- `models/` - ML model files
- `Tasks/` - Task management files

### Configuration Files
- `haarcascade_frontalface_default.xml` - Haar cascade classifier
- `facenet_keras.h5` - FaceNet Keras model
- `weather_config.txt` - Weather API configuration
- `psd.txt` - Password file (in TrainingImageLabel/)

### Documentation
- `README.md` - Original Python system documentation
- `USAGE_GUIDE.md` - Usage instructions
- `SYSTEM_SUMMARY.md` - System summary
- `WEATHER_SETUP.md` - Weather setup guide

## 🚀 Running the Python System

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the main application:
   ```bash
   python main.py
   ```

3. Run the admin panel:
   ```bash
   python admin_panel.py
   ```

## 📝 Notes

- Default admin password: `admin123`
- The system uses OpenCV for face recognition
- Attendance files are created daily in CSV format
- Training images are stored per faculty member

## 🔄 Migration

This Python backend has been migrated to Flutter/Dart for cross-platform mobile support. The Flutter app is located in the parent directory.
