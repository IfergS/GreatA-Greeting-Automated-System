import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:csv/csv.dart';
import '../models/faculty.dart';
import '../models/attendance.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  Directory? _appDirectory;
  Directory? _facultyDetailsDir;
  Directory? _attendanceDir;
  Directory? _trainingImageDir;
  Directory? _trainingImageLabelDir;

  Future<void> initialize() async {
    final appDocDir = await getApplicationDocumentsDirectory();
    _appDirectory = Directory(path.join(appDocDir.path, 'GreetA'));
    
    _facultyDetailsDir = Directory(path.join(_appDirectory!.path, 'FacultyDetails'));
    _attendanceDir = Directory(path.join(_appDirectory!.path, 'Attendance'));
    _trainingImageDir = Directory(path.join(_appDirectory!.path, 'TrainingImage'));
    _trainingImageLabelDir = Directory(path.join(_appDirectory!.path, 'TrainingImageLabel'));

    // Create directories if they don't exist
    await _facultyDetailsDir!.create(recursive: true);
    await _attendanceDir!.create(recursive: true);
    await _trainingImageDir!.create(recursive: true);
    await _trainingImageLabelDir!.create(recursive: true);
  }

  // Faculty Management
  Future<List<Faculty>> getAllFaculty() async {
    if (_facultyDetailsDir == null) {
      await initialize();
    }
    
    final file = File(path.join(_facultyDetailsDir!.path, 'FacultyDetails.csv'));
    if (!await file.exists()) {
      return [];
    }

    final content = await file.readAsString();
    final rows = const CsvToListConverter().convert(content);
    
    if (rows.isEmpty || rows.length < 2) {
      return [];
    }

    final facultyList = <Faculty>[];
    // Skip header row
    for (int i = 1; i < rows.length; i++) {
      if (rows[i].length >= 2) {
        facultyList.add(Faculty(
          id: rows[i][0].toString(),
          name: rows[i][1].toString(),
          email: rows[i].length > 2 ? rows[i][2].toString() : null,
          phone: rows[i].length > 3 ? rows[i][3].toString() : null,
        ));
      }
    }
    return facultyList;
  }

  Future<void> saveFaculty(Faculty faculty) async {
    final file = File(path.join(_facultyDetailsDir!.path, 'FacultyDetails.csv'));
    final facultyList = await getAllFaculty();
    
    // Check if faculty already exists
    final existingIndex = facultyList.indexWhere((f) => f.id == faculty.id);
    if (existingIndex != -1) {
      facultyList[existingIndex] = faculty;
    } else {
      facultyList.add(faculty);
    }

    // Write to CSV
    final rows = <List>[
      ['ID', 'Name', 'Email', 'Phone', 'Registration Date']
    ];
    
    for (var f in facultyList) {
      rows.add([
        f.id,
        f.name,
        f.email ?? '',
        f.phone ?? '',
        f.registrationDate?.toIso8601String() ?? '',
      ]);
    }

    final csv = const ListToCsvConverter().convert(rows);
    await file.writeAsString(csv);
  }

  Future<bool> deleteFaculty(String facultyId) async {
    final facultyList = await getAllFaculty();
    final updatedList = facultyList.where((f) => f.id != facultyId).toList();
    
    final file = File(path.join(_facultyDetailsDir!.path, 'FacultyDetails.csv'));
    final rows = <List>[
      ['ID', 'Name', 'Email', 'Phone', 'Registration Date']
    ];
    
    for (var f in updatedList) {
      rows.add([
        f.id,
        f.name,
        f.email ?? '',
        f.phone ?? '',
        f.registrationDate?.toIso8601String() ?? '',
      ]);
    }

    final csv = const ListToCsvConverter().convert(rows);
    await file.writeAsString(csv);
    
    // Delete training images
    final trainingDir = Directory(path.join(_trainingImageDir!.path, 'User.$facultyId'));
    if (await trainingDir.exists()) {
      await trainingDir.delete(recursive: true);
    }
    
    return true;
  }

  // Attendance Management
  Future<List<Attendance>> getAttendanceForDate(DateTime date) async {
    final dateStr = _formatDate(date);
    final file = File(path.join(_attendanceDir!.path, 'Attendance_$dateStr.csv'));
    
    if (!await file.exists()) {
      return [];
    }

    final content = await file.readAsString();
    final rows = const CsvToListConverter().convert(content);
    
    if (rows.isEmpty || rows.length < 2) {
      return [];
    }

    final attendanceList = <Attendance>[];
    for (int i = 1; i < rows.length; i++) {
      if (rows[i].length >= 4) {
        try {
          attendanceList.add(Attendance(
            id: rows[i][0].toString(),
            facultyId: rows[i][1].toString(),
            facultyName: rows[i][2].toString(),
            date: DateTime.parse(rows[i][3].toString()),
            time: rows[i].length > 4 ? DateTime.parse(rows[i][4].toString()) : DateTime.now(),
            status: rows[i].length > 5 ? rows[i][5].toString() : 'present',
          ));
        } catch (e) {
          // Skip invalid rows
        }
      }
    }
    return attendanceList;
  }

  Future<bool> markAttendance(Attendance attendance) async {
    // Check if already marked today
    final todayAttendance = await getAttendanceForDate(attendance.date);
    final alreadyMarked = todayAttendance.any((a) => 
      a.facultyId == attendance.facultyId && a.isSameDay(attendance.date)
    );
    
    if (alreadyMarked) {
      return false; // Already marked
    }

    final dateStr = _formatDate(attendance.date);
    final file = File(path.join(_attendanceDir!.path, 'Attendance_$dateStr.csv'));
    
    final rows = <List>[];
    
    // Check if file exists and read existing data
    if (await file.exists()) {
      final content = await file.readAsString();
      final existingRows = const CsvToListConverter().convert(content);
      rows.addAll(existingRows);
    } else {
      // Create header
      rows.add(['ID', 'Faculty ID', 'Faculty Name', 'Date', 'Time', 'Status']);
    }

    // Add new attendance
    rows.add([
      attendance.id,
      attendance.facultyId,
      attendance.facultyName,
      attendance.date.toIso8601String(),
      attendance.time.toIso8601String(),
      attendance.status ?? 'present',
    ]);

    final csv = const ListToCsvConverter().convert(rows);
    await file.writeAsString(csv);
    return true;
  }

  Future<List<Attendance>> getAllAttendance() async {
    final allAttendance = <Attendance>[];
    
    if (!await _attendanceDir!.exists()) {
      return allAttendance;
    }

    final files = _attendanceDir!.listSync();
    for (var file in files) {
      if (file is File && file.path.endsWith('.csv')) {
        final content = await file.readAsString();
        final rows = const CsvToListConverter().convert(content);
        
        for (int i = 1; i < rows.length; i++) {
          if (rows[i].length >= 4) {
            try {
              allAttendance.add(Attendance(
                id: rows[i][0].toString(),
                facultyId: rows[i][1].toString(),
                facultyName: rows[i][2].toString(),
                date: DateTime.parse(rows[i][3].toString()),
                time: rows[i].length > 4 ? DateTime.parse(rows[i][4].toString()) : DateTime.now(),
                status: rows[i].length > 5 ? rows[i][5].toString() : 'present',
              ));
            } catch (e) {
              // Skip invalid rows
            }
          }
        }
      }
    }
    
    return allAttendance;
  }

  // Training Images
  String getTrainingImagePath(String facultyId, int imageNumber) {
    return path.join(_trainingImageDir!.path, 'User.$facultyId', 'image_$imageNumber.jpg');
  }

  Future<void> saveTrainingImage(String facultyId, int imageNumber, List<int> imageData) async {
    final userDir = Directory(path.join(_trainingImageDir!.path, 'User.$facultyId'));
    await userDir.create(recursive: true);
    
    final file = File(getTrainingImagePath(facultyId, imageNumber));
    await file.writeAsBytes(imageData);
  }

  Future<List<String>> getTrainingImages(String facultyId) async {
    final userDir = Directory(path.join(_trainingImageDir!.path, 'User.$facultyId'));
    if (!await userDir.exists()) {
      return [];
    }
    
    final files = userDir.listSync()
        .whereType<File>()
        .where((f) => f.path.endsWith('.jpg'))
        .map((f) => f.path)
        .toList();
    
    files.sort();
    return files;
  }

  // Password Management
  Future<String?> getPassword() async {
    final file = File(path.join(_trainingImageLabelDir!.path, 'psd.txt'));
    if (await file.exists()) {
      return await file.readAsString();
    }
    return null;
  }

  Future<void> savePassword(String password) async {
    final file = File(path.join(_trainingImageLabelDir!.path, 'psd.txt'));
    await file.writeAsString(password);
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}-${date.month.toString().padLeft(2, '0')}-${date.year}';
  }

  // Get directory paths
  String get facultyDetailsPath => _facultyDetailsDir!.path;
  String get attendancePath => _attendanceDir!.path;
  String get trainingImagePath => _trainingImageDir!.path;
}

