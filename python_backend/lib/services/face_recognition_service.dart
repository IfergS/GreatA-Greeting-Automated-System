import 'dart:io';
import 'dart:typed_data';
import 'dart:ui';
import 'package:camera/camera.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:image/image.dart' as img;
import '../models/faculty.dart';
import '../services/storage_service.dart';

class FaceRecognitionService {
  static final FaceRecognitionService _instance = FaceRecognitionService._internal();
  factory FaceRecognitionService() => _instance;
  FaceRecognitionService._internal();

  final FaceDetector _faceDetector = FaceDetector(
    options: FaceDetectorOptions(
      enableClassification: true,
      enableLandmarks: true,
      enableTracking: true,
      minFaceSize: 0.1,
    ),
  );

  final StorageService _storage = StorageService();
  
  // Simple face recognition using LBPH-like approach
  // In production, you'd use TensorFlow Lite models
  Map<String, List<Uint8List>> _faceEmbeddings = {};

  Future<void> initialize() async {
    // Load existing face data
    await _loadFaceData();
  }

  Future<void> _loadFaceData() async {
    final facultyList = await _storage.getAllFaculty();
    for (var faculty in facultyList) {
      final images = await _storage.getTrainingImages(faculty.id);
      _faceEmbeddings[faculty.id] = [];
      
      for (var imagePath in images) {
        final file = File(imagePath);
        if (await file.exists()) {
          final bytes = await file.readAsBytes();
          _faceEmbeddings[faculty.id]!.add(bytes);
        }
      }
    }
  }

  Future<List<Face>> detectFaces(CameraImage cameraImage) async {
    try {
      final inputImage = _cameraImageToInputImage(cameraImage);
      if (inputImage == null) return [];
      
      return await _faceDetector.processImage(inputImage);
    } catch (e) {
      print('Face detection error: $e');
      return [];
    }
  }

  InputImage? _cameraImageToInputImage(CameraImage cameraImage) {
    try {
      final imageRotation = InputImageRotation.rotation0deg;
      final format = InputImageFormat.nv21;

      return InputImage.fromBytes(
        bytes: _concatenatePlanes(cameraImage.planes),
        metadata: InputImageMetadata(
          size: Size(cameraImage.width.toDouble(), cameraImage.height.toDouble()),
          rotation: imageRotation,
          format: format,
          bytesPerRow: cameraImage.planes[0].bytesPerRow,
        ),
      );
    } catch (e) {
      print('Error converting camera image: $e');
      return null;
    }
  }

  Uint8List _concatenatePlanes(List<Plane> planes) {
    final allBytes = <int>[];
    for (final plane in planes) {
      allBytes.addAll(plane.bytes);
    }
    return Uint8List.fromList(allBytes);
  }

  Future<Face?> detectFaceInImage(File imageFile) async {
    try {
      final inputImage = InputImage.fromFile(imageFile);
      final faces = await _faceDetector.processImage(inputImage);
      return faces.isNotEmpty ? faces.first : null;
    } catch (e) {
      print('Face detection error: $e');
      return null;
    }
  }

  Future<String?> recognizeFace(Uint8List faceImageBytes) async {
    // Simplified recognition - in production, use TensorFlow Lite
    // This is a placeholder that compares image similarity
    
    double bestMatch = 0.0;
    String? matchedFacultyId;

    for (var entry in _faceEmbeddings.entries) {
      for (var storedImage in entry.value) {
        final similarity = _compareImages(faceImageBytes, storedImage);
        if (similarity > bestMatch && similarity > 0.7) {
          bestMatch = similarity;
          matchedFacultyId = entry.key;
        }
      }
    }

    return matchedFacultyId;
  }

  double _compareImages(Uint8List img1, Uint8List img2) {
    // Simple image comparison using histogram
    // In production, use proper face embedding comparison
    try {
      final image1 = img.decodeImage(img1);
      final image2 = img.decodeImage(img2);
      
      if (image1 == null || image2 == null) return 0.0;

      // Resize to same size for comparison
      final resized1 = img.copyResize(image1, width: 100, height: 100);
      final resized2 = img.copyResize(image2, width: 100, height: 100);

      // Calculate histogram similarity
      double similarity = 0.0;
      for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 100; j++) {
          final pixel1 = resized1.getPixel(i, j);
          final pixel2 = resized2.getPixel(i, j);
          
          final r1 = pixel1.r;
          final g1 = pixel1.g;
          final b1 = pixel1.b;
          
          final r2 = pixel2.r;
          final g2 = pixel2.g;
          final b2 = pixel2.b;
          
          final diff = (r1 - r2).abs() + (g1 - g2).abs() + (b1 - b2).abs();
          similarity += 1.0 - (diff / 765.0); // 765 = max diff (255*3)
        }
      }
      
      return similarity / (100 * 100);
    } catch (e) {
      print('Image comparison error: $e');
      return 0.0;
    }
  }

  Future<bool> validateFaceQuality(Uint8List faceImageBytes) async {
    try {
      final image = img.decodeImage(faceImageBytes);
      if (image == null) return false;

      // Check minimum size
      if (image.width < 50 || image.height < 50) return false;

      // Check aspect ratio
      final aspectRatio = image.width / image.height;
      if (aspectRatio < 0.7 || aspectRatio > 1.4) return false;

      // Check brightness
      double totalBrightness = 0.0;
      int pixelCount = 0;
      
      for (int i = 0; i < image.width; i++) {
        for (int j = 0; j < image.height; j++) {
          final pixel = image.getPixel(i, j);
          final r = pixel.r;
          final g = pixel.g;
          final b = pixel.b;
          totalBrightness += (r + g + b) / 3.0;
          pixelCount++;
        }
      }
      
      final meanBrightness = totalBrightness / pixelCount;
      if (meanBrightness < 50 || meanBrightness > 200) return false;

      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> addTrainingImage(String facultyId, Uint8List imageBytes) async {
    if (!_faceEmbeddings.containsKey(facultyId)) {
      _faceEmbeddings[facultyId] = [];
    }
    
    final imageCount = _faceEmbeddings[facultyId]!.length;
    await _storage.saveTrainingImage(facultyId, imageCount + 1, imageBytes);
    _faceEmbeddings[facultyId]!.add(imageBytes);
  }

  void dispose() {
    _faceDetector.close();
  }
}

