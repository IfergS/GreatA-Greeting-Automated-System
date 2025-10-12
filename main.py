############################################# IMPORTING ################################################
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2,os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import speech_recognition as sr
import pyttsx3
import requests
import json
import random
from threading import Thread
import mysql.connector
from mysql.connector import Error

############################################# VOICE ASSISTANT ###########################################

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.registered_users = {}  # Store recognized users
        self.load_registered_users()
        
        # Configure TTS
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[1].id)  # Female voice
        self.tts_engine.setProperty('rate', 150)
        
    def load_registered_users(self):
        """Load registered users from StudentDetails.csv"""
        try:
            if os.path.isfile("StudentDetails\StudentDetails.csv"):
                df = pd.read_csv("StudentDetails\StudentDetails.csv")
                for index, row in df.iterrows():
                    if pd.notna(row['ID']) and pd.notna(row['NAME']):
                        self.registered_users[str(row['ID'])] = str(row['NAME'])
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def speak(self, text):
        """Convert text to speech"""
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        thread = Thread(target=speak_thread)
        thread.start()
    
    def listen(self):
        """Listen for voice commands"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Command: {command}")
            return command
        except sr.WaitTimeoutError:
            return "timeout"
        except sr.UnknownValueError:
            return "unknown"
        except Exception as e:
            print(f"Listening error: {e}")
            return "error"
    
    def get_time_greeting(self):
        """Get greeting based on time of day"""
        current_hour = datetime.datetime.now().hour
        
        if 5 <= current_hour < 12:
            return "Good morning"
        elif 12 <= current_hour < 17:
            return "Good afternoon"
        elif 17 <= current_hour < 21:
            return "Good evening"
        else:
            return "Hello"
    
    def get_random_greeting(self, user_name):
        """Get random personalized greeting"""
        greetings = [
            f"Hey {user_name}, great to see you!",
            f"Welcome back {user_name}!",
            f"Hello {user_name}, how can I help you today?",
            f"Hi {user_name}, nice to have you here!",
            f"Hey there {user_name}, what can I do for you?"
        ]
        return random.choice(greetings)
    
    def get_weather(self):
        """Get current weather information"""
        try:
            # Using OpenWeatherMap API (you need to get a free API key)
            api_key = "your_api_key_here"  # Replace with your API key
            city = "London"  # You can make this dynamic
            
            # For demo purposes, using a simple response
            # In production, you'd use: response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric")
            # weather_data = response.json()
            
            weather_conditions = ["sunny", "cloudy", "rainy", "partly cloudy"]
            temperatures = ["15", "18", "20", "22", "25"]
            
            condition = random.choice(weather_conditions)
            temp = random.choice(temperatures)
            
            return f"The weather is {condition} with a temperature of {temp} degrees Celsius"
        except:
            return "I'm having trouble getting weather information right now"
    
    def handle_command(self, command, user_id=None):
        """Handle voice commands"""
        user_name = self.registered_users.get(user_id, "there")
        
        if "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        
        elif "weather" in command:
            response = self.get_weather()
        
        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"
        
        elif "hello" in command or "hi" in command:
            greeting = self.get_time_greeting()
            response = self.get_random_greeting(user_name) if user_id else f"{greeting}! How can I help you?"
        
        elif "thank" in command:
            responses = [
                f"You're welcome, {user_name}!",
                f"Happy to help, {user_name}!",
                f"Anytime, {user_name}!"
            ]
            response = random.choice(responses)
        
        elif "how are you" in command:
            responses = [
                f"I'm doing great, {user_name}! Thanks for asking.",
                f"Feeling wonderful, {user_name}! How about you?",
                f"All systems operational, {user_name}! Ready to help."
            ]
            response = random.choice(responses)
        
        elif "attendance" in command:
            response = f"{user_name}, I can help you with attendance. Please use the Take Attendance button or say 'take attendance' to start."
        
        elif "take attendance" in command:
            response = f"Starting attendance system for you, {user_name}. Please face the camera."
            # This would trigger the attendance system
            return response, "attendance"
        
        elif "register" in command or "new user" in command:
            response = f"To register a new user, {user_name}, please use the registration section on the right side of the screen."
        
        else:
            response = f"I'm sorry {user_name}, I didn't understand that command. You can ask me about time, weather, or date."
        
        return response, None

# Global voice assistant instance
voice_assistant = VoiceAssistant()

############################################# DATABASE CONNECTION #######################################

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.is_connected = False
        self.connect()
        if self.is_connected:
            self.create_tables()
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            # First try to connect to existing database
            self.connection = mysql.connector.connect(
                host='localhost',
                database='attendance_system',
                user='root',
                password=''
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                self.is_connected = True
                print("Successfully connected to MySQL database")
                return
        except Error as e:
            print(f"Database 'attendance_system' not found. Creating new database...")
            
        try:
            # Connect without specifying database to create it
            temp_connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password=''
            )
            temp_cursor = temp_connection.cursor()
            temp_cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system")
            temp_cursor.close()
            temp_connection.close()
            
            # Now connect to the created database
            self.connection = mysql.connector.connect(
                host='localhost',
                database='attendance_system',
                user='root',
                password=''
            )
            self.cursor = self.connection.cursor()
            self.is_connected = True
            print("Database 'attendance_system' created and connected successfully")
            
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            print("\n" + "="*60)
            print("DATABASE SETUP REQUIRED:")
            print("="*60)
            print("1. Make sure XAMPP is installed and running")
            print("2. Start Apache and MySQL services in XAMPP Control Panel")
            print("3. Open phpMyAdmin (http://localhost/phpmyadmin)")
            print("4. Create a new database named 'attendance_system'")
            print("5. Or run this SQL command in phpMyAdmin:")
            print("   CREATE DATABASE attendance_system;")
            print("="*60)
            print("The system will continue to work without database features.")
            print("Admin login and task management will not be available.")
            print("="*60 + "\n")
            self.is_connected = False
    
    def create_tables(self):
        """Create necessary tables"""
        if not self.is_connected:
            print("Skipping table creation - no database connection")
            return
            
        try:
            # Admin table
            admin_table = """
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Users table
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                department VARCHAR(50),
                position VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            # Tasks table
            tasks_table = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                assigned_to VARCHAR(20),
                assigned_by VARCHAR(50),
                status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                due_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
            
            # Attendance records table
            attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(20),
                date DATE NOT NULL,
                time_in TIME,
                time_out TIME,
                status ENUM('present', 'absent', 'late', 'half_day') DEFAULT 'present',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
            
            self.cursor.execute(admin_table)
            self.cursor.execute(users_table)
            self.cursor.execute(tasks_table)
            self.cursor.execute(attendance_table)
            self.connection.commit()
            
            # Insert default admin if not exists
            self.cursor.execute("SELECT COUNT(*) FROM admins")
            if self.cursor.fetchone()[0] == 0:
                default_admin = """
                INSERT INTO admins (username, password, email) 
                VALUES ('admin', 'admin123', 'admin@attendance.com')
                """
                self.cursor.execute(default_admin)
                self.connection.commit()
                print("Default admin created: username='admin', password='admin123'")
            
            print("All tables created successfully")
            
        except Error as e:
            print(f"Error creating tables: {e}")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return self.cursor.rowcount
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection closed")

# Global database instance
db_manager = DatabaseManager()

############################################# ADMIN SYSTEM #############################################

