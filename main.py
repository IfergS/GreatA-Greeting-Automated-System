############################################# IMPORTING ################################################
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
import time
import speech_recognition as sr
import pyttsx3
import requests
import json
import random
from threading import Thread, Lock
import platform
import subprocess
from queue import Queue

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

############################################# VOICE ASSISTANT ###########################################

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.registered_users = {}  # Store recognized users
        self.load_registered_users()
        
        # Voice queue to prevent overlapping speech
        self.speech_queue = Queue()
        self.speech_lock = Lock()
        self.is_speaking = False
        
        # Start the speech worker thread
        self.speech_worker_thread = Thread(target=self._speech_worker, daemon=True)
        self.speech_worker_thread.start()
        
        # Configure TTS - Set American English voice
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find American English voice (en_US)
        american_voice = None
        for voice in voices:
            # Look for US English voices
            if 'en_US' in voice.id or 'en-US' in voice.id or 'US' in voice.name:
                american_voice = voice.id
                break
            # Fallback: Look for any English voice
            elif 'en' in voice.id.lower() or 'english' in voice.name.lower():
                american_voice = voice.id
        
        # Set the American English voice if found, otherwise use default
        if american_voice:
            self.tts_engine.setProperty('voice', american_voice)
        
        # Set faster speech rate to avoid prolonged speech (200 = faster, natural pace)
        self.tts_engine.setProperty('rate', 200)
        
        # Set volume to maximum for clarity
        self.tts_engine.setProperty('volume', 1.0)
    
    def _speech_worker(self):
        """Worker thread that processes speech queue sequentially"""
        while True:
            try:
                # Get next text from queue (blocks until available)
                text = self.speech_queue.get()
                
                if text is None:  # Poison pill to stop worker
                    break
                
                # Actually speak the text
                self._do_speak(text)
                
                # Mark task as done
                self.speech_queue.task_done()
                
            except Exception as e:
                print(f"Speech worker error: {e}")
    
    def _do_speak(self, text):
        """Actually perform the speech (called sequentially by worker)"""
        try:
            print(f"🔊 Speaking: {text}")
            system = platform.system()
            
            with self.speech_lock:  # Ensure only one speech at a time
                self.is_speaking = True
                
                if system == "Darwin":  # macOS
                    # Use macOS native 'say' command
                    subprocess.run(['say', '-v', 'Samantha', '-r', '200', text], 
                                 check=False, capture_output=True)
                
                elif system == "Windows":  # Windows
                    # Use pyttsx3 SAPI5
                    engine = pyttsx3.init('sapi5')
                    voices = engine.getProperty('voices')
                    
                    american_voice = None
                    for voice in voices:
                        if 'zira' in voice.name.lower() or 'david' in voice.name.lower():
                            american_voice = voice.id
                            break
                        elif 'en' in voice.id.lower() or 'US' in voice.id:
                            american_voice = voice.id
                            break
                    
                    if american_voice:
                        engine.setProperty('voice', american_voice)
                    
                    engine.setProperty('rate', 200)
                    engine.setProperty('volume', 1.0)
                    engine.say(text)
                    engine.runAndWait()
                    engine.stop()
                
                else:  # Linux or other
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 200)
                    engine.setProperty('volume', 1.0)
                    engine.say(text)
                    engine.runAndWait()
                
                self.is_speaking = False
                
        except Exception as e:
            print(f"❌ Voice error: {e}")
            self.is_speaking = False
        
    def load_registered_users(self):
        """Load registered users from FacultyDetails.csv"""
        try:
            faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
            if os.path.isfile(faculty_details_path):
                df = pd.read_csv(faculty_details_path)
                for index, row in df.iterrows():
                    if pd.notna(row['ID']) and pd.notna(row['NAME']):
                        self.registered_users[str(row['ID'])] = str(row['NAME'])
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def speak(self, text):
        """Queue text for speech - ensures sequential playback without overlap"""
        # Add text to the queue
        self.speech_queue.put(text)
        print(f"📝 Queued for speech: {text}")
    
    def wait_until_done(self):
        """Wait for all queued speech to finish"""
        self.speech_queue.join()
    
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
        elif 12 <= current_hour < 14:
            return "Good noon"
        elif 14 <= current_hour < 17:
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
        
        else:
            response = f"I'm sorry {user_name}, I didn't understand that command. You can ask me about time, weather, or date."
        
        return response, None

