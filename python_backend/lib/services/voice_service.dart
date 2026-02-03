import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:intl/intl.dart';
import 'weather_service.dart';

class VoiceService {
  static final VoiceService _instance = VoiceService._internal();
  factory VoiceService() => _instance;
  VoiceService._internal();

  final FlutterTts _tts = FlutterTts();
  final stt.SpeechToText _stt = stt.SpeechToText();
  final WeatherService _weatherService = WeatherService();
  
  bool _isInitialized = false;
  bool _isListening = false;

  Future<void> initialize() async {
    if (_isInitialized) return;

    // Configure TTS
    await _tts.setLanguage("en-US");
    await _tts.setSpeechRate(0.8); // Slightly slower than Python's 200 WPM
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);

    // Get available voices and try to find American English
    final voices = await _tts.getVoices;
    if (voices != null) {
      final usVoice = voices.firstWhere(
        (voice) => voice['locale']?.toString().contains('en-US') ?? false,
        orElse: () => voices.first,
      );
      if (usVoice['locale'] != null) {
        await _tts.setLanguage(usVoice['locale']);
      }
    }

    _isInitialized = true;
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) {
      await initialize();
    }
    
    try {
      print('🔊 Speaking: $text');
      await _tts.speak(text);
    } catch (e) {
      print('Voice error: $e');
    }
  }

  Future<void> stop() async {
    await _tts.stop();
  }

  String getTimeBasedGreeting() {
    final hour = DateTime.now().hour;
    if (hour >= 5 && hour < 12) {
      return 'Good morning';
    } else if (hour >= 12 && hour < 14) {
      return 'Good noon';
    } else if (hour >= 14 && hour < 17) {
      return 'Good afternoon';
    } else if (hour >= 17 && hour < 21) {
      return 'Good evening';
    } else {
      return 'Hello';
    }
  }

  String getGreetingMessage(String name) {
    final timeGreeting = getTimeBasedGreeting();
    return 'Hi $name, $timeGreeting, Welcome to Faculty Office';
  }

  Future<bool> isListeningAvailable() async {
    return await _stt.initialize();
  }

  Future<String?> listen({Duration timeout = const Duration(seconds: 10)}) async {
    if (!await isListeningAvailable()) {
      return 'error';
    }

    if (_isListening) {
      return null;
    }

    _isListening = true;
    String? result;

    try {
      await _stt.listen(
        onResult: (val) {
          if (val.finalResult) {
            result = val.recognizedWords.toLowerCase();
            _stt.stop();
          }
        },
        listenFor: timeout,
        pauseFor: const Duration(seconds: 3),
      );

      // Wait for result or timeout
      final startTime = DateTime.now();
      while (result == null && DateTime.now().difference(startTime) < timeout) {
        await Future.delayed(const Duration(milliseconds: 100));
      }

      if (result == null) {
        result = 'timeout';
      }
    } catch (e) {
      print('Listening error: $e');
      result = 'error';
    } finally {
      _isListening = false;
      await _stt.stop();
    }

    return result;
  }

  Future<String> handleCommand(String command) async {
    command = command.toLowerCase().trim();

    if (command.contains('hello') || command.contains('hi')) {
      return 'Hello! How can I help you?';
    } else if (command.contains('time')) {
      final now = DateTime.now();
      final timeStr = DateFormat('hh:mm a').format(now);
      return 'The current time is $timeStr';
    } else if (command.contains('date')) {
      final now = DateTime.now();
      final dateStr = DateFormat('EEEE, MMMM d, yyyy').format(now);
      return 'Today is $dateStr';
    } else if (command.contains('weather')) {
      // Extract city name if mentioned, otherwise use saved location
      String? city;
      final cityPatterns = [
        'in manila', 'in quezon city', 'in makati', 'in cebu',
        'in davao', 'in baguio', 'in iloilo', 'in cagayan',
      ];
      
      for (var pattern in cityPatterns) {
        if (command.contains(pattern)) {
          city = pattern.replaceAll('in ', '').trim();
          break;
        }
      }
      
      // If no city mentioned, try to get from command or use saved location
      if (city == null) {
        // Try to extract city name from command
        final words = command.split(' ');
        final inIndex = words.indexWhere((w) => w == 'in');
        if (inIndex != -1 && inIndex < words.length - 1) {
          city = words.sublist(inIndex + 1).join(' ');
        }
      }
      
      if (city != null && city.isNotEmpty) {
        return await _weatherService.getWeatherByCity(city);
      } else {
        return await _weatherService.getWeatherByLocation();
      }
    } else if (command.contains('attendance') || command.contains('mark')) {
      return 'Please use face recognition to mark your attendance.';
    } else {
      return 'I did not understand that command. Please try again.';
    }
  }

  void dispose() {
    _tts.stop();
    _stt.stop();
  }
}

