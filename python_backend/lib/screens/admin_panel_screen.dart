import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import '../models/faculty.dart';
import '../models/attendance.dart';
import '../services/storage_service.dart';
import '../services/database_service.dart';
import '../services/weather_service.dart';
import '../services/face_recognition_service.dart';
import '../utils/app_theme.dart';
import 'admin_login_screen.dart';
import 'add_faculty_screen.dart';
import 'view_faculty_screen.dart';
import 'attendance_records_screen.dart';

class AdminPanelScreen extends StatefulWidget {
  const AdminPanelScreen({super.key});

  @override
  State<AdminPanelScreen> createState() => _AdminPanelScreenState();
}

class _AdminPanelScreenState extends State<AdminPanelScreen> {
  final StorageService _storageService = StorageService();
  final DatabaseService _databaseService = DatabaseService();
  final WeatherService _weatherService = WeatherService();
  int _selectedIndex = 0;
  int _totalFaculty = 0;
  int _todayAttendance = 0;
  int _totalAttendance = 0;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeAndAuthenticate();
  }

  Future<void> _initializeAndAuthenticate() async {
    // Initialize MySQL database first
    try {
      final connected = await _databaseService.testConnection();
      if (connected) {
        print('✅ MySQL database connected');
      } else {
        print('⚠️ MySQL connection failed');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('⚠️ MySQL connection failed. Please check your database configuration.'),
              backgroundColor: Colors.orange,
              duration: Duration(seconds: 5),
            ),
          );
        }
      }
    } catch (e) {
      print('❌ MySQL database initialization error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Database error: ${e.toString()}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }

    // Check authentication
    final authenticated = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AdminLoginScreen()),
    );

    if (authenticated != true) {
      if (mounted) {
        Navigator.pop(context);
      }
      return;
    }

    // Load statistics after successful authentication
    if (mounted) {
      setState(() {
        _isInitialized = true;
      });
      _loadStatistics();
    }
  }

  Future<void> _loadStatistics() async {
    final facultyList = await _storageService.getAllFaculty();
    final today = DateTime.now();
    final todayAttendanceList = await _storageService.getAttendanceForDate(today);
    final allAttendance = await _storageService.getAllAttendance();

    if (mounted) {
      setState(() {
        _totalFaculty = facultyList.length;
        _todayAttendance = todayAttendanceList.length;
        _totalAttendance = allAttendance.length;
      });
    }
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  Widget _buildDashboard() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '📊 Dashboard',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 30),
          
          // Statistics Cards
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  'Total Faculty',
                  _totalFaculty.toString(),
                  Icons.people,
                  AppTheme.accentColor,
                ),
              ),
              const SizedBox(width: 15),
              Expanded(
                child: _buildStatCard(
                  'Today\'s Attendance',
                  _todayAttendance.toString(),
                  Icons.today,
                  Colors.green,
                ),
              ),
              const SizedBox(width: 15),
              Expanded(
                child: _buildStatCard(
                  'Total Records',
                  _totalAttendance.toString(),
                  Icons.history,
                  Colors.orange,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 30),
          
          // Quick Actions
          const Text(
            'Quick Actions',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 15),
          
          Wrap(
            spacing: 15,
            runSpacing: 15,
            children: [
              _buildActionCard(
                '➕ Add Faculty',
                Icons.person_add,
                () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AddFacultyScreen()),
                  ).then((_) => _loadStatistics());
                },
              ),
              _buildActionCard(
                '👥 View Faculty',
                Icons.people_outline,
                () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const ViewFacultyScreen()),
                  );
                },
              ),
              _buildActionCard(
                '📋 Attendance Records',
                Icons.assignment,
                () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AttendanceRecordsScreen()),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      color: AppTheme.secondaryColor,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 10),
            Text(
              value,
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 5),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(String title, IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Card(
        color: AppTheme.secondaryColor,
        child: Container(
          width: 150,
          height: 120,
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: AppTheme.accentColor),
              const SizedBox(height: 10),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  color: AppTheme.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFacultyManagement() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '👥 Faculty Management',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimary,
                ),
              ),
              ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AddFacultyScreen()),
                  ).then((_) => _loadStatistics());
                },
                icon: const Icon(Icons.add),
                label: const Text('Add Faculty'),
              ),
            ],
          ),
          const SizedBox(height: 20),
          FutureBuilder<List<Faculty>>(
            future: _storageService.getAllFaculty(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return const Center(
                  child: Text(
                    'No faculty members registered yet',
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                );
              }

              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: snapshot.data!.length,
                itemBuilder: (context, index) {
                  final faculty = snapshot.data![index];
                  return Card(
                    color: AppTheme.secondaryColor,
                    margin: const EdgeInsets.only(bottom: 10),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: AppTheme.accentColor,
                        child: Text(
                          faculty.name[0].toUpperCase(),
                          style: const TextStyle(color: AppTheme.textPrimary),
                        ),
                      ),
                      title: Text(
                        faculty.name,
                        style: const TextStyle(
                          color: AppTheme.textPrimary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        'ID: ${faculty.id}',
                        style: const TextStyle(color: AppTheme.textSecondary),
                      ),
                      trailing: IconButton(
                        icon: const Icon(Icons.delete, color: Colors.red),
                        onPressed: () async {
                          final confirm = await showDialog<bool>(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: const Text('Delete Faculty'),
                              content: Text('Are you sure you want to delete ${faculty.name}?'),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context, false),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed: () => Navigator.pop(context, true),
                                  child: const Text('Delete', style: TextStyle(color: Colors.red)),
                                ),
                              ],
                            ),
                          );

                          if (confirm == true) {
                            await _storageService.deleteFaculty(faculty.id);
                            _loadStatistics();
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Faculty deleted successfully')),
                              );
                            }
                          }
                        },
                      ),
                    ),
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAttendanceRecords() {
    return const AttendanceRecordsScreen();
  }

  Widget _buildSettings() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '⚙️ Settings',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 30),
          
          Card(
            color: AppTheme.secondaryColor,
            child: ListTile(
              leading: const Icon(Icons.lock, color: AppTheme.accentColor),
              title: const Text(
                'Change Password',
                style: TextStyle(color: AppTheme.textPrimary),
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                _showChangePasswordDialog();
              },
            ),
          ),
          
          const SizedBox(height: 10),
          
          Card(
            color: AppTheme.secondaryColor,
            child: ListTile(
              leading: const Icon(Icons.location_on, color: AppTheme.accentColor),
              title: const Text(
                'Weather Location',
                style: TextStyle(color: AppTheme.textPrimary),
              ),
              subtitle: FutureBuilder<String?>(
                future: _weatherService.getSavedLocation(),
                builder: (context, snapshot) {
                  final location = snapshot.data ?? 'Manila (default)';
                  return Text(
                    location,
                    style: const TextStyle(color: AppTheme.textSecondary),
                  );
                },
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                _showWeatherLocationDialog();
              },
            ),
          ),
          
          const SizedBox(height: 10),
          
          Card(
            color: AppTheme.secondaryColor,
            child: ListTile(
              leading: const Icon(Icons.info, color: AppTheme.accentColor),
              title: const Text(
                'About',
                style: TextStyle(color: AppTheme.textPrimary),
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    backgroundColor: AppTheme.secondaryColor,
                    title: const Text(
                      'About GreetA',
                      style: TextStyle(color: AppTheme.textPrimary),
                    ),
                    content: const Text(
                      'GreetA - Faculty Attendance System\n\n'
                      'Version: 1.0.0\n'
                      'AI-Powered Recognition & Management System',
                      style: TextStyle(color: AppTheme.textSecondary),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text(
                          'OK',
                          style: TextStyle(color: AppTheme.accentColor),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showChangePasswordDialog() async {
    final oldPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();
    final usernameController = TextEditingController(text: 'admin');

    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.secondaryColor,
        title: const Text(
          'Change Password',
          style: TextStyle(color: AppTheme.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: usernameController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                labelText: 'Username',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'Enter username',
                hintStyle: TextStyle(color: AppTheme.textMuted),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: oldPasswordController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                labelText: 'Old Password',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'Enter old password',
                hintStyle: TextStyle(color: AppTheme.textMuted),
              ),
              obscureText: true,
            ),
            const SizedBox(height: 10),
            TextField(
              controller: newPasswordController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                labelText: 'New Password',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'Enter new password',
                hintStyle: TextStyle(color: AppTheme.textMuted),
              ),
              obscureText: true,
            ),
            const SizedBox(height: 10),
            TextField(
              controller: confirmPasswordController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                labelText: 'Confirm New Password',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'Confirm new password',
                hintStyle: TextStyle(color: AppTheme.textMuted),
              ),
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Cancel',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              if (newPasswordController.text.length < 4) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Password must be at least 4 characters')),
                );
                return;
              }

              if (newPasswordController.text != confirmPasswordController.text) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Passwords do not match')),
                );
                return;
              }

              final success = await _databaseService.changePassword(
                usernameController.text.trim().toLowerCase(),
                oldPasswordController.text,
                newPasswordController.text,
              );

              if (mounted) {
                if (success) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Password changed successfully')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Incorrect old password')),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accentColor,
            ),
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  Future<void> _showWeatherLocationDialog() async {
    final locationController = TextEditingController();
    final savedLocation = await _weatherService.getSavedLocation();
    locationController.text = savedLocation ?? 'Manila';

    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.secondaryColor,
        title: const Text(
          'Set Weather Location',
          style: TextStyle(color: AppTheme.textPrimary),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Enter the city name for weather updates:',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 15),
            TextField(
              controller: locationController,
              style: const TextStyle(color: AppTheme.textPrimary),
              decoration: const InputDecoration(
                labelText: 'City Name',
                labelStyle: TextStyle(color: AppTheme.textSecondary),
                hintText: 'e.g., Manila, Quezon City, Cebu',
                hintStyle: TextStyle(color: AppTheme.textMuted),
                border: OutlineInputBorder(),
                enabledBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: AppTheme.accentColor),
                ),
                focusedBorder: OutlineInputBorder(
                  borderSide: BorderSide(color: AppTheme.accentColor, width: 2),
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Examples: Manila, Quezon City, Makati, Cebu, Davao',
              style: TextStyle(
                color: AppTheme.textMuted,
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text(
              'Cancel',
              style: TextStyle(color: AppTheme.textSecondary),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              final city = locationController.text.trim();
              if (city.isNotEmpty) {
                await _weatherService.setLocation(city);
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Weather location set to $city'),
                    ),
                  );
                  setState(() {}); // Refresh to show new location
                }
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accentColor,
            ),
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('🎓 GreetA - Admin Panel'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pop(context),
            tooltip: 'Logout',
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _buildDashboard(),
          _buildFacultyManagement(),
          _buildAttendanceRecords(),
          _buildSettings(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: AppTheme.accentColor,
        unselectedItemColor: AppTheme.textSecondary,
        backgroundColor: AppTheme.secondaryColor,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.people),
            label: 'Faculty',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment),
            label: 'Attendance',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}