# Global voice assistant instance
voice_assistant = VoiceAssistant()

############################################# FUNCTIONS ################################################

def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        mess.showerror('File Missing', 'Please add haarcascade_frontalface_default.xml')
        return False
    return True

def contact():
    mess.showinfo('Contact Us', "Please contact us on: 'greeta.support@email.com'")

def save_pass():
    assure_path_exists("TrainingImageLabel/")
    psd_path = os.path.join("TrainingImageLabel", "psd.txt")
    exists1 = os.path.isfile(psd_path)
    if exists1:
        with open(psd_path, "r") as tf:
            key = tf.read()
    else:
        master.destroy()
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess.showwarning('No Password Entered', 'Password not set!! Please try again')
        else:
            with open(psd_path, "w") as tf:
                tf.write(new_pas)
            mess.showinfo('Password Registered', 'New password was registered successfully!!')
            return
    op = old.get()
    newp = new.get()
    nnewp = nnew.get()
    if op == key:
        if newp == nnewp:
            with open(psd_path, "w") as txf:
                txf.write(newp)
            mess.showinfo('Password Changed', 'Password changed successfully!!')
            master.destroy()
        else:
            mess.showerror('Error', 'Confirm new password again!!!')
    else:
        mess.showerror('Wrong Password', 'Please enter correct old password.')

def change_pass():
    global master, old, new, nnew
    master = ctk.CTkToplevel()
    master.geometry("450x250")
    master.title("Change Password")
    
    ctk.CTkLabel(master, text="Change Password", font=("Arial Bold", 20)).pack(pady=20)
    
    ctk.CTkLabel(master, text="Enter Old Password:").pack(pady=5)
    old = ctk.CTkEntry(master, width=300, show='*')
    old.pack(pady=5)
    
    ctk.CTkLabel(master, text="Enter New Password:").pack(pady=5)
    new = ctk.CTkEntry(master, width=300, show='*')
    new.pack(pady=5)
    
    ctk.CTkLabel(master, text="Confirm New Password:").pack(pady=5)
    nnew = ctk.CTkEntry(master, width=300, show='*')
    nnew.pack(pady=5)
    
    button_frame = ctk.CTkFrame(master, fg_color="transparent")
    button_frame.pack(pady=20)
    
    ctk.CTkButton(button_frame, text="Save", command=save_pass, width=140).pack(side="left", padx=5)
    ctk.CTkButton(button_frame, text="Cancel", command=master.destroy, width=140, fg_color="gray").pack(side="left", padx=5)

def psw():
    assure_path_exists("TrainingImageLabel/")
    psd_path = os.path.join("TrainingImageLabel", "psd.txt")
    exists1 = os.path.isfile(psd_path)
    if exists1:
        with open(psd_path, "r") as tf:
            key = tf.read()
    else:
        new_pas = tsd.askstring('Old Password not found', 'Please enter a new password below', show='*')
        if new_pas == None:
            mess.showwarning('No Password Entered', 'Password not set!! Please try again')
        else:
            with open(psd_path, "w") as tf:
                tf.write(new_pas)
            mess.showinfo('Password Registered', 'New password was registered successfully!!')
            return
    password = tsd.askstring('Password', 'Enter Password', show='*')
    if password == key:
        TrainImages()
    elif password == None:
        pass
    else:
        mess.showerror('Wrong Password', 'You have entered wrong password')

def clear():
    txt.delete(0, 'end')
    message1.configure(text="1) Take Images  >>>  2) Save Profile")

def clear2():
    txt2.delete(0, 'end')
    message1.configure(text="1) Take Images  >>>  2) Save Profile")

