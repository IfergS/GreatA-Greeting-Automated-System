import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class WeatherService {
  static final WeatherService _instance = WeatherService._internal();
  factory WeatherService() => _instance;
  WeatherService._internal();

  // Using OpenWeatherMap API (free tier)
  // You can get a free API key from https://openweathermap.org/api
  static const String _apiKey = 'YOUR_API_KEY_HERE'; // Replace with your API key
  static const String _baseUrl = 'https://api.openweathermap.org/data/2.5';
  
  // Fallback to a free weather API that doesn't require key
  static const String _freeApiUrl = 'https://wttr.in';

  // Cache weather data for 10 minutes
  Map<String, dynamic>? _cachedWeather;
  DateTime? _cacheTime;
  static const Duration _cacheDuration = Duration(minutes: 10);

  Future<String> getWeatherByCity(String city) async {
    try {
      // Check cache first
      if (_cachedWeather != null && 
          _cacheTime != null && 
          DateTime.now().difference(_cacheTime!) < _cacheDuration &&
          _cachedWeather!['city'] == city) {
        return _formatWeatherResponse(_cachedWeather!);
      }

      // Try OpenWeatherMap first if API key is set
      if (_apiKey != 'YOUR_API_KEY_HERE' && _apiKey.isNotEmpty) {
        try {
          final response = await http.get(
            Uri.parse(
              '$_baseUrl/weather?q=$city&appid=$_apiKey&units=metric',
            ),
          ).timeout(const Duration(seconds: 5));

          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            _cachedWeather = {
              'city': city,
              'temperature': data['main']['temp'],
              'description': data['weather'][0]['description'],
              'humidity': data['main']['humidity'],
              'windSpeed': data['wind']['speed'],
            };
            _cacheTime = DateTime.now();
            return _formatWeatherResponse(_cachedWeather!);
          }
        } catch (e) {
          print('OpenWeatherMap API error: $e');
        }
      }

      // Fallback to free API (wttr.in)
      try {
        final response = await http.get(
          Uri.parse('$_freeApiUrl/$city?format=j1'),
        ).timeout(const Duration(seconds: 5));

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          final current = data['current_condition'][0];
          
          _cachedWeather = {
            'city': city,
            'temperature': double.parse(current['temp_C']),
            'description': current['weatherDesc'][0]['value'],
            'humidity': int.parse(current['humidity']),
            'windSpeed': double.parse(current['windspeedKmph']) / 3.6, // Convert to m/s
          };
          _cacheTime = DateTime.now();
          return _formatWeatherResponse(_cachedWeather!);
        }
      } catch (e) {
        print('Free weather API error: $e');
      }

      // If all APIs fail, return a helpful message
      return 'Unable to fetch weather data. Please check your internet connection or try again later.';
    } catch (e) {
      print('Weather service error: $e');
      return 'Sorry, I encountered an error while fetching weather information.';
    }
  }

  Future<String> getWeatherByLocation() async {
    try {
      // Get saved location from preferences
      final prefs = await SharedPreferences.getInstance();
      final savedCity = prefs.getString('weather_city');
      
      if (savedCity != null && savedCity.isNotEmpty) {
        return await getWeatherByCity(savedCity);
      }

      // Default to a common city if no location is set
      return await getWeatherByCity('Manila');
    } catch (e) {
      return 'Unable to fetch weather data. Please set your location in settings.';
    }
  }

  Future<void> setLocation(String city) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('weather_city', city);
    // Clear cache when location changes
    _cachedWeather = null;
    _cacheTime = null;
  }

  Future<String?> getSavedLocation() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('weather_city');
  }

  String _formatWeatherResponse(Map<String, dynamic> weather) {
    final temp = weather['temperature']?.toStringAsFixed(1) ?? 'N/A';
    final desc = weather['description'] ?? 'unknown';
    final humidity = weather['humidity']?.toString() ?? 'N/A';
    final windSpeed = weather['windSpeed']?.toStringAsFixed(1) ?? 'N/A';
    final city = weather['city'] ?? 'your location';

    return 'Current weather in $city: $temp degrees Celsius, $desc. '
           'Humidity is $humidity percent, and wind speed is $windSpeed meters per second.';
  }

  // Get a simple weather description
  String getSimpleWeatherDescription(Map<String, dynamic> weather) {
    final temp = weather['temperature']?.toStringAsFixed(1) ?? 'N/A';
    final desc = weather['description'] ?? 'unknown';
    return 'It is $temp degrees Celsius and $desc.';
  }
}

