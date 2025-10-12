############################################# ADMIN PANEL ################################################
import customtkinter as ctk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
from tkinter import ttk
import cv2
import os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import shutil

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

############################################# ADMIN AUTHENTICATION ################################################

def authenticate_admin():
    """Check admin password"""
    psd_path = os.path.join("TrainingImageLabel", "psd.txt")
    
    # Create default password if not exists
    if not os.path.isfile(psd_path):
        os.makedirs("TrainingImageLabel", exist_ok=True)
        with open(psd_path, "w") as f:
            f.write("admin123")  # Default password
        mess.showinfo("Default Password", "Default admin password is: admin123\nPlease change it after login!")
        return "admin123"
    
    with open(psd_path, "r") as f:
        return f.read()

def check_password():
    """Verify admin password"""
    correct_password = authenticate_admin()
    password = tsd.askstring('Admin Login', 'Enter Admin Password:', show='*')
    
    if password == correct_password:
        return True
    elif password is None:
        return False
    else:
        mess.showerror('Access Denied', 'Incorrect password!')
        return False

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
        df = pd.read_csv(faculty_details_path)
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
        df = pd.read_csv(tasks_path)
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
        self.root.title("GreetA - Admin Panel")
        self.root.geometry("1200x700")
        
        # Header
        self.create_header()
        
        # Navigation
        self.create_navigation()
        
        # Content Area
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_header(self):
        """Create header section"""
        header = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="🔐 Admin Control Panel",
            font=("Arial Bold", 32),
            text_color="#FF6B6B"
        )
        title.pack(pady=20)
    
    def create_navigation(self):
        """Create navigation buttons"""
        nav_frame = ctk.CTkFrame(self.root, height=60, fg_color="#1f1f1f")
        nav_frame.pack(fill="x", padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        button_config = {
            "height": 40,
            "font": ("Arial Bold", 14),
            "corner_radius": 8
        }
        
        buttons_info = [
            ("📊 Dashboard", self.show_dashboard, "#4CAF50"),
            ("➕ Add Faculty", self.show_add_faculty, "#2196F3"),
            ("📋 View Faculty", self.show_view_faculty, "#9C27B0"),
            ("📝 Manage Tasks", self.show_manage_tasks, "#E91E63"),
            ("📈 Attendance Records", self.show_attendance_records, "#FF9800"),
            ("⚙️ Settings", self.show_settings, "#607D8B"),
        ]
        
        for text, command, color in buttons_info:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color=self.darken_color(color),
                **button_config
            )
            btn.pack(side="left", padx=10, pady=10)
        
        # Logout button on the right side
        def logout():
            confirm = mess.askyesno("Logout", "🚪 Are you sure you want to logout?")
            if confirm:
                self.root.destroy()
        
        logout_btn = ctk.CTkButton(
            nav_frame,
            text="🚪 Logout",
            command=logout,
            fg_color="#f44336",
            hover_color="#da190b",
            **button_config
        )
        logout_btn.pack(side="right", padx=20, pady=10)
    
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
        """Show dashboard with statistics"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Dashboard Overview",
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Statistics Frame
        stats_frame = ctk.CTkFrame(self.content_frame)
        stats_frame.pack(fill="x", padx=40, pady=20)
        
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
        
        # Display stats
        stats = [
            ("👥 Total Faculty", total_faculty, "#4CAF50"),
            ("📸 Training Images", image_count, "#2196F3"),
            ("📅 Attendance Days", attendance_count, "#FF9800"),
        ]
        
        for label, value, color in stats:
            stat_card = ctk.CTkFrame(stats_frame, width=300, height=120, fg_color=color)
            stat_card.pack(side="left", padx=20, pady=20, expand=True)
            stat_card.pack_propagate(False)
            
            ctk.CTkLabel(
                stat_card,
                text=label,
                font=("Arial Bold", 18)
            ).pack(pady=(20, 5))
            
            ctk.CTkLabel(
                stat_card,
                text=str(value),
                font=("Arial Bold", 36)
            ).pack()
        
        # Recent Activity
        recent_frame = ctk.CTkFrame(self.content_frame)
        recent_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(
            recent_frame,
            text="📋 Recent Faculty Members",
            font=("Arial Bold", 20)
        ).pack(pady=10)
        
        if len(df) > 0:
            # Show last 5 faculty members
            for idx, row in df.tail(5).iterrows():
                if pd.notna(row.get('ID')):
                    faculty_card = ctk.CTkFrame(recent_frame, fg_color="#2b2b2b")
                    faculty_card.pack(fill="x", padx=20, pady=5)
                    
                    info_text = f"ID: {row['ID']}  |  Name: {row['NAME']}"
                    ctk.CTkLabel(
                        faculty_card,
                        text=info_text,
                        font=("Arial", 14)
                    ).pack(pady=10, padx=20)
        else:
            ctk.CTkLabel(
                recent_frame,
                text="No faculty registered yet",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
    
    def show_add_faculty(self):
        """Show enhanced add faculty interface"""
        self.clear_content()
        
        # Header with gradient-like effect
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="#2196F3", height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header_frame,
            text="➕ Register New Faculty Member",
            font=("Arial Bold", 32),
            text_color="white"
        )
        title.pack(pady=20)
        
        ctk.CTkLabel(
            header_frame,
            text="Complete the form below to add a new faculty member to the system",
            font=("Arial", 14),
            text_color="#E3F2FD"
        ).pack()
        
        # Main form container
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=40)
        
        # Left side - Form
        form_frame = ctk.CTkFrame(main_container, width=500, fg_color="#1e1e1e")
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        ctk.CTkLabel(
            form_frame,
            text="📝 Faculty Information",
            font=("Arial Bold", 20),
            text_color="#2196F3"
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
            corner_radius=8
        )
        id_entry.pack(pady=5)
        
        ctk.CTkLabel(
            id_frame,
            text="💡 Use unique identifier (letters, numbers, dashes)",
            font=("Arial", 11),
            text_color="gray"
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
            corner_radius=8
        )
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(
            name_frame,
            text="💡 Full name with proper capitalization",
            font=("Arial", 11),
            text_color="gray"
        ).pack(anchor="w", pady=(2, 0))
        
        # Status/Progress Section
        status_frame = ctk.CTkFrame(form_frame, fg_color="#2b2b2b", corner_radius=10)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="📋 Ready to capture images",
            font=("Arial Bold", 14),
            text_color="#4CAF50"
        )
        status_label.pack(pady=15, padx=20)
        
        progress_bar = ctk.CTkProgressBar(status_frame, width=410, height=20)
        progress_bar.pack(pady=(0, 15), padx=20)
        progress_bar.set(0)
        
        # Right side - Instructions
        info_frame = ctk.CTkFrame(main_container, width=350, fg_color="#1e1e1e")
        info_frame.pack(side="right", fill="both", padx=(20, 0))
        info_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            info_frame,
            text="📸 Photo Capture Guidelines",
            font=("Arial Bold", 18),
            text_color="#FF9800"
        ).pack(pady=20, padx=20, anchor="w")
        
        guidelines = [
            ("✓", "Ensure good lighting conditions", "#4CAF50"),
            ("✓", "Face the camera directly", "#4CAF50"),
            ("✓", "Neutral facial expression", "#4CAF50"),
            ("✓", "Remove sunglasses/masks", "#4CAF50"),
            ("✓", "100 photos will be captured", "#2196F3"),
            ("✓", "Process takes ~30 seconds", "#2196F3"),
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
        camera_info = ctk.CTkFrame(info_frame, fg_color="#2b2b2b", corner_radius=10)
        camera_info.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            camera_info,
            text="🎥 Camera Requirements",
            font=("Arial Bold", 14),
            text_color="#FF6B6B"
        ).pack(pady=10, padx=15, anchor="w")
        
        ctk.CTkLabel(
            camera_info,
            text="• Webcam must be connected\n• Close other camera apps\n• Grant camera permissions",
            font=("Arial", 12),
            justify="left",
            anchor="w"
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
                df = pd.read_csv(faculty_details_path)
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
                text_color="#FF9800"
            )
            progress_bar.set(0.1)
            self.root.update()
            
            try:
                cam = cv2.VideoCapture(0)
                if not cam.isOpened():
                    mess.showerror("Camera Error", "❌ Cannot access camera!\n\nPlease check:\n• Camera is connected\n• No other apps using camera\n• Camera permissions granted")
                    status_label.configure(text="❌ Camera not accessible", text_color="#f44336")
                    progress_bar.set(0)
                    return
                
                detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
                sample_num = 0
                
                status_label.configure(
                    text="📸 Camera ready! Look at the camera and stay still",
                    text_color="#4CAF50"
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
                            status_label.configure(text="❌ Capture cancelled", text_color="#f44336")
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
                                         text_color="#FF9800")
                    progress_bar.set(0)
                    return
                
                # Save to CSV using append mode to avoid concat issues
                with open(faculty_details_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([serial, '', faculty_id, '', faculty_name])
                
                status_label.configure(
                    text=f"✅ {sample_num} images captured successfully!",
                    text_color="#4CAF50"
                )
                progress_bar.set(0.8)
                self.root.update()
                
                # Train model automatically
                status_label.configure(text="🔄 Training model... Please wait", text_color="#2196F3")
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
                    text_color="#4CAF50"
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
                status_label.configure(text="❌ Registration failed", text_color="#f44336")
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
            fg_color="#4CAF50",
            hover_color="#45a049",
            corner_radius=10
        )
        capture_btn.pack(side="left", padx=(0, 10))
        
        # Clear Button
        def clear_form():
            id_entry.delete(0, 'end')
            name_entry.delete(0, 'end')
            status_label.configure(text="📋 Ready to capture images", text_color="#4CAF50")
            progress_bar.set(0)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Clear Form",
            command=clear_form,
            width=110,
            height=55,
            font=("Arial Bold", 14),
            fg_color="#757575",
            hover_color="#616161",
            corner_radius=10
        )
        clear_btn.pack(side="left", padx=5)
        
        # Cancel Button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.show_dashboard,
            width=110,
            height=55,
            font=("Arial Bold", 14),
            fg_color="#f44336",
            hover_color="#da190b",
            corner_radius=10
        )
        cancel_btn.pack(side="left", padx=5)
    
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
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            self.content_frame,
            text="🔄 Refresh",
            command=self.show_view_faculty,
            width=120,
            height=35,
            fg_color="#2196F3"
        )
        refresh_btn.pack(pady=5)
        
        # Table Frame
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                       fieldbackground="#2b2b2b", font=('Arial', 11))
        style.configure("Treeview.Heading", background="#1f6aa5", foreground="white",
                       font=('Arial Bold', 12))
        style.map('Treeview', background=[('selected', '#1f6aa5')])
        
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
            fg_color="#f44336",
            hover_color="#da190b",
            width=150
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
            font=("Arial Bold", 28)
        )
        title.pack(pady=20)
        
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
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                       fieldbackground="#2b2b2b", font=('Arial', 11))
        style.configure("Treeview.Heading", background="#1f6aa5", foreground="white",
                       font=('Arial Bold', 12))
        
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
        
        # Load button
        ctk.CTkButton(
            date_frame,
            text="📊 Load Records",
            command=load_attendance,
            width=120,
            fg_color="#4CAF50"
        ).pack(side="left", padx=10)
        
        # Export button
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
            width=120,
            fg_color="#2196F3"
        ).pack(side="left", padx=10)
        
        # Auto-load latest
        load_attendance()
    
    def show_manage_tasks(self):
        """Show enhanced task management interface"""
        self.clear_content()
        
        # Compact Header with gradient effect
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="#E91E63", height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True)
        
        ctk.CTkLabel(
            header_content,
            text="📝 Task & Deadline Manager",
            font=("Arial Bold", 28),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            header_content,
            text="Assign tasks and track faculty deadlines",
            font=("Arial", 12),
            text_color="#FCE4EC"
        ).pack()
        
        # Main container with better spacing
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=5)
        
        # Left - Compact Add Task Form
        form_frame = ctk.CTkFrame(main_container, width=480, fg_color="#1a1a1a", 
                                 border_width=2, border_color="#E91E63")
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Compact form header with icon
        form_header = ctk.CTkFrame(form_frame, fg_color="#E91E63", height=50, corner_radius=0)
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
                                         font=("Arial", 12), fg_color="#2196F3",
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
        
        priority_colors = {
            "Low": "#4CAF50",
            "Medium": "#FF9800", 
            "High": "#FF5722",
            "Urgent": "#f44336"
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
        status_frame = ctk.CTkFrame(fields_container, fg_color="#2b2b2b", corner_radius=8, height=40)
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
                     fg_color="#4CAF50", hover_color="#45a049",
                     corner_radius=10).pack(side="left", padx=5)
        
        def clear_form():
            task_title_entry.delete(0, 'end')
            task_desc.delete("1.0", "end")
            date_entry.delete(0, 'end')
            date_entry.insert(0, today)
            selected_faculty.set("🔽 Select Faculty Member")
            select_priority("Medium")
            status_label.configure(text="✏️ Fill in the form to create a task", text_color="gray")
        
        ctk.CTkButton(button_inner, text="🔄 Reset", command=clear_form,
                     width=100, height=45, font=("Arial Bold", 13),
                     fg_color="#757575", hover_color="#616161",
                     corner_radius=10).pack(side="left", padx=5)
        
        ctk.CTkButton(button_inner, text="❌ Cancel", command=self.show_dashboard,
                     width=100, height=45, font=("Arial Bold", 13),
                     fg_color="#f44336", hover_color="#da190b",
                     corner_radius=10).pack(side="left", padx=5)
        
        # Right - Compact Task List View
        tasks_view_frame = ctk.CTkFrame(main_container, fg_color="#1a1a1a",
                                       border_width=2, border_color="#FF9800")
        tasks_view_frame.pack(side="right", fill="both", expand=True)
        
        # Tasks header
        tasks_header = ctk.CTkFrame(tasks_view_frame, fg_color="#FF9800", height=50, corner_radius=0)
        tasks_header.pack(fill="x")
        tasks_header.pack_propagate(False)
        
        ctk.CTkLabel(tasks_header, text="📋 Task List & Overview", 
                    font=("Arial Bold", 18), text_color="white").pack(pady=12)
        
        # Compact filter and controls
        control_bar = ctk.CTkFrame(tasks_view_frame, fg_color="#2b2b2b", height=45)
        control_bar.pack(fill="x", padx=10, pady=10)
        control_bar.pack_propagate(False)
        
        ctk.CTkLabel(control_bar, text="📊", font=("Arial", 16)).pack(side="left", padx=8)
        
        filter_var = ctk.StringVar(value="Today")
        filter_menu = ctk.CTkOptionMenu(control_bar, variable=filter_var,
                                        values=["All", "Today", "This Week", "Pending", "Completed"],
                                        width=140, height=32, font=("Arial", 11),
                                        fg_color="#607D8B", button_color="#455A64")
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
                empty_frame = ctk.CTkFrame(tasks_list_frame, fg_color="#2b2b2b", corner_radius=10)
                empty_frame.pack(fill="both", expand=True, pady=50, padx=20)
                
                ctk.CTkLabel(empty_frame, text="📭", font=("Arial", 48)).pack(pady=20)
                ctk.CTkLabel(empty_frame, text="No tasks found", 
                           font=("Arial Bold", 16), text_color="gray").pack()
                ctk.CTkLabel(empty_frame, text="Create a new task to get started", 
                           font=("Arial", 12), text_color="gray").pack(pady=(5, 20))
            else:
                for idx, task in tasks_df.iterrows():
                    # Compact task card with modern design
                    task_card = ctk.CTkFrame(tasks_list_frame, fg_color="#242424", 
                                            corner_radius=8, border_width=1, border_color="#444")
                    task_card.pack(fill="x", pady=4, padx=3)
                    
                    # Priority colors
                    priority_colors = {"Low": "#4CAF50", "Medium": "#FF9800", 
                                      "High": "#FF5722", "Urgent": "#f44336"}
                    p_color = priority_colors.get(task['PRIORITY'], "#FF9800")
                    
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
                        status_frame = ctk.CTkFrame(btn_row, fg_color="#4CAF50", corner_radius=4, height=24)
                        status_frame.pack(side="left", padx=5)
                        ctk.CTkLabel(status_frame, text="✓ Completed", font=("Arial Bold", 10),
                                   text_color="white").pack(padx=10, pady=3)
                    else:
                        ctk.CTkButton(btn_row, text="✓ Done", command=complete_task,
                                    width=70, height=24, fg_color="#4CAF50", 
                                    hover_color="#45a049",
                                    font=("Arial Bold", 9), corner_radius=5).pack(side="left", padx=3)
                    
                    ctk.CTkButton(btn_row, text="🗑️", command=delete_task,
                                width=35, height=24, fg_color="#f44336",
                                hover_color="#da190b",
                                font=("Arial", 10), corner_radius=5).pack(side="right", padx=3)
        
        # Refresh and filter controls
        ctk.CTkButton(control_bar, text="🔄", command=refresh_tasks,
                     width=40, height=32, font=("Arial", 14),
                     fg_color="#4CAF50", hover_color="#45a049").pack(side="left", padx=5)
        
        # Task count label
        task_count_label = ctk.CTkLabel(control_bar, text="", font=("Arial Bold", 11))
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
            
            current_pass = authenticate_admin()
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
                f.write(new_pass)
            
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
    if check_password():
        root = ctk.CTk()
        app = AdminPanel(root)
        root.mainloop()
    else:
        print("Access denied. Exiting...")

if __name__ == "__main__":
    main()

