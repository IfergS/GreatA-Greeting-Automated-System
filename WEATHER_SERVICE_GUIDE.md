# 🌤️ Weather Service Guide - GreetA System

## Overview

The weather service provides accurate, real-time weather information through voice commands. It uses free weather APIs that don't require API keys, making it ready to use immediately.

---

## ✨ Features

- ✅ **Real-time weather data** from free APIs
- ✅ **No API key required** (uses free wttr.in API)
- ✅ **City-specific queries** ("weather in Manila")
- ✅ **Default location** (saved in settings)
- ✅ **Caching** (10-minute cache to reduce API calls)
- ✅ **Error handling** with user-friendly messages
- ✅ **Multiple city support** (Philippine cities)

---

## 🎤 Voice Commands

### **Basic Weather Query:**
- "What's the weather?"
- "Weather"
- "Tell me the weather"

**Response:** Weather for your saved location (default: Manila)

### **City-Specific Query:**
- "Weather in Manila"
- "What's the weather in Quezon City?"
- "Weather in Cebu"
- "Tell me the weather in Davao"

**Response:** Weather for the specified city

### **Supported Cities:**
- Manila
- Quezon City
- Makati
- Cebu
- Davao
- Baguio
- Iloilo
- Cagayan
- Any city name (works with most cities worldwide)

---

## 📊 Weather Information Provided

The service provides:
- **Temperature** (in Celsius)
- **Weather description** (e.g., "partly cloudy", "sunny")
- **Humidity** (percentage)
- **Wind speed** (meters per second)

**Example Response:**
> "Current weather in Manila: 28.5 degrees Celsius, partly cloudy. Humidity is 75 percent, and wind speed is 3.2 meters per second."

---

## ⚙️ Settings Configuration

### **Set Default Weather Location:**

1. Open the app
2. Go to **Admin Panel**
3. Navigate to **Settings** tab
4. Tap **"Weather Location"**
5. Enter your city name (e.g., "Manila", "Quezon City")
6. Tap **"Save"**

The saved location will be used when you ask for weather without specifying a city.

---

## 🔧 Technical Details

### **APIs Used:**

1. **Primary (Optional):** OpenWeatherMap API
   - Requires free API key
   - More accurate data
   - To use: Get API key from https://openweathermap.org/api
   - Update `_apiKey` in `weather_service.dart`

2. **Fallback (Default):** wttr.in API
   - **No API key required**
   - Free and unlimited
   - Works immediately
   - Supports most cities worldwide

### **Caching:**
- Weather data is cached for **10 minutes**
- Reduces API calls
- Improves response time
- Cache is cleared when location changes

### **Error Handling:**
- Network timeout: 5 seconds
- Graceful fallback if API fails
- User-friendly error messages
- No crashes on API errors

---

## 📝 Code Structure

### **Files:**
- `lib/services/weather_service.dart` - Weather service implementation
- `lib/services/voice_service.dart` - Voice command handler (updated)
- `lib/screens/admin_panel_screen.dart` - Settings UI (updated)

### **Key Methods:**

```dart
// Get weather for a specific city
await weatherService.getWeatherByCity('Manila');

// Get weather for saved location
await weatherService.getWeatherByLocation();

// Set default location
await weatherService.setLocation('Manila');

// Get saved location
final location = await weatherService.getSavedLocation();
```

---

## 🚀 Usage Examples

### **Example 1: Basic Weather Query**
```
User: "What's the weather?"
System: "Current weather in Manila: 28.5 degrees Celsius, partly cloudy..."
```

### **Example 2: City-Specific Query**
```
User: "Weather in Cebu"
System: "Current weather in Cebu: 30.2 degrees Celsius, sunny..."
```

### **Example 3: Setting Location**
```
1. Admin Panel → Settings → Weather Location
2. Enter: "Quezon City"
3. Save
4. Now "What's the weather?" will show Quezon City weather
```

---

## 🔒 Privacy & Data

- **No personal data collected**
- **No location tracking**
- **City names only** (user-provided)
- **Data cached locally** (10 minutes)
- **No third-party tracking**

---

## 🐛 Troubleshooting

### **Issue: "Unable to fetch weather data"**

**Solutions:**
1. Check internet connection
2. Try again after a few seconds
3. Verify city name is correct
4. Try a different city name

### **Issue: Wrong city weather**

**Solutions:**
1. Be more specific (e.g., "Quezon City" instead of "Quezon")
2. Check spelling of city name
3. Set default location in settings

### **Issue: Slow response**

**Solutions:**
1. Wait for cache to update (10 minutes)
2. Check internet speed
3. API may be temporarily slow

---

## 📈 Future Enhancements

Potential improvements:
- [ ] GPS-based automatic location detection
- [ ] Weather forecasts (3-day, 7-day)
- [ ] Weather alerts and warnings
- [ ] Multiple location support
- [ ] Weather history
- [ ] Customizable units (Fahrenheit, etc.)

---

## ✅ Testing

### **Test Voice Commands:**
1. Open app
2. Click "🎤 Start Listening"
3. Say: "What's the weather?"
4. Should hear weather information

### **Test City-Specific:**
1. Say: "Weather in Manila"
2. Should get Manila weather

### **Test Settings:**
1. Admin Panel → Settings
2. Set weather location
3. Ask for weather (should use new location)

---

## 📚 API Documentation

### **wttr.in API:**
- URL: `https://wttr.in/{city}?format=j1`
- Format: JSON
- Free: Yes
- Rate Limit: None (reasonable use)

### **OpenWeatherMap API (Optional):**
- URL: `https://api.openweathermap.org/data/2.5/weather`
- Requires: API key (free tier available)
- Rate Limit: 60 calls/minute (free tier)
- More accurate: Yes

---

**Weather service is ready to use!** 🌤️

No setup required - it works immediately with the free API.

