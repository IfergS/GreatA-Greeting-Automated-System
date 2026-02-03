import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'attendance_screen.dart';
import 'admin_panel_screen.dart';
import '../utils/app_theme.dart';
import '../services/voice_service.dart';
import '../services/storage_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final VoiceService _voiceService = VoiceService();
  final StorageService _storageService = StorageService();
  
  String _currentTime = '';
  String _currentDate = '';
  int _facultyCount = 0;
  bool _isListening = false;
  String _voiceStatus = '';
  String _voiceResponse = '';

  @override
  void initState() {
    super.initState();
    _initializeServices();
    _updateDateTime();
    _updateFacultyCount();
    _startWelcomeGreeting();
    
    // Update time every second
    _updateTimePeriodically();
  }

  Future<void> _initializeServices() async {
    try {
      await _storageService.initialize();
      await _voiceService.initialize();
    } catch (e) {
      print('Error initializing services: $e');
    }
  }

  void _updateTimePeriodically() {
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted) {
        _updateDateTime();
        _updateTimePeriodically();
      }
    });
  }

  void _updateDateTime() {
    final now = DateTime.now();
    setState(() {
      _currentTime = DateFormat('HH:mm:ss').format(now);
      _currentDate = DateFormat('dd MMMM yyyy').format(now);
    });
  }

  Future<void> _updateFacultyCount() async {
    final facultyList = await _storageService.getAllFaculty();
    if (mounted) {
      setState(() {
        _facultyCount = facultyList.length;
      });
    }
  }

  Future<void> _startWelcomeGreeting() async {
    await Future.delayed(const Duration(seconds: 1));
    await _voiceService.speak('Welcome to Great A Attendance System');
  }

  Future<void> _startVoiceCommand() async {
    if (_isListening) return;
    
    setState(() {
      _isListening = true;
      _voiceStatus = 'Listening...';
      _voiceResponse = '';
    });

    final command = await _voiceService.listen();
    
    if (!mounted) return;

    if (command == 'timeout') {
      setState(() {
        _voiceStatus = 'No command detected';
        _isListening = false;
      });
    } else if (command == 'error') {
      setState(() {
        _voiceStatus = 'Microphone error';
        _isListening = false;
      });
    } else if (command != null) {
      setState(() {
        _voiceStatus = 'Heard: $command';
      });

      final response = await _voiceService.handleCommand(command);
      setState(() {
        _voiceResponse = response;
        _isListening = false;
      });

      await _voiceService.speak(response);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Header
            Container(
              height: 120,
              decoration: const BoxDecoration(
                color: AppTheme.secondaryColor,
                border: Border(
                  bottom: BorderSide(color: AppTheme.accentColor, width: 2),
                ),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text(
                      '🔐 GreetA - Faculty Attendance System',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '✨ AI-Powered Recognition & Management System ✨',
                      style: TextStyle(
                        fontSize: 14,
                        color: AppTheme.accentColor,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Date and Time
            Container(
              margin: const EdgeInsets.all(20),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
              decoration: BoxDecoration(
                color: AppTheme.secondaryColor,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: AppTheme.accentColor, width: 2),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '📅 $_currentDate',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  Text(
                    _currentTime,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.accentColor,
                    ),
                  ),
                ],
              ),
            ),

            // Faculty Count
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.secondaryColor,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: AppTheme.accentColor, width: 2),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.people, color: AppTheme.accentColor, size: 32),
                  const SizedBox(width: 12),
                  Text(
                    '📊 Total Faculty: $_facultyCount',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Voice Assistant Section
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 20),
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.secondaryColor,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.accentColor, width: 2),
              ),
              child: Column(
                children: [
                  const Text(
                    '🎤 Voice Assistant',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.accentColor,
                    ),
                  ),
                  const SizedBox(height: 15),
                  ElevatedButton.icon(
                    onPressed: _isListening ? null : _startVoiceCommand,
                    icon: Icon(_isListening ? Icons.mic : Icons.mic_none),
                    label: Text(_isListening ? 'Listening...' : '🎯 Start Listening'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    ),
                  ),
                  if (_voiceStatus.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      _voiceStatus,
                      style: TextStyle(
                        color: _voiceStatus.contains('error') || _voiceStatus.contains('No command')
                            ? Colors.orange
                            : Colors.green,
                      ),
                    ),
                  ],
                  if (_voiceResponse.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(
                      _voiceResponse,
                      style: const TextStyle(color: AppTheme.textSecondary),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 30),

            // Main Action Buttons
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                children: [
                  SizedBox(
                    width: double.infinity,
                    height: 60,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => const AttendanceScreen()),
                        ).then((_) => _updateFacultyCount());
                      },
                      icon: const Icon(Icons.camera_alt, size: 28),
                      label: const Text(
                        '▶ Take Attendance',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.accentColor,
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  SizedBox(
                    width: double.infinity,
                    height: 60,
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        final result = await Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => const AdminPanelScreen()),
                        );
                        if (result == true) {
                          _updateFacultyCount();
                        }
                      },
                      icon: const Icon(Icons.admin_panel_settings, size: 28),
                      label: const Text(
                        '⚙️ Admin Panel',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.accentColor,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }
}

