# Weather Configuration Guide

The voice assistant now uses real weather APIs to provide accurate weather information.

## Quick Setup (No API Key Required)

The system uses **wttr.in** by default, which is free and doesn't require an API key.

### To Set Your City:

1. Create a file named `weather_config.txt` in the project root directory
2. Enter your city name (e.g., "New York", "Tokyo", "Paris")
3. Save the file

**Example:**
```
New York
```

Or set an environment variable:
```bash
set WEATHER_CITY=New York
```

## Advanced Setup (Optional - More Accurate)

For more detailed weather information, you can use OpenWeatherMap API:

1. Get a free API key from: https://openweathermap.org/api
2. Set the environment variable:
   ```bash
   set OPENWEATHER_API_KEY=your_api_key_here
   ```

The system will automatically use OpenWeatherMap if an API key is configured, otherwise it will use wttr.in.

## Default City

If no city is configured, the system defaults to "London".

