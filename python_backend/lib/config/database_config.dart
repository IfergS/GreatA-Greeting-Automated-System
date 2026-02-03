class DatabaseConfig {
  // ============================================
  // XAMPP MySQL Database Configuration
  // ============================================
  // Configured for XAMPP MySQL (default settings)
  // ============================================
  
  // XAMPP MySQL Server Settings
  // IMPORTANT: For mobile devices (Android/iOS), use your computer's IP address instead of 'localhost'
  // Find your IP: Windows: ipconfig | findstr IPv4
  // Example: '192.168.1.10' (your computer's IP on local network)
  static const String host = '10.0.2.2'; // Android emulator uses 10.0.2.2 to access host machine's localhost
  static const int port = 3306; // XAMPP MySQL default port
  static const String database = 'greeta_attendance'; // Database name
  
  // For mobile devices, change to your computer's IP address:
  // Your computer's IP: 192.168.1.10 (found via: ipconfig | findstr IPv4)
  // static const String host = '192.168.1.10'; // Uncomment this for mobile devices
  
  // XAMPP MySQL Credentials (Default)
  // XAMPP MySQL default: username = 'root', password = '' (empty)
  static const String username = 'root'; // XAMPP default username
  static const String password = ''; // XAMPP default password (empty/blank)
  
  // ============================================
  // Connection Settings
  // ============================================
  static const int maxConnections = 5;
  static const int connectionTimeout = 30; // seconds
  
  // ============================================
  // XAMPP Setup Instructions:
  // ============================================
  // 1. Install XAMPP from: https://www.apachefriends.org/
  // 2. Start MySQL in XAMPP Control Panel
  // 3. Open phpMyAdmin: http://localhost/phpmyadmin
  // 4. Create database: greeta_attendance
  // 5. Run the app - tables will be created automatically
  // 
  // If you set a MySQL password in XAMPP, update 'password' above
  // For detailed setup, see: XAMPP_SETUP.md
  // ============================================
  
  // Get connection string for logging (without password)
  static String getConnectionInfo() {
    return 'mysql://$username@$host:$port/$database';
  }
  
  // Validate configuration
  static bool isValid() {
    return host.isNotEmpty && 
           database.isNotEmpty && 
           username.isNotEmpty;
  }
  
  // Check if password is set (warns if using default)
  static bool isPasswordSet() {
    return password.isNotEmpty;
  }
}

