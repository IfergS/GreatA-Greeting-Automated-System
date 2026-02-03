import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/home_screen.dart';
import 'services/database_service.dart';
import 'utils/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize XAMPP MySQL database (skip on web)
  if (!kIsWeb) {
    try {
      final dbService = DatabaseService();
      final connected = await dbService.testConnection();
      if (connected) {
        print('✅ XAMPP MySQL database connected on app start');
      } else {
        print('⚠️ XAMPP MySQL connection failed');
        print('⚠️ Make sure XAMPP MySQL is running (green in XAMPP Control Panel)');
        print('⚠️ Create database: greeta_attendance in phpMyAdmin');
      }
    } catch (e) {
      print('❌ XAMPP MySQL database initialization error: $e');
      print('⚠️ Troubleshooting:');
      print('   1. Check XAMPP Control Panel - MySQL should be "Running" (green)');
      print('   2. Open phpMyAdmin: http://localhost/phpmyadmin');
      print('   3. Create database: greeta_attendance');
      print('   4. Verify config in: lib/config/database_config.dart');
    }
  } else {
    print('ℹ️ Running on web platform - MySQL direct connection not available');
    print('ℹ️ Database features will be limited on web');
    print('ℹ️ For full functionality, run on Android, iOS, Windows, macOS, or Linux');
  }
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  runApp(const GreetAApp());
}

class GreetAApp extends StatelessWidget {
  const GreetAApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GreetA - Faculty Attendance System',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.dark,
      home: const HomeScreen(),
    );
  }
}