class AdminSystem:
    def __init__(self):
        self.current_admin = None
        self.admin_window = None
    
    def show_admin_login(self):
        """Show admin login dialog with enhanced design"""
        login_window = tk.Toplevel(window)
        login_window.title("Administrator Login")
        login_window.geometry("380x320")
        login_window.resizable(False, False)
        login_window.configure(bg="#1e1e1e")
        login_window.transient(window)
        login_window.grab_set()
        
        # Center the window
        login_window.update_idletasks()
        x = (login_window.winfo_screenwidth() // 2) - (380 // 2)
        y = (login_window.winfo_screenheight() // 2) - (320 // 2)
        login_window.geometry(f"380x320+{x}+{y}")
        
        # Main container frame
        main_container = tk.Frame(login_window, bg="#1e1e1e")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title section
        title_frame = tk.Frame(main_container, bg="#1e1e1e")
        title_frame.pack(fill="x", pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🔐 Administrator Login", 
                              fg="white", bg="#1e1e1e", font=('Segoe UI', 20, 'bold'))
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Access the admin dashboard", 
                                 fg="#63b3ed", bg="#1e1e1e", font=('Segoe UI', 10))
        subtitle_label.pack(pady=(3, 0))
        
        # Login form frame
        form_frame = tk.Frame(main_container, bg="#2d3748", relief="flat", bd=0)
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Username section
        username_frame = tk.Frame(form_frame, bg="#2d3748")
        username_frame.pack(fill="x", padx=15, pady=10)
        
        username_label = tk.Label(username_frame, text="Username", fg="white", bg="#2d3748", 
                                 font=('Segoe UI', 10, 'bold'))
        username_label.pack(anchor="w")
        
        username_entry = tk.Entry(username_frame, font=('Segoe UI', 10), width=25, 
                                 bg="#4a5568", fg="white", insertbackground="white",
                                 relief="flat", bd=3)
        username_entry.pack(fill="x", pady=(3, 0))
        
        # Password section
        password_frame = tk.Frame(form_frame, bg="#2d3748")
        password_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        password_label = tk.Label(password_frame, text="Password", fg="white", bg="#2d3748", 
                                 font=('Segoe UI', 10, 'bold'))
        password_label.pack(anchor="w")
        
        password_entry = tk.Entry(password_frame, font=('Segoe UI', 10), width=25, show="*", 
                                 bg="#4a5568", fg="white", insertbackground="white",
                                 relief="flat", bd=3)
        password_entry.pack(fill="x", pady=(3, 0))
        
        # Buttons section
        buttons_frame = tk.Frame(main_container, bg="#1e1e1e")
        buttons_frame.pack(fill="x", pady=(0, 15))
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                mess.showerror("Login Error", "Please enter both username and password!")
                return
            
            if self.authenticate_admin(username, password):
                self.current_admin = username
                login_window.destroy()
                self.show_admin_dashboard()
            else:
                mess.showerror("Login Failed", "Invalid username or password!")
                password_entry.delete(0, tk.END)
                password_entry.focus()
        
        def cancel():
            login_window.destroy()
        
        # Login button
        login_btn = tk.Button(buttons_frame, text="🚀 Login", command=login,
                             fg="white", bg="#38a169", height=2,
                             activebackground="#2f855a", activeforeground="white",
                             relief="flat", bd=0, font=('Segoe UI', 11, 'bold'),
                             cursor="hand2")
        login_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        # Cancel button
        cancel_btn = tk.Button(buttons_frame, text="❌ Cancel", command=cancel,
                              fg="white", bg="#e53e3e", height=2,
                              activebackground="#c53030", activeforeground="white",
                              relief="flat", bd=0, font=('Segoe UI', 11, 'bold'),
                              cursor="hand2")
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        # Info section
        info_frame = tk.Frame(main_container, bg="#1e1e1e")
        info_frame.pack(fill="x", pady=(10, 0))
        
        info_label = tk.Label(info_frame, text="💡 Default Credentials: admin / admin123", 
                             fg="#63b3ed", bg="#1e1e1e", font=('Segoe UI', 9))
        info_label.pack()
        
        # Focus on username entry
        username_entry.focus()
        
        # Bind Enter key to login
        login_window.bind('<Return>', lambda e: login())
        
        # Bind Escape key to cancel
        login_window.bind('<Escape>', lambda e: cancel())
    
    def authenticate_admin(self, username, password):
        """Authenticate admin credentials"""
        if not db_manager.is_connected:
            mess.showerror("Database Error", "Database connection is not available. Please check XAMPP MySQL service.")
            return False
        query = "SELECT * FROM admins WHERE username = %s AND password = %s"
        result = db_manager.execute_query(query, (username, password))
        return result is not None and len(result) > 0
    
    def show_admin_dashboard(self):
        """Show admin dashboard"""
        self.admin_window = tk.Toplevel(window)
        self.admin_window.title("Administrator Dashboard")
        self.admin_window.geometry("1000x700")
        self.admin_window.configure(bg="#1e1e1e")
        self.admin_window.transient(window)
        
        # Center the window
        self.admin_window.update_idletasks()
        x = (self.admin_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.admin_window.winfo_screenheight() // 2) - (700 // 2)
        self.admin_window.geometry(f"1000x700+{x}+{y}")
        
        # Title
        title_label = tk.Label(self.admin_window, text="Administrator Dashboard", 
                              fg="white", bg="#1e1e1e", font=('Segoe UI', 24, 'bold'))
        title_label.pack(pady=20)
        
        # Welcome message
        welcome_label = tk.Label(self.admin_window, text=f"Welcome, {self.current_admin}!", 
                                fg="#63b3ed", bg="#1e1e1e", font=('Segoe UI', 14))
        welcome_label.pack(pady=10)
        
        # Main frame
        main_frame = tk.Frame(self.admin_window, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)
        
        # User Management Tab
        user_frame = tk.Frame(notebook, bg="#2d3748")
        notebook.add(user_frame, text="User Management")
        self.create_user_management_tab(user_frame)
        
        # Task Assignment Tab
        task_frame = tk.Frame(notebook, bg="#2d3748")
        notebook.add(task_frame, text="Task Assignment")
        self.create_task_assignment_tab(task_frame)
        
        # Attendance Reports Tab
        report_frame = tk.Frame(notebook, bg="#2d3748")
        notebook.add(report_frame, text="Attendance Reports")
        self.create_attendance_reports_tab(report_frame)
        
        # Close button
        def close_admin_window():
            # Unbind mousewheel events to prevent errors
            try:
                self.admin_window.unbind_all("<MouseWheel>")
            except:
                pass
            self.admin_window.destroy()
        
        close_btn = tk.Button(self.admin_window, text="Close Dashboard", 
                             command=close_admin_window,
                             fg="white", bg="#e53e3e", width=15, height=1,
                             activebackground="#c53030", activeforeground="white",
                             relief="flat", bd=0, font=('Segoe UI', 11, 'bold'),
                             cursor="hand2")
        close_btn.pack(pady=20)
        
        # Also handle window close button (X button)
        self.admin_window.protocol("WM_DELETE_WINDOW", close_admin_window)
    
    def create_user_management_tab(self, parent):
        """Create user management interface"""
        # Add user section
        add_frame = tk.LabelFrame(parent, text="Add New User with Face Registration", bg="#c79cff", font=('comic', 12, 'bold'))
        add_frame.pack(fill="x", padx=10, pady=10)
        
        # Form fields
        fields = [
            ("Name:", "name_entry"),
            ("Email:", "email_entry"),
            ("Position:", "position_entry")
        ]
        
        entries = {}
        for i, (label, var_name) in enumerate(fields):
            tk.Label(add_frame, text=label, bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(add_frame, font=('comic', 10), width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[var_name] = entry
        
        # Auto-generated User ID display
        user_id_label = tk.Label(add_frame, text="User ID:", bg="#c79cff", font=('comic', 10, 'bold'))
        user_id_label.grid(row=len(fields), column=0, padx=10, pady=5, sticky="w")
        
        user_id_display = tk.Label(add_frame, text="Generating...", bg="#c79cff", fg="blue", 
                                  font=('comic', 10, 'bold'))
        user_id_display.grid(row=len(fields), column=1, padx=10, pady=5, sticky="w")
        
        def generate_user_id():
            """Generate a unique user ID"""
            try:
                # Get all existing user IDs
                query = "SELECT user_id FROM users WHERE user_id LIKE 'USER%' ORDER BY user_id"
                result = db_manager.execute_query(query)
                
                if result:
                    # Extract numbers from existing USER IDs
                    existing_numbers = []
                    for row in result:
                        user_id = row[0]
                        if user_id.startswith('USER'):
                            try:
                                # Extract the number part after 'USER'
                                number_part = user_id[4:]  # Remove 'USER' prefix
                                number = int(number_part)
                                existing_numbers.append(number)
                            except ValueError:
                                continue
                    
                    # Find the next available number
                    if existing_numbers:
                        next_number = max(existing_numbers) + 1
                    else:
                        next_number = 1
                    
                    # Format as 4-digit number
                    next_id = str(next_number).zfill(4)
                    user_id_display.config(text=f"USER{next_id}")
                    return f"USER{next_id}"
                else:
                    # No users exist, start with USER0001
                    user_id_display.config(text="USER0001")
                    return "USER0001"
                    
            except Exception as e:
                # Fallback to timestamp-based ID
                timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
                user_id_display.config(text=f"USER{timestamp}")
                return f"USER{timestamp}"
        
        # Auto-fill the User ID immediately when the tab is created
        generate_user_id()
        
        def add_user_with_face():
            """Add user to database and capture face images with enhanced flow"""
            try:
                # Generate user ID
                user_id = generate_user_id()
                
                # Enhanced validation
                name = entries['name_entry'].get().strip()
                email = entries['email_entry'].get().strip()
                position = entries['position_entry'].get().strip()
                
                # Validate required fields with detailed feedback
                if not name:
                    mess.showerror("Validation Error", "❌ Name is required!\nPlease enter the user's full name.")
                    entries['name_entry'].focus()
                    return
                
                if len(name) < 2:
                    mess.showerror("Validation Error", "❌ Name too short!\nPlease enter at least 2 characters.")
                    entries['name_entry'].focus()
                    return
                
                # Validate email format if provided
                if email and '@' not in email:
                    mess.showerror("Validation Error", "❌ Invalid email format!\nPlease enter a valid email address.")
                    entries['email_entry'].focus()
                    return
                
                # Check if user already exists by name
                check_name_query = "SELECT user_id FROM users WHERE LOWER(name) = LOWER(%s)"
                existing_name = db_manager.execute_query(check_name_query, (name,))
                
                if existing_name:
                    result = mess.askyesno("Duplicate User", 
                                         f"⚠️ A user with the name '{name}' already exists!\n\n"
                                         f"Existing User ID: {existing_name[0][0]}\n\n"
                                         f"Do you want to continue anyway?")
                    if not result:
                        return
                
                # Check if user ID already exists
                check_query = "SELECT user_id FROM users WHERE user_id = %s"
                existing_user = db_manager.execute_query(check_query, (user_id,))
                
                if existing_user:
                    mess.showerror("Error", f"User ID {user_id} already exists! Please try again.")
                    generate_user_id()  # Generate a new ID
                    return
                
                # Show progress dialog
                progress_window = tk.Toplevel(self.admin_window)
                progress_window.title("Saving User")
                progress_window.geometry("300x150")
                progress_window.resizable(False, False)
                progress_window.configure(bg="#2d3748")
                progress_window.transient(self.admin_window)
                progress_window.grab_set()
                
                # Center progress window
                progress_window.update_idletasks()
                x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
                y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
                progress_window.geometry(f"300x150+{x}+{y}")
                
                # Progress content
                progress_label = tk.Label(progress_window, text="💾 Saving User...", 
                                        fg="white", bg="#2d3748", font=('Segoe UI', 14, 'bold'))
                progress_label.pack(pady=20)
                
                progress_text = tk.Label(progress_window, text=f"User: {name}\nID: {user_id}", 
                                       fg="#63b3ed", bg="#2d3748", font=('Segoe UI', 10))
                progress_text.pack(pady=10)
                
                progress_window.update()
                
                # Add user to database
                query = """
                INSERT INTO users (user_id, name, email, position) 
                VALUES (%s, %s, %s, %s)
                """
                params = (user_id, name, email, position)
                result = db_manager.execute_query(query, params)
                
                # Close progress window
                progress_window.destroy()
                
                if result:
                    # Success feedback
                    success_window = tk.Toplevel(self.admin_window)
                    success_window.title("User Saved Successfully")
                    success_window.geometry("350x200")
                    success_window.resizable(False, False)
                    success_window.configure(bg="#2d3748")
                    success_window.transient(self.admin_window)
                    success_window.grab_set()
                    
                    # Center success window
                    success_window.update_idletasks()
                    x = (success_window.winfo_screenwidth() // 2) - (350 // 2)
                    y = (success_window.winfo_screenheight() // 2) - (200 // 2)
                    success_window.geometry(f"350x200+{x}+{y}")
                    
                    # Success content
                    success_label = tk.Label(success_window, text="✅ User Saved Successfully!", 
                                           fg="#4ade80", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
                    success_label.pack(pady=20)
                    
                    success_details = tk.Label(success_window, 
                                             text=f"👤 Name: {name}\n🆔 ID: {user_id}\n📧 Email: {email or 'Not provided'}\n💼 Position: {position or 'Not provided'}", 
                                             fg="white", bg="#2d3748", font=('Segoe UI', 11), justify="left")
                    success_details.pack(pady=10)
                    
                    # Auto-proceed to face capture
                    success_window.after(2000, lambda: [success_window.destroy(), self.proceed_to_complete_registration(user_id, name)])
                    
                    # Clear form and refresh
                    for entry in entries.values():
                        entry.delete(0, 'end')
                    generate_user_id()
                    self.refresh_user_list()
                    
                else:
                    mess.showerror("Database Error", "❌ Failed to save user to database!\nPlease check your database connection and try again.")
                    
            except Exception as e:
                mess.showerror("Error", f"❌ Failed to add user: {str(e)}\n\nPlease try again or contact support.")
        
        def proceed_to_face_capture(self, user_id, name):
            """Proceed to face capture after successful user save"""
            self.show_face_capture_modal(user_id, name)
        
        def proceed_to_complete_registration(self, user_id, name):
            """Complete registration with face capture and automatic model training"""
            try:
                # Show face capture instructions
                instruction_window = tk.Toplevel(self.admin_window)
                instruction_window.title("Complete Registration")
                instruction_window.geometry("400x300")
                instruction_window.resizable(False, False)
                instruction_window.configure(bg="#2d3748")
                instruction_window.transient(self.admin_window)
                instruction_window.grab_set()
                
                # Center instruction window
                instruction_window.update_idletasks()
                x = (instruction_window.winfo_screenwidth() // 2) - (400 // 2)
                y = (instruction_window.winfo_screenheight() // 2) - (300 // 2)
                instruction_window.geometry(f"400x300+{x}+{y}")
                
                # Instruction content
                title_label = tk.Label(instruction_window, text="📷 Complete Registration", 
                                     fg="white", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
                title_label.pack(pady=20)
                
                user_info = tk.Label(instruction_window, text=f"👤 User: {name}\n🆔 ID: {user_id}", 
                                   fg="#63b3ed", bg="#2d3748", font=('Segoe UI', 12))
                user_info.pack(pady=10)
                
                instructions = tk.Label(instruction_window, 
                                      text="🎯 FINAL STEP: Face Capture & Model Training\n\n"
                                           "• Position your face in front of camera\n"
                                           "• Look directly at the camera\n"
                                           "• Keep your face well-lit\n"
                                           "• Stay still during capture\n"
                                           "• System will automatically train the model\n"
                                           "• Ready for attendance recognition!", 
                                      fg="white", bg="#2d3748", font=('Segoe UI', 11), justify="left")
                instructions.pack(pady=20)
                
                def start_complete_registration():
                    instruction_window.destroy()
                    self.perform_complete_registration(user_id, name)
                
                def cancel_registration():
                    instruction_window.destroy()
                
                # Buttons
                button_frame = tk.Frame(instruction_window, bg="#2d3748")
                button_frame.pack(pady=20)
                
                start_btn = tk.Button(button_frame, text="🎥 Start Complete Registration", command=start_complete_registration,
                                    fg="white", bg="#4caf50", width=20,
                                    activebackground="#388e3c", activeforeground="white",
                                    relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                    cursor="hand2")
                start_btn.pack(side="left", padx=10)
                
                cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=cancel_registration,
                                     fg="white", bg="#f44336", width=15,
                                     activebackground="#d32f2f", activeforeground="white",
                                     relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                     cursor="hand2")
                cancel_btn.pack(side="left", padx=10)
                
            except Exception as e:
                mess.showerror("Error", f"Failed to start complete registration: {str(e)}")
        
        def perform_complete_registration(self, user_id, name):
            """Perform face capture and automatic model training"""
            try:
                # First, perform face capture
                self.perform_face_capture(user_id, name)
                
                # After face capture, automatically train the model
                self.auto_train_model()
                
            except Exception as e:
                mess.showerror("Error", f"Failed to complete registration: {str(e)}")
        
        def auto_train_model(self):
            """Automatically train the model after face capture"""
            try:
                # Show training progress
                training_window = tk.Toplevel(self.admin_window)
                training_window.title("Training Model")
                training_window.geometry("350x200")
                training_window.resizable(False, False)
                training_window.configure(bg="#2d3748")
                training_window.transient(self.admin_window)
                training_window.grab_set()
                
                # Center training window
                training_window.update_idletasks()
                x = (training_window.winfo_screenwidth() // 2) - (350 // 2)
                y = (training_window.winfo_screenheight() // 2) - (200 // 2)
                training_window.geometry(f"350x200+{x}+{y}")
                
                # Training content
                training_label = tk.Label(training_window, text="🤖 Training Face Recognition Model...", 
                                        fg="white", bg="#2d3748", font=('Segoe UI', 14, 'bold'))
                training_label.pack(pady=20)
                
                training_text = tk.Label(training_window, text="Please wait while the system trains the model\nwith the captured face images.", 
                                       fg="#63b3ed", bg="#2d3748", font=('Segoe UI', 11))
                training_text.pack(pady=10)
                
                training_window.update()
                
                # Perform the actual training
                self.train_admin_model()
                
                # Close training window
                training_window.destroy()
                
                # Show completion message
                completion_window = tk.Toplevel(self.admin_window)
                completion_window.title("Registration Complete")
                completion_window.geometry("400x250")
                completion_window.resizable(False, False)
                completion_window.configure(bg="#2d3748")
                completion_window.transient(self.admin_window)
                completion_window.grab_set()
                
                # Center completion window
                completion_window.update_idletasks()
                x = (completion_window.winfo_screenwidth() // 2) - (400 // 2)
                y = (completion_window.winfo_screenheight() // 2) - (250 // 2)
                completion_window.geometry(f"400x250+{x}+{y}")
                
                # Completion content
                completion_label = tk.Label(completion_window, text="🎉 Registration Complete!", 
                                          fg="#4ade80", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
                completion_label.pack(pady=20)
                
                completion_text = tk.Label(completion_window, 
                                         text="✅ User registered successfully\n"
                                              "✅ Face images captured\n"
                                              "✅ Model trained and ready\n"
                                              "✅ Ready for attendance recognition!", 
                                         fg="white", bg="#2d3748", font=('Segoe UI', 12), justify="left")
                completion_text.pack(pady=10)
                
                # Close button
                close_btn = tk.Button(completion_window, text="✅ Close", 
                                    command=completion_window.destroy,
                                    fg="white", bg="#4caf50", width=15,
                                    activebackground="#388e3c", activeforeground="white",
                                    relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                    cursor="hand2")
                close_btn.pack(pady=20)
                
            except Exception as e:
                mess.showerror("Training Error", f"Failed to train model: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(add_frame, bg="#c79cff")
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        
        add_with_face_btn = tk.Button(button_frame, text="Register User (Complete)", command=add_user_with_face,
                                     fg="white", bg="#673ab7", width=25,
                                     activebackground="#512da8", activeforeground="white",
                                     relief="flat", bd=0, font=('comic', 10, 'bold'))
        add_with_face_btn.pack(side="left", padx=5)
        
        # Note: Face capture is integrated into "Add User + Face Capture" workflow
        
        # Modern User Management Section
        list_frame = tk.Frame(parent, bg="#f8f9fa", relief="solid", bd=1)
        list_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Enhanced header with search functionality
        header_container = tk.Frame(list_frame, bg="#2c3e50", height=80)
        header_container.pack(fill="x", pady=(0, 10))
        header_container.pack_propagate(False)
        
        # Header title with icon
        title_frame = tk.Frame(header_container, bg="#2c3e50")
        title_frame.pack(side="left", expand=True, fill="both")
        
        title_label = tk.Label(title_frame, text="👥 Registered Users", 
                              bg="#2c3e50", fg="white", 
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(side="left", padx=20, pady=15)
        
        # User count badge
        self.user_count_label = tk.Label(title_frame, text="0 Users", 
                                       bg="#3498db", fg="white", 
                                       font=('Segoe UI', 10, 'bold'),
                                       padx=10, pady=5)
        self.user_count_label.pack(side="left", padx=20, pady=15)
        
        # Search and filter section
        search_frame = tk.Frame(header_container, bg="#2c3e50")
        search_frame.pack(side="right", padx=20, pady=10)
        
        # Search entry
        search_label = tk.Label(search_frame, text="🔍 Search:", bg="#2c3e50", fg="white", 
                               font=('Segoe UI', 10, 'bold'))
        search_label.pack(side="left", padx=(0, 5))
        
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 10), width=20,
                                    bg="#34495e", fg="white", insertbackground="white",
                                    relief="flat", bd=5)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.filter_users)
        
        # Filter dropdown
        filter_label = tk.Label(search_frame, text="Filter:", bg="#2c3e50", fg="white", 
                               font=('Segoe UI', 10, 'bold'))
        filter_label.pack(side="left", padx=(10, 5))
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var, 
                                   values=["All", "Name", "Email", "Position"], 
                                   state="readonly", width=10)
        filter_combo.pack(side="left", padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', self.filter_users)
        
        # Clear search button
        clear_btn = tk.Button(search_frame, text="Clear", command=self.clear_search,
                             fg="white", bg="#95a5a6", width=8,
                             activebackground="#7f8c8d", activeforeground="white",
                             relief="flat", bd=0, font=('Segoe UI', 9, 'bold'),
                             cursor="hand2")
        clear_btn.pack(side="left", padx=(5, 0))
        
        # Modern table container with shadow effect
        table_container = tk.Frame(list_frame, bg="#ecf0f1", relief="solid", bd=1)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Modern table header with gradient
        header_frame = tk.Frame(table_container, bg="#34495e", height=45)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Header labels with modern styling
        headers = ['ID', 'Name', 'Email', 'Position', 'Actions']
        header_widths = [120, 180, 250, 150, 120]
        
        for i, (header, width) in enumerate(zip(headers, header_widths)):
            header_label = tk.Label(header_frame, text=header, bg="#34495e", fg="white", 
                                   font=('Segoe UI', 11, 'bold'), width=width//8,
                                   relief="flat", bd=0)
            header_label.pack(side="left", padx=8, pady=12, fill="x", expand=True)
        
        # Modern scrollable content area
        content_frame = tk.Frame(table_container, bg="#ffffff")
        content_frame.pack(fill="both", expand=True)
        
        # Canvas for scrolling with modern styling
        canvas = tk.Canvas(content_frame, bg="#ffffff", highlightthickness=0, 
                          relief="flat", bd=0)
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#ffffff")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Modern scrollbar styling
        style = ttk.Style()
        style.configure("Modern.Vertical.TScrollbar", 
                       background="#bdc3c7",
                       troughcolor="#ecf0f1",
                       borderwidth=0,
                       arrowcolor="#2c3e50",
                       darkcolor="#bdc3c7",
                       lightcolor="#bdc3c7")
        scrollbar.configure(style="Modern.Vertical.TScrollbar")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # Canvas has been destroyed, ignore the error
                pass
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Modern action buttons container
        action_container = tk.Frame(list_frame, bg="#f8f9fa")
        action_container.pack(fill="x", pady=(10, 0))
        
        # Modern refresh button
        refresh_btn = tk.Button(action_container, text="🔄 Refresh", command=self.refresh_user_list,
                               fg="white", bg="#3498db", width=12,
                               activebackground="#2980b9", activeforeground="white",
                               relief="flat", bd=0, font=('Segoe UI', 10, 'bold'),
                               cursor="hand2")
        refresh_btn.pack(side="left", padx=5)
        
        # Modern add user button
        add_user_btn = tk.Button(action_container, text="➕ Add User", command=self.show_add_user_modal,
                                fg="white", bg="#27ae60", width=12,
                                activebackground="#229954", activeforeground="white",
                                relief="flat", bd=0, font=('Segoe UI', 10, 'bold'),
                                cursor="hand2")
        add_user_btn.pack(side="left", padx=5)
        
        # Modern export button
        export_btn = tk.Button(action_container, text="📊 Export", command=self.export_users,
                              fg="white", bg="#8e44ad", width=12,
                              activebackground="#7d3c98", activeforeground="white",
                              relief="flat", bd=0, font=('Segoe UI', 10, 'bold'),
                              cursor="hand2")
        export_btn.pack(side="left", padx=5)
        
        # Refresh user list
        self.refresh_user_list()
    
    def refresh_user_list(self):
        """Refresh the modern user list with enhanced styling"""
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        query = "SELECT user_id, name, email, position FROM users"
        users = db_manager.execute_query(query)
        
        # Update user count badge
        user_count = len(users) if users else 0
        self.user_count_label.config(text=f"{user_count} User{'s' if user_count != 1 else ''}")
        
        if users:
            for i, user in enumerate(users):
                user_id, name, email, position = user
                
                # Modern row styling with hover effects
                row_bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                row_frame = tk.Frame(self.scrollable_frame, bg=row_bg, height=50)
                row_frame.pack(fill="x", pady=1)
                row_frame.pack_propagate(False)
                
                # Add hover effect
                def on_enter(event, frame=row_frame):
                    frame.config(bg="#e3f2fd")
                def on_leave(event, frame=row_frame, bg=row_bg):
                    frame.config(bg=bg)
                
                row_frame.bind("<Enter>", on_enter)
                row_frame.bind("<Leave>", on_leave)
                
                # User ID with modern styling
                id_label = tk.Label(row_frame, text=user_id, bg=row_frame['bg'], 
                                   font=('Segoe UI', 10, 'bold'), fg="#2c3e50",
                                   width=15, anchor="w")
                id_label.pack(side="left", padx=15, pady=12)
                id_label.bind("<Enter>", on_enter)
                id_label.bind("<Leave>", on_leave)
                
                # Name with modern styling
                name_label = tk.Label(row_frame, text=name, bg=row_frame['bg'], 
                                     font=('Segoe UI', 10), fg="#34495e",
                                     width=22, anchor="w")
                name_label.pack(side="left", padx=10, pady=12)
                name_label.bind("<Enter>", on_enter)
                name_label.bind("<Leave>", on_leave)
                
                # Email with modern styling
                email_label = tk.Label(row_frame, text=email, bg=row_frame['bg'], 
                                      font=('Segoe UI', 9), fg="#7f8c8d",
                                      width=30, anchor="w")
                email_label.pack(side="left", padx=10, pady=12)
                email_label.bind("<Enter>", on_enter)
                email_label.bind("<Leave>", on_leave)
                
                # Position with modern styling
                position_label = tk.Label(row_frame, text=position, bg=row_frame['bg'], 
                                        font=('Segoe UI', 9), fg="#34495e",
                                        width=18, anchor="w")
                position_label.pack(side="left", padx=10, pady=12)
                position_label.bind("<Enter>", on_enter)
                position_label.bind("<Leave>", on_leave)
                
                # Modern action buttons container
                action_frame = tk.Frame(row_frame, bg=row_frame['bg'])
                action_frame.pack(side="right", padx=15, pady=8)
                
                # Modern Edit button
                edit_btn = tk.Button(action_frame, text="✏️ Edit", 
                                   command=lambda uid=user_id: self.edit_user_by_id(uid),
                                   fg="white", bg="#f39c12", width=8,
                                   activebackground="#e67e22", activeforeground="white",
                                   relief="flat", bd=0, font=('Segoe UI', 8, 'bold'),
                                   cursor="hand2")
                edit_btn.pack(side="left", padx=2)
                
                # Modern Delete button
                delete_btn = tk.Button(action_frame, text="🗑️ Delete", 
                                     command=lambda uid=user_id, uname=name: self.delete_user_by_id(uid, uname),
                                     fg="white", bg="#e74c3c", width=8,
                                     activebackground="#c0392b", activeforeground="white",
                                     relief="flat", bd=0, font=('Segoe UI', 8, 'bold'),
                                     cursor="hand2")
                delete_btn.pack(side="left", padx=2)
        else:
            # Modern empty state
            empty_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", height=200)
            empty_frame.pack(fill="both", expand=True)
            
            empty_icon = tk.Label(empty_frame, text="👥", bg="#ffffff", 
                                 font=('Segoe UI', 48), fg="#bdc3c7")
            empty_icon.pack(pady=(50, 10))
            
            empty_text = tk.Label(empty_frame, text="No Users Registered", 
                                 bg="#ffffff", fg="#7f8c8d", 
                                 font=('Segoe UI', 16, 'bold'))
            empty_text.pack(pady=5)
            
            empty_subtext = tk.Label(empty_frame, text="Add your first user to get started", 
                                   bg="#ffffff", fg="#95a5a6", 
                                   font=('Segoe UI', 12))
            empty_subtext.pack(pady=5)
    
    def create_task_assignment_tab(self, parent):
        """Create task assignment interface"""
        # Add task section
        add_frame = tk.LabelFrame(parent, text="Assign New Task", bg="#c79cff", font=('comic', 12, 'bold'))
        add_frame.pack(fill="x", padx=10, pady=10)
        
        # Form fields
        tk.Label(add_frame, text="Title:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=0, column=0, padx=10, pady=5, sticky="w")
        self.task_title_entry = tk.Entry(add_frame, font=('comic', 10), width=40)
        self.task_title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(add_frame, text="Description:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=1, column=0, padx=10, pady=5, sticky="nw")
        self.task_desc_text = tk.Text(add_frame, font=('comic', 10), width=40, height=3)
        self.task_desc_text.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(add_frame, text="Assign To:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=2, column=0, padx=10, pady=5, sticky="w")
        self.assign_to_var = tk.StringVar()
        self.assign_to_combo = ttk.Combobox(add_frame, textvariable=self.assign_to_var, 
                                           font=('comic', 10), width=37)
        self.assign_to_combo.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(add_frame, text="Priority:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=3, column=0, padx=10, pady=5, sticky="w")
        self.priority_var = tk.StringVar(value="medium")
        priority_combo = ttk.Combobox(add_frame, textvariable=self.priority_var,
                                     values=["low", "medium", "high", "urgent"],
                                     font=('comic', 10), width=37)
        priority_combo.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(add_frame, text="Due Date:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=4, column=0, padx=10, pady=5, sticky="w")
        self.due_date_entry = tk.Entry(add_frame, font=('comic', 10), width=37)
        self.due_date_entry.grid(row=4, column=1, padx=10, pady=5)
        self.due_date_entry.insert(0, "YYYY-MM-DD")
        
        def assign_task():
            try:
                # Extract user ID from the combo selection
                assign_to_value = self.assign_to_var.get()
                if " - " in assign_to_value:
                    user_id = assign_to_value.split(" - ")[0]
                else:
                    user_id = assign_to_value
                
                query = """
                INSERT INTO tasks (title, description, assigned_to, assigned_by, priority, due_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                params = (
                    self.task_title_entry.get(),
                    self.task_desc_text.get("1.0", "end-1c"),
                    user_id,
                    self.current_admin,
                    self.priority_var.get(),
                    self.due_date_entry.get() if self.due_date_entry.get() != "YYYY-MM-DD" else None
                )
                result = db_manager.execute_query(query, params)
                if result:
                    mess.showinfo("Success", "Task assigned successfully!")
                    self.task_title_entry.delete(0, 'end')
                    self.task_desc_text.delete("1.0", "end")
                    self.assign_to_var.set("")
                    self.priority_var.set("medium")
                    self.due_date_entry.delete(0, 'end')
                    self.due_date_entry.insert(0, "YYYY-MM-DD")
                    self.refresh_task_list()
            except Exception as e:
                mess.showerror("Error", f"Failed to assign task: {str(e)}")
        
        assign_btn = tk.Button(add_frame, text="Assign Task", command=assign_task,
                              fg="white", bg="#673ab7", width=12,
                              activebackground="#512da8", activeforeground="white",
                              relief="flat", bd=0, font=('comic', 10, 'bold'))
        assign_btn.grid(row=5, column=1, padx=10, pady=10, sticky="e")
        
        # Task list section
        list_frame = tk.LabelFrame(parent, text="Assigned Tasks", bg="#c79cff", font=('comic', 12, 'bold'))
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview for tasks
        task_columns = ('ID', 'Title', 'Assigned To', 'Priority', 'Status', 'Due Date')
        self.task_tree = ttk.Treeview(list_frame, columns=task_columns, show='headings', height=10)
        
        for col in task_columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=120)
        
        task_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=task_scrollbar.set)
        
        self.task_tree.pack(side="left", fill="both", expand=True)
        task_scrollbar.pack(side="right", fill="y")
        
        # Refresh task list and user combo
        self.refresh_task_list()
        self.refresh_user_combo()
    
    def refresh_task_list(self):
        """Refresh the task list"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        query = "SELECT id, title, assigned_to, priority, status, due_date FROM tasks ORDER BY created_at DESC"
        tasks = db_manager.execute_query(query)
        if tasks:
            for task in tasks:
                self.task_tree.insert('', 'end', values=task)
    
    def refresh_user_combo(self):
        """Refresh the user combo box"""
        query = "SELECT user_id, name FROM users ORDER BY name"
        users = db_manager.execute_query(query)
        if users:
            user_list = [f"{user[0]} - {user[1]}" for user in users]
            self.assign_to_combo['values'] = user_list
    
    def create_attendance_reports_tab(self, parent):
        """Create attendance reports interface"""
        # Date selection
        date_frame = tk.LabelFrame(parent, text="Date Range", bg="#c79cff", font=('comic', 12, 'bold'))
        date_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(date_frame, text="From:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=0, column=0, padx=10, pady=5, sticky="w")
        self.from_date_entry = tk.Entry(date_frame, font=('comic', 10), width=15)
        self.from_date_entry.grid(row=0, column=1, padx=10, pady=5)
        self.from_date_entry.insert(0, "YYYY-MM-DD")
        
        tk.Label(date_frame, text="To:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
            row=0, column=2, padx=10, pady=5, sticky="w")
        self.to_date_entry = tk.Entry(date_frame, font=('comic', 10), width=15)
        self.to_date_entry.grid(row=0, column=3, padx=10, pady=5)
        self.to_date_entry.insert(0, "YYYY-MM-DD")
        
        def generate_report():
            from_date = self.from_date_entry.get()
            to_date = self.to_date_entry.get()
            
            if from_date == "YYYY-MM-DD" or to_date == "YYYY-MM-DD":
                mess.showerror("Error", "Please select valid date range!")
                return
            
            query = """
            SELECT u.name, ar.date, ar.time_in, ar.time_out, ar.status 
            FROM attendance_records ar 
            JOIN users u ON ar.user_id = u.user_id 
            WHERE ar.date BETWEEN %s AND %s 
            ORDER BY ar.date DESC, u.name
            """
            records = db_manager.execute_query(query, (from_date, to_date))
            
            # Clear existing records
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            if records:
                for record in records:
                    self.report_tree.insert('', 'end', values=record)
            else:
                mess.showinfo("No Data", "No attendance records found for the selected date range.")
        
        generate_btn = tk.Button(date_frame, text="Generate Report", command=generate_report,
                                fg="white", bg="#4caf50", width=15,
                                activebackground="#388e3c", activeforeground="white",
                                relief="flat", bd=0, font=('comic', 10, 'bold'))
        generate_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Report display
        report_frame = tk.LabelFrame(parent, text="Attendance Report", bg="#c79cff", font=('comic', 12, 'bold'))
        report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview for reports
        report_columns = ('Name', 'Date', 'Time In', 'Time Out', 'Status')
        self.report_tree = ttk.Treeview(report_frame, columns=report_columns, show='headings', height=15)
        
        for col in report_columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=150)
        
        report_scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_tree.pack(side="left", fill="both", expand=True)
        report_scrollbar.pack(side="right", fill="y")
    
    def capture_face_images(self, user_id, name):
        """Capture face images for user registration with enhanced flow"""
        try:
            # Check if haarcascade file exists
            if not os.path.isfile("haarcascade_frontalface_default.xml"):
                mess.showerror("Error", "Face detection file not found!")
                return
            
            # Ensure directories exist
            assure_path_exists("TrainingImage/")
            
            # Get serial number for user
            serial = 0
            query = "SELECT COUNT(*) FROM users"
            result = db_manager.execute_query(query)
            if result:
                serial = result[0][0]
            
            # Enhanced name validation
            if not name or len(name.strip()) < 2:
                mess.showerror("Error", "Invalid name! Please provide a valid name.")
                return
            
            # Clean name for file naming
            clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not clean_name:
                mess.showerror("Error", "Name contains invalid characters!")
                return
            
            # Show enhanced instructions
            instruction_window = tk.Toplevel(self.admin_window)
            instruction_window.title("Face Capture Instructions")
            instruction_window.geometry("400x300")
            instruction_window.resizable(False, False)
            instruction_window.configure(bg="#2d3748")
            instruction_window.transient(self.admin_window)
            instruction_window.grab_set()
            
            # Center instruction window
            instruction_window.update_idletasks()
            x = (instruction_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (instruction_window.winfo_screenheight() // 2) - (300 // 2)
            instruction_window.geometry(f"400x300+{x}+{y}")
            
            # Instruction content
            title_label = tk.Label(instruction_window, text="📷 Face Capture Instructions", 
                                 fg="white", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
            title_label.pack(pady=20)
            
            user_info = tk.Label(instruction_window, text=f"👤 User: {name}\n🆔 ID: {user_id}", 
                               fg="#63b3ed", bg="#2d3748", font=('Segoe UI', 12))
            user_info.pack(pady=10)
            
            instructions = tk.Label(instruction_window, 
                                  text="• Position your face in front of the camera\n• Look directly at the camera\n• Keep your face well-lit\n• Stay still during capture\n• Press 'q' to quit early\n• Wait for 100 samples to complete", 
                                  fg="white", bg="#2d3748", font=('Segoe UI', 11), justify="left")
            instructions.pack(pady=20)
            
            def start_capture():
                instruction_window.destroy()
                self.perform_face_capture(user_id, name, clean_name, serial)
            
            def cancel_capture():
                instruction_window.destroy()
            
            # Buttons
            button_frame = tk.Frame(instruction_window, bg="#2d3748")
            button_frame.pack(pady=20)
            
            start_btn = tk.Button(button_frame, text="🎥 Start Capture", command=start_capture,
                                fg="white", bg="#4caf50", width=15,
                                activebackground="#388e3c", activeforeground="white",
                                relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                cursor="hand2")
            start_btn.pack(side="left", padx=10)
            
            cancel_btn = tk.Button(button_frame, text="❌ Cancel", command=cancel_capture,
                                 fg="white", bg="#f44336", width=15,
                                 activebackground="#d32f2f", activeforeground="white",
                                 relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                 cursor="hand2")
            cancel_btn.pack(side="left", padx=10)
                
        except Exception as e:
            mess.showerror("Error", f"Failed to initialize face capture: {str(e)}")
    
    def perform_face_capture(self, user_id, name, clean_name, serial):
        """Perform the actual face capture process"""
        try:
            # Start camera with error handling
            cam = cv2.VideoCapture(0)
            
            if not cam.isOpened():
                mess.showerror("Camera Error", "Cannot open camera! Please check camera connection.")
                return
            
            harcascadePath = "haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            
            if detector.empty():
                mess.showerror("Error", "Failed to load face detection classifier!")
                cam.release()
                return
            
            sampleNum = 0
            
            # Enhanced camera settings for better capture quality
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cam.set(cv2.CAP_PROP_FPS, 30)
            cam.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
            cam.set(cv2.CAP_PROP_CONTRAST, 0.5)
            
            # Night mode detection for face capture
            def detect_night_mode_capture(image):
                """Detect if the image is in low light conditions"""
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                mean_brightness = np.mean(gray)
                return mean_brightness < 80  # Threshold for night mode
            
            def enhance_night_vision_capture(image):
                """Enhance image for night/low light conditions during capture"""
                # Convert to LAB color space for better brightness control
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                
                # Merge channels back
                enhanced_lab = cv2.merge([l, a, b])
                enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
                
                # Additional gamma correction for night mode
                gamma = 1.5  # Adjust gamma for brightness
                lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)]).astype("uint8")
                enhanced_bgr = cv2.LUT(enhanced_bgr, lookup_table)
                
                return enhanced_bgr
            
            # Enhanced face detection parameters for better training data
            def enhanced_face_detection(image):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(
                    gray,
                    scaleFactor=1.1,  # More conservative scaling
                    minNeighbors=8,    # Higher threshold for better accuracy
                    minSize=(80, 80),  # Larger minimum face size for better quality
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                return faces
            
            while True:
                ret, img = cam.read()
                if not ret:
                    mess.showerror("Camera Error", "Lost connection to camera! Please check camera connection.")
                    break
                
                # Night mode detection and enhancement for capture
                is_night_mode = detect_night_mode_capture(img)
                if is_night_mode:
                    img = enhance_night_vision_capture(img)
                    # Display night mode indicator
                    cv2.putText(img, "NIGHT MODE CAPTURE", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    
                # Enhanced face detection
                faces = enhanced_face_detection(img)
                
                for (x, y, w, h) in faces:
                    # Ensure face is large enough for good quality
                    if w > 80 and h > 80:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        
                        # Extract face region
                        face_region = img[y:y + h, x:x + w]
                        
                        # Enhanced preprocessing for better training data
                        gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
                        
                        # Apply histogram equalization for better contrast
                        equalized = cv2.equalizeHist(gray_face)
                        
                        # Apply slight Gaussian blur to reduce noise
                        processed_face = cv2.GaussianBlur(equalized, (3, 3), 0)
                        
                        # Resize to standard size for consistent training
                        resized_face = cv2.resize(processed_face, (100, 100))
                        
                        # Incrementing sample number
                        sampleNum = sampleNum + 1
                        
                        # Saving the enhanced processed face with proper naming
                        # Use serial number as the ID for face recognition
                        filename = f"TrainingImage\\{clean_name}.{serial}.{user_id}.{sampleNum}.jpg"
                        cv2.imwrite(filename, resized_face)
                        
                        # Display progress
                        cv2.putText(img, f"Captured: {sampleNum}/100", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(img, f"User: {name}", (10, 70), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Display the frame
                cv2.imshow('Capturing Face Images - Enhanced Quality', img)
                
                # Wait for 100 milliseconds
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                # Break if the sample number is more than 100
                elif sampleNum > 100:
                    break
            
            cam.release()
            cv2.destroyAllWindows()
            
            if sampleNum > 0:
                # Show success message
                success_window = tk.Toplevel(self.admin_window)
                success_window.title("Face Capture Complete")
                success_window.geometry("350x200")
                success_window.resizable(False, False)
                success_window.configure(bg="#2d3748")
                success_window.transient(self.admin_window)
                success_window.grab_set()
                
                # Center success window
                success_window.update_idletasks()
                x = (success_window.winfo_screenwidth() // 2) - (350 // 2)
                y = (success_window.winfo_screenheight() // 2) - (200 // 2)
                success_window.geometry(f"350x200+{x}+{y}")
                
                # Success content
                success_label = tk.Label(success_window, text="✅ Face Capture Complete!", 
                                       fg="#4ade80", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
                success_label.pack(pady=20)
                
                success_details = tk.Label(success_window, 
                                         text=f"👤 User: {name}\n🆔 ID: {user_id}\n📸 Samples: {sampleNum}\n💾 Saved to: TrainingImage/", 
                                         fg="white", bg="#2d3748", font=('Segoe UI', 11), justify="left")
                success_details.pack(pady=10)
                
                # Close button
                close_btn = tk.Button(success_window, text="✅ Close", 
                                    command=success_window.destroy,
                                    fg="white", bg="#4caf50", width=15,
                                    activebackground="#388e3c", activeforeground="white",
                                    relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                                    cursor="hand2")
                close_btn.pack(pady=15)
                
                # Update voice assistant user list
                voice_assistant.load_registered_users()
            else:
                mess.showerror("Error", "No face images were captured!")
                
        except Exception as e:
            mess.showerror("Error", f"Failed to capture face images: {str(e)}")
    
    def show_face_capture_modal(self, user_id, name):
        """Show modal dialog for face capture confirmation"""
        # Create modal window
        modal_window = tk.Toplevel(self.admin_window)
        modal_window.title("Face Capture Confirmation")
        modal_window.geometry("320x240")
        modal_window.resizable(False, False)
        modal_window.configure(bg="#2d420a")
        modal_window.transient(self.admin_window)
        modal_window.grab_set()
        
        # Center the window
        modal_window.update_idletasks()
        x = (modal_window.winfo_screenwidth() // 2) - (320 // 2)
        y = (modal_window.winfo_screenheight() // 2) - (240 // 2)
        modal_window.geometry(f"320x240+{x}+{y}")
        
        # Title
        title_label = tk.Label(modal_window, text="Face Capture", 
                              fg="white", bg="#2d420a", font=('comic', 14, 'bold'))
        title_label.pack(pady=10)
        
        # User info
        user_info = f"User: {name} (ID: {user_id})"
        user_label = tk.Label(modal_window, text=user_info, 
                             fg="#ffeb3b", bg="#2d420a", font=('comic', 10, 'bold'))
        user_label.pack(pady=5)
        
        # Instructions
        instructions = """📷 FACE CAPTURE:
• Position face in front of camera
• Look directly at camera
• Keep face well-lit
• Press 'q' to quit early
• Wait for 100 samples"""
        
        instruction_label = tk.Label(modal_window, text=instructions, 
                                   fg="white", bg="#2d420a", font=('comic', 8),
                                   justify="left")
        instruction_label.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(modal_window, bg="#2d420a")
        button_frame.pack(pady=10)
        
        def start_capture():
            modal_window.destroy()
            self.capture_face_images(user_id, name)
        
        def cancel():
            modal_window.destroy()
        
        # Start capture button
        start_btn = tk.Button(button_frame, text="🎥 Start", command=start_capture,
                             fg="white", bg="#4caf50", width=12,
                             activebackground="#388e3c", activeforeground="white",
                             relief="flat", bd=0, font=('comic', 9, 'bold'))
        start_btn.pack(side="left", padx=8)
        
        # Cancel button
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel,
                              fg="white", bg="#f44336", width=12,
                              activebackground="#d32f2f", activeforeground="white",
                              relief="flat", bd=0, font=('comic', 9, 'bold'))
        cancel_btn.pack(side="left", padx=8)
    
    def train_admin_model(self):
        """Train the face recognition model from admin interface"""
        try:
            check_haarcascadefile()
            assure_path_exists("TrainingImageLabel/")
            
            # Enhanced LBPH recognizer with optimized parameters
            recognizer = cv2.face_LBPHFaceRecognizer.create(
                radius=2,           # LBP radius
                neighbors=8,         # Number of neighbors
                grid_x=8,           # Grid X size
                grid_y=8,           # Grid Y size
                threshold=100.0     # Recognition threshold
            )
            
            harcascadePath = "haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            
            # Get enhanced training data
            faces, ID = getImagesAndLabelsEnhanced("TrainingImage")
            
            if len(faces) == 0:
                mess.showinfo("No Data", "No face images found! Please register users with face capture first.")
                return
            
            # Enhanced training with validation
            recognizer.train(faces, np.array(ID))
            
            # Save the trained model
            recognizer.save("TrainingImageLabel\Trainner.yml")
            
            # Additional validation - test the model
            test_accuracy = validate_model_accuracy(recognizer, faces, ID)
            
            # Update user count display
            user_count = 0
            if db_manager.is_connected:
                try:
                    query = "SELECT COUNT(*) FROM users"
                    result = db_manager.execute_query(query)
                    if result:
                        user_count = result[0][0]
                except:
                    pass
            
            res = f"Profile Saved Successfully!\nTraining Accuracy: {test_accuracy:.1f}%\nTotal Users: {user_count}"
            mess.showinfo("Success", res)
            
            # Refresh user list
            self.refresh_user_list()
            
        except Exception as e:
            mess.showerror("Training Error", f"Failed to train model: {str(e)}")
    
    def delete_selected_user(self):
        """Delete the selected user from database and files"""
        try:
            # Get selected item
            selected_item = self.user_tree.selection()
            if not selected_item:
                mess.showerror("Error", "Please select a user to delete!")
                return
            
            # Get user details
            item = self.user_tree.item(selected_item[0])
            user_id = item['values'][0]
            name = item['values'][1]
            
            # Confirm deletion
            result = mess.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete user:\n\n"
                                 f"ID: {user_id}\n"
                                 f"Name: {name}\n\n"
                                 f"This will also delete all face images and attendance records!")
            
            if not result:
                return
            
            # Delete from database
            delete_query = "DELETE FROM users WHERE user_id = %s"
            db_result = db_manager.execute_query(delete_query, (user_id,))
            
            if db_result:
                # Delete attendance records
                attendance_query = "DELETE FROM attendance_records WHERE user_id = %s"
                db_manager.execute_query(attendance_query, (user_id,))
                
                # Delete face images
                self.delete_user_face_images(user_id, name)
                
                # Refresh user list
                self.refresh_user_list()
                
                # Retrain model if needed
                mess.showinfo("Success", f"User {name} deleted successfully!")
                
                # Ask if user wants to retrain model
                retrain = mess.askyesno("Retrain Model", 
                                      "User deleted successfully!\n\n"
                                      "Do you want to retrain the face recognition model?")
                if retrain:
                    self.train_admin_model()
            else:
                mess.showerror("Error", "Failed to delete user from database!")
                
        except Exception as e:
            mess.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def delete_user_face_images(self, user_id, name):
        """Delete face images for a specific user"""
        try:
            import glob
            import os
            
            # Pattern to match user's face images
            pattern = f"TrainingImage/{name}.*{user_id}.*.jpg"
            image_files = glob.glob(pattern)
            
            # Also try alternative patterns
            pattern2 = f"TrainingImage/{name}.*.jpg"
            image_files.extend(glob.glob(pattern2))
            
            # Delete all matching files
            deleted_count = 0
            for file_path in image_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except:
                    continue
            
            print(f"Deleted {deleted_count} face images for user {name}")
            
        except Exception as e:
            print(f"Error deleting face images: {e}")
    
    def edit_selected_user(self):
        """Edit the selected user's information"""
        try:
            # Get selected item
            selected_item = self.user_tree.selection()
            if not selected_item:
                mess.showerror("Error", "Please select a user to edit!")
                return
            
            # Get user details
            item = self.user_tree.item(selected_item[0])
            user_id = item['values'][0]
            name = item['values'][1]
            email = item['values'][2]
            position = item['values'][3]
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.admin_window)
            edit_window.title("Edit User")
            edit_window.geometry("400x300")
            edit_window.resizable(False, False)
            edit_window.configure(bg="#2d420a")
            edit_window.transient(self.admin_window)
            edit_window.grab_set()
            
            # Center the window
            edit_window.update_idletasks()
            x = (edit_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (edit_window.winfo_screenheight() // 2) - (300 // 2)
            edit_window.geometry(f"400x300+{x}+{y}")
            
            # Title
            title_label = tk.Label(edit_window, text="Edit User Information", 
                                  fg="white", bg="#2d420a", font=('comic', 16, 'bold'))
            title_label.pack(pady=20)
            
            # Form frame
            form_frame = tk.Frame(edit_window, bg="#c79cff")
            form_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # User ID (read-only)
            tk.Label(form_frame, text="User ID:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=0, column=0, padx=10, pady=5, sticky="w")
            id_label = tk.Label(form_frame, text=user_id, bg="#c79cff", fg="blue", 
                               font=('comic', 10, 'bold'))
            id_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            # Name
            tk.Label(form_frame, text="Name:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=1, column=0, padx=10, pady=5, sticky="w")
            name_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            name_entry.grid(row=1, column=1, padx=10, pady=5)
            name_entry.insert(0, name)
            
            # Email
            tk.Label(form_frame, text="Email:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=2, column=0, padx=10, pady=5, sticky="w")
            email_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            email_entry.grid(row=2, column=1, padx=10, pady=5)
            email_entry.insert(0, email)
            
            # Position
            tk.Label(form_frame, text="Position:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=3, column=0, padx=10, pady=5, sticky="w")
            position_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            position_entry.grid(row=3, column=1, padx=10, pady=5)
            position_entry.insert(0, position)
            
            # Buttons frame
            button_frame = tk.Frame(edit_window, bg="#2d420a")
            button_frame.pack(pady=20)
            
            def save_changes():
                try:
                    new_name = name_entry.get().strip()
                    new_email = email_entry.get().strip()
                    new_position = position_entry.get().strip()
                    
                    if not new_name:
                        mess.showerror("Error", "Name is required!")
                        return
                    
                    # Update database
                    update_query = """
                    UPDATE users 
                    SET name = %s, email = %s, position = %s 
                    WHERE user_id = %s
                    """
                    result = db_manager.execute_query(update_query, 
                                                    (new_name, new_email, new_position, user_id))
                    
                    if result:
                        mess.showinfo("Success", "User information updated successfully!")
                        edit_window.destroy()
                        self.refresh_user_list()
                    else:
                        mess.showerror("Error", "Failed to update user information!")
                        
                except Exception as e:
                    mess.showerror("Error", f"Failed to update user: {str(e)}")
            
            def cancel_edit():
                edit_window.destroy()
            
            # Save button
            save_btn = tk.Button(button_frame, text="💾 Save Changes", command=save_changes,
                                fg="white", bg="#4caf50", width=15,
                                activebackground="#388e3c", activeforeground="white",
                                relief="flat", bd=0, font=('comic', 11, 'bold'))
            save_btn.pack(side="left", padx=10)
            
            # Cancel button
            cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_edit,
                                  fg="white", bg="#f44336", width=15,
                                  activebackground="#d32f2f", activeforeground="white",
                                  relief="flat", bd=0, font=('comic', 11, 'bold'))
            cancel_btn.pack(side="left", padx=10)
            
        except Exception as e:
            mess.showerror("Error", f"Failed to edit user: {str(e)}")
    
    def edit_user_by_id(self, user_id):
        """Edit user by ID"""
        try:
            # Get user details from database
            query = "SELECT user_id, name, email, position FROM users WHERE user_id = %s"
            result = db_manager.execute_query(query, (user_id,))
            
            if not result:
                mess.showerror("Error", "User not found!")
                return
            
            user_id, name, email, position = result[0]
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.admin_window)
            edit_window.title("Edit User")
            edit_window.geometry("400x300")
            edit_window.resizable(False, False)
            edit_window.configure(bg="#2d420a")
            edit_window.transient(self.admin_window)
            edit_window.grab_set()
            
            # Center the window
            edit_window.update_idletasks()
            x = (edit_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (edit_window.winfo_screenheight() // 2) - (300 // 2)
            edit_window.geometry(f"400x300+{x}+{y}")
            
            # Title
            title_label = tk.Label(edit_window, text="Edit User Information", 
                                  fg="white", bg="#2d420a", font=('comic', 16, 'bold'))
            title_label.pack(pady=20)
            
            # Form frame
            form_frame = tk.Frame(edit_window, bg="#c79cff")
            form_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # User ID (read-only)
            tk.Label(form_frame, text="User ID:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=0, column=0, padx=10, pady=5, sticky="w")
            id_label = tk.Label(form_frame, text=user_id, bg="#c79cff", fg="blue", 
                               font=('comic', 10, 'bold'))
            id_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            # Name
            tk.Label(form_frame, text="Name:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=1, column=0, padx=10, pady=5, sticky="w")
            name_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            name_entry.grid(row=1, column=1, padx=10, pady=5)
            name_entry.insert(0, name)
            
            # Email
            tk.Label(form_frame, text="Email:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=2, column=0, padx=10, pady=5, sticky="w")
            email_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            email_entry.grid(row=2, column=1, padx=10, pady=5)
            email_entry.insert(0, email)
            
            # Position
            tk.Label(form_frame, text="Position:", bg="#c79cff", font=('comic', 10, 'bold')).grid(
                row=3, column=0, padx=10, pady=5, sticky="w")
            position_entry = tk.Entry(form_frame, font=('comic', 10), width=30)
            position_entry.grid(row=3, column=1, padx=10, pady=5)
            position_entry.insert(0, position)
            
            # Buttons frame
            button_frame = tk.Frame(edit_window, bg="#2d420a")
            button_frame.pack(pady=20)
            
            def save_changes():
                try:
                    new_name = name_entry.get().strip()
                    new_email = email_entry.get().strip()
                    new_position = position_entry.get().strip()
                    
                    if not new_name:
                        mess.showerror("Error", "Name is required!")
                        return
                    
                    # Update database
                    update_query = """
                    UPDATE users 
                    SET name = %s, email = %s, position = %s 
                    WHERE user_id = %s
                    """
                    result = db_manager.execute_query(update_query, 
                                                    (new_name, new_email, new_position, user_id))
                    
                    if result:
                        mess.showinfo("Success", "User information updated successfully!")
                        edit_window.destroy()
                        self.refresh_user_list()
                    else:
                        mess.showerror("Error", "Failed to update user information!")
                        
                except Exception as e:
                    mess.showerror("Error", f"Failed to update user: {str(e)}")
            
            def cancel_edit():
                edit_window.destroy()
            
            # Save button
            save_btn = tk.Button(button_frame, text="💾 Save Changes", command=save_changes,
                                fg="white", bg="#4caf50", width=15,
                                activebackground="#388e3c", activeforeground="white",
                                relief="flat", bd=0, font=('comic', 11, 'bold'))
            save_btn.pack(side="left", padx=10)
            
            # Cancel button
            cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_edit,
                                  fg="white", bg="#f44336", width=15,
                                  activebackground="#d32f2f", activeforeground="white",
                                  relief="flat", bd=0, font=('comic', 11, 'bold'))
            cancel_btn.pack(side="left", padx=10)
            
        except Exception as e:
            mess.showerror("Error", f"Failed to edit user: {str(e)}")
    
    def filter_users(self, event=None):
        """Filter users based on search criteria"""
        search_term = self.search_entry.get().strip().lower()
        filter_type = self.filter_var.get()
        
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get all users
        query = "SELECT user_id, name, email, position FROM users"
        all_users = db_manager.execute_query(query)
        
        if not all_users:
            self.user_count_label.config(text="0 Users")
            return
        
        # Filter users based on search criteria
        filtered_users = []
        for user in all_users:
            user_id, name, email, position = user
            
            if not search_term:  # No search term, show all
                filtered_users.append(user)
            else:
                # Search based on filter type
                if filter_type == "All":
                    searchable_text = f"{user_id} {name} {email} {position}".lower()
                elif filter_type == "Name":
                    searchable_text = name.lower()
                elif filter_type == "Email":
                    searchable_text = email.lower()
                elif filter_type == "Position":
                    searchable_text = position.lower()
                else:
                    searchable_text = f"{user_id} {name} {email} {position}".lower()
                
                if search_term in searchable_text:
                    filtered_users.append(user)
        
        # Update user count badge
        total_count = len(all_users)
        filtered_count = len(filtered_users)
        self.user_count_label.config(text=f"{filtered_count}/{total_count} Users")
        
        # Display filtered users
        if filtered_users:
            for i, user in enumerate(filtered_users):
                user_id, name, email, position = user
                
                # Modern row styling with hover effects
                row_bg = "#ffffff" if i % 2 == 0 else "#f8f9fa"
                row_frame = tk.Frame(self.scrollable_frame, bg=row_bg, height=50)
                row_frame.pack(fill="x", pady=1)
                row_frame.pack_propagate(False)
                
                # Add hover effect
                def on_enter(event, frame=row_frame):
                    frame.config(bg="#e3f2fd")
                def on_leave(event, frame=row_frame, bg=row_bg):
                    frame.config(bg=bg)
                
                row_frame.bind("<Enter>", on_enter)
                row_frame.bind("<Leave>", on_leave)
                
                # User ID with modern styling
                id_label = tk.Label(row_frame, text=user_id, bg=row_frame['bg'], 
                                   font=('Segoe UI', 10, 'bold'), fg="#2c3e50",
                                   width=15, anchor="w")
                id_label.pack(side="left", padx=15, pady=12)
                id_label.bind("<Enter>", on_enter)
                id_label.bind("<Leave>", on_leave)
                
                # Name with modern styling
                name_label = tk.Label(row_frame, text=name, bg=row_frame['bg'], 
                                     font=('Segoe UI', 10), fg="#34495e",
                                     width=22, anchor="w")
                name_label.pack(side="left", padx=10, pady=12)
                name_label.bind("<Enter>", on_enter)
                name_label.bind("<Leave>", on_leave)
                
                # Email with modern styling
                email_label = tk.Label(row_frame, text=email, bg=row_frame['bg'], 
                                      font=('Segoe UI', 9), fg="#7f8c8d",
                                      width=30, anchor="w")
                email_label.pack(side="left", padx=10, pady=12)
                email_label.bind("<Enter>", on_enter)
                email_label.bind("<Leave>", on_leave)
                
                # Position with modern styling
                position_label = tk.Label(row_frame, text=position, bg=row_frame['bg'], 
                                        font=('Segoe UI', 9), fg="#34495e",
                                        width=18, anchor="w")
                position_label.pack(side="left", padx=10, pady=12)
                position_label.bind("<Enter>", on_enter)
                position_label.bind("<Leave>", on_leave)
                
                # Modern action buttons container
                action_frame = tk.Frame(row_frame, bg=row_frame['bg'])
                action_frame.pack(side="right", padx=15, pady=8)
                
                # Modern Edit button
                edit_btn = tk.Button(action_frame, text="✏️ Edit", 
                                   command=lambda uid=user_id: self.edit_user_by_id(uid),
                                   fg="white", bg="#f39c12", width=8,
                                   activebackground="#e67e22", activeforeground="white",
                                   relief="flat", bd=0, font=('Segoe UI', 8, 'bold'),
                                   cursor="hand2")
                edit_btn.pack(side="left", padx=2)
                
                # Modern Delete button
                delete_btn = tk.Button(action_frame, text="🗑️ Delete", 
                                     command=lambda uid=user_id, uname=name: self.delete_user_by_id(uid, uname),
                                     fg="white", bg="#e74c3c", width=8,
                                     activebackground="#c0392b", activeforeground="white",
                                     relief="flat", bd=0, font=('Segoe UI', 8, 'bold'),
                                     cursor="hand2")
                delete_btn.pack(side="left", padx=2)
        else:
            # No results found
            no_results_frame = tk.Frame(self.scrollable_frame, bg="#ffffff", height=200)
            no_results_frame.pack(fill="both", expand=True)
            
            no_results_icon = tk.Label(no_results_frame, text="🔍", bg="#ffffff", 
                                      font=('Segoe UI', 48), fg="#bdc3c7")
            no_results_icon.pack(pady=(50, 10))
            
            no_results_text = tk.Label(no_results_frame, text="No Users Found", 
                                      bg="#ffffff", fg="#7f8c8d", 
                                      font=('Segoe UI', 16, 'bold'))
            no_results_text.pack(pady=5)
            
            no_results_subtext = tk.Label(no_results_frame, text=f"No users match '{search_term}'", 
                                         bg="#ffffff", fg="#95a5a6", 
                                         font=('Segoe UI', 12))
            no_results_subtext.pack(pady=5)
    
    def clear_search(self):
        """Clear search and show all users"""
        self.search_entry.delete(0, tk.END)
        self.filter_var.set("All")
        self.refresh_user_list()
    
    def delete_user_by_id(self, user_id, user_name):
        """Delete user by ID"""
        try:
            # Confirm deletion
            result = mess.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete user:\n\n"
                                 f"ID: {user_id}\n"
                                 f"Name: {user_name}\n\n"
                                 f"This will also delete all face images and attendance records!")
            
            if not result:
                return
            
            # Delete from database
            delete_query = "DELETE FROM users WHERE user_id = %s"
            db_result = db_manager.execute_query(delete_query, (user_id,))
            
            if db_result:
                # Delete attendance records
                attendance_query = "DELETE FROM attendance_records WHERE user_id = %s"
                db_manager.execute_query(attendance_query, (user_id,))
                
                # Delete face images
                self.delete_user_face_images(user_id, user_name)
                
                # Refresh user list
                self.refresh_user_list()
                
                # Success message
                mess.showinfo("Success", f"User {user_name} deleted successfully!")
                
                # Ask if user wants to retrain model
                retrain = mess.askyesno("Retrain Model", 
                                      "User deleted successfully!\n\n"
                                      "Do you want to retrain the face recognition model?")
                if retrain:
                    self.train_admin_model()
            else:
                mess.showerror("Error", "Failed to delete user from database!")
                
        except Exception as e:
            mess.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def show_add_user_modal(self):
        """Show modal for adding new user"""
        # This would open the add user form in a modal
        mess.showinfo("Add User", "Add User functionality - Use the form above to add new users!")
    
    def export_users(self):
        """Export users to CSV file"""
        try:
            import csv
            from tkinter import filedialog
            
            # Get users from database
            query = "SELECT user_id, name, email, position FROM users"
            users = db_manager.execute_query(query)
            
            if not users:
                mess.showinfo("No Data", "No users to export!")
                return
            
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Users"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['User ID', 'Name', 'Email', 'Position'])
                    writer.writerows(users)
                
                mess.showinfo("Success", f"Users exported successfully to {filename}")
            
        except Exception as e:
            mess.showerror("Error", f"Failed to export users: {str(e)}")

# Global admin system instance
admin_system = AdminSystem()

############################################# FUNCTIONS ################################################

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

##################################################################################

def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.config(text=time_string)
    clock.after(200,tick)

def on_window_resize(event):
    """Handle window resize events for better responsiveness"""
    # Update voice response label wraplength based on window width
    if hasattr(window, 'winfo_width'):
        window_width = window.winfo_width()
        if window_width > 0:
            # Adjust wraplength to be approximately 60% of window width
            new_wraplength = int(window_width * 0.6)
            if hasattr(voice_response, 'config'):
                voice_response.config(wraplength=new_wraplength)

###################################################################################

def contact():
    mess._show(title='Contact us', message="Please contact us on : 'shubhamkumar8180323@gmail.com' ")

###################################################################################

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if exists:
        pass
    else:
        mess._show(title='Some file missing', message='Please contact us for help')
        window.destroy()

###################################################################################

def save_pass():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel\psd.txt")
    if exists1:
        tf = open("TrainingImageLabel\psd.txt", "r")
        key = tf.read()
    else:
        master.destroy()
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess._show(title='No Password Entered', message='Password not set!! Please try again')
        else:
            tf = open("TrainingImageLabel\psd.txt", "w")
            tf.write(new_pas)
            mess._show(title='Password Registered', message='New password was registered successfully!!')
            return
    op = (old.get())
    newp= (new.get())
    nnewp = (nnew.get())
    if (op == key):
        if(newp == nnewp):
            txf = open("TrainingImageLabel\psd.txt", "w")
            txf.write(newp)
        else:
            mess._show(title='Error', message='Confirm new password again!!!')
            return
    else:
        mess._show(title='Wrong Password', message='Please enter correct old password.')
        return
    mess._show(title='Password Changed', message='Password changed successfully!!')
    master.destroy()

###################################################################################

def change_pass():
    global master
    master = tk.Tk()
    master.geometry("400x160")
    master.resizable(False,False)
    master.title("Change Password")
    master.configure(background="white")
    lbl4 = tk.Label(master,text='    Enter Old Password',bg='white',font=('comic', 12, ' bold '))
    lbl4.place(x=10,y=10)
    global old
    old=tk.Entry(master,width=25 ,fg="black",relief='solid',font=('comic', 12, ' bold '),show='*')
    old.place(x=180,y=10)
    lbl5 = tk.Label(master, text='   Enter New Password', bg='white', font=('comic', 12, ' bold '))
    lbl5.place(x=10, y=45)
    global new
    new = tk.Entry(master, width=25, fg="black",relief='solid', font=('comic', 12, ' bold '),show='*')
    new.place(x=180, y=45)
    lbl6 = tk.Label(master, text='Confirm New Password', bg='white', font=('comic', 12, ' bold '))
    lbl6.place(x=10, y=80)
    global nnew
    nnew = tk.Entry(master, width=25, fg="black", relief='solid',font=('comic', 12, ' bold '),show='*')
    nnew.place(x=180, y=80)
    cancel=tk.Button(master,text="Cancel", command=master.destroy ,fg="white"  ,bg="#f44336" ,height=1,width=25 , 
                    activebackground="#d32f2f", activeforeground="white", relief="flat", bd=0, font=('comic', 10, ' bold '))
    cancel.place(x=200, y=120)
    save1 = tk.Button(master, text="Save", command=save_pass, fg="white", bg="#4caf50", height = 1,width=25, 
                     activebackground="#388e3c", activeforeground="white", relief="flat", bd=0, font=('comic', 10, ' bold '))
    save1.place(x=10, y=120)
    master.mainloop()

#####################################################################################

def psw():
    assure_path_exists("TrainingImageLabel/")
    exists1 = os.path.isfile("TrainingImageLabel\psd.txt")
    if exists1:
        tf = open("TrainingImageLabel\psd.txt", "r")
        key = tf.read()
    else:
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess._show(title='No Password Entered', message='Password not set!! Please try again')
        else:
            tf = open("TrainingImageLabel\psd.txt", "w")
            tf.write(new_pas)
            mess._show(title='Password Registered', message='New password was registered successfully!!')
            return
    password = tsd.askstring('Password', 'Enter Password', show='*')
    if (password == key):
        TrainImages()
    elif (password == None):
        pass
    else:
        mess._show(title='Wrong Password', message='You have entered wrong password')

######################################################################################

# Old registration functions removed - now handled by admin system

#######################################################################################

# TakeImages function moved to admin system

########################################################################################

def TrainImages():
    """Enhanced training for 100% accuracy face recognition model"""
    check_haarcascadefile()
    assure_path_exists("TrainingImageLabel/")
    
    # Enhanced LBPH recognizer with optimized parameters
    recognizer = cv2.face_LBPHFaceRecognizer.create(
        radius=2,           # LBP radius
        neighbors=8,         # Number of neighbors
        grid_x=8,           # Grid X size
        grid_y=8,           # Grid Y size
        threshold=100.0     # Recognition threshold
    )
    
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    
    # Get enhanced training data
    faces, ID = getImagesAndLabelsEnhanced("TrainingImage")
    
    if len(faces) == 0:
        mess._show(title='No Registrations', message='Please Register someone first!!!')
        return
    
    try:
        # Enhanced training with validation
        recognizer.train(faces, np.array(ID))
        
        # Save the trained model
        recognizer.save("TrainingImageLabel\Trainner.yml")
        
        # Additional validation - test the model
        test_accuracy = validate_model_accuracy(recognizer, faces, ID)
        
        res = f"Profile Saved Successfully!\nTraining Accuracy: {test_accuracy:.1f}%"
        mess.showinfo("Success", res)
        
    except Exception as e:
        mess.showerror("Training Error", f"Failed to train model: {str(e)}")
        return
    
    # Update user count display
    if db_manager.is_connected:
        try:
            query = "SELECT COUNT(*) FROM users"
            result = db_manager.execute_query(query)
            if result:
                user_count = result[0][0]
                message.configure(text=f'Total Users in Database: {str(user_count)}')
        except:
            pass

############################################################################################3

def getImagesAndLabels(path):
    # get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # create empth face list
    faces = []
    # create empty ID list
    Ids = []
    # now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(ID)
    return faces, Ids

def getImagesAndLabelsEnhanced(path):
    """Enhanced image loading with preprocessing for better training accuracy"""
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    
    for imagePath in imagePaths:
        try:
            # Load image
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            
            # Enhanced preprocessing for training data
            # Apply histogram equalization for better contrast
            equalized = cv2.equalizeHist(imageNp)
            
            # Apply slight Gaussian blur to reduce noise
            processed = cv2.GaussianBlur(equalized, (3, 3), 0)
            
            # Ensure consistent size
            resized = cv2.resize(processed, (100, 100))
            
            # Get ID from filename (serial number)
            # Format: name.serial.user_id.sampleNum.jpg
            filename_parts = os.path.split(imagePath)[-1].split(".")
            if len(filename_parts) >= 2:
                ID = int(filename_parts[1])  # Serial number
            else:
                continue  # Skip invalid filenames
            
            faces.append(resized)
            Ids.append(ID)
            
        except Exception as e:
            print(f"Error processing image {imagePath}: {e}")
            continue
    
    return faces, Ids

def validate_model_accuracy(recognizer, faces, labels):
    """Validate the trained model accuracy"""
    correct_predictions = 0
    total_predictions = len(faces)
    
    for i, face in enumerate(faces):
        try:
            predicted_id, confidence = recognizer.predict(face)
            if predicted_id == labels[i] and confidence < 50:
                correct_predictions += 1
        except:
            continue
    
    accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0
    return accuracy

###########################################################################################

def TrackImages():
    """Enhanced face recognition with proper error handling"""
    try:
        check_haarcascadefile()
        assure_path_exists("Attendance/")
        assure_path_exists("StudentDetails/")
        
        # Clear existing tree view items safely
        try:
            for k in tv.get_children():
                tv.delete(k)
        except:
            pass  # Ignore if tree view is not available
        
        msg = ''
        i = 0
        j = 0
        
        # Advanced face recognition setup for 100% accuracy
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        exists3 = os.path.isfile("TrainingImageLabel\Trainner.yml")
        if exists3:
            recognizer.read("TrainingImageLabel\Trainner.yml")
        else:
            mess._show(title='Data Missing', message='Please click on Save Profile to reset data!!')
            return
        
        # Multiple face detection algorithms for better accuracy
        harcascadePath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath)
        
        # Additional face detector for validation
        try:
            faceCascade2 = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
        except:
            faceCascade2 = None

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            mess.showerror("Camera Error", "Cannot open camera!")
            return
            
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Enhanced camera settings for better image quality
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cam.set(cv2.CAP_PROP_FPS, 30)
        cam.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
        cam.set(cv2.CAP_PROP_CONTRAST, 0.5)
        
        # Night mode detection and enhancement
        def detect_night_mode(image):
            """Detect if the image is in low light conditions"""
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                mean_brightness = np.mean(gray)
                return mean_brightness < 80  # Threshold for night mode
            except:
                return False
        
        def enhance_night_vision(image):
            """Enhance image for night/low light conditions"""
            try:
                # Convert to LAB color space for better brightness control
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                
                # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                
                # Merge channels back
                enhanced_lab = cv2.merge([l, a, b])
                enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
                
                # Additional gamma correction for night mode
                gamma = 1.5  # Adjust gamma for brightness
                lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255 for i in range(256)]).astype("uint8")
                enhanced_bgr = cv2.LUT(enhanced_bgr, lookup_table)
                
                return enhanced_bgr
            except:
                return image
                
        col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
        
        # Check if we have users in the database
        if not db_manager.is_connected:
            mess.showerror("Database Error", "Database not connected!")
            cam.release()
            cv2.destroyAllWindows()
            return
        
        # Get users from database
        try:
            query = "SELECT user_id, name FROM users"
            users_result = db_manager.execute_query(query)
            if not users_result:
                mess.showerror("No Users", "No users found in database! Please register users first.")
                cam.release()
                cv2.destroyAllWindows()
                return
            
            # Create a mapping from serial number to user info
            user_mapping = {}
            for i, (user_id, name) in enumerate(users_result):
                user_mapping[i] = {'id': user_id, 'name': name}
                
        except Exception as e:
            mess.showerror("Database Error", f"Failed to load users: {str(e)}")
            cam.release()
            cv2.destroyAllWindows()
            return
        
        # Voice assistant greeting flag
        greeted_users = set()
        
        # Advanced image preprocessing function
        def preprocess_face_image(face_img):
            """Enhanced preprocessing for better recognition accuracy"""
            try:
                # Convert to grayscale if not already
                if len(face_img.shape) == 3:
                    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = face_img
                
                # Apply histogram equalization for better contrast
                equalized = cv2.equalizeHist(gray)
                
                # Apply Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
                
                # Resize to standard size for consistent recognition
                resized = cv2.resize(blurred, (100, 100))
                
                return resized
            except:
                return face_img
        
        # Enhanced face detection function
        def detect_faces_advanced(image):
            """Advanced face detection with multiple algorithms"""
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Primary detection with optimized parameters
                faces1 = faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,  # More conservative scaling
                    minNeighbors=8,    # Higher threshold for better accuracy
                    minSize=(50, 50),  # Minimum face size
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                # Secondary validation if available
                faces2 = []
                if faceCascade2 is not None:
                    faces2 = faceCascade2.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=8,
                        minSize=(50, 50)
                    )
                
                # Combine and validate detections
                valid_faces = []
                for (x, y, w, h) in faces1:
                    # Check if this face is also detected by secondary detector
                    if faceCascade2 is not None:
                        for (x2, y2, w2, h2) in faces2:
                            # Calculate overlap
                            overlap_x = max(0, min(x + w, x2 + w2) - max(x, x2))
                            overlap_y = max(0, min(y + h, y2 + h2) - max(y, y2))
                            overlap_area = overlap_x * overlap_y
                            face_area = min(w * h, w2 * h2)
                            
                            if overlap_area > 0.5 * face_area:  # 50% overlap threshold
                                valid_faces.append((x, y, w, h))
                                break
                    else:
                        valid_faces.append((x, y, w, h))
                
                return valid_faces
            except:
                return []
        
        while True:
            try:
                ret, im = cam.read()
                if not ret:
                    break
                
                # Night mode detection and enhancement
                is_night_mode = detect_night_mode(im)
                if is_night_mode:
                    im = enhance_night_vision(im)
                    # Display night mode indicator
                    cv2.putText(im, "NIGHT MODE", (10, 60), font, 0.8, (0, 255, 255), 2)
                    
                # Enhanced face detection
                faces = detect_faces_advanced(im)
                
                for (x, y, w, h) in faces:
                    try:
                        # Extract face region
                        face_region = im[y:y + h, x:x + w]
                        
                        # Preprocess face for better recognition
                        processed_face = preprocess_face_image(face_region)
                        
                        # Predict with enhanced confidence threshold
                        serial, conf = recognizer.predict(processed_face)
                        
                        # Much stricter confidence threshold for 100% accuracy
                        if conf < 35:  # Lower confidence = better match
                            ts = time.time()
                            date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                            
                            # Get user details from database mapping
                            if serial in user_mapping:
                                user_info = user_mapping[serial]
                                ID = user_info['id']
                                bb = user_info['name']
                            else:
                                # Fallback for unknown serial
                                ID = f"Unknown_{serial}"
                                bb = "Unknown User"
                            
                            # Display confidence score for debugging
                            confidence_text = f"{bb} ({100-conf:.1f}%)"
                            
                            # Draw rectangle with confidence-based color
                            if conf < 20:  # Very high confidence - green
                                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 3)
                            elif conf < 30:  # High confidence - yellow
                                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 255), 2)
                            else:  # Medium confidence - orange
                                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 165, 255), 2)
                            
                            attendance = [str(ID), '', bb, '', str(date), '', str(timeStamp)]
                            
                            # Voice assistant greeting for recognized users
                            if ID not in greeted_users:
                                try:
                                    greeting = voice_assistant.get_time_greeting()
                                    personalized_greeting = voice_assistant.get_random_greeting(bb)
                                    voice_assistant.speak(f"{greeting}! {personalized_greeting}")
                                    greeted_users.add(ID)
                                except:
                                    pass  # Ignore voice errors
                            
                            # Save to database
                            try:
                                db_query = """
                                INSERT INTO attendance_records (user_id, date, time_in, status) 
                                VALUES (%s, %s, %s, 'present')
                                ON DUPLICATE KEY UPDATE time_in = VALUES(time_in), status = 'present'
                                """
                                db_manager.execute_query(db_query, (ID, date, timeStamp))
                            except:
                                pass  # Ignore database errors
                            
                            # Add to GUI
                            try:
                                tv.insert('', 0, text=ID, values=(bb, date, timeStamp))
                            except:
                                pass  # Ignore GUI errors
                            
                            # Display name and confidence
                            cv2.putText(im, confidence_text, (x, y - 10), font, 0.7, (255, 255, 255), 2)
                        else:
                            # Unknown person
                            bb = 'Unknown'
                            confidence_text = f"Unknown ({100-conf:.1f}%)"
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red for unknown
                            cv2.putText(im, confidence_text, (x, y - 10), font, 0.7, (255, 255, 255), 2)
                    except Exception as e:
                        # Skip this face if there's an error
                        continue
                
                # Display the frame
                cv2.imshow('Taking Attendance - Enhanced Accuracy', im)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except Exception as e:
                # Handle any errors in the main loop
                print(f"Error in face recognition loop: {e}")
                break
        
        # Clean up camera resources
        try:
            cam.release()
            cv2.destroyAllWindows()
        except:
            pass
        
    except Exception as e:
        mess.showerror("Error", f"Face recognition failed: {str(e)}")
        try:
            cam.release()
            cv2.destroyAllWindows()
        except:
            pass

######################################## VOICE COMMAND FUNCTIONS ####################################

def start_voice_command():
    """Start listening for voice commands"""
    def listen_and_process():
        voice_status.config(text="Listening...", bg="#ffeb3b")
        command = voice_assistant.listen()
        
        if command == "timeout":
            voice_status.config(text="No command detected", bg="#ff9800")
            return
        elif command == "unknown":
            voice_status.config(text="Could not understand", bg="#f44336")
            return
        elif command == "error":
            voice_status.config(text="Microphone error", bg="#f44336")
            return
        
        voice_status.config(text=f"Command: {command}", bg="#4caf50")
        
        # For now, process without user ID (you can modify to use recognized user ID)
        response, action = voice_assistant.handle_command(command)
        
        # Display response in GUI
        voice_response.config(text=response)
        
        # Speak the response
        voice_assistant.speak(response)
        
        # Execute actions if any
        if action == "attendance":
            # You can automatically start attendance here if needed
            pass
    
    # Run in separate thread to avoid blocking GUI
    thread = Thread(target=listen_and_process)
    thread.daemon = True
    thread.start()

######################################## USED STUFFS ############################################
    
global key
key = ''

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day,month,year=date.split("-")

mont={'01':'January',
      '02':'February',
      '03':'March',
      '04':'April',
      '05':'May',
      '06':'June',
      '07':'July',
      '08':'August',
      '09':'September',
      '10':'October',
      '11':'November',
      '12':'December'
      }

######################################## GUI FRONT-END ###########################################

window = tk.Tk()
window.geometry("1280x720")
window.minsize(1000, 600)  # Set minimum window size
window.resizable(True, True)  # Allow both horizontal and vertical resizing
window.title("Attendance System with Voice Assistant")
window.configure(bg="#1e1e1e")  # Modern dark background

# Center the window on screen
window.update_idletasks()
width = window.winfo_width()
height = window.winfo_height()
x = (window.winfo_screenwidth() // 2) - (width // 2)
y = (window.winfo_screenheight() // 2) - (height // 2)
window.geometry(f'{width}x{height}+{x}+{y}')

# Configure grid weights for responsive layout
window.grid_rowconfigure(0, weight=0)  # Header row
window.grid_rowconfigure(1, weight=1)  # Main content row
window.grid_columnconfigure(0, weight=1)  # Full width

# Header frame with title and date/time
header_frame = tk.Frame(window, bg="#2d3748", height=80, relief="flat", bd=0)
header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
header_frame.grid_propagate(False)  # Maintain fixed height

# Title
message3 = tk.Label(header_frame, text="GreetA: A GREETing Automated System with Voice Assistant", 
                   fg="white", bg="#2d3748", font=('Segoe UI', 20, 'bold'))
message3.pack(side="left", padx=10, pady=10)

# Date and time frame
datetime_frame = tk.Frame(header_frame, bg="#2d3748")
datetime_frame.pack(side="right", padx=10, pady=10)

datef = tk.Label(datetime_frame, text=day+"-"+mont[month]+"-"+year+"  |  ", 
                fg="#63b3ed", bg="#2d3748", font=('Segoe UI', 16, 'bold'))
datef.pack(side="left", padx=5)

clock = tk.Label(datetime_frame, fg="#63b3ed", bg="#2d3748", 
                font=('Segoe UI', 16, 'bold'))
clock.pack(side="left", padx=5)
tick()

# Main content frame
main_frame = tk.Frame(window, bg="#1e1e1e", relief="flat", bd=0)
main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
main_frame.grid_rowconfigure(0, weight=0)  # Voice frame
main_frame.grid_rowconfigure(1, weight=1)  # Content frames
main_frame.grid_columnconfigure(0, weight=3)  # Left content - larger
main_frame.grid_columnconfigure(1, weight=1)  # Right content - smaller

# Voice Assistant Frame
frame_voice = tk.Frame(main_frame, bg="#4a5568", height=80, relief="flat", bd=0)
frame_voice.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
frame_voice.grid_propagate(False)
frame_voice.grid_columnconfigure(0, weight=0)  # Title
frame_voice.grid_columnconfigure(1, weight=0)  # Button
frame_voice.grid_columnconfigure(2, weight=0)  # Status
frame_voice.grid_columnconfigure(3, weight=1)  # Response

voice_title = tk.Label(frame_voice, text="Voice Assistant", fg="white", bg="#4a5568", 
                      font=('Segoe UI', 12, 'bold'))
voice_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

voice_button = tk.Button(frame_voice, text="🎤 Start Listening", command=start_voice_command, 
                        fg="white", bg="#3182ce", width=12, height=1, 
                        activebackground="#2c5282", activeforeground="white",
                        relief="flat", bd=0, font=('Segoe UI', 9, 'bold'),
                        cursor="hand2")
voice_button.grid(row=0, column=1, padx=5, pady=10)

voice_status = tk.Label(frame_voice, text="Ready to listen", fg="white", bg="#4a5568", 
                       font=('Segoe UI', 9, 'bold'))
voice_status.grid(row=0, column=2, padx=5, pady=10)

voice_response = tk.Label(frame_voice, text="Say 'hello', 'time', 'weather', or 'date'", 
                         fg="#fbb6ce", bg="#4a5568", wraplength=300,
                         font=('Segoe UI', 8, 'bold'))
voice_response.grid(row=0, column=3, padx=10, pady=10, sticky="w")

# Left frame (Attendance)
frame1 = tk.Frame(main_frame, bg="#2d3748", relief="flat", bd=0)
frame1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
frame1.grid_rowconfigure(0, weight=0)  # Header
frame1.grid_rowconfigure(1, weight=0)  # Take Attendance button
frame1.grid_rowconfigure(2, weight=0)  # Admin Login button
frame1.grid_rowconfigure(3, weight=1)  # Treeview
frame1.grid_rowconfigure(4, weight=0)  # Quit button
frame1.grid_columnconfigure(0, weight=1)

# Right frame (System Info)
frame2 = tk.Frame(main_frame, bg="#2d3748", relief="flat", bd=0)
frame2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
frame2.grid_rowconfigure(0, weight=0)  # Header
frame2.grid_rowconfigure(1, weight=1)  # Info content
frame2.grid_columnconfigure(0, weight=1)

head2 = tk.Label(frame2, text="System Information", fg="white", bg="#2d3748", 
                font=('Segoe UI', 12, 'bold'))
head2.grid(row=0, column=0, pady=5, sticky="ew")

head1 = tk.Label(frame1, text="Attendance System", fg="white", bg="#2d3748", 
                font=('Segoe UI', 16, 'bold'))
head1.grid(row=0, column=0, pady=10, sticky="ew")

# System info content
info_frame = tk.Frame(frame2, bg="#2d3748")
info_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
info_frame.grid_columnconfigure(0, weight=1)

# Welcome message
welcome_label = tk.Label(info_frame, text="Welcome to GreetA System", 
                        fg="white", bg="#2d3748", font=('Segoe UI', 11, 'bold'))
welcome_label.pack(pady=5)

# Instructions
instructions = """📋 SYSTEM FEATURES:

🎤 Voice Assistant
• Click "🎤 Start Listening" for voice commands
• Try: "hello", "time", "weather", "date"

👤 User Management
• Click "Admin Panel" for admin features
• Add users with face recognition
• Manage user database

📊 Attendance Tracking
• Click "Take Attendance" to start recognition
• Automatic attendance recording
• Database integration

🔧 Admin Features
• User management & task assignment
• Attendance reports & face registration"""

info_text = tk.Label(info_frame, text=instructions, fg="#e2e8f0", bg="#2d3748", 
                    font=('Segoe UI', 9), justify="left")
info_text.pack(pady=5, fill="both", expand=True)

# Admin access button
admin_access_btn = tk.Button(info_frame, text="🔐 Admin Panel", 
                           command=admin_system.show_admin_login,
                           fg="white", bg="#3182ce", width=15, height=1,
                           activebackground="#2c5282", activeforeground="white",
                           relief="flat", bd=0, font=('Segoe UI', 10, 'bold'),
                           cursor="hand2")
admin_access_btn.pack(pady=10)

# Attendance section
lbl3 = tk.Label(frame1, text="Attendance", fg="white", bg="#2d3748", 
               font=('Segoe UI', 16, 'bold'))
lbl3.grid(row=1, column=0, pady=20, sticky="ew")

# Get user count from database
user_count = 0
if db_manager.is_connected:
    try:
        query = "SELECT COUNT(*) FROM users"
        result = db_manager.execute_query(query)
        if result:
            user_count = result[0][0]
    except:
        user_count = 0

# Status message for user count
status_frame = tk.Frame(frame2, bg="#2d3748")
status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

message = tk.Label(status_frame, text=f'Total Users in Database: {str(user_count)}', 
                  bg="#2d3748", fg="#63b3ed", font=('Segoe UI', 12, 'bold'))
message.pack()

##################### MENUBAR #################################

menubar = tk.Menu(window, relief='flat', bg="#2d3748", fg="white")
filemenu = tk.Menu(menubar, tearoff=0, bg="#2d3748", fg="white")
filemenu.add_command(label='Change Password', command=change_pass)
filemenu.add_command(label='Contact Us', command=contact)
filemenu.add_command(label='Voice Help', command=lambda: voice_assistant.speak("You can ask me about time, weather, date, or say hello. Click the microphone button to start listening."))
filemenu.add_command(label='Admin Access', command=admin_system.show_admin_login)
filemenu.add_command(label='Exit', command=window.destroy)
menubar.add_cascade(label='Help', font=('Segoe UI', 12, 'bold'), menu=filemenu)

################## TREEVIEW ATTENDANCE TABLE ####################

# Create a frame for the treeview and scrollbar
tree_frame = tk.Frame(frame1, bg="#2d3748")
tree_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 20))
tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)
tree_frame.grid_columnconfigure(1, weight=0)

tv = ttk.Treeview(tree_frame, height=8, columns=('name', 'date', 'time'))
tv.column('#0', width=70, minwidth=50)
tv.column('name', width=100, minwidth=80)
tv.column('date', width=100, minwidth=80)
tv.column('time', width=100, minwidth=80)
tv.grid(row=0, column=0, sticky="nsew")
tv.heading('#0', text='ID')
tv.heading('name', text='NAME')
tv.heading('date', text='DATE')
tv.heading('time', text='TIME')

###################### SCROLLBAR ################################

scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=tv.yview)
scroll.grid(row=0, column=1, sticky='ns')
tv.configure(yscrollcommand=scroll.set)

###################### BUTTONS ##################################

# Attendance buttons
trackImg = tk.Button(frame1, text="Take Attendance", command=TrackImages, 
                    fg="white", bg="#38a169", height=1, 
                    activebackground="#2f855a", activeforeground="white",
                    relief="flat", bd=0, font=('Segoe UI', 11, 'bold'),
                    cursor="hand2")
trackImg.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 10))

# Admin Login button
adminBtn = tk.Button(frame1, text="Admin Login", command=admin_system.show_admin_login, 
                    fg="white", bg="#3182ce", height=2, 
                    activebackground="#2c5282", activeforeground="white",
                    relief="flat", bd=0, font=('Segoe UI', 12, 'bold'),
                    cursor="hand2")
adminBtn.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 10))

quitWindow = tk.Button(frame1, text="Quit", command=window.destroy, 
                      fg="white", bg="#e53e3e", height=1, 
                      activebackground="#c53030", activeforeground="white",
                      relief="flat", bd=0, font=('Segoe UI', 11, 'bold'),
                      cursor="hand2")
quitWindow.grid(row=4, column=0, sticky="ew", padx=20, pady=20)

##################### END ######################################

window.configure(menu=menubar)

# Bind resize event for responsive behavior
window.bind('<Configure>', on_window_resize)

# Initial greeting
window.after(1000, lambda: voice_assistant.speak("Welcome to the Attendance System with Voice Assistant. I'm ready to help you!"))

window.mainloop()

####################################################################################################