import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/attendance.dart';
import '../services/storage_service.dart';
import '../utils/app_theme.dart';

class AttendanceRecordsScreen extends StatefulWidget {
  const AttendanceRecordsScreen({super.key});

  @override
  State<AttendanceRecordsScreen> createState() => _AttendanceRecordsScreenState();
}

class _AttendanceRecordsScreenState extends State<AttendanceRecordsScreen> {
  final StorageService _storageService = StorageService();
  DateTime? _selectedDate;
  List<Attendance> _attendanceList = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _selectedDate = DateTime.now();
    _loadAttendance();
  }

  Future<void> _loadAttendance() async {
    setState(() {
      _isLoading = true;
    });

    try {
      if (_selectedDate != null) {
        _attendanceList = await _storageService.getAttendanceForDate(_selectedDate!);
      } else {
        _attendanceList = await _storageService.getAllAttendance();
      }
    } catch (e) {
      print('Error loading attendance: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _selectDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );

    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
      _loadAttendance();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          // Date Selector
          Container(
            padding: const EdgeInsets.all(20),
            color: AppTheme.secondaryColor,
            child: Row(
              children: [
                const Text(
                  'Select Date:',
                  style: TextStyle(
                    color: AppTheme.textPrimary,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(width: 15),
                ElevatedButton.icon(
                  onPressed: () => _selectDate(context),
                  icon: const Icon(Icons.calendar_today),
                  label: Text(
                    _selectedDate != null
                        ? DateFormat('dd-MM-yyyy').format(_selectedDate!)
                        : 'Select Date',
                  ),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _selectedDate = null;
                    });
                    _loadAttendance();
                  },
                  icon: const Icon(Icons.list),
                  label: const Text('View All'),
                ),
              ],
            ),
          ),

          // Attendance List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _attendanceList.isEmpty
                    ? const Center(
                        child: Text(
                          'No attendance records found',
                          style: TextStyle(color: AppTheme.textSecondary),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(20),
                        itemCount: _attendanceList.length,
                        itemBuilder: (context, index) {
                          final attendance = _attendanceList[index];
                          return Card(
                            color: AppTheme.secondaryColor,
                            margin: const EdgeInsets.only(bottom: 10),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: AppTheme.accentColor,
                                child: Text(
                                  attendance.facultyName[0].toUpperCase(),
                                  style: const TextStyle(color: AppTheme.textPrimary),
                                ),
                              ),
                              title: Text(
                                attendance.facultyName,
                                style: const TextStyle(
                                  color: AppTheme.textPrimary,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'ID: ${attendance.facultyId}',
                                    style: const TextStyle(color: AppTheme.textSecondary),
                                  ),
                                  Text(
                                    'Date: ${DateFormat('dd-MM-yyyy').format(attendance.date)}',
                                    style: const TextStyle(color: AppTheme.textSecondary),
                                  ),
                                  Text(
                                    'Time: ${DateFormat('HH:mm:ss').format(attendance.time)}',
                                    style: const TextStyle(color: AppTheme.textSecondary),
                                  ),
                                ],
                              ),
                              trailing: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.green,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: const Text(
                                  'Present',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}

