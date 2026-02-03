import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/home_screen.dart';
import 'services/database_service.dart';
import 'utils/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize SQLite database
  try {
    final dbService = DatabaseService();
    final connected = await dbService.testConnection();
    if (connected) {
      print('✅ SQLite database initialized and connected');
    } else {
      print('⚠️ SQLite database connection failed');
    }
  } catch (e) {
    print('❌ SQLite database initialization error: $e');
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

