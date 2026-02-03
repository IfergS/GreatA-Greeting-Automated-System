import 'dart:typed_data';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:uuid/uuid.dart';
import '../models/attendance.dart';
import '../models/faculty.dart';
import '../services/face_recognition_service.dart';
import '../services/storage_service.dart';
import '../services/voice_service.dart';
import '../utils/app_theme.dart';

class AttendanceScreen extends StatefulWidget {
  const AttendanceScreen({super.key});

  @override
  State<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends State<AttendanceScreen> {
  CameraController? _cameraController;
  final FaceRecognitionService _faceService = FaceRecognitionService();
  final StorageService _storageService = StorageService();
  final VoiceService _voiceService = VoiceService();
  
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  bool _isProcessing = false;
  String _statusMessage = 'Position your face in front of the camera';
  String? _detectedName;
  bool _attendanceMarked = false;
  Set<String> _markedToday = {};

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _loadMarkedAttendance();
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
        setState(() {
          _statusMessage = 'No camera available';
        });
        return;
      }

      _cameraController = CameraController(
        _cameras![0],
        ResolutionPreset.medium,
        enableAudio: false,
      );

      await _cameraController!.initialize();
      await _faceService.initialize();
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
        _startFaceDetection();
      }
    } catch (e) {
      setState(() {
        _statusMessage = 'Error initializing camera: $e';
      });
    }
  }

  Future<void> _loadMarkedAttendance() async {
    final today = DateTime.now();
    final todayAttendance = await _storageService.getAttendanceForDate(today);
    _markedToday = todayAttendance.map((a) => a.facultyId).toSet();
  }

  Future<void> _startFaceDetection() async {
    if (!_isInitialized || _cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    if (_isProcessing) return;
    _isProcessing = true;

    try {
      final image = await _cameraController!.takePicture();
      if (!mounted) return;

      // Process the image
      await _processImage(image.path);
    } catch (e) {
      print('Error taking picture: $e');
    } finally {
      _isProcessing = false;
      
      // Continue detection after a delay
      if (mounted && _isInitialized) {
        Future.delayed(const Duration(milliseconds: 500), () {
          _startFaceDetection();
        });
      }
    }
  }

  Future<void> _processImage(String imagePath) async {
    try {
      // Detect faces
      final imageFile = File(imagePath);
      final faces = await _faceService.detectFaceInImage(imageFile);
      
      if (faces == null) {
        if (mounted) {
          setState(() {
            _statusMessage = 'No face detected. Please position your face in front of the camera';
            _detectedName = null;
          });
        }
        return;
      }

      // Read image bytes for recognition
      final imageBytes = await imageFile.readAsBytes();
      
      // Recognize face
      final facultyId = await _faceService.recognizeFace(imageBytes);
      
      if (facultyId == null) {
        if (mounted) {
          setState(() {
            _statusMessage = 'Face not recognized. Please register in admin panel.';
            _detectedName = null;
          });
        }
        return;
      }

      // Get faculty details
      final facultyList = await _storageService.getAllFaculty();
      final faculty = facultyList.firstWhere(
        (f) => f.id == facultyId,
        orElse: () => Faculty(id: facultyId, name: 'Unknown'),
      );

      if (mounted) {
        setState(() {
          _detectedName = faculty.name;
        });
      }

      // Check if already marked today
      if (_markedToday.contains(facultyId)) {
        if (mounted) {
          setState(() {
            _statusMessage = 'Already Recorded';
            _attendanceMarked = true;
          });
        }
        await _voiceService.speak('Hi $faculty.name, you have already marked your attendance today');
        return;
      }

      // Mark attendance
      final attendance = Attendance(
        id: const Uuid().v4(),
        facultyId: facultyId,
        facultyName: faculty.name,
        date: DateTime.now(),
        time: DateTime.now(),
        status: 'present',
      );

      final success = await _storageService.markAttendance(attendance);
      
      if (success) {
        _markedToday.add(facultyId);
        if (mounted) {
          setState(() {
            _statusMessage = '${faculty.name} - Recorded';
            _attendanceMarked = true;
          });
        }
        
        // Voice greeting
        final greeting = _voiceService.getGreetingMessage(faculty.name);
        await _voiceService.speak(greeting);
      } else {
        if (mounted) {
          setState(() {
            _statusMessage = 'Error marking attendance';
          });
        }
      }
    } catch (e) {
      print('Error processing image: $e');
      if (mounted) {
        setState(() {
          _statusMessage = 'Error: $e';
        });
      }
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _faceService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🎓 Faculty Attendance Recognition'),
      ),
      body: _isInitialized && _cameraController != null
          ? Stack(
              children: [
                // Camera Preview
                SizedBox(
                  width: double.infinity,
                  height: double.infinity,
                  child: CameraPreview(_cameraController!),
                ),
                
                // Overlay
                Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        Colors.black.withOpacity(0.7),
                        Colors.transparent,
                        Colors.transparent,
                        Colors.black.withOpacity(0.7),
                      ],
                    ),
                  ),
                ),

                // Status Information
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppTheme.secondaryColor.withOpacity(0.95),
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.circular(20),
                        topRight: Radius.circular(20),
                      ),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (_detectedName != null) ...[
                          Text(
                            _detectedName!,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.accentColor,
                            ),
                          ),
                          const SizedBox(height: 8),
                        ],
                        Text(
                          _statusMessage,
                          style: TextStyle(
                            fontSize: 16,
                            color: _attendanceMarked ? Colors.green : AppTheme.textPrimary,
                            fontWeight: _attendanceMarked ? FontWeight.bold : FontWeight.normal,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton(
                          onPressed: () => Navigator.pop(context),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.accentColor,
                            padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 12),
                          ),
                          child: const Text('Close'),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            )
          : Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircularProgressIndicator(),
                  const SizedBox(height: 20),
                  Text(
                    _statusMessage,
                    style: const TextStyle(color: AppTheme.textPrimary),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
    );
  }
}

