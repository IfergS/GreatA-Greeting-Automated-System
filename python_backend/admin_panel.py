############################################# ADMIN PANEL ################################################
import customtkinter as ctk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
from tkinter import ttk
import cv2
import os
import csv
import json
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import shutil
import speech_recognition as sr
import pyttsx3
import time
from threading import Thread

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modern 3-Color Aesthetic Palette
UI_COLORS = {
    "primary": "#1a1a2e",      # Deep Navy - Main background
    "secondary": "#16213e",    # Darker Navy - Cards and panels  
    "accent": "#2196F3",       # Blue - Single accent color for all buttons and highlights
    "text_primary": "#ffffff", # White - Primary text
    "text_secondary": "#bdc3c7", # Light Gray - Secondary text
    "text_muted": "#7f8c8d",   # Muted Gray - Muted text
    # Legacy colors mapped to three-color scheme
    "highlight": "#2196F3",    # Same as accent
    "success": "#2196F3",      # Same as accent
    "warning": "#2196F3",      # Same as accent
    "border": "#2196F3",       # Same as accent
    "surface": "#16213e"       # Same as secondary
}

############################################# VOICE REGISTRATION ################################################

class VoiceRegistration:
    """Handle voice registration for faculty members"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        voices = self.tts_engine.getProperty('voices')
        american_voice = None
        for voice in voices:
            if 'en_US' in voice.id or 'en-US' in voice.id or 'US' in voice.name:
                american_voice = voice.id
                break
            elif 'en' in voice.id.lower() or 'english' in voice.name.lower():
                american_voice = voice.id
        
        if american_voice:
            self.tts_engine.setProperty('voice', american_voice)
        
        self.tts_engine.setProperty('rate', 200)
        self.tts_engine.setProperty('volume', 1.0)
    
    def speak(self, text):
        """Speak text"""
        try:
            print(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Voice error: {e}")
    
    def listen(self):
        """Listen for voice input"""
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
    
    def register_voice_sample(self, faculty_id, faculty_name, sample_text="Hello, this is my voice sample"):
        """Register a voice sample for a faculty member"""
        try:
            self.speak(f"Please say: {sample_text}")
            
            # Listen for the voice sample
            voice_text = self.listen()
            
            if voice_text == "timeout":
                return False, "No voice detected. Please try again."
            elif voice_text == "unknown":
                return False, "Could not understand. Please speak clearly."
            elif voice_text == "error":
                return False, "Microphone error. Please check your microphone."
            
            # Save voice sample to file
            voice_samples_dir = os.path.join("VoiceSamples", faculty_id)
            os.makedirs(voice_samples_dir, exist_ok=True)
            
            voice_file = os.path.join(voice_samples_dir, f"{faculty_name}_voice_sample.txt")
            with open(voice_file, 'w', encoding='utf-8') as f:
                f.write(voice_text)
            
            return True, f"Voice sample registered successfully for {faculty_name}"
            
        except Exception as e:
            return False, f"Error registering voice sample: {str(e)}"
    
    def verify_voice(self, faculty_id, faculty_name):
        """Verify voice against registered sample"""
        try:
            voice_samples_dir = os.path.join("VoiceSamples", faculty_id)
            voice_file = os.path.join(voice_samples_dir, f"{faculty_name}_voice_sample.txt")
            
            if not os.path.exists(voice_file):
                return False, "No voice sample found for this faculty member"
            
            # Read registered voice sample
            with open(voice_file, 'r', encoding='utf-8') as f:
                registered_text = f.read().strip().lower()
            
            self.speak("Please say your registered phrase for verification")
            
            # Listen for verification
            voice_text = self.listen()
            
            if voice_text == "timeout":
                return False, "No voice detected. Please try again."
            elif voice_text == "unknown":
                return False, "Could not understand. Please speak clearly."
            elif voice_text == "error":
                return False, "Microphone error. Please check your microphone."
            
            # Simple text comparison (in real implementation, use voice recognition algorithms)
            if voice_text.lower().strip() == registered_text:
                return True, "Voice verification successful"
            else:
                return False, "Voice verification failed. Please try again."
                
        except Exception as e:
            return False, f"Error verifying voice: {str(e)}"

# Global voice registration instance
voice_registration = VoiceRegistration()

############################################# ADMIN AUTHENTICATION ################################################

def authenticate_admin():
    """Read admin credentials (username and password) with backward compatibility."""
    psd_path = os.path.join("TrainingImageLabel", "psd.txt")
    
    # Create default credentials if not exists
    if not os.path.isfile(psd_path):
        os.makedirs("TrainingImageLabel", exist_ok=True)
        with open(psd_path, "w") as f:
            # Store as username:password for future compatibility
            f.write("admin:admin123")
        mess.showinfo(
            "Default Credentials",
            "Default admin username/password is:\nUsername: admin\nPassword: admin123\nPlease change it after login!"
        )
        return ("admin", "admin123")
    
    with open(psd_path, "r") as f:
        content = f.read().strip()
        # Backward compatibility: if file contains only password, assume username 'admin'
        if ":" in content:
            parts = content.split(":", 1)
            return (parts[0], parts[1])
        else:
            return ("admin", content)

def check_password():
    """Verify admin username and password."""
    correct_username, correct_password = authenticate_admin()
    username = tsd.askstring('Admin Login', 'Enter Admin Username:')
    if username is None:
        return False
    password = tsd.askstring('Admin Login', 'Enter Admin Password:', show='*')
    
    if password is None:
        return False
    
    if username == correct_username and password == correct_password:
        return True
    else:
        mess.showerror('Access Denied', 'Incorrect username or password!')
        return False

############################################# MODERN LOGIN UI ################################################

def show_login_window():
    """Display a modern login window and return True if authenticated."""
    creds_username, creds_password = authenticate_admin()
    
    # Three-color scheme: Background, Card, Accent
    COLOR_BG = "#f5f5f5"      # Light gray background
    COLOR_CARD = "#ffffff"     # White card
    COLOR_ACCENT = "#2196F3"   # Blue accent for buttons
    
    login_success = {"ok": False}
    remember_file = os.path.join("TrainingImageLabel", "remember_me.json")
    remembered_username = ""
    try:
        if os.path.isfile(remember_file):
            with open(remember_file, 'r') as f:
                data = json.load(f)
                remembered_username = data.get("username", "")
    except Exception:
        remembered_username = ""
    
    win = ctk.CTk()
    win.title("GreetA - Admin Login")
    win.geometry("800x520")
    win.resizable(False, False)
    win.configure(fg_color=COLOR_BG)
    
    # Center card - white
    card = ctk.CTkFrame(win, width=560, height=380, fg_color=COLOR_CARD, corner_radius=18)
    card.place(relx=0.5, rely=0.5, anchor="center")
    
    # User icon - using accent color
    user_icon = ctk.CTkLabel(card, text="", width=96, height=96, fg_color=COLOR_BG,
                 corner_radius=48)
    user_icon.place(relx=0.5, y=70, anchor="center")
    ctk.CTkLabel(card, text="", width=40, height=40, fg_color=COLOR_ACCENT,
                 corner_radius=20).place(relx=0.5, y=70, anchor="center")
    
    form_frame = ctk.CTkFrame(card, fg_color="transparent")
    form_frame.place(relx=0.5, rely=0.55, anchor="center")
    
    username_entry = ctk.CTkEntry(form_frame, width=420, height=44, placeholder_text="Username",
                                  border_color=COLOR_BG, fg_color=COLOR_BG)
    username_entry.grid(row=0, column=0, padx=6, pady=8)
    if remembered_username:
        username_entry.insert(0, remembered_username)
    
    password_entry = ctk.CTkEntry(form_frame, width=420, height=44, placeholder_text="Password", 
                                  show='*', border_color=COLOR_BG, fg_color=COLOR_BG)
    password_entry.grid(row=1, column=0, padx=6, pady=8)
    
    bottom_row = ctk.CTkFrame(form_frame, fg_color="transparent")
    bottom_row.grid(row=2, column=0, sticky="we", pady=(6, 2))
    remember_var = ctk.BooleanVar(value=bool(remembered_username))
    remember_cb = ctk.CTkCheckBox(bottom_row, text="Remember me", variable=remember_var,
                                  fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT)
    remember_cb.pack(side="left")
    
    def forgot_password():
        mess.showinfo(
            "Forgot Password",
            "If you forgot the password, please contact the system owner.\n"
            "You can reset by deleting 'TrainingImageLabel/psd.txt' to restore defaults (admin/admin123)."
        )
    
    forgot_btn = ctk.CTkButton(bottom_row, text="Forgot Password?", width=10, height=28,
                               fg_color="transparent", hover_color=COLOR_BG,
                               text_color=COLOR_ACCENT, command=forgot_password)
    forgot_btn.pack(side="right")
    
    status_label = ctk.CTkLabel(form_frame, text="", text_color="#1976D2")
    status_label.grid(row=3, column=0, pady=(0, 6))
    
    def attempt_login():
        u = username_entry.get().strip()
        p = password_entry.get()
        if not u or not p:
            status_label.configure(text="Please enter username and password")
            return
        if u == creds_username and p == creds_password:
            # Persist remember me
            try:
                os.makedirs("TrainingImageLabel", exist_ok=True)
                if remember_var.get():
                    with open(remember_file, 'w') as f:
                        json.dump({"username": u}, f)
                else:
                    if os.path.isfile(remember_file):
                        os.remove(remember_file)
            except Exception:
                pass
            login_success["ok"] = True
            win.destroy()
        else:
            status_label.configure(text="Incorrect username or password")
    
    login_btn = ctk.CTkButton(form_frame, text="LOGIN", width=420, height=44,
                              fg_color=COLOR_ACCENT, hover_color="#1976D2",
                              command=attempt_login)
    login_btn.grid(row=4, column=0, pady=(6, 2))
    
    # Bind Return key
    win.bind('<Return>', lambda _e: attempt_login())
    
    win.mainloop()
    return login_success["ok"]

############################################# HELPER FUNCTIONS ################################################

def assure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        mess.showerror('File Missing', 'haarcascade_frontalface_default.xml not found!')
        return False
    return True

def load_faculty():
    """Load all faculty from CSV"""
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    if os.path.isfile(faculty_details_path):
        df = pd.read_csv(faculty_details_path, encoding='latin-1')
        return df
    return pd.DataFrame(columns=['SERIAL NO.', '', 'ID', '', 'NAME'])

def save_faculty(df):
    """Save faculty to CSV"""
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    df.to_csv(faculty_details_path, index=False)

def load_tasks():
    """Load all tasks from CSV"""
    tasks_path = os.path.join("Tasks", "Tasks.csv")
    assure_path_exists("Tasks")
    if os.path.isfile(tasks_path):
        df = pd.read_csv(tasks_path, encoding='latin-1')
        return df
    else:
        # Create tasks file with headers
        df = pd.DataFrame(columns=['TASK_ID', 'FACULTY_ID', 'FACULTY_NAME', 'TASK_TITLE', 
                                   'TASK_DESCRIPTION', 'DUE_DATE', 'PRIORITY', 'STATUS'])
        df.to_csv(tasks_path, index=False)
        return df

def save_tasks(df):
    """Save tasks to CSV"""
    tasks_path = os.path.join("Tasks", "Tasks.csv")
    df.to_csv(tasks_path, index=False)

def get_tasks_for_faculty(faculty_id, date_str=None):
    """Get tasks for a specific faculty member"""
    df = load_tasks()
    if date_str is None:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Filter by faculty ID and due date
    tasks = df[(df['FACULTY_ID'] == faculty_id) & (df['DUE_DATE'] == date_str) & (df['STATUS'] != 'Completed')]
    return tasks

############################################# ADMIN PANEL CLASS ################################################

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 GreetA - Admin Panel")
        self.root.geometry("1400x800")
        self.root.configure(fg_color=UI_COLORS["primary"])
        
        # Header
        self.create_header()
        
        # Navigation
        self.create_navigation()
        
        # Content Area with modern design
        self.content_frame = ctk.CTkFrame(
            self.root, 
            fg_color=UI_COLORS["primary"],
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def register_voice_for_faculty(self, faculty_id, faculty_name):
        """Register voice sample for a faculty member"""
        def register_voice():
            try:
                self.voice_status.configure(text="🎤 Registering voice sample...", text_color=UI_COLORS["accent"])
                
                success, message = voice_registration.register_voice_sample(faculty_id, faculty_name)
                
                if success:
                    self.voice_status.configure(text="✅ Voice registered successfully!", text_color=UI_COLORS["success"])
                    mess.showinfo("Voice Registration", message)
                else:
                    self.voice_status.configure(text="❌ Voice registration failed", text_color=UI_COLORS["warning"])
                    mess.showerror("Voice Registration Error", message)
                
            except Exception as e:
                self.voice_status.configure(text="❌ Voice registration error", text_color=UI_COLORS["warning"])
                mess.showerror("Voice Registration Error", f"Error: {str(e)}")
        
        # Run in background thread
        thread = Thread(target=register_voice, daemon=True)
        thread.start()
    
    def verify_voice_for_faculty(self, faculty_id, faculty_name):
        """Verify voice for a faculty member"""
        def verify_voice():
            try:
                self.voice_status.configure(text="🎤 Verifying voice...", text_color=UI_COLORS["accent"])
                
                success, message = voice_registration.verify_voice(faculty_id, faculty_name)
                
                if success:
                    self.voice_status.configure(text="✅ Voice verified successfully!", text_color=UI_COLORS["success"])
                    mess.showinfo("Voice Verification", message)
                else:
                    self.voice_status.configure(text="❌ Voice verification failed", text_color=UI_COLORS["warning"])
                    mess.showerror("Voice Verification Error", message)
                
            except Exception as e:
                self.voice_status.configure(text="❌ Voice verification error", text_color=UI_COLORS["warning"])
                mess.showerror("Voice Verification Error", f"Error: {str(e)}")
        
        # Run in background thread
        thread = Thread(target=verify_voice, daemon=True)
        thread.start()
    
    def create_header(self):
        """Create header section with enhanced modern design"""
        header = ctk.CTkFrame(
            self.root, 
            height=100, 
            corner_radius=0,
            fg_color=UI_COLORS["secondary"],
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Header content container
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=20)
        
        # Left side - Title and subtitle
        left_header = ctk.CTkFrame(header_content, fg_color="transparent")
        left_header.pack(side="left", fill="y", expand=True)
        
        # Main title with modern styling
        title = ctk.CTkLabel(
            left_header,
            text="🔐 Admin Control Panel",
            font=("Arial Bold", 38),
            text_color=UI_COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(8, 2))
        
        # Subtitle with accent color
        subtitle = ctk.CTkLabel(
            left_header,
            text="✨ Faculty Management & System Administration ✨",
            font=("Arial", 13),
            text_color=UI_COLORS["accent"]
        )
        subtitle.pack(anchor="w", pady=(0, 8))
        
        # Right side - Date, Time, and Status
        right_header = ctk.CTkFrame(header_content, fg_color="transparent")
        right_header.pack(side="right", fill="y")
        
        # Date and time frame
        datetime_frame = ctk.CTkFrame(
            right_header,
            fg_color=UI_COLORS["accent"],
            corner_radius=12,
            border_width=1,
            border_color=UI_COLORS["accent"]
        )
        datetime_frame.pack(pady=5)
        
        # Date label
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
        day, month, year = date.split("-")
        mont = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June',
                '07':'July', '08':'August', '09':'September', '10':'October', '11':'November', '12':'December'}
        
        self.date_label = ctk.CTkLabel(
            datetime_frame,
            text=f"📅 {day} {mont[month]} {year}",
            font=("Arial Bold", 12),
            text_color=UI_COLORS["text_primary"]
        )
        self.date_label.pack(padx=15, pady=5)
        
        # Clock label
        self.clock_label = ctk.CTkLabel(
            datetime_frame,
            text="",
            font=("Arial Bold", 12),
            text_color=UI_COLORS["text_primary"]
        )
        self.clock_label.pack(padx=15, pady=(0, 5))
        
        def update_clock():
            time_string = time.strftime('%H:%M:%S')
            self.clock_label.configure(text=f"⏰ {time_string}")
            self.clock_label.after(200, update_clock)
        
        update_clock()
        
        # Voice status indicator
        self.voice_status = ctk.CTkLabel(
            right_header,
            text="🎤 Voice System Ready",
            font=("Arial Bold", 12),
            text_color=UI_COLORS["text_secondary"]
        )
        self.voice_status.pack(pady=5)
    
    def create_navigation(self):
        """Create navigation buttons with enhanced modern design"""
        nav_frame = ctk.CTkFrame(
            self.root, 
            height=75, 
            fg_color=UI_COLORS["secondary"],
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        nav_frame.pack(fill="x", padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # Store current active button
        self.active_nav_button = None
        
        button_config = {
            "height": 48,
            "font": ("Arial Bold", 14),
            "corner_radius": 15,
            "border_width": 2
        }
        
        buttons_info = [
            ("📊 Dashboard", self.show_dashboard, UI_COLORS["accent"]),
            ("➕ Add Faculty", self.show_add_faculty, UI_COLORS["accent"]),
            ("📋 View Faculty", self.show_view_faculty, UI_COLORS["accent"]),
            ("📝 Manage Tasks", self.show_manage_tasks, UI_COLORS["accent"]),
            ("📈 Attendance Records", self.show_attendance_records, UI_COLORS["accent"]),
            ("⚙️ Settings", self.show_settings, UI_COLORS["accent"]),
        ]
        
        self.nav_buttons = {}
        for text, command, color in buttons_info:
            def make_command(cmd, btn_text):
                def nav_command():
                    # Reset previous active button
                    if self.active_nav_button and self.active_nav_button != btn_text:
                        prev_btn = self.nav_buttons.get(self.active_nav_button)
                        if prev_btn:
                            prev_color = next((c for t, _, c in buttons_info if t == self.active_nav_button), UI_COLORS["accent"])
                            prev_btn.configure(fg_color=prev_color, hover_color=self.darken_color(prev_color))
                    
                    # Set new active button
                    self.active_nav_button = btn_text
                    current_btn = self.nav_buttons.get(btn_text)
                    if current_btn:
                        # Active button uses lighter shade of accent
                        current_btn.configure(fg_color="#42a5f5", hover_color="#1e88e5")
                    
                    cmd()
                return nav_command
            
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=make_command(command, text),
                fg_color=color,
                hover_color=self.darken_color(color),
                border_color=color,
                **button_config
            )
            btn.pack(side="left", padx=10, pady=13)
            self.nav_buttons[text] = btn
        
        # Set dashboard as active initially
        self.active_nav_button = "📊 Dashboard"
        self.nav_buttons["📊 Dashboard"].configure(
            fg_color="#42a5f5",
            hover_color="#1e88e5"
        )
        
        # Logout button on the right side with modern styling
        def logout():
            confirm = mess.askyesno("Logout", "🚪 Are you sure you want to logout?")
            if confirm:
                self.root.destroy()
        
        logout_btn = ctk.CTkButton(
            nav_frame,
            text="🚪 Logout",
            command=logout,
            fg_color=UI_COLORS["accent"],
            hover_color=self.darken_color(UI_COLORS["accent"]),
            border_color=UI_COLORS["accent"],
            **button_config
        )
        logout_btn.pack(side="right", padx=20, pady=13)
    
    def darken_color(self, color):
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darkened)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard with modern statistics"""
        self.clear_content()
        
        # Modern title with accent styling
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Dashboard Overview",
            font=("Arial Bold", 32),
            text_color=UI_COLORS["text_primary"]
        )
        title.pack(pady=25)
        
        # Statistics Frame with modern design
        stats_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_COLORS["secondary"],
            corner_radius=20,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        stats_frame.pack(fill="x", padx=40, pady=25)
        
        # Count faculty
        df = load_faculty()
        total_faculty = len(df) // 2 if len(df) > 0 else 0
        
        # Count training images
        image_count = 0
        if os.path.exists("TrainingImage"):
            image_count = len([f for f in os.listdir("TrainingImage") if f.endswith(('.jpg', '.png', '.jpeg'))])
        
        # Count attendance files
        attendance_count = 0
        if os.path.exists("Attendance"):
            attendance_count = len([f for f in os.listdir("Attendance") if f.endswith('.csv')])
        
        # Display stats with enhanced modern styling (three-color scheme)
        stats = [
            ("👥 Total Faculty", total_faculty, UI_COLORS["accent"]),
            ("📸 Training Images", image_count, UI_COLORS["accent"]),
            ("📅 Attendance Days", attendance_count, UI_COLORS["accent"]),
        ]
        
        for label, value, color in stats:
            stat_card = ctk.CTkFrame(
                stats_frame, 
                width=350, 
                height=160, 
                fg_color=color,
                corner_radius=18,
                border_width=3,
                border_color=UI_COLORS["text_primary"]
            )
            stat_card.pack(side="left", padx=20, pady=20, expand=True)
            stat_card.pack_propagate(False)
            
            # Icon and label container
            label_frame = ctk.CTkFrame(stat_card, fg_color="transparent")
            label_frame.pack(pady=(20, 5))
            
            ctk.CTkLabel(
                label_frame,
                text=label,
                font=("Arial Bold", 18),
                text_color=UI_COLORS["text_primary"]
            ).pack()
            
            # Value with enhanced styling
            value_label = ctk.CTkLabel(
                stat_card,
                text=str(value),
                font=("Arial Bold", 48),
                text_color=UI_COLORS["text_primary"]
            )
            value_label.pack(pady=10)
            
            # Decorative line
            line = ctk.CTkFrame(
                stat_card,
                height=3,
                fg_color=UI_COLORS["text_primary"],
                corner_radius=2
            )
            line.pack(fill="x", padx=30, pady=(0, 15))
        
        # Recent Activity with modern design
        recent_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=UI_COLORS["secondary"],
            corner_radius=20,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        recent_frame.pack(fill="both", expand=True, padx=40, pady=25)
        
        ctk.CTkLabel(
            recent_frame,
            text="📋 Recent Faculty Members",
            font=("Arial Bold", 24),
            text_color=UI_COLORS["text_primary"]
        ).pack(pady=20)
        
        if len(df) > 0:
            # Show last 5 faculty members with modern cards
            for idx, row in df.tail(5).iterrows():
                if pd.notna(row.get('ID')):
                    faculty_card = ctk.CTkFrame(
                        recent_frame, 
                        fg_color=UI_COLORS["primary"],
                        corner_radius=12,
                        border_width=1,
                        border_color=UI_COLORS["accent"]
                    )
                    faculty_card.pack(fill="x", padx=25, pady=8)
                    
                    info_text = f"🆔 {row['ID']}  |  👤 {row['NAME']}"
                    ctk.CTkLabel(
                        faculty_card,
                        text=info_text,
                        font=("Arial Bold", 16),
                        text_color=UI_COLORS["text_primary"]
                    ).pack(pady=15, padx=25)
        else:
            empty_frame = ctk.CTkFrame(
                recent_frame,
                fg_color=UI_COLORS["primary"],
                corner_radius=12
            )
            empty_frame.pack(fill="both", expand=True, padx=25, pady=25)
            
            ctk.CTkLabel(
                empty_frame,
                text="📭 No faculty registered yet",
                font=("Arial Bold", 18),
                text_color=UI_COLORS["text_muted"]
            ).pack(pady=30)
            
            ctk.CTkLabel(
                empty_frame,
                text="Use the 'Add Faculty' button to register new members",
                font=("Arial", 14),
                text_color=UI_COLORS["text_secondary"]
            ).pack(pady=(0, 30))
    
    def show_add_faculty(self):
        """Show enhanced add faculty interface"""
        self.clear_content()
        
        # Header with three-color scheme
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=UI_COLORS["accent"], height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="➕ Register New Faculty Member",
            font=("Arial Bold", 32),
            text_color=UI_COLORS["text_primary"]
        )
        title.pack(pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Complete the form below to add a new faculty member to the system",
            font=("Arial", 14),
            text_color=UI_COLORS["text_secondary"]
        ).pack()
        
        # Main form container
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=40)
        
        # Left side - Form
        form_frame = ctk.CTkFrame(main_container, width=500, fg_color=UI_COLORS["secondary"], 
                                 border_width=2, border_color=UI_COLORS["accent"], corner_radius=15)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(
            form_frame,
            text="📝 Faculty Information",
            font=("Arial Bold", 22),
            text_color=UI_COLORS["accent"]
        ).pack(pady=20, padx=20, anchor="w")
        
        # Faculty ID Section
        id_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        id_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            id_frame,
            text="Faculty ID:",
            font=("Arial Bold", 16),
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        id_entry = ctk.CTkEntry(
            id_frame,
            width=450,
            height=45,
            font=("Arial", 14),
            placeholder_text="e.g., FAC-2024-001",
            border_width=2,
            border_color=UI_COLORS["accent"],
            corner_radius=10,
            fg_color=UI_COLORS["primary"]
        )
        id_entry.pack(pady=5)
        
        ctk.CTkLabel(
            id_frame,
            text="💡 Use unique identifier (letters, numbers, dashes)",
            font=("Arial", 11),
            text_color=UI_COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))
        
        # Faculty Name Section
        name_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            name_frame,
            text="Faculty Name:",
            font=("Arial Bold", 16),
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            name_frame,
            width=450,
            height=45,
            font=("Arial", 14),
            placeholder_text="Enter full name (First Last)",
            border_width=2,
            border_color=UI_COLORS["accent"],
            corner_radius=10,
            fg_color=UI_COLORS["primary"]
        )
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="💡 Full name with proper capitalization",
            font=("Arial", 11),
            text_color=UI_COLORS["text_muted"]
        ).pack(anchor="w", pady=(2, 0))
        
        # Status/Progress Section
        status_frame = ctk.CTkFrame(form_frame, fg_color=UI_COLORS["primary"], 
                                   corner_radius=12, border_width=2, border_color=UI_COLORS["accent"])
        status_frame.pack(fill="x", padx=20, pady=20)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="📋 Ready to capture images",
            font=("Arial Bold", 14),
            text_color=UI_COLORS["accent"]
        )
        status_label.pack(pady=15, padx=20)
        
        progress_bar = ctk.CTkProgressBar(status_frame, width=410, height=22, 
                                          progress_color=UI_COLORS["accent"])
        progress_bar.pack(pady=(0, 15), padx=20)
        progress_bar.set(0)
        
        # Right side - Instructions
        info_frame = ctk.CTkFrame(main_container, width=350, fg_color=UI_COLORS["secondary"],
                                 border_width=2, border_color=UI_COLORS["accent"], corner_radius=15)
        info_frame.pack(side="right", fill="both", padx=(20, 0))
        info_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            info_frame,
            text="📸 Photo Capture Guidelines",
            font=("Arial Bold", 20),
            text_color=UI_COLORS["accent"]
        ).pack(pady=20, padx=20, anchor="w")
        
        guidelines = [
            ("✓", "Ensure good lighting conditions", UI_COLORS["accent"]),
            ("✓", "Face the camera directly", UI_COLORS["accent"]),
            ("✓", "Neutral facial expression", UI_COLORS["accent"]),
            ("✓", "Remove sunglasses/masks", UI_COLORS["accent"]),
            ("✓", "100 photos will be captured", UI_COLORS["accent"]),
            ("✓", "Process takes ~30 seconds", UI_COLORS["accent"]),
        ]
        
        for icon, text, color in guidelines:
            guideline_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            guideline_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                guideline_frame,
                text=icon,
                font=("Arial Bold", 16),
                text_color=color,
                width=30
            ).pack(side="left")
            
            ctk.CTkLabel(
                guideline_frame,
                text=text,
                font=("Arial", 13),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)
        
        # Camera test info
        camera_info = ctk.CTkFrame(info_frame, fg_color=UI_COLORS["primary"], 
                                  corner_radius=12, border_width=2, border_color=UI_COLORS["accent"])
        camera_info.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            camera_info,
            text="🎥 Camera Requirements",
            font=("Arial Bold", 14),
            text_color=UI_COLORS["accent"]
        ).pack(pady=10, padx=15, anchor="w")
        
        ctk.CTkLabel(
            camera_info,
            text="• Webcam must be connected\n• Close other camera apps\n• Grant camera permissions",
            font=("Arial", 12),
            justify="left",
            anchor="w",
            text_color=UI_COLORS["text_secondary"]
        ).pack(pady=(0, 10), padx=15, anchor="w")
        
        def validate_inputs():
            """Validate form inputs"""
            faculty_id = id_entry.get().strip()
            faculty_name = name_entry.get().strip()
            
            # Validate ID
            if not faculty_id:
                mess.showerror("Validation Error", "❌ Faculty ID is required!")
                id_entry.focus()
                return None, None
            
            if len(faculty_id) < 3:
                mess.showerror("Validation Error", "❌ Faculty ID must be at least 3 characters!")
                id_entry.focus()
                return None, None
            
            # Validate Name
            if not faculty_name:
                mess.showerror("Validation Error", "❌ Faculty Name is required!")
                name_entry.focus()
                return None, None
            
            if not faculty_name.replace(' ', '').replace('-', '').isalpha():
                mess.showerror("Validation Error", "❌ Name should contain only letters and spaces!")
                name_entry.focus()
                return None, None
            
            if len(faculty_name.split()) < 2:
                response = mess.askyesno("Confirm Name", 
                    "⚠️ It's recommended to enter full name (First Last).\n\nContinue anyway?")
                if not response:
                    name_entry.focus()
                    return None, None
            
            # Check for duplicate ID
            faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
            if os.path.isfile(faculty_details_path):
                df = pd.read_csv(faculty_details_path, encoding='latin-1')
                if faculty_id in df['ID'].values:
                    mess.showerror("Duplicate ID", f"❌ Faculty ID '{faculty_id}' already exists!")
                    id_entry.focus()
                    return None, None
            
            return faculty_id, faculty_name
        
        def capture_images():
            # Validate inputs first
            faculty_id, faculty_name = validate_inputs()
            if not faculty_id or not faculty_name:
                return
            
            if not check_haarcascadefile():
                return
            
            # Prepare paths
            assure_path_exists("FacultyDetails")
            assure_path_exists("TrainingImage")
            
            # Get serial number
            faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
            serial = 1
            if os.path.isfile(faculty_details_path):
                # Read CSV without header to avoid duplicate column issues
                try:
                    df = pd.read_csv(faculty_details_path, header=0)
                    # Count non-empty rows
                    valid_rows = df[df['SERIAL NO.'].notna()]
                    serial = len(valid_rows) + 1
                except:
                    # If file is corrupted, create new one
                    df = pd.DataFrame(columns=['SERIAL NO.', '', 'ID', '', 'NAME'])
                    df.to_csv(faculty_details_path, index=False)
                    serial = 1
            else:
                df = pd.DataFrame(columns=['SERIAL NO.', '', 'ID', '', 'NAME'])
                df.to_csv(faculty_details_path, index=False)
            
            # Update status
            status_label.configure(
                text="📸 Initializing camera... Please wait",
                text_color=UI_COLORS["accent"]
            )
            progress_bar.set(0.1)
            self.root.update()
            
            try:
                cam = cv2.VideoCapture(0)
                if not cam.isOpened():
                    mess.showerror("Camera Error", "❌ Cannot access camera!\n\nPlease check:\n• Camera is connected\n• No other apps using camera\n• Camera permissions granted")
                    status_label.configure(text="❌ Camera not accessible", text_color=UI_COLORS["accent"])
                    progress_bar.set(0)
                    return
                
                detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                sample_num = 0
                
                status_label.configure(
                    text="📸 Camera ready! Look at the camera and stay still",
                    text_color=UI_COLORS["accent"]
                )
                progress_bar.set(0.2)
                self.root.update()
                
                while sample_num < 100:
                    ret, img = cam.read()
                    if not ret:
                        break
                    
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                        sample_num += 1
                        
                        filename = f"{faculty_name}.{serial}.{faculty_id}.{sample_num}.jpg"
                        filepath = os.path.join("TrainingImage", filename)
                        cv2.imwrite(filepath, gray[y:y + h, x:x + w])
                        
                        # Update progress
                        progress = 0.2 + (sample_num / 100) * 0.6
                        progress_bar.set(progress)
                        
                        # Display on camera window
                        cv2.putText(img, f"Captured: {sample_num}/100", (10, 40),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                        cv2.putText(img, "Press 'Q' to cancel", (10, img.shape[0] - 20),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    if len(faces) == 0:
                        cv2.putText(img, "No face detected - Please look at camera", (10, 40),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    cv2.imshow('📸 Faculty Registration - Image Capture', img)
                    
                    if cv2.waitKey(100) & 0xFF == ord('q'):
                        if mess.askyesno("Cancel Capture", "⚠️ Cancel image capture?\n\nProgress will be lost."):
                            cam.release()
                            # Aggressive cleanup on cancel
                            for _ in range(5):
                                cv2.destroyAllWindows()
                                cv2.waitKey(1)
                            status_label.configure(text="❌ Capture cancelled", text_color=UI_COLORS["accent"])
                            progress_bar.set(0)
                            return
                
                # Release camera and close all windows immediately
                cam.release()
                
                # Destroy specific window by name first
                try:
                    cv2.destroyWindow('📸 Faculty Registration - Image Capture')
                except:
                    pass
                
                # Aggressive window cleanup - destroy multiple times to ensure closure
                for _ in range(10):
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                
                # Give OS time to process window destruction
                import time as time_module
                time_module.sleep(0.5)
                
                if sample_num < 50:
                    # Additional cleanup for early exit
                    for _ in range(5):
                        cv2.destroyAllWindows()
                        cv2.waitKey(1)
                    
                    mess.showwarning("Insufficient Images", 
                        f"⚠️ Only {sample_num} images captured!\n\nAt least 50 images recommended for accuracy.\n\nPlease try again.")
                    status_label.configure(text=f"⚠️ Only {sample_num} images captured - Please retry", 
                                         text_color=UI_COLORS["accent"])
                    progress_bar.set(0)
                    return
                
                # Save to CSV using append mode to avoid concat issues
                with open(faculty_details_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([serial, '', faculty_id, '', faculty_name])
                
                status_label.configure(
                    text=f"✅ {sample_num} images captured successfully!",
                    text_color=UI_COLORS["accent"]
                )
                progress_bar.set(0.8)
                self.root.update()
                
                # Train model automatically
                status_label.configure(text="🔄 Training model... Please wait", text_color=UI_COLORS["accent"])
                self.root.update()
                
                self.train_model()
                
                # AGGRESSIVE: Ensure all OpenCV windows are fully closed after training
                # Destroy specific window by name
                try:
                    cv2.destroyWindow('📸 Faculty Registration - Image Capture')
                except:
                    pass
                
                # Multiple cleanup calls to force window closure (increased to 20)
                for _ in range(20):
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                
                # Longer wait to ensure windows are closed
                import time as time_module
                time_module.sleep(0.5)
                
                # Final check - one more destroy all
                cv2.destroyAllWindows()
                for _ in range(5):
                    cv2.waitKey(1)
                
                progress_bar.set(1.0)
                status_label.configure(
                    text=f"🎉 Faculty '{faculty_name}' registered successfully!",
                    text_color=UI_COLORS["accent"]
                )
                
                # Clear form
                id_entry.delete(0, 'end')
                name_entry.delete(0, 'end')
                
                mess.showinfo("Success", 
                    f"✅ Faculty member registered successfully!\n\n"
                    f"Name: {faculty_name}\n"
                    f"ID: {faculty_id}\n"
                    f"Images: {sample_num}\n"
                    f"Model: Trained")
                
            except Exception as e:
                mess.showerror("Error", f"❌ An error occurred:\n\n{str(e)}")
                status_label.configure(text="❌ Registration failed", text_color=UI_COLORS["accent"])
                progress_bar.set(0)
            finally:
                # FINAL AGGRESSIVE CLEANUP - ensure all camera resources are released
                try:
                    # Destroy specific window by name
                    try:
                        cv2.destroyWindow('📸 Faculty Registration - Image Capture')
                    except:
                        pass
                    
                    # Multiple destroy calls to ensure all windows close (30 times)
                    for _ in range(30):
                        cv2.destroyAllWindows()
                        cv2.waitKey(1)
                    
                    # Longer wait for window manager to process
                    import time as time_module
                    time_module.sleep(0.5)
                    
                    # Force garbage collection
                    import gc
                    gc.collect()
                    
                    # One final destroy
                    cv2.destroyAllWindows()
                except:
                    pass
        
        # Action Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20, padx=20, fill="x")
        
        # Capture Button
        capture_btn = ctk.CTkButton(
            button_frame,
            text="📷 Start Image Capture",
            command=capture_images,
            width=220,
            height=55,
            font=("Arial Bold", 16),
            fg_color=UI_COLORS["accent"],
            hover_color="#1976D2",
            corner_radius=12,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        capture_btn.pack(side="left", padx=(0, 10))
        
        # Clear Button
        def clear_form():
            id_entry.delete(0, 'end')
            name_entry.delete(0, 'end')
            status_label.configure(text="📋 Ready to capture images", text_color=UI_COLORS["accent"])
            progress_bar.set(0)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Clear Form",
            command=clear_form,
            width=120,
            height=55,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["secondary"],
            hover_color="#1f4b8f",
            corner_radius=12,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        clear_btn.pack(side="left", padx=5)
        
        # Cancel Button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.show_dashboard,
            width=120,
            height=55,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color="#1976D2",
            corner_radius=12,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Voice Registration Section
        voice_frame = ctk.CTkFrame(form_frame, fg_color=UI_COLORS["primary"], 
                                  corner_radius=12, border_width=2, border_color=UI_COLORS["accent"])
        voice_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            voice_frame,
            text="🎤 Voice Registration",
            font=("Arial Bold", 18),
            text_color=UI_COLORS["accent"]
        ).pack(pady=15, padx=20, anchor="w")
        
        ctk.CTkLabel(
            voice_frame,
            text="Register voice sample for backup attendance verification",
            font=("Arial", 12),
            text_color=UI_COLORS["text_secondary"]
        ).pack(pady=(0, 15), padx=20, anchor="w")
        
        # Voice registration buttons
        voice_button_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        voice_button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        def register_voice():
            faculty_id, faculty_name = validate_inputs()
            if faculty_id and faculty_name:
                self.register_voice_for_faculty(faculty_id, faculty_name)
        
        def verify_voice():
            faculty_id, faculty_name = validate_inputs()
            if faculty_id and faculty_name:
                self.verify_voice_for_faculty(faculty_id, faculty_name)
        
        voice_register_btn = ctk.CTkButton(
            voice_button_frame,
            text="🎤 Register Voice",
            command=register_voice,
            width=160,
            height=42,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color="#1976D2",
            corner_radius=10,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        voice_register_btn.pack(side="left", padx=(0, 10))
        
        voice_verify_btn = ctk.CTkButton(
            voice_button_frame,
            text="🔍 Verify Voice",
            command=verify_voice,
            width=160,
            height=42,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color="#1976D2",
            corner_radius=10,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        voice_verify_btn.pack(side="left", padx=5)
    
    def train_model(self):
        """Train the face recognition model"""
        if not check_haarcascadefile():
            return
        
        assure_path_exists("TrainingImageLabel")
        
        try:
            recognizer = cv2.face_LBPHFaceRecognizer.create()
            faces, ids = self.get_images_and_labels("TrainingImage")
            
            if len(faces) == 0:
                mess.showerror("Error", "No training images found!")
                return
            
            recognizer.train(faces, np.array(ids))
            trainer_path = os.path.join("TrainingImageLabel", "Trainner.yml")
            recognizer.save(trainer_path)
            
            mess.showinfo("Success", "✅ Model trained successfully!")
        except Exception as e:
            mess.showerror("Training Error", f"Error training model: {str(e)}")
    
    def get_images_and_labels(self, path):
        """Get images and labels for training"""
        image_paths = [os.path.join(path, f) for f in os.listdir(path) 
                      if f.endswith(('.jpg', '.png', '.jpeg'))]
        faces = []
        ids = []
        
        for image_path in image_paths:
            try:
                pil_image = Image.open(image_path).convert('L')
                image_np = np.array(pil_image, 'uint8')
                id = int(os.path.split(image_path)[-1].split(".")[1])
                faces.append(image_np)
                ids.append(id)
            except:
                continue
        
        return faces, ids
    
    def show_view_faculty(self):
        """Show all registered faculty"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📋 Registered Faculty",
            font=("Arial Bold", 32),
            text_color=UI_COLORS["text_primary"]
        )
        title.pack(pady=25)
        
        # Refresh button with enhanced styling
        refresh_btn = ctk.CTkButton(
            self.content_frame,
            text="🔄 Refresh",
            command=self.show_view_faculty,
            width=140,
            height=40,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color=UI_COLORS["accent"],
            corner_radius=15,
            border_width=2,
            border_color=UI_COLORS["accent"]
        )
        refresh_btn.pack(pady=10)
        
        # Table Frame
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview with enhanced styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=UI_COLORS["primary"], 
                       foreground=UI_COLORS["text_primary"],
                       fieldbackground=UI_COLORS["primary"], 
                       font=('Arial Bold', 12),
                       rowheight=35)
        style.configure("Treeview.Heading", 
                       background=UI_COLORS["accent"], 
                       foreground=UI_COLORS["text_primary"],
                       font=('Arial Bold', 14),
                       relief="flat")
        style.map('Treeview', 
                 background=[('selected', '#42a5f5')],  # Lighter shade of accent for selection
                 foreground=[('selected', UI_COLORS["text_primary"])])
        
        tree = ttk.Treeview(table_frame, columns=('Serial', 'ID', 'Name', 'Actions'), 
                           show='headings', height=20)
        tree.heading('Serial', text='Serial No.')
        tree.heading('ID', text='Faculty ID')
        tree.heading('Name', text='Faculty Name')
        tree.heading('Actions', text='Actions')
        
        tree.column('Serial', width=100)
        tree.column('ID', width=200)
        tree.column('Name', width=300)
        tree.column('Actions', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load data
        df = load_faculty()
        for idx, row in df.iterrows():
            if pd.notna(row.get('ID')):
                tree.insert('', 'end', values=(row['SERIAL NO.'], row['ID'], row['NAME'], ''))
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(self.content_frame)
        action_frame.pack(pady=10)
        
        def delete_selected():
            selected = tree.selection()
            if not selected:
                mess.showwarning("No Selection", "Please select a faculty member to delete")
                return
            
            item = tree.item(selected[0])
            serial_no = item['values'][0]
            faculty_name = item['values'][2]
            
            confirm = mess.askyesno("Confirm Delete", 
                                   f"⚠️ Are you sure you want to delete {faculty_name}?\n\n"
                                   f"This will remove:\n"
                                   f"• Faculty record\n"
                                   f"• All training images\n\n"
                                   f"This action cannot be undone!")
            if confirm:
                # Count and delete training images for this faculty
                deleted_images = 0
                if os.path.exists("TrainingImage"):
                    try:
                        for filename in os.listdir("TrainingImage"):
                            if filename.endswith(('.jpg', '.png', '.jpeg')):
                                # File format: name.serial.id.sample.jpg
                                parts = filename.split('.')
                                if len(parts) >= 4:
                                    try:
                                        file_serial = int(parts[1])
                                        if file_serial == serial_no:
                                            file_path = os.path.join("TrainingImage", filename)
                                            os.remove(file_path)
                                            deleted_images += 1
                                    except ValueError:
                                        continue
                    except Exception as e:
                        mess.showwarning("Image Deletion Warning", 
                                       f"Could not delete some training images:\n{str(e)}")
                
                # Delete from CSV
                df = load_faculty()
                df = df[df['SERIAL NO.'] != serial_no]
                save_faculty(df)
                
                # Retrain the model if there are still faculty members
                remaining_faculty = len(df) // 2 if len(df) > 0 else 0
                if remaining_faculty > 0:
                    try:
                        self.train_model()
                        model_msg = "\n• Model retrained"
                    except:
                        model_msg = "\n• ⚠️ Please retrain model manually"
                else:
                    model_msg = "\n• No faculty remaining - model cleared"
                    # Delete the trained model file since no faculty left
                    trainer_path = os.path.join("TrainingImageLabel", "Trainner.yml")
                    if os.path.exists(trainer_path):
                        os.remove(trainer_path)
                
                # Refresh view
                self.show_view_faculty()
                mess.showinfo("Success", 
                    f"✅ Faculty '{faculty_name}' deleted successfully!\n\n"
                    f"• CSV record removed\n"
                    f"• {deleted_images} training images deleted"
                    f"{model_msg}")
        
        ctk.CTkButton(
            action_frame,
            text="🗑️ Delete Selected",
            command=delete_selected,
            fg_color=UI_COLORS["accent"],
            hover_color=UI_COLORS["accent"],
            width=180,
            height=45,
            font=("Arial Bold", 14),
            corner_radius=15,
            border_width=2,
            border_color=UI_COLORS["accent"]
        ).pack(side="left", padx=10)
        
        total_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Total Faculty: {len(df) // 2 if len(df) > 0 else 0}",
            font=("Arial Bold", 16)
        )
        total_label.pack(pady=10)
    
    def show_attendance_records(self):
        """Show attendance records"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📈 Attendance Records",
            font=("Arial Bold", 32),
            text_color=UI_COLORS["text_primary"]
        )
        title.pack(pady=25)
        
        # Date selector
        date_frame = ctk.CTkFrame(self.content_frame)
        date_frame.pack(pady=10)
        
        ctk.CTkLabel(date_frame, text="Select Date:", font=("Arial", 14)).pack(side="left", padx=10)
        
        # Get available dates
        dates = []
        if os.path.exists("Attendance"):
            dates = [f.replace("Attendance_", "").replace(".csv", "") 
                    for f in os.listdir("Attendance") if f.endswith('.csv')]
        
        if not dates:
            ctk.CTkLabel(
                self.content_frame,
                text="No attendance records found",
                font=("Arial", 16),
                text_color="gray"
            ).pack(pady=50)
            return
        
        selected_date = ctk.StringVar(value=dates[-1] if dates else "")
        
        date_menu = ctk.CTkOptionMenu(
            date_frame,
            variable=selected_date,
            values=dates,
            width=200
        )
        date_menu.pack(side="left", padx=10)
        
        # Table Frame
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=UI_COLORS["primary"], 
                       foreground=UI_COLORS["text_primary"],
                       fieldbackground=UI_COLORS["primary"], 
                       font=('Arial Bold', 12),
                       rowheight=35)
        style.configure("Treeview.Heading", 
                       background=UI_COLORS["accent"], 
                       foreground=UI_COLORS["text_primary"],
                       font=('Arial Bold', 14),
                       relief="flat")
        style.map('Treeview', 
                 background=[('selected', '#42a5f5')],  # Lighter shade of accent for selection
                 foreground=[('selected', UI_COLORS["text_primary"])])
        
        tree = ttk.Treeview(table_frame, columns=('ID', 'Name', 'Date', 'Time'),
                           show='headings', height=20)
        tree.heading('ID', text='Faculty ID')
        tree.heading('Name', text='Name')
        tree.heading('Date', text='Date')
        tree.heading('Time', text='Time')
        
        tree.column('ID', width=150)
        tree.column('Name', width=250)
        tree.column('Date', width=150)
        tree.column('Time', width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def load_attendance():
            # Clear existing data
            for item in tree.get_children():
                tree.delete(item)
            
            date = selected_date.get()
            attendance_path = os.path.join("Attendance", f"Attendance_{date}.csv")
            
            if os.path.isfile(attendance_path):
                with open(attendance_path, 'r') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        if len(row) >= 7 and row[0]:
                            tree.insert('', 'end', values=(row[0], row[2], row[4], row[6]))
        
        # Load button with enhanced styling
        ctk.CTkButton(
            date_frame,
            text="📊 Load Records",
            command=load_attendance,
            width=150,
            height=40,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color=UI_COLORS["accent"],
            corner_radius=15,
            border_width=2,
            border_color=UI_COLORS["accent"]
        ).pack(side="left", padx=10)
        
        # Export button with enhanced styling
        def export_records():
            date = selected_date.get()
            src = os.path.join("Attendance", f"Attendance_{date}.csv")
            dst = f"Exported_Attendance_{date}.csv"
            
            if os.path.exists(src):
                shutil.copy(src, dst)
                mess.showinfo("Success", f"Exported to {dst}")
        
        ctk.CTkButton(
            date_frame,
            text="💾 Export CSV",
            command=export_records,
            width=150,
            height=40,
            font=("Arial Bold", 14),
            fg_color=UI_COLORS["accent"],
            hover_color=UI_COLORS["accent"],
            corner_radius=15,
            border_width=2,
            border_color=UI_COLORS["accent"]
        ).pack(side="left", padx=10)
        
        # Auto-load latest
        load_attendance()
    
    def show_manage_tasks(self):
        """Show enhanced task management interface"""
        self.clear_content()
        
        # Header aligned to three-color scheme
        header_frame = ctk.CTkFrame(self.content_frame, fg_color=UI_COLORS["accent"], height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True)
        
        ctk.CTkLabel(
            header_content,
            text="📝 Task & Deadline Manager",
            font=("Arial Bold", 28),
            text_color=UI_COLORS["text_primary"]
        ).pack()
        
        ctk.CTkLabel(
            header_content,
            text="Assign tasks and track faculty deadlines",
            font=("Arial", 12),
            text_color=UI_COLORS["text_secondary"]
        ).pack()
        
        # Main container with better spacing
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=5)
        
        # Left - Compact Add Task Form
        form_frame = ctk.CTkFrame(main_container, width=480, fg_color=UI_COLORS["secondary"], 
                                 border_width=2, border_color=UI_COLORS["accent"])
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Compact form header with icon
        form_header = ctk.CTkFrame(form_frame, fg_color=UI_COLORS["accent"], height=50, corner_radius=0)
        form_header.pack(fill="x")
        form_header.pack_propagate(False)
        
        ctk.CTkLabel(
            form_header,
            text="➕ New Task Assignment",
            font=("Arial Bold", 18),
            text_color="white"
        ).pack(pady=12)
        
        # Compact form fields container
        fields_container = ctk.CTkScrollableFrame(form_frame, fg_color="transparent", height=400)
        fields_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Load faculty list
        faculty_df = load_faculty()
        faculty_options = ["🔽 Select Faculty Member"]
        faculty_map = {}
        for idx, row in faculty_df.iterrows():
            if pd.notna(row.get('ID')):
                option = f"{row['NAME']} - {row['ID']}"
                faculty_options.append(option)
                faculty_map[option] = (str(row['ID']), str(row['NAME']))
        
        # 1. Faculty Selection (Compact)
        ctk.CTkLabel(fields_container, text="👤 Faculty Member", 
                    font=("Arial Bold", 13), anchor="w").pack(anchor="w", pady=(5, 3))
        selected_faculty = ctk.StringVar(value="🔽 Select Faculty Member")
        faculty_menu = ctk.CTkOptionMenu(fields_container, variable=selected_faculty, 
                                         values=faculty_options, width=430, height=38,
                                         font=("Arial", 12), fg_color=UI_COLORS["accent"],
                                         button_color="#1976D2", button_hover_color="#1565C0")
        faculty_menu.pack(pady=(0, 12))
        
        # 2. Task Title (Compact)
        ctk.CTkLabel(fields_container, text="📌 Task Title", 
                    font=("Arial Bold", 13), anchor="w").pack(anchor="w", pady=(0, 3))
        task_title_entry = ctk.CTkEntry(fields_container, width=430, height=38, 
                                        placeholder_text="Brief description of the task",
                                        font=("Arial", 12), border_width=2, border_color="#555")
        task_title_entry.pack(pady=(0, 12))
        
        # 3. Description (Compact)
        ctk.CTkLabel(fields_container, text="📝 Details (Optional)", 
                    font=("Arial Bold", 13), anchor="w").pack(anchor="w", pady=(0, 3))
        task_desc = ctk.CTkTextbox(fields_container, width=430, height=70,
                                   font=("Arial", 11), border_width=2, border_color="#555")
        task_desc.pack(pady=(0, 12))
        
        # Row for Date and Priority (side by side)
        date_priority_row = ctk.CTkFrame(fields_container, fg_color="transparent")
        date_priority_row.pack(fill="x", pady=(0, 12))
        
        # 4. Due Date (Half width)
        date_col = ctk.CTkFrame(date_priority_row, fg_color="transparent")
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(date_col, text="📅 Due Date", 
                    font=("Arial Bold", 13), anchor="w").pack(anchor="w", pady=(0, 3))
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        date_entry = ctk.CTkEntry(date_col, width=210, height=38, 
                                 font=("Arial", 12), border_width=2, border_color="#555")
        date_entry.insert(0, today)
        date_entry.pack()
        
        # 5. Priority (Half width)
        priority_col = ctk.CTkFrame(date_priority_row, fg_color="transparent")
        priority_col.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(priority_col, text="🎯 Priority", 
                    font=("Arial Bold", 13), anchor="w").pack(anchor="w", pady=(0, 3))
        priority_var = ctk.StringVar(value="Medium")
        
        # Color-coded priority buttons
        priority_buttons_frame = ctk.CTkFrame(priority_col, fg_color="transparent")
        priority_buttons_frame.pack()
        
        # Priority visual is subtle; we remain within the accent scheme
        priority_colors = {
            "Low": "#1565C0",      # darker accent
            "Medium": "#2196F3",   # accent
            "High": "#42A5F5",     # lighter accent
            "Urgent": "#64B5F6"    # lightest accent
        }
        
        def select_priority(p):
            priority_var.set(p)
            for btn in priority_btns.values():
                btn.configure(fg_color="#2b2b2b", border_width=0)
            priority_btns[p].configure(fg_color=priority_colors[p], border_width=2)
        
        priority_btns = {}
        for priority in ["Low", "Medium", "High", "Urgent"]:
            btn = ctk.CTkButton(
                priority_buttons_frame,
                text=priority,
                command=lambda p=priority: select_priority(p),
                width=48,
                height=32,
                font=("Arial Bold", 10),
                fg_color="#2b2b2b" if priority != "Medium" else priority_colors[priority],
                border_width=2 if priority == "Medium" else 0,
                border_color=priority_colors[priority]
            )
            btn.pack(side="left", padx=2)
            priority_btns[priority] = btn
        
        # Status indicator
        status_frame = ctk.CTkFrame(fields_container, fg_color=UI_COLORS["secondary"], corner_radius=8, height=40)
        status_frame.pack(fill="x", pady=(5, 10))
        status_frame.pack_propagate(False)
        
        status_label = ctk.CTkLabel(status_frame, text="✏️ Fill in the form to create a task", 
                                    font=("Arial", 12), text_color="gray")
        status_label.pack(pady=8)
        
        # Add Task Button
        def add_task():
            faculty_sel = selected_faculty.get()
            if faculty_sel == "Select Faculty":
                mess.showerror("Error", "Please select a faculty member!")
                return
            
            task_title = task_title_entry.get().strip()
            if not task_title:
                mess.showerror("Error", "Please enter a task title!")
                return
            
            task_description = task_desc.get("1.0", "end-1c").strip()
            due_date = date_entry.get().strip()
            
            # Validate date format
            try:
                datetime.datetime.strptime(due_date, '%Y-%m-%d')
            except:
                mess.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            # Get faculty info
            faculty_id, faculty_name = faculty_map[faculty_sel]
            
            # Generate task ID
            tasks_df = load_tasks()
            task_id = len(tasks_df) + 1
            
            # Add task
            new_task = {
                'TASK_ID': task_id,
                'FACULTY_ID': faculty_id,
                'FACULTY_NAME': faculty_name,
                'TASK_TITLE': task_title,
                'TASK_DESCRIPTION': task_description,
                'DUE_DATE': due_date,
                'PRIORITY': priority_var.get(),
                'STATUS': 'Pending'
            }
            
            # Append to CSV
            tasks_path = os.path.join("Tasks", "Tasks.csv")
            with open(tasks_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=new_task.keys())
                writer.writerow(new_task)
            
            status_label.configure(text=f"✅ Task assigned to {faculty_name} successfully!", 
                                 text_color="#4CAF50")
            
            # Clear form
            clear_form()
            
            # Refresh tasks view
            refresh_tasks()
            
            # Show compact success notification
            mess.showinfo("Task Created", 
                f"✅ Task assigned successfully!\n\n"
                f"📌 {task_title}\n"
                f"👤 {faculty_name}\n"
                f"📅 Due: {due_date}\n"
                f"🎯 Priority: {priority_var.get()}")
        
        # Action buttons (Compact, centered)
        button_container = ctk.CTkFrame(form_frame, fg_color="transparent", height=65)
        button_container.pack(fill="x", side="bottom", pady=10, padx=15)
        button_container.pack_propagate(False)
        
        button_inner = ctk.CTkFrame(button_container, fg_color="transparent")
        button_inner.pack(expand=True)
        
        ctk.CTkButton(button_inner, text="✓ Create Task", command=add_task,
                     width=200, height=45, font=("Arial Bold", 15),
                     fg_color=UI_COLORS["accent"], hover_color="#1976D2",
                     corner_radius=12, border_width=2, border_color=UI_COLORS["accent"]).pack(side="left", padx=5)
        
        def clear_form():
            task_title_entry.delete(0, 'end')
            task_desc.delete("1.0", "end")
            date_entry.delete(0, 'end')
            date_entry.insert(0, today)
            selected_faculty.set("🔽 Select Faculty Member")
            select_priority("Medium")
            status_label.configure(text="✏️ Fill in the form to create a task", text_color="gray")
        
        ctk.CTkButton(button_inner, text="🔄 Reset", command=clear_form,
                     width=110, height=45, font=("Arial Bold", 13),
                     fg_color=UI_COLORS["secondary"], hover_color="#1f4b8f",
                     corner_radius=12, border_width=2, border_color=UI_COLORS["accent"]).pack(side="left", padx=5)
        
        ctk.CTkButton(button_inner, text="❌ Cancel", command=self.show_dashboard,
                     width=110, height=45, font=("Arial Bold", 13),
                     fg_color=UI_COLORS["accent"], hover_color="#1976D2",
                     corner_radius=12, border_width=2, border_color=UI_COLORS["accent"]).pack(side="left", padx=5)
        
        # Right - Compact Task List View
        tasks_view_frame = ctk.CTkFrame(main_container, fg_color=UI_COLORS["secondary"],
                                       border_width=2, border_color=UI_COLORS["accent"])
        tasks_view_frame.pack(side="right", fill="both", expand=True)
        
        # Tasks header
        tasks_header = ctk.CTkFrame(tasks_view_frame, fg_color=UI_COLORS["accent"], height=50, corner_radius=0)
        tasks_header.pack(fill="x")
        tasks_header.pack_propagate(False)
        
        ctk.CTkLabel(tasks_header, text="📋 Task List & Overview", 
                    font=("Arial Bold", 18), text_color="white").pack(pady=12)
        
        # Compact filter and controls
        control_bar = ctk.CTkFrame(tasks_view_frame, fg_color=UI_COLORS["secondary"], height=45)
        control_bar.pack(fill="x", padx=10, pady=10)
        control_bar.pack_propagate(False)
        
        ctk.CTkLabel(control_bar, text="📊", font=("Arial", 16)).pack(side="left", padx=8)
        
        filter_var = ctk.StringVar(value="Today")
        filter_menu = ctk.CTkOptionMenu(control_bar, variable=filter_var,
                                        values=["All", "Today", "This Week", "Pending", "Completed"],
                                        width=160, height=34, font=("Arial", 12),
                                        fg_color=UI_COLORS["accent"], button_color="#1976D2", button_hover_color="#1565C0")
        filter_menu.pack(side="left", padx=5)
        
        def refresh_tasks():
            # Clear existing
            for widget in tasks_list_frame.winfo_children():
                widget.destroy()
            
            # Load tasks
            tasks_df = load_tasks()
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            
            filter_val = filter_var.get()
            if filter_val == "Today":
                tasks_df = tasks_df[tasks_df['DUE_DATE'] == today]
            elif filter_val == "Pending":
                tasks_df = tasks_df[tasks_df['STATUS'] == 'Pending']
            elif filter_val == "Completed":
                tasks_df = tasks_df[tasks_df['STATUS'] == 'Completed']
            elif filter_val == "This Week":
                # Get this week's tasks
                week_end = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
                tasks_df = tasks_df[(tasks_df['DUE_DATE'] >= today) & (tasks_df['DUE_DATE'] <= week_end)]
            
            # Update count
            task_count_label.configure(text=f"📊 {len(tasks_df)} task(s)")
            
            if len(tasks_df) == 0:
                empty_frame = ctk.CTkFrame(tasks_list_frame, fg_color=UI_COLORS["secondary"], corner_radius=10)
                empty_frame.pack(fill="both", expand=True, pady=50, padx=20)
                
                ctk.CTkLabel(empty_frame, text="📭", font=("Arial", 48)).pack(pady=20)
                ctk.CTkLabel(empty_frame, text="No tasks found", 
                           font=("Arial Bold", 16), text_color="gray").pack()
                ctk.CTkLabel(empty_frame, text="Create a new task to get started", 
                           font=("Arial", 12), text_color="gray").pack(pady=(5, 20))
            else:
                for idx, task in tasks_df.iterrows():
                    # Compact task card with modern design
                    task_card = ctk.CTkFrame(tasks_list_frame, fg_color=UI_COLORS["primary"], 
                                            corner_radius=10, border_width=2, border_color=UI_COLORS["accent"])
                    task_card.pack(fill="x", pady=4, padx=3)
                    
                    # Priority colors
                    priority_colors = {"Low": "#1565C0", "Medium": "#2196F3", 
                                      "High": "#42A5F5", "Urgent": "#64B5F6"}
                    p_color = priority_colors.get(task['PRIORITY'], UI_COLORS["accent"])
                    
                    # Compact header with priority stripe
                    header = ctk.CTkFrame(task_card, fg_color="transparent")
                    header.pack(fill="x", padx=8, pady=6)
                    
                    # Priority indicator (vertical stripe)
                    priority_stripe = ctk.CTkFrame(header, fg_color=p_color, width=4, corner_radius=2)
                    priority_stripe.pack(side="left", fill="y", padx=(0, 10))
                    
                    # Task info column
                    info_col = ctk.CTkFrame(header, fg_color="transparent")
                    info_col.pack(side="left", fill="both", expand=True)
                    
                    # Title row
                    title_row = ctk.CTkFrame(info_col, fg_color="transparent")
                    title_row.pack(fill="x")
                    
                    ctk.CTkLabel(title_row, text=f"📌 {task['TASK_TITLE']}", 
                               font=("Arial Bold", 13), anchor="w").pack(side="left")
                    
                    # Priority badge
                    priority_badge = ctk.CTkLabel(title_row, text=task['PRIORITY'], 
                                                 font=("Arial Bold", 9), 
                                                 fg_color=p_color, corner_radius=4,
                                                 width=55, height=18)
                    priority_badge.pack(side="right", padx=5)
                    
                    # Details row
                    details_row = ctk.CTkFrame(info_col, fg_color="transparent")
                    details_row.pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(details_row, text=f"👤 {task['FACULTY_NAME'][:20]}", 
                               font=("Arial", 10), anchor="w", text_color="#B0B0B0").pack(side="left", padx=(0, 15))
                    
                    ctk.CTkLabel(details_row, text=f"📅 {task['DUE_DATE']}", 
                               font=("Arial", 10), anchor="w", text_color="#B0B0B0").pack(side="left")
                    
                    # Description (if exists, compact)
                    if pd.notna(task['TASK_DESCRIPTION']) and task['TASK_DESCRIPTION']:
                        desc_text = task['TASK_DESCRIPTION'][:60] + "..." if len(task['TASK_DESCRIPTION']) > 60 else task['TASK_DESCRIPTION']
                        ctk.CTkLabel(info_col, text=f"💬 {desc_text}", 
                                   font=("Arial", 9), anchor="w", 
                                   text_color="#808080").pack(fill="x", pady=(2, 0))
                    
                    # Compact action buttons
                    btn_row = ctk.CTkFrame(task_card, fg_color="transparent")
                    btn_row.pack(fill="x", padx=8, pady=(0, 6))
                    
                    def complete_task(task_id=task['TASK_ID']):
                        tasks = load_tasks()
                        tasks.loc[tasks['TASK_ID'] == task_id, 'STATUS'] = 'Completed'
                        save_tasks(tasks)
                        refresh_tasks()
                        mess.showinfo("Success", "Task marked as completed!")
                    
                    def delete_task(task_id=task['TASK_ID']):
                        if mess.askyesno("Confirm", "Delete this task?"):
                            tasks = load_tasks()
                            tasks = tasks[tasks['TASK_ID'] != task_id]
                            save_tasks(tasks)
                            refresh_tasks()
                    
                    # Status indicator
                    if task['STATUS'] == 'Completed':
                        status_frame = ctk.CTkFrame(btn_row, fg_color=UI_COLORS["accent"], corner_radius=4, height=24)
                        status_frame.pack(side="left", padx=5)
                        ctk.CTkLabel(status_frame, text="✓ Completed", font=("Arial Bold", 10),
                                   text_color="white").pack(padx=10, pady=3)
                    else:
                        ctk.CTkButton(btn_row, text="✓ Done", command=complete_task,
                                    width=80, height=26, fg_color=UI_COLORS["accent"], 
                                    hover_color="#1976D2",
                                    font=("Arial Bold", 10), corner_radius=6).pack(side="left", padx=3)
                    
                    ctk.CTkButton(btn_row, text="🗑️", command=delete_task,
                                width=40, height=26, fg_color=UI_COLORS["accent"],
                                hover_color="#1976D2",
                                font=("Arial", 10), corner_radius=6).pack(side="right", padx=3)
        
        # Refresh and filter controls
        ctk.CTkButton(control_bar, text="🔄", command=refresh_tasks,
                     width=44, height=34, font=("Arial", 14),
                     fg_color=UI_COLORS["accent"], hover_color="#1976D2").pack(side="left", padx=6)
        
        # Task count label
        task_count_label = ctk.CTkLabel(control_bar, text="", font=("Arial Bold", 12), text_color=UI_COLORS["text_secondary"])
        task_count_label.pack(side="right", padx=10)
        
        # Compact tasks list with better styling
        tasks_list_frame = ctk.CTkScrollableFrame(tasks_view_frame, fg_color="transparent")
        tasks_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Initial load
        refresh_tasks()
    
    def show_settings(self):
        """Show settings panel"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ System Settings",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        settings_frame = ctk.CTkFrame(self.content_frame, width=600)
        settings_frame.pack(pady=30)
        
        # Change Password
        ctk.CTkLabel(
            settings_frame,
            text="🔐 Security Settings",
            font=("Arial Bold", 20)
        ).pack(pady=20)
        
        def change_password():
            old_pass = tsd.askstring('Old Password', 'Enter current password:', show='*')
            if not old_pass:
                return
            
            current_user, current_pass = authenticate_admin()
            if old_pass != current_pass:
                mess.showerror("Error", "Incorrect current password!")
                return
            
            new_pass = tsd.askstring('New Password', 'Enter new password:', show='*')
            if not new_pass:
                return
            
            confirm_pass = tsd.askstring('Confirm Password', 'Confirm new password:', show='*')
            if new_pass != confirm_pass:
                mess.showerror("Error", "Passwords do not match!")
                return
            
            psd_path = os.path.join("TrainingImageLabel", "psd.txt")
            with open(psd_path, "w") as f:
                # Persist as username:password
                f.write(f"{current_user}:{new_pass}")
            
            mess.showinfo("Success", "Password changed successfully!")
        
        ctk.CTkButton(
            settings_frame,
            text="🔑 Change Admin Password",
            command=change_password,
            width=350,
            height=50,
            font=("Arial Bold", 16),
            fg_color="#FF9800"
        ).pack(pady=10)
        
        # System Info
        ctk.CTkLabel(
            settings_frame,
            text="ℹ️ System Information",
            font=("Arial Bold", 20)
        ).pack(pady=(40, 20))
        
        info_frame = ctk.CTkFrame(settings_frame, fg_color="#2b2b2b")
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_texts = [
            f"Version: 2.0 Enhanced",
            f"Database: FacultyDetails/FacultyDetails.csv",
            f"Training Data: TrainingImageLabel/Trainner.yml",
            f"System: GreetA Faculty Attendance System"
        ]
        
        for text in info_texts:
            ctk.CTkLabel(
                info_frame,
                text=text,
                font=("Arial", 14),
                anchor="w"
            ).pack(pady=5, padx=20, anchor="w")

############################################# MAIN ################################################

def main():
    """Main function to run admin panel"""
    if show_login_window():
        root = ctk.CTk()
        app = AdminPanel(root)
        root.mainloop()
    else:
        print("Access denied. Exiting...")

if __name__ == "__main__":
    main()