def TakeImages():
    if not check_haarcascadefile():
        return
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("FacultyDetails/")
    assure_path_exists("TrainingImage/")
    serial = 0
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    exists = os.path.isfile(faculty_details_path)
    if exists:
        with open(faculty_details_path, 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
    else:
        with open(faculty_details_path, 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
    Id = txt.get()
    name = txt2.get()
    if name.replace(' ', '').isalpha() and Id:
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        while True:
            ret, img = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                sampleNum = sampleNum + 1
                image_filename = name + "." + str(serial) + "." + Id + '.' + str(sampleNum) + ".jpg"
                image_path = os.path.join("TrainingImage", image_filename)
                cv2.imwrite(image_path, gray[y:y + h, x:x + w])
                cv2.imshow('Capturing Face - Press Q to stop', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum >= 100:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "✓ Images Captured for ID: " + Id
        row = [serial, '', Id, '', name]
        with open(faculty_details_path, 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        message1.configure(text=res)
        voice_assistant.load_registered_users()
        update_registration_count()
    else:
        mess.showerror("Invalid Input", "Please enter a valid name and ID")

def TrainImages():
    if not check_haarcascadefile():
        return
    assure_path_exists("TrainingImageLabel/")
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    faces, ID = getImagesAndLabels("TrainingImage")
    if len(faces) == 0:
        mess.showerror('No Registrations', 'Please Register someone first!!!')
        return
    try:
        recognizer.train(faces, np.array(ID))
    except:
        mess.showerror('No Registrations', 'Please Register someone first!!!')
        return
    trainer_path = os.path.join("TrainingImageLabel", "Trainner.yml")
    recognizer.save(trainer_path)
    res = "✓ Profile Saved Successfully"
    message1.configure(text=res)
    mess.showinfo("Success", "Training completed successfully!")

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            ID = int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(imageNp)
            Ids.append(ID)
        except:
            continue
    return faces, Ids

def TrackImages():
    if not check_haarcascadefile():
        return
    assure_path_exists("Attendance/")
    assure_path_exists("FacultyDetails/")
    
    for k in tv.get_children():
        tv.delete(k)
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    trainer_path = os.path.join("TrainingImageLabel", "Trainner.yml")
    exists3 = os.path.isfile(trainer_path)
    if exists3:
        recognizer.read(trainer_path)
    else:
        mess.showerror('Data Missing', 'Please click on Save Profile to reset data!!')
        return
    
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)

    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    exists1 = os.path.isfile(faculty_details_path)
    if exists1:
        df = pd.read_csv(faculty_details_path)
    else:
        mess.showerror('Details Missing', 'Faculty details are missing! Please register faculty in Admin Panel first.')
        cam.release()
        cv2.destroyAllWindows()
        return
    
    greeted_users = set()
    recorded_users = set()  # Track who has been recorded in this session
    
    # Load today's attendance to check for existing records
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    attendance_filename = "Attendance_" + date + ".csv"
    attendance_path = os.path.join("Attendance", attendance_filename)
    
    # Check if attendance file exists and load existing IDs
    existing_attendance_ids = set()
    if os.path.isfile(attendance_path):
        try:
            with open(attendance_path, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if len(row) >= 7 and row[0]:
                        existing_attendance_ids.add(row[0].strip().strip("'"))
        except:
            pass
    
    voice_assistant.speak("Starting attendance system. Please look at the camera.")
    
    # Counter for session stats
    session_count = 0
    
    while True:
        ret, im = cam.read()
        if not ret:
            break
        
        # Resize for better display
        display_im = im.copy()
        h_img, w_img = display_im.shape[:2]
        
        # Create overlay for header
        overlay = display_im.copy()
        cv2.rectangle(overlay, (0, 0), (w_img, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_im, 0.3, 0, display_im)
        
        # Header text
        cv2.putText(display_im, "Faculty Attendance System", (20, 30), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cv2.putText(display_im, f"Time: {current_time}", (20, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, f"Recorded Today: {len(existing_attendance_ids)}", 
                   (w_img - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, f"Session Count: {session_count}", 
                   (w_img - 250, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Create footer overlay
        footer_overlay = display_im.copy()
        cv2.rectangle(footer_overlay, (0, h_img - 50), (w_img, h_img), (0, 0, 0), -1)
        cv2.addWeighted(footer_overlay, 0.7, display_im, 0.3, 0, display_im)
        
        # Footer instructions
        cv2.putText(display_im, "Press 'Q' to Exit", (20, h_img - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, "Look at camera for recognition", (w_img - 350, h_img - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # Enhanced detection parameters for better accuracy
        # scaleFactor=1.1 (more precise), minNeighbors=8 (stricter detection)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=8, 
                                            minSize=(100, 100), maxSize=(500, 500))
        
        for (x, y, w, h) in faces:
            # Initialize variables for THIS face (prevents data from previous face)
            bb = "Unknown"
            ID = "Unknown"
            faculty_tasks = []
            color = (0, 0, 255)  # Default red for unknown
            status_text = "UNKNOWN"
            
            try:
                serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
            except:
                # If prediction fails, treat as unknown
                conf = 100
            
            # Stricter confidence threshold for better accuracy
            # Lower value = more confident match
            # Changed from 50 to 40 for better precision
            if conf < 40:  # Recognized faculty (high confidence only)
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                ID = str(ID)
                ID = ID[1:-1]
                bb = str(aa)
                bb = bb[2:-2]
                
                # Check for tasks due today for this faculty (needed for display)
                today_date = datetime.datetime.now().strftime('%Y-%m-%d')
                tasks_path = os.path.join("Tasks", "Tasks.csv")
                faculty_tasks = []
                
                # Debug: Print the ID we're checking
                print(f"🔍 Checking tasks for Faculty ID: '{ID}', Name: '{bb}', Date: {today_date}")
                
                if os.path.isfile(tasks_path):
                    try:
                        tasks_df = pd.read_csv(tasks_path)
                        print(f"📋 Total tasks in database: {len(tasks_df)}")
                        
                        # Clean and compare IDs (remove quotes, whitespace, etc.)
                        clean_id = str(ID).strip().strip("'").strip('"')
                        print(f"🔍 Cleaned Faculty ID: '{clean_id}'")
                        
                        # Filter tasks for this faculty member due today and not completed
                        faculty_tasks_df = tasks_df[
                            (tasks_df['FACULTY_ID'].astype(str).str.strip() == clean_id) & 
                            (tasks_df['DUE_DATE'].astype(str) == today_date) & 
                            (tasks_df['STATUS'] != 'Completed')
                        ]
                        
                        print(f"📝 Found {len(faculty_tasks_df)} tasks for this faculty today")
                        
                        for idx, task in faculty_tasks_df.iterrows():
                            print(f"✓ Task found: {task['TASK_TITLE']} (Priority: {task['PRIORITY']})")
                            faculty_tasks.append({
                                'title': task['TASK_TITLE'],
                                'description': task['TASK_DESCRIPTION'] if pd.notna(task['TASK_DESCRIPTION']) else '',
                                'priority': task['PRIORITY']
                            })
                    except Exception as e:
                        print(f"❌ Task check error: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Check if this faculty already has attendance today
                already_recorded = ID in existing_attendance_ids or ID in recorded_users
                
                if not already_recorded:
                    # Record attendance
                    attendance = [str(ID), '', bb, '', str(date), '', str(timeStamp)]
                    
                    # Save to file immediately
                    exists = os.path.isfile(attendance_path)
                    with open(attendance_path, 'a+') as csvFile1:
                        writer = csv.writer(csvFile1)
                        if not exists:
                            writer.writerow(col_names)
                        writer.writerow(attendance)
                    
                    # Add to treeview
                    tv.insert('', 0, values=(str(ID), bb, str(date), str(timeStamp)))
                    
                    # Mark as recorded
                    recorded_users.add(ID)
                    existing_attendance_ids.add(ID)
                    session_count += 1
                
                # Greet faculty (only once per session)
                if ID not in greeted_users:
                    time_greeting = voice_assistant.get_time_greeting()
                    
                    # Build greeting with task announcements
                    if already_recorded and ID not in recorded_users:
                        # Already recorded today (from earlier)
                        full_greeting = f"Hi {bb}, {time_greeting}, Your attendance for today is already recorded"
                    else:
                        # First time today
                        full_greeting = f"Hi {bb}, {time_greeting}, Welcome to Faculty Office"
                    
                    # Add detailed task announcements if any
                    if len(faculty_tasks) > 0:
                        if len(faculty_tasks) == 1:
                            task = faculty_tasks[0]
                            task_msg = f". You have 1 task due today. Task title: {task['title']}. "
                            
                            if task['description']:
                                task_msg += f"Description: {task['description']}. "
                            
                            task_msg += f"Priority: {task['priority']}"
                        else:
                            task_count = len(faculty_tasks)
                            task_msg = f". You have {task_count} tasks due today. "
                            
                            for i, task in enumerate(faculty_tasks, 1):
                                task_msg += f"Task {i}: {task['title']}. "
                                if task['description']:
                                    task_msg += f"{task['description']}. "
                                task_msg += f"Priority: {task['priority']}. "
                        
                        full_greeting += task_msg
                    
                    # Debug print
                    print(f"Speaking: {full_greeting}")
                    
                    # Speak the greeting
                    try:
                        voice_assistant.speak(full_greeting)
                    except Exception as e:
                        print(f"Voice error: {e}")
                    
                    greeted_users.add(ID)
                
                # Enhanced face rectangle with rounded effect (multiple rectangles)
                if already_recorded and ID not in recorded_users:
                    # Orange for already recorded
                    color = (0, 165, 255)  # BGR: Orange
                    status_text = "ALREADY RECORDED TODAY"
                    status_color = (0, 165, 255)
                else:
                    # Green for newly recorded
                    color = (0, 255, 0)  # BGR: Green
                    status_text = "ATTENDANCE RECORDED ✓"
                    status_color = (0, 255, 0)
                
                # Draw thick rectangle around face
                cv2.rectangle(display_im, (x-5, y-5), (x+w+5, y+h+5), color, 3)
                cv2.rectangle(display_im, (x-3, y-3), (x+w+3, y+h+3), (255, 255, 255), 1)
                
                # Create info box above face
                info_y = max(y - 120, 100)
                box_width = max(len(bb) * 15, 300)
                
                # Semi-transparent background for info
                overlay_box = display_im.copy()
                cv2.rectangle(overlay_box, (x, info_y), (x + box_width, info_y + 90), (0, 0, 0), -1)
                cv2.addWeighted(overlay_box, 0.7, display_im, 0.3, 0, display_im)
                
                # Name (larger, bold)
                cv2.putText(display_im, bb, (x + 10, info_y + 30), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
                
                # ID
                cv2.putText(display_im, f"ID: {ID}", (x + 10, info_y + 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Status
                cv2.putText(display_im, status_text, (x + 10, info_y + 78), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
                
                # Enhanced confidence display
                # Show actual confidence level (lower conf = better match)
                match_quality = 100 - (conf * 2)  # Scale confidence for display
                match_quality = max(0, min(100, match_quality))  # Clamp between 0-100
                
                # Color code the confidence
                if conf < 30:
                    conf_color = (0, 255, 0)  # Green - Excellent match
                elif conf < 40:
                    conf_color = (0, 255, 255)  # Yellow - Good match
                else:
                    conf_color = (0, 165, 255)  # Orange - Acceptable match
                
                cv2.putText(display_im, f"Confidence: {match_quality:.0f}%", (x + w - 150, y + h + 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, conf_color, 2)
                
                # Display tasks if any (show on camera)
                if len(faculty_tasks) > 0:
                    task_box_y = min(y + h + 35, h_img - 100)
                    task_box_width = min(400, w_img - x - 10)
                    
                    # Task notification box
                    task_overlay = display_im.copy()
                    cv2.rectangle(task_overlay, (x, task_box_y), 
                                (x + task_box_width, task_box_y + 30 + (len(faculty_tasks) * 25)), 
                                (255, 100, 0), -1)
                    cv2.addWeighted(task_overlay, 0.8, display_im, 0.2, 0, display_im)
                    
                    # Task header
                    cv2.putText(display_im, f"📋 {len(faculty_tasks)} Task(s) Due Today:", 
                               (x + 10, task_box_y + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # List tasks (max 3 visible)
                    for i, task in enumerate(faculty_tasks[:3]):
                        priority_icon = "🔴" if task['priority'] == "Urgent" else "🟠" if task['priority'] == "High" else "🟡"
                        task_text = f"{priority_icon} {task['title'][:35]}"
                        cv2.putText(display_im, task_text, 
                                   (x + 15, task_box_y + 45 + (i * 25)), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            else:
                # Unknown person - use initialized default values (bb="Unknown", ID="Unknown")
                # Red rectangle with warning effect
                cv2.rectangle(display_im, (x-5, y-5), (x+w+5, y+h+5), (0, 0, 255), 3)
                cv2.rectangle(display_im, (x-3, y-3), (x+w+3, y+h+3), (255, 255, 255), 1)
                
                # Unknown label with background
                info_y = max(y - 70, 100)
                overlay_unknown = display_im.copy()
                cv2.rectangle(overlay_unknown, (x, info_y), (x + 250, info_y + 55), (0, 0, 0), -1)
                cv2.addWeighted(overlay_unknown, 0.7, display_im, 0.3, 0, display_im)
                
                cv2.putText(display_im, "UNKNOWN PERSON", (x + 10, info_y + 30), 
                           cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(display_im, "Not Registered", (x + 10, info_y + 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 255), 1)
                
                # Note: No tasks displayed for unknown persons (faculty_tasks is empty list by default)
        
        # If no faces detected
        if len(faces) == 0:
            cv2.putText(display_im, "No face detected - Please look at camera", 
                       (int(w_img/2) - 250, int(h_img/2)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Show enhanced frame
        cv2.imshow('🎓 Faculty Attendance Recognition', display_im)
        
        # Check for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('r') or key == ord('R'):
            # Refresh recognition (reset greeted users)
            greeted_users.clear()
    
    # Release camera
    cam.release()
    
    # AGGRESSIVE window cleanup - destroy specific window by name first
    try:
        cv2.destroyWindow('🎓 Faculty Attendance Recognition')
    except:
        pass
    
    # Multiple destroy calls to ensure window closes
    for _ in range(20):
        cv2.destroyAllWindows()
        cv2.waitKey(1)
    
    # Give OS time to process
    time.sleep(0.3)
    
    # Final cleanup
    cv2.destroyAllWindows()
    for _ in range(5):
        cv2.waitKey(1)

def start_voice_command():
    """Start listening for voice commands"""
    def listen_and_process():
        voice_status.configure(text="🎤 Listening...", text_color="yellow")
        command = voice_assistant.listen()
        
        if command == "timeout":
            voice_status.configure(text="⏱️ No command detected", text_color="orange")
            return
        elif command == "unknown":
            voice_status.configure(text="❌ Could not understand", text_color="red")
            return
        elif command == "error":
            voice_status.configure(text="❌ Microphone error", text_color="red")
            return
        
        voice_status.configure(text=f"✓ Heard: {command}", text_color="green")
        
        response, action = voice_assistant.handle_command(command)
        voice_response.configure(text=response)
        voice_assistant.speak(response)
    
    thread = Thread(target=listen_and_process)
    thread.daemon = True
    thread.start()

def update_registration_count():
    """Update the registration count display"""
    res = 0
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    exists = os.path.isfile(faculty_details_path)
    if exists:
        with open(faculty_details_path, 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                res = res + 1
        res = (res // 2) - 1
    else:
        res = 0
    message.configure(text=f'📊 Total Faculty: {res}')

######################################## GUI FRONT-END ###########################################

window = ctk.CTk()
window.geometry("1500x850")
window.title("GreetA - Faculty Attendance System")

# Header
header_frame = ctk.CTkFrame(window, height=70, corner_radius=0)
header_frame.pack(fill="x", padx=0, pady=0)
header_frame.pack_propagate(False)

title_label = ctk.CTkLabel(
    header_frame, 
    text="🎓 GreetA: Faculty Attendance System",
    font=("Arial Bold", 28),
    text_color="#00D9FF"
)
title_label.pack(pady=15)

# Date and Time Frame
datetime_frame = ctk.CTkFrame(window, height=35, fg_color="transparent")
datetime_frame.pack(fill="x", padx=20, pady=2)

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")
mont = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June',
        '07':'July', '08':'August', '09':'September', '10':'October', '11':'November', '12':'December'}

date_label = ctk.CTkLabel(datetime_frame, text=f"📅 {day} {mont[month]} {year}", font=("Arial", 14))
date_label.pack(side="left", padx=20)

clock = ctk.CTkLabel(datetime_frame, text="", font=("Arial", 14))
clock.pack(side="right", padx=20)

def tick():
    time_string = time.strftime('🕐 %H:%M:%S')
    clock.configure(text=time_string)
    clock.after(200, tick)

tick()

# Voice Assistant Frame
voice_frame = ctk.CTkFrame(window, height=90)
voice_frame.pack(fill="x", padx=20, pady=5)
voice_frame.pack_propagate(False)

voice_title = ctk.CTkLabel(voice_frame, text="🎤 Voice Assistant", font=("Arial Bold", 16))
voice_title.pack(pady=5)

voice_button_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
voice_button_frame.pack()

voice_button = ctk.CTkButton(
    voice_button_frame, 
    text="🎤 Start Listening",
    command=start_voice_command,
    width=180,
    height=35,
    font=("Arial Bold", 13),
    fg_color="#FF6B6B",
    hover_color="#FF5252"
)
voice_button.pack(side="left", padx=10)

voice_status = ctk.CTkLabel(voice_button_frame, text="Ready to listen", font=("Arial", 12))
voice_status.pack(side="left", padx=15)

voice_response = ctk.CTkLabel(voice_frame, text="Say: 'hello', 'time', 'weather', or 'date'", 
                              font=("Arial", 11), text_color="gray")
voice_response.pack(pady=2)

# Main Content Frame
content_frame = ctk.CTkFrame(window, fg_color="transparent")
content_frame.pack(fill="both", expand=True, padx=20, pady=5)

# Left Panel - Attendance
left_frame = ctk.CTkFrame(content_frame, width=700)
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

left_header = ctk.CTkLabel(left_frame, text="📸 Attendance System", font=("Arial Bold", 22))
left_header.pack(pady=10)

attendance_btn = ctk.CTkButton(
    left_frame,
    text="▶ Take Attendance",
    command=TrackImages,
    width=280,
    height=45,
    font=("Arial Bold", 16),
    fg_color="#4CAF50",
    hover_color="#45a049"
)
attendance_btn.pack(pady=8)

# Treeview for attendance
tree_frame = ctk.CTkFrame(left_frame)
tree_frame.pack(fill="both", expand=True, padx=15, pady=8)

# Create a style for the treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#2b2b2b", foreground="white", 
                fieldbackground="#2b2b2b", font=('Arial', 11))
style.configure("Treeview.Heading", background="#1f6aa5", foreground="white", 
                font=('Arial Bold', 12))
style.map('Treeview', background=[('selected', '#1f6aa5')])

tv = ttk.Treeview(tree_frame, height=14, columns=('ID', 'Name', 'Date', 'Time'), show='headings')
tv.column('ID', width=140)
tv.column('Name', width=220)
tv.column('Date', width=130)
tv.column('Time', width=110)
tv.heading('ID', text='ID')
tv.heading('Name', text='NAME')
tv.heading('Date', text='DATE')
tv.heading('Time', text='TIME')
tv.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tv.yview)
scrollbar.pack(side="right", fill="y")
tv.configure(yscrollcommand=scrollbar.set)

quit_btn = ctk.CTkButton(
    left_frame,
    text="❌ Exit Application",
    command=window.destroy,
    width=280,
    height=38,
    font=("Arial Bold", 13),
    fg_color="#f44336",
    hover_color="#da190b"
)
quit_btn.pack(pady=10)

# Right Panel - Admin Access & Info
right_frame = ctk.CTkFrame(content_frame, width=700)
right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

right_header = ctk.CTkLabel(right_frame, text="🔐 Admin Panel", font=("Arial Bold", 22))
right_header.pack(pady=10)

# Admin Panel Info
info_frame = ctk.CTkFrame(right_frame, fg_color="#2b2b2b")
info_frame.pack(fill="both", expand=True, padx=20, pady=10)

ctk.CTkLabel(
    info_frame,
    text="🔐 Administrator Functions",
    font=("Arial Bold", 18),
    text_color="#FF9800"
).pack(pady=15)

ctk.CTkLabel(
    info_frame,
    text="For faculty registration and\nuser management, please use\nthe Admin Panel.",
    font=("Arial", 14),
    justify="center"
).pack(pady=10)

# Open Admin Panel Button
def open_admin_panel():
    """Launch admin panel in new process"""
    import subprocess
    admin_path = os.path.join(os.path.dirname(__file__), "admin_panel.py")
    subprocess.Popen(["python3", admin_path])

admin_btn = ctk.CTkButton(
    info_frame,
    text="🚀 Open Admin Panel",
    command=open_admin_panel,
    width=280,
    height=55,
    font=("Arial Bold", 16),
    fg_color="#FF6B6B",
    hover_color="#FF5252"
)
admin_btn.pack(pady=15)

# System Info
info_text_frame = ctk.CTkFrame(info_frame, fg_color="#1f1f1f")
info_text_frame.pack(fill="x", padx=15, pady=15)

ctk.CTkLabel(
    info_text_frame,
    text="Admin Panel Features:",
    font=("Arial Bold", 14),
    anchor="w"
).pack(pady=8, padx=15, anchor="w")

features = [
    "✓ Add new faculty",
    "✓ View all registrations",
    "✓ Delete faculty",
    "✓ View attendance records",
    "✓ Export data",
    "✓ Change admin password"
]

for feature in features:
    ctk.CTkLabel(
        info_text_frame,
        text=feature,
        font=("Arial", 12),
        anchor="w"
    ).pack(pady=2, padx=25, anchor="w")

# Faculty count
message = ctk.CTkLabel(right_frame, text="", font=("Arial Bold", 13), text_color="#4CAF50")
message.pack(pady=10)

# Update registration count
update_registration_count()

# Menu Bar
menubar = ctk.CTkFrame(window, height=40, corner_radius=0, fg_color="#1f1f1f")
menubar.pack(side="bottom", fill="x")

help_btn = ctk.CTkButton(menubar, text="🔧 Change Password", command=change_pass, 
                         width=140, height=32, font=("Arial", 11))
help_btn.pack(side="left", padx=10, pady=4)

contact_btn = ctk.CTkButton(menubar, text="📧 Contact Us", command=contact,
                            width=110, height=32, font=("Arial", 11))
contact_btn.pack(side="left", padx=5, pady=4)

def test_voice():
    """Test voice output"""
    print("🔊 Testing voice...")
    voice_assistant.speak("Testing voice. If you can hear this, the audio is working.")

voice_help_btn = ctk.CTkButton(menubar, text="🎤 Voice Help", 
                               command=lambda: voice_assistant.speak("You can ask me about time, weather, date, or say hello. Click the microphone button to start listening."),
                               width=110, height=32, font=("Arial", 11))
voice_help_btn.pack(side="left", padx=5, pady=4)

test_voice_btn = ctk.CTkButton(menubar, text="🔊 Test Voice", 
                               command=test_voice,
                               width=110, height=32, font=("Arial", 11), fg_color="#FF9800")
test_voice_btn.pack(side="left", padx=5, pady=4)

# Initial voice greeting
window.after(1000, lambda: voice_assistant.speak("Welcome to the Great A Attendance System. I'm ready to help you!"))

window.mainloop()

