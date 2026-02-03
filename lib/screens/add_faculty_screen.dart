import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';
import '../models/faculty.dart';
import '../services/storage_service.dart';
import '../services/face_recognition_service.dart';
import '../utils/app_theme.dart';

class AddFacultyScreen extends StatefulWidget {
  const AddFacultyScreen({super.key});

  @override
  State<AddFacultyScreen> createState() => _AddFacultyScreenState();
}

class _AddFacultyScreenState extends State<AddFacultyScreen> {
  final _formKey = GlobalKey<FormState>();
  final _idController = TextEditingController();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();
  
  final StorageService _storageService = StorageService();
  final FaceRecognitionService _faceService = FaceRecognitionService();
  final ImagePicker _imagePicker = ImagePicker();
  
  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isCameraInitialized = false;
  int _imagesCaptured = 0;
  static const int _requiredImages = 100;
  bool _isCapturing = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
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
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      print('Error initializing camera: $e');
    }
  }

  Future<void> _captureImage() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized) {
      return;
    }

    if (_isCapturing) return;
    _isCapturing = true;

    try {
      final image = await _cameraController!.takePicture();
      final imageFile = File(image.path);
      final imageBytes = await imageFile.readAsBytes();

      // Detect face
      final face = await _faceService.detectFaceInImage(imageFile);
      if (face == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('No face detected. Please try again.')),
          );
        }
        _isCapturing = false;
        return;
      }

      // Validate face quality
      final isValid = await _faceService.validateFaceQuality(imageBytes);
      if (!isValid) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Face quality is poor. Please try again.')),
          );
        }
        _isCapturing = false;
        return;
      }

      // Save training image
      final facultyId = _idController.text.trim();
      if (facultyId.isNotEmpty) {
        await _faceService.addTrainingImage(facultyId, imageBytes);
        await _storageService.saveTrainingImage(facultyId, _imagesCaptured + 1, imageBytes);
        
        setState(() {
          _imagesCaptured++;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Image $_imagesCaptured/$_requiredImages captured')),
          );
        }
      }
    } catch (e) {
      print('Error capturing image: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      _isCapturing = false;
    }
  }

  Future<void> _saveFaculty() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_imagesCaptured < _requiredImages) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please capture $_requiredImages images. Currently: $_imagesCaptured')),
      );
      return;
    }

    try {
      final faculty = Faculty(
        id: _idController.text.trim(),
        name: _nameController.text.trim(),
        email: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
        phone: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
        registrationDate: DateTime.now(),
      );

      await _storageService.saveFaculty(faculty);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Faculty added successfully!')),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving faculty: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('➕ Add Faculty'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Form Fields
              TextFormField(
                controller: _idController,
                decoration: const InputDecoration(
                  labelText: 'Faculty ID *',
                  hintText: 'Enter faculty ID',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter faculty ID';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Faculty Name *',
                  hintText: 'Enter faculty name',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter faculty name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: 'Email (Optional)',
                  hintText: 'Enter email address',
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 20),
              
              TextFormField(
                controller: _phoneController,
                decoration: const InputDecoration(
                  labelText: 'Phone (Optional)',
                  hintText: 'Enter phone number',
                ),
                keyboardType: TextInputType.phone,
              ),
              
              const SizedBox(height: 30),
              
              // Camera Section
              if (_isCameraInitialized && _cameraController != null) ...[
                const Text(
                  'Capture Training Images',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 10),
                
                Container(
                  height: 300,
                  decoration: BoxDecoration(
                    color: AppTheme.secondaryColor,
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(color: AppTheme.accentColor, width: 2),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(15),
                    child: CameraPreview(_cameraController!),
                  ),
                ),
                const SizedBox(height: 15),
                
                // Progress
                Text(
                  'Images Captured: $_imagesCaptured/$_requiredImages',
                  style: const TextStyle(
                    fontSize: 16,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const SizedBox(height: 10),
                
                LinearProgressIndicator(
                  value: _imagesCaptured / _requiredImages,
                  backgroundColor: AppTheme.secondaryColor,
                  valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.accentColor),
                ),
                const SizedBox(height: 15),
                
                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton.icon(
                    onPressed: _isCapturing ? null : _captureImage,
                    icon: const Icon(Icons.camera_alt),
                    label: Text(_isCapturing ? 'Capturing...' : 'Capture Image'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.accentColor,
                    ),
                  ),
                ),
              ] else ...[
                const Center(
                  child: CircularProgressIndicator(),
                ),
              ],
              
              const SizedBox(height: 30),
              
              // Save Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _saveFaculty,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentColor,
                  ),
                  child: const Text(
                    'Save Faculty',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _idController.dispose();
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _cameraController?.dispose();
    super.dispose();
  }
}

