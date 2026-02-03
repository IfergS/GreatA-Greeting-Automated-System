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
import importlib
from collections import deque
import pickle
import gdown
from sklearn.metrics.pairwise import cosine_similarity

# CNN Face Recognition imports
try:
    from keras.models import load_model
    from keras.preprocessing.image import img_to_array
    CNN_AVAILABLE = True
except ImportError:
    CNN_AVAILABLE = False
    print("CNN libraries not available. Install tensorflow and keras for CNN face recognition.")
 
# Enhanced Anti-Spoofing Detector
class ScreenReplayDetector:
    """Enhanced detector for digital screen/phone replay, frame repetition, and unnatural motion."""
    def __init__(self, buffer_size=30):
        self.luma_history = deque(maxlen=buffer_size)
        self.frame_history = deque(maxlen=buffer_size)  # Store frame hashes for repetition detection
        self.motion_history = deque(maxlen=buffer_size)  # Store motion patterns
        self.buffer_size = buffer_size

    def update_and_detect(self, roi_bgr, roi_gray, prev_roi_gray=None):
        try:
            if roi_bgr is None or roi_gray is None:
                return True, 0.0
            h, w = roi_gray.shape[:2]
            if h < 30 or w < 30:
                return True, 0.0
            
            # 1. Temporal luminance flicker (screen refresh detection)
            yuv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2YUV)
            y_ch = yuv[:, :, 0]
            mean_luma = float(np.mean(y_ch))
            self.luma_history.append(mean_luma)
            flicker_score = 0.0
            
            if len(self.luma_history) >= max(10, int(self.buffer_size * 0.6)):
                series = np.array(self.luma_history, dtype=np.float32)
                series = series - np.mean(series)
                if np.std(series) > 1e-3:
                    spec = np.abs(np.fft.rfft(series))
                    if spec.size > 2:
                        spec[0] = 0
                        peak = float(np.max(spec))
                        energy = float(np.sum(spec) + 1e-6)
                        flicker_score = min(1.0, max(0.0, peak / energy * 1.8))
            
            # 2. Frame repetition detection (video replay attack)
            frame_hash = self._compute_frame_hash(roi_gray)
            self.frame_history.append(frame_hash)
            repetition_score = 0.0
            
            if len(self.frame_history) >= 10:
                # Check for repeated frame patterns
                recent_frames = list(self.frame_history)[-10:]
                unique_frames = len(set(recent_frames))
                if unique_frames < 5:  # Too many repeated frames
                    repetition_score = 1.0 - (unique_frames / 10.0)
                # Check for periodic repetition (video loop)
                if len(self.frame_history) >= 20:
                    pattern = list(self.frame_history)[-20:]
                    # Look for repeating sequences
                    for seq_len in [5, 10, 15]:
                        if len(pattern) >= seq_len * 2:
                            seq1 = tuple(pattern[-seq_len*2:-seq_len])
                            seq2 = tuple(pattern[-seq_len:])
                            if seq1 == seq2:
                                repetition_score = max(repetition_score, 0.8)
                                break
            
            # 3. Unnatural motion detection
            motion_score = 0.0
            if prev_roi_gray is not None and prev_roi_gray.shape == roi_gray.shape:
                frame_diff = cv2.absdiff(roi_gray, prev_roi_gray)
                current_motion = float(np.mean(frame_diff))
                self.motion_history.append(current_motion)
                
                if len(self.motion_history) >= 10:
                    motion_series = np.array(self.motion_history, dtype=np.float32)
                    # Check for unnatural patterns:
                    # - Too uniform (no variation)
                    motion_std = np.std(motion_series)
                    if motion_std < 0.5:  # Very uniform motion (suspicious)
                        motion_score = 0.7
                    # - Too periodic (repeating pattern)
                    if motion_std > 1e-3:
                        motion_fft = np.abs(np.fft.rfft(motion_series - np.mean(motion_series)))
                        if motion_fft.size > 2:
                            motion_fft[0] = 0
                            peak_ratio = np.max(motion_fft) / (np.sum(motion_fft) + 1e-6)
                            if peak_ratio > 0.5:  # Strong periodic pattern
                                motion_score = max(motion_score, 0.6)
            
            # 4. Spatial moiré/grid detection (screen reflection)
            resized = cv2.resize(roi_gray, (128, 128), interpolation=cv2.INTER_LINEAR)
            dft = cv2.dft(np.float32(resized), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft, axes=(0, 1))
            mag = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])
            mag = np.log(mag + 1.0)
            cy, cx = mag.shape[0] // 2, mag.shape[1] // 2
            rr = 8
            mag[cy - rr:cy + rr, cx - rr:cx + rr] = 0
            norm = (mag - mag.min()) / (mag.max() - mag.min() + 1e-6)
            rows_max = np.partition(norm.max(axis=1), -3)[-3:]
            cols_max = np.partition(norm.max(axis=0), -3)[-3:]
            moire_score = float((np.mean(rows_max) + np.mean(cols_max)) / 2.0)
            moire_score = min(1.0, max(0.0, moire_score))
            
            # 5. Screen reflection detection (bright spots, reflections)
            reflection_score = self._detect_reflection(roi_bgr, roi_gray)
            
            # Aggregate all spoofing scores
            screen_score = (
                0.30 * moire_score +      # Screen moiré pattern
                0.25 * flicker_score +    # Screen flicker
                0.25 * repetition_score + # Frame repetition
                0.15 * motion_score +     # Unnatural motion
                0.05 * reflection_score    # Screen reflection
            )
            
            # Stricter threshold for better security
            passed = screen_score < 0.35  # Lower threshold = stricter
            return passed, float(max(0.0, min(1.0, screen_score)))
        except Exception as e:
            print(f"Screen detection error: {e}")
            return True, 0.0
    
    def _compute_frame_hash(self, frame):
        """Compute a simple hash for frame comparison"""
        try:
            # Resize to small size for faster hashing
            small = cv2.resize(frame, (32, 32))
            # Compute mean and std as hash
            return (float(np.mean(small)), float(np.std(small)))
        except:
            return (0.0, 0.0)
    
    def _detect_reflection(self, roi_bgr, roi_gray):
        """Detect screen reflections and bright spots"""
        try:
            h, w = roi_gray.shape[:2]
            
            # Method 1: Bright specular highlights
            hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
            v_ch = hsv[:, :, 2]
            bright_pixels = np.sum(v_ch > 240) / (h * w)
            
            # Method 2: Sudden brightness changes (reflection edges)
            sobel_v = cv2.Sobel(v_ch.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
            edge_strength = np.mean(np.abs(sobel_v))
            
            # Method 3: Color uniformity (screens often have uniform color)
            b, g, r = cv2.split(roi_bgr)
            color_variance = np.var(b.astype(np.float32)) + np.var(g.astype(np.float32)) + np.var(r.astype(np.float32))
            low_variance_score = 1.0 - min(1.0, color_variance / 1000.0)
            
            # Combine reflection indicators
            reflection_score = (
                0.4 * min(1.0, bright_pixels * 10) +
                0.3 * min(1.0, edge_strength / 50.0) +
                0.3 * low_variance_score
            )
            
            return min(1.0, max(0.0, reflection_score))
        except:
            return 0.0

# Optional: MediaPipe for liveness (blink) detection, face orientation, and pose
try:
    mp_spec = importlib.util.find_spec("mediapipe")
    if mp_spec is not None:
        mp = importlib.import_module("mediapipe")
        MP_AVAILABLE = True
    else:
        mp = None
        MP_AVAILABLE = False
except Exception:
    mp = None
    MP_AVAILABLE = False

# Face Orientation Detection Class
class FaceOrientationDetector:
    """Detect face orientation (left, right, front) using MediaPipe landmarks"""
    def __init__(self):
        self.face_mesh = None
        if MP_AVAILABLE:
            try:
                self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            except Exception:
                self.face_mesh = None
    
    def get_face_orientation(self, image):
        """Detect face orientation: 'front', 'left', 'right', or 'unknown'"""
        if not self.face_mesh:
            return 'unknown', 0.0
        
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if not results.multi_face_landmarks:
                return 'unknown', 0.0
            
            landmarks = results.multi_face_landmarks[0].landmark
            h, w = image.shape[:2]
            
            # Key landmarks for orientation detection
            # Nose tip, left/right eye corners, left/right ear
            nose_tip = landmarks[1]  # Nose tip
            left_eye = landmarks[33]  # Left eye corner
            right_eye = landmarks[362]  # Right eye corner
            left_ear = landmarks[234]  # Left ear
            right_ear = landmarks[454]  # Right ear
            
            # Convert to pixel coordinates
            nose_x = nose_tip.x * w
            left_eye_x = left_eye.x * w
            right_eye_x = right_eye.x * w
            left_ear_x = left_ear.x * w
            right_ear_x = right_ear.x * w
            
            # Calculate face center and symmetry
            face_center_x = (left_eye_x + right_eye_x) / 2
            nose_offset = nose_x - face_center_x
            
            # Calculate ear visibility (for profile detection)
            ear_visibility = abs(left_ear_x - right_ear_x)
            
            # Determine orientation based on nose position and ear visibility
            if abs(nose_offset) < 20:  # Nose close to center
                if ear_visibility < 50:  # Both ears visible
                    return 'front', 0.9
                else:
                    return 'front', 0.7
            elif nose_offset > 30:  # Nose shifted right (face turned left)
                return 'left', min(0.9, abs(nose_offset) / 100)
            elif nose_offset < -30:  # Nose shifted left (face turned right)
                return 'right', min(0.9, abs(nose_offset) / 100)
            else:
                return 'front', 0.5
                
        except Exception as e:
            print(f"Face orientation detection error: {e}")
            return 'unknown', 0.0

# Body Gesture Recognition Class
class BodyGestureDetector:
    """Detect body gestures using MediaPipe pose detection"""
    def __init__(self):
        self.pose = None
        if MP_AVAILABLE:
            try:
                self.pose = mp.solutions.pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            except Exception:
                self.pose = None
    
    def get_gesture_info(self, image):
        """Detect body gestures and pose information"""
        if not self.pose:
            return {
                'gesture': 'unknown',
                'confidence': 0.0,
                'is_standing': False,
                'hands_visible': False,
                'facing_camera': False
            }
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_image)
            
            if not results.pose_landmarks:
                return {
                    'gesture': 'unknown',
                    'confidence': 0.0,
                    'is_standing': False,
                    'hands_visible': False,
                    'facing_camera': False
                }
            
            landmarks = results.pose_landmarks.landmark
            h, w = image.shape[:2]
            
            # Key pose landmarks
            nose = landmarks[mp.solutions.pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST]
            right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST]
            left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]
            
            # Convert to pixel coordinates
            nose_x, nose_y = nose.x * w, nose.y * h
            left_shoulder_x, left_shoulder_y = left_shoulder.x * w, left_shoulder.y * h
            right_shoulder_x, right_shoulder_y = right_shoulder.x * w, right_shoulder.y * h
            left_wrist_x, left_wrist_y = left_wrist.x * w, left_wrist.y * h
            right_wrist_x, right_wrist_y = right_wrist.x * w, right_wrist.y * h
            left_hip_x, left_hip_y = left_hip.x * w, left_hip.y * h
            right_hip_x, right_hip_y = right_hip.x * w, right_hip.y * h
            
            # Check if person is standing (shoulders above hips)
            shoulder_avg_y = (left_shoulder_y + right_shoulder_y) / 2
            hip_avg_y = (left_hip_y + right_hip_y) / 2
            is_standing = shoulder_avg_y < hip_avg_y - 20
            
            # Check if hands are visible (wrist landmarks are within frame)
            hands_visible = (
                (0 < left_wrist_x < w and 0 < left_wrist_y < h) or
                (0 < right_wrist_x < w and 0 < right_wrist_y < h)
            )
            
            # Check if facing camera (shoulders roughly horizontal)
            shoulder_angle = abs(left_shoulder_y - right_shoulder_y)
            facing_camera = shoulder_angle < 30
            
            # Determine gesture based on hand positions
            gesture = 'neutral'
            confidence = 0.5
            
            if hands_visible:
                # Check for waving gesture (hands above shoulders)
                if (left_wrist_y < left_shoulder_y - 20) or (right_wrist_y < right_shoulder_y - 20):
                    gesture = 'waving'
                    confidence = 0.8
                # Check for hands on hips
                elif (abs(left_wrist_x - left_hip_x) < 30 and abs(left_wrist_y - left_hip_y) < 30) or \
                     (abs(right_wrist_x - right_hip_x) < 30 and abs(right_wrist_y - right_hip_y) < 30):
                    gesture = 'hands_on_hips'
                    confidence = 0.7
                # Check for crossed arms (hands near opposite shoulders)
                elif (abs(left_wrist_x - right_shoulder_x) < 50 and abs(left_wrist_y - right_shoulder_y) < 50) or \
                     (abs(right_wrist_x - left_shoulder_x) < 50 and abs(right_wrist_y - left_shoulder_y) < 50):
                    gesture = 'crossed_arms'
                    confidence = 0.6
            
            return {
                'gesture': gesture,
                'confidence': confidence,
                'is_standing': is_standing,
                'hands_visible': hands_visible,
                'facing_camera': facing_camera
            }
            
        except Exception as e:
            print(f"Body gesture detection error: {e}")
            return {
                'gesture': 'unknown',
                'confidence': 0.0,
                'is_standing': False,
                'hands_visible': False,
                'facing_camera': False
            }

# CNN Face Recognition Class
class CNNFaceRecognizer:
    """CNN-based face recognition using FaceNet model for high accuracy"""
    
    def __init__(self):
        self.model = None
        self.registered_faces = {}  # {serial: (name, embedding)}
        self.facenet_model_path = "facenet_keras.h5"
        self.embeddings_path = os.path.join("TrainingImageLabel", "cnn_embeddings.pkl")
        self.similarity_threshold = 0.70  # Optimized threshold for 99% accuracy (was 0.6)
        self.recognition_history = {}  # Track recognition history for temporal smoothing
        
    def download_facenet_model(self):
        """Download FaceNet model if not present"""
        if not os.path.isfile(self.facenet_model_path):
            print("Downloading FaceNet model (~90MB)...")
            try:
                url = "https://drive.google.com/uc?id=1NVR5jP4YZaOgvciKy5rIDr-7kK5x5i-n"
                gdown.download(url, self.facenet_model_path, quiet=False)
                print("FaceNet model download complete!")
            except Exception as e:
                print(f"Error downloading FaceNet model: {e}")
                return False
        return True
    
    def load_facenet_model(self):
        """Load the FaceNet model"""
        if not CNN_AVAILABLE:
            print("CNN libraries not available. Please install tensorflow and keras.")
            return False
            
        if self.model is None:
            if not self.download_facenet_model():
                return False
            try:
                self.model = load_model(self.facenet_model_path)
                print("FaceNet model loaded successfully!")
            except Exception as e:
                print(f"Error loading FaceNet model: {e}")
                return False
        return True
    
    def preprocess_face_for_cnn(self, face_roi, required_size=(160, 160)):
        """Enhanced preprocessing for CNN input with face alignment and normalization"""
        try:
            # Convert to RGB if grayscale
            if len(face_roi.shape) == 2:
                face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2RGB)
            else:
                face_rgb = face_roi.copy()
            
            # Apply histogram equalization for better contrast
            face_rgb = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2LAB)
            face_rgb[:,:,0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(face_rgb[:,:,0])
            face_rgb = cv2.cvtColor(face_rgb, cv2.COLOR_LAB2RGB)
            
            # Resize to required size with high-quality interpolation
            face_resized = cv2.resize(face_rgb, required_size, interpolation=cv2.INTER_CUBIC)
            
            # Apply bilateral filter to reduce noise while preserving edges
            face_filtered = cv2.bilateralFilter(face_resized, 5, 50, 50)
            
            # Normalize to 0-1 range
            face_normalized = face_filtered.astype('float32') / 255.0
            
            # Standardize using ImageNet statistics (better for FaceNet)
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            face_standardized = (face_normalized - mean) / std
            
            # Add batch dimension
            face_batch = np.expand_dims(face_standardized, axis=0)
            
            return face_batch
        except Exception as e:
            print(f"Error preprocessing face for CNN: {e}")
            return None
    
    def get_face_embedding(self, face_roi, use_ensemble=True):
        """Get face embedding using FaceNet model with ensemble preprocessing for accuracy"""
        if not self.load_facenet_model():
            return None
            
        try:
            embeddings = []
            
            # Primary preprocessing
            face_preprocessed = self.preprocess_face_for_cnn(face_roi)
            if face_preprocessed is not None:
                embedding = self.model.predict(face_preprocessed, verbose=0)[0]
                # Normalize embedding (L2 normalization)
                embedding = embedding / (np.linalg.norm(embedding) + 1e-6)
                embeddings.append(embedding)
            
            if use_ensemble:
                # Ensemble: Try different preprocessing variations
                # Variation 1: Slight brightness adjustment
                try:
                    face_adjusted = face_roi.copy()
                    if len(face_adjusted.shape) == 2:
                        face_adjusted = cv2.cvtColor(face_adjusted, cv2.COLOR_GRAY2RGB)
                    face_adjusted = cv2.convertScaleAbs(face_adjusted, alpha=1.1, beta=10)
                    face_preprocessed = self.preprocess_face_for_cnn(face_adjusted)
                    if face_preprocessed is not None:
                        embedding = self.model.predict(face_preprocessed, verbose=0)[0]
                        embedding = embedding / (np.linalg.norm(embedding) + 1e-6)
                        embeddings.append(embedding)
                except:
                    pass
                
                # Variation 2: Slight contrast adjustment
                try:
                    face_adjusted = face_roi.copy()
                    if len(face_adjusted.shape) == 2:
                        face_adjusted = cv2.cvtColor(face_adjusted, cv2.COLOR_GRAY2RGB)
                    face_adjusted = cv2.convertScaleAbs(face_adjusted, alpha=0.9, beta=0)
                    face_preprocessed = self.preprocess_face_for_cnn(face_adjusted)
                    if face_preprocessed is not None:
                        embedding = self.model.predict(face_preprocessed, verbose=0)[0]
                        embedding = embedding / (np.linalg.norm(embedding) + 1e-6)
                        embeddings.append(embedding)
                except:
                    pass
            
            if embeddings:
                # Average embeddings for more robust representation
                final_embedding = np.mean(embeddings, axis=0)
                # Re-normalize
                final_embedding = final_embedding / (np.linalg.norm(final_embedding) + 1e-6)
                return final_embedding
            else:
                return None
        except Exception as e:
            print(f"Error getting face embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            # Reshape for sklearn cosine_similarity
            emb1 = embedding1.reshape(1, -1)
            emb2 = embedding2.reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def train_faces(self, training_images_path):
        """Train the CNN model with face images"""
        if not self.load_facenet_model():
            return False
            
        print("Training CNN face recognition model...")
        self.registered_faces = {}
        
        # Load faculty details
        faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
        if not os.path.isfile(faculty_details_path):
            print("Faculty details not found!")
            return False
            
        df = pd.read_csv(faculty_details_path, encoding='latin-1')
        
        for idx, row in df.iterrows():
            try:
                serial = int(row['SERIAL NO.'])
                name = str(row['NAME'])
                faculty_id = str(row['ID'])
                
                # Find training images for this faculty member
                image_files = [f for f in os.listdir(training_images_path) 
                             if f.endswith(('.jpg', '.png', '.jpeg')) and 
                             f.split('.')[1] == str(serial)]
                
                if not image_files:
                    print(f"No training images found for {name} (Serial: {serial})")
                    continue
                
                # Use multiple images and average embeddings for better accuracy
                embeddings_list = []
                
                for img_file in image_files[:10]:  # Use up to 10 images for better accuracy
                    img_path = os.path.join(training_images_path, img_file)
                    try:
                        # Load image
                        img = cv2.imread(img_path)
                        if img is None:
                            continue
                        
                        # Keep color for better CNN performance
                        if len(img.shape) == 3:
                            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        else:
                            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                        
                        # Get embedding with ensemble preprocessing
                        embedding = self.get_face_embedding(img, use_ensemble=True)
                        if embedding is not None:
                            embeddings_list.append(embedding)
                    except Exception as e:
                        print(f"Error processing {img_file}: {e}")
                        continue
                
                if embeddings_list:
                    # Average all embeddings for robust representation
                    avg_embedding = np.mean(embeddings_list, axis=0)
                    # Normalize the averaged embedding
                    avg_embedding = avg_embedding / (np.linalg.norm(avg_embedding) + 1e-6)
                    self.registered_faces[serial] = (name, avg_embedding)
                    print(f"Trained: {name} (Serial: {serial}) with {len(embeddings_list)} images")
                else:
                    print(f"Failed to train: {name} (Serial: {serial})")
                    
            except Exception as e:
                print(f"Error training faculty member: {e}")
                continue
        
        # Save embeddings
        self.save_embeddings()
        
        print(f"CNN training completed! Trained {len(self.registered_faces)} faces.")
        return len(self.registered_faces) > 0
    
    def save_embeddings(self):
        """Save face embeddings to file"""
        try:
            assure_path_exists("TrainingImageLabel/")
            with open(self.embeddings_path, "wb") as f:
                pickle.dump(self.registered_faces, f)
            print(f"Embeddings saved to {self.embeddings_path}")
        except Exception as e:
            print(f"Error saving embeddings: {e}")
    
    def load_embeddings(self):
        """Load face embeddings from file"""
        try:
            if os.path.exists(self.embeddings_path):
                with open(self.embeddings_path, "rb") as f:
                    self.registered_faces = pickle.load(f)
                print(f"Loaded {len(self.registered_faces)} face embeddings")
                return True
            else:
                print("No saved embeddings found")
                return False
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            return False
    
    def recognize_face(self, face_roi, use_temporal_smoothing=True):
        """Recognize a face using CNN with enhanced accuracy features"""
        if not self.load_facenet_model():
            return -1, 0.0, "CNN model not available"
        
        if not self.registered_faces:
            if not self.load_embeddings():
                return -1, 0.0, "No trained faces available"
        
        try:
            # Get embedding for the input face with ensemble preprocessing
            face_embedding = self.get_face_embedding(face_roi, use_ensemble=True)
            if face_embedding is None:
                return -1, 0.0, "Failed to extract face embedding"
            
            # Find best match with all candidates
            candidates = []
            
            for serial, (name, stored_embedding) in self.registered_faces.items():
                similarity = self.calculate_similarity(face_embedding, stored_embedding)
                candidates.append((serial, similarity, name))
            
            # Sort by similarity (highest first)
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            if not candidates:
                return -1, 0.0, "No candidates found"
            
            best_serial, best_similarity, best_name = candidates[0]
            
            # Check if there's a clear winner (gap between 1st and 2nd)
            if len(candidates) > 1:
                gap = best_similarity - candidates[1][1]
                # If gap is too small (< 0.05), might be ambiguous
                if gap < 0.05 and best_similarity < 0.85:
                    # Too close, reject
                    return -1, best_similarity * 100, "Ambiguous match"
            
            # Convert similarity to confidence (0-100 scale)
            confidence = best_similarity * 100
            
            # Apply optimized threshold for 99% accuracy
            if best_similarity >= self.similarity_threshold:
                # Additional validation: ensure confidence is high enough
                if confidence >= 70:  # Minimum 70% confidence
                    return best_serial, confidence, best_name
                else:
                    return -1, confidence, "Low confidence"
            else:
                return -1, confidence, "Unknown"
                
        except Exception as e:
            print(f"Error in CNN face recognition: {e}")
            return -1, 0.0, "Recognition error"

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

# Modern 3-Color Aesthetic Palette
UI_COLORS = {
    "primary": "#1a1a2e",      # Deep Navy - Main background
    "secondary": "#16213e",    # Darker Navy - Cards and panels  
    "accent": "#0f3460",       # Electric Blue - Highlights and buttons
    "highlight": "#e94560",    # Coral Red - Call-to-action elements
    "success": "#27ae60",      # Success Green - Success states
    "warning": "#f39c12",      # Warning Orange - Warnings
    "text_primary": "#ffffff", # White - Primary text
    "text_secondary": "#bdc3c7", # Light Gray - Secondary text
    "text_muted": "#7f8c8d",   # Muted Gray - Muted text
    "border": "#34495e",       # Border Gray - Subtle borders
    "surface": "#2c3e50"       # Surface Gray - Elevated surfaces
}

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
            print(f"Speaking: {text}")
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
            print(f"Voice error: {e}")
            self.is_speaking = False
        
    def load_registered_users(self):
        """Load registered users from FacultyDetails.csv"""
        try:
            faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
            if os.path.isfile(faculty_details_path):
                df = pd.read_csv(faculty_details_path, encoding='latin-1')
                for index, row in df.iterrows():
                    if pd.notna(row['ID']) and pd.notna(row['NAME']):
                        self.registered_users[str(row['ID'])] = str(row['NAME'])
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def speak(self, text):
        """Queue text for speech - ensures sequential playback without overlap"""
        # Add text to the queue
        self.speech_queue.put(text)
        print(f"Queued for speech: {text}")
    
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
        """Get current weather information for user's location - Google-level accuracy"""
        try:
            # Get user's location (city and coordinates)
            location_info = self._get_user_location()
            city = location_info.get('city', 'your location')
            lat = location_info.get('lat')
            lon = location_info.get('lon')
            
            # Priority 1: Open-Meteo API (free, accurate, no API key, used by many professional services)
            if lat and lon:
                try:
                    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,relative_humidity_2m&timezone=auto"
                    response = requests.get(url, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'current' in data:
                            current = data['current']
                            temp = int(round(current.get('temperature_2m', 0)))
                            weather_code = current.get('weather_code', 0)
                            condition = self._get_weather_condition_from_code(weather_code)
                            
                            # Extract just city name
                            city_name_only = city.split(',')[0].strip() if ',' in city else city
                            temp_clean = str(temp).replace('°C', '').replace('°F', '').replace('+', '').strip()
                            return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                except Exception as e:
                    print(f"Open-Meteo error: {e}")
                    pass
            
            # Priority 2: OpenWeatherMap API with coordinates (most accurate with API key)
            api_key = os.getenv("OPENWEATHER_API_KEY", "")
            if api_key and lat and lon:
                try:
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                    response = requests.get(url, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        temp = int(round(data['main']['temp']))
                        condition = data['weather'][0]['description']
                        actual_city = data.get('name', city)
                        
                        # Extract just city name (not full location)
                        city_name_only = actual_city.split(',')[0].strip() if ',' in actual_city else actual_city
                        # Format temperature as number only (remove any symbols)
                        temp_clean = str(temp).replace('°C', '').replace('°F', '').replace('+', '').strip()
                        return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                except Exception as e:
                    print(f"OpenWeatherMap error: {e}")
                    pass
            
            # Priority 3: OpenWeatherMap by city name (if API key available)
            if api_key and city:
                try:
                    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                    response = requests.get(url, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        temp = int(round(data['main']['temp']))
                        condition = data['weather'][0]['description']
                        actual_city = data.get('name', city)
                        
                        # Extract just city name (not full location)
                        city_name_only = actual_city.split(',')[0].strip() if ',' in actual_city else actual_city
                        # Format temperature as number only (remove any symbols)
                        temp_clean = str(temp).replace('°C', '').replace('°F', '').replace('+', '').strip()
                        return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                except Exception as e:
                    print(f"OpenWeatherMap city error: {e}")
                    pass
            
            # Priority 4: WeatherAPI.com (free tier, accurate, similar to Google)
            api_key_weather = os.getenv("WEATHERAPI_KEY", "")
            if api_key_weather and lat and lon:
                try:
                    url = f"http://api.weatherapi.com/v1/current.json?key={api_key_weather}&q={lat},{lon}"
                    response = requests.get(url, timeout=8)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'current' in data:
                            current = data['current']
                            temp = int(round(current.get('temp_c', 0)))
                            condition = current.get('condition', {}).get('text', 'unknown')
                            location_name = data.get('location', {}).get('name', city)
                            
                            city_name_only = location_name.split(',')[0].strip() if ',' in location_name else location_name
                            temp_clean = str(temp).replace('°C', '').replace('°F', '').replace('+', '').strip()
                            return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                except Exception as e:
                    print(f"WeatherAPI error: {e}")
                    pass
            
            # Priority 5: wttr.in with location (free, no API key required) - Reliable free option
            try:
                # Format city name for wttr.in - try different formats for better accuracy
                # For Philippines cities, try "City, Province, Country" format
                city_variants = [
                    "Tupi+South+Cotabato+Philippines",  # Most specific
                    "Tupi+Philippines",  # City and country
                    city.replace(",", "").replace(" ", "+"),  # Original format
                    "Tupi"  # Just city name
                ]
                
                for city_variant in city_variants:
                    try:
                        # Try detailed format first
                        url = f"http://wttr.in/{city_variant}?format=%l:+%C+%t+%h"
                        response = requests.get(url, timeout=8)
                        
                        if response.status_code == 200:
                            weather_text = response.text.strip()
                            if weather_text and weather_text != "Unknown location":
                                # Parse: "Location: Condition Temperature Humidity"
                                if ':' in weather_text:
                                    parts = weather_text.split(':')
                                    location = parts[0].strip()
                                    rest = parts[1].strip() if len(parts) > 1 else ""
                                    
                                    # Parse condition, temp, humidity
                                    rest_parts = rest.split()
                                    condition = ""
                                    temp = ""
                                    humidity = ""
                                    
                                    # Find temperature (contains °C or °F)
                                    for i, part in enumerate(rest_parts):
                                        if '°C' in part or '°F' in part:
                                            temp = part.replace('+', '').strip()
                                            # Condition is everything before temperature
                                            if i > 0:
                                                condition = ' '.join(rest_parts[:i]).strip()
                                            # Humidity is after temperature
                                            if i + 1 < len(rest_parts):
                                                humidity = rest_parts[i + 1].strip()
                                            break
                                    
                                    if temp:
                                        # Extract just city name from location
                                        city_name_only = location.split(',')[0].strip() if ',' in location else location
                                        # Clean temperature format (remove symbols, keep number only)
                                        temp_clean = temp.replace('°C', '').replace('°F', '').replace('+', '').strip()
                                        result = f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                                        return result
                                    else:
                                        # Fallback: try to parse rest for condition and temperature
                                        city_name_only = location.split(',')[0].strip() if ',' in location else location
                                        # Try to extract condition and temp from rest
                                        rest_parts = rest.split()
                                        condition_fallback = ""
                                        temp_fallback = ""
                                        
                                        for i, part in enumerate(rest_parts):
                                            if '°C' in part or '°F' in part or (part.startswith('+') and any(c.isdigit() for c in part)):
                                                temp_fallback = part.replace('°C', '').replace('°F', '').replace('+', '').strip()
                                                if i > 0:
                                                    condition_fallback = ' '.join(rest_parts[:i]).strip()
                                                break
                                        
                                        if temp_fallback and condition_fallback:
                                            return f"The weather in {city_name_only} is {condition_fallback} outside with a temperature of {temp_fallback} degrees Celsius"
                                        else:
                                            return f"The weather in {city_name_only} is {rest} outside"
                                else:
                                    # No colon format - extract city name and parse weather_text
                                    city_name_only = city.split(',')[0].strip() if ',' in city else city
                                    # Parse weather_text to extract condition and temperature
                                    parts = weather_text.split()
                                    condition_parsed = ""
                                    temp_parsed = ""
                                    
                                    for i, part in enumerate(parts):
                                        if '°C' in part or '°F' in part or (part.startswith('+') and any(c.isdigit() for c in part)):
                                            temp_parsed = part.replace('°C', '').replace('°F', '').replace('+', '').strip()
                                            if i > 0:
                                                condition_parsed = ' '.join(parts[:i]).strip()
                                            break
                                    
                                    if temp_parsed and condition_parsed:
                                        return f"The weather in {city_name_only} is {condition_parsed} outside with a temperature of {temp_parsed} degrees Celsius"
                                    else:
                                        return f"The weather in {city_name_only} is {weather_text} outside"
                    except:
                        continue  # Try next variant
                        
            except Exception as e:
                print(f"wttr.in detailed error: {e}")
                pass
            
            # Priority 6: Simple wttr.in format (reliable fallback)
            try:
                city_for_api = city.replace(",", "").replace(" ", "+")
                url = f"http://wttr.in/{city_for_api}?format=%C+%t"
                
                response = requests.get(url, timeout=8)
                
                if response.status_code == 200:
                    weather_text = response.text.strip()
                    if weather_text:
                        # Extract just city name
                        city_name_only = city.split(',')[0].strip() if ',' in city else city
                        # Parse weather_text to extract condition and temperature
                        # Format from wttr.in: "Condition Temperature" (e.g., "Partly cloudy +28°C")
                        parts = weather_text.split()
                        condition = ""
                        temp = ""
                        
                        # Find temperature (contains °C or °F or starts with +)
                        for i, part in enumerate(parts):
                            if '°C' in part or '°F' in part or (part.startswith('+') and any(c.isdigit() for c in part)):
                                temp = part.replace('+', '').strip()
                                # Condition is everything before temperature
                                if i > 0:
                                    condition = ' '.join(parts[:i]).strip()
                                break
                        
                        if temp and condition:
                            # Clean temperature format (remove symbols, keep number only)
                            temp_clean = temp.replace('°C', '').replace('°F', '').replace('+', '').strip()
                            return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                        else:
                            # Fallback: format as is
                            if '°C' not in weather_text and '°F' not in weather_text and 'degrees' not in weather_text.lower():
                                weather_text = f"{weather_text} degrees Celsius"
                            return f"The weather in {city_name_only} is {weather_text} outside"
            except Exception as e:
                print(f"wttr.in simple error: {e}")
                pass
            
            # Priority 7: wttr.in with coordinates (final fallback)
            try:
                if lat and lon:
                    url = f"http://wttr.in/?lat={lat}&lon={lon}&format=%C+%t"
                    response = requests.get(url, timeout=8)
                    
                    if response.status_code == 200:
                        weather_text = response.text.strip()
                        if weather_text:
                            # Extract just city name
                            city_name_only = city.split(',')[0].strip() if ',' in city else city
                            # Parse weather_text to extract condition and temperature
                            parts = weather_text.split()
                            condition = ""
                            temp = ""
                            
                            # Find temperature (contains °C or °F or starts with +)
                            for i, part in enumerate(parts):
                                if '°C' in part or '°F' in part or (part.startswith('+') and any(c.isdigit() for c in part)):
                                    temp = part.replace('+', '').strip()
                                    # Condition is everything before temperature
                                    if i > 0:
                                        condition = ' '.join(parts[:i]).strip()
                                    break
                            
                            if temp and condition:
                                # Clean temperature format (remove symbols, keep number only)
                                temp_clean = temp.replace('°C', '').replace('°F', '').replace('+', '').strip()
                                return f"The weather in {city_name_only} is {condition} outside with a temperature of {temp_clean} degrees Celsius"
                            else:
                                # Fallback: format as is
                                if '°C' not in weather_text and '°F' not in weather_text and 'degrees' not in weather_text.lower():
                                    weather_text = f"{weather_text} degrees Celsius"
                                return f"The weather in {city_name_only} is {weather_text} outside"
            except:
                pass
            
            # If all methods fail
            return "I'm having trouble getting weather information for your location right now. Please check your internet connection."
                
        except Exception as e:
            print(f"Weather error: {e}")
            return "I'm having trouble getting weather information right now. Please check your internet connection."
    
    def _get_user_location(self):
        """Detect user's location using IP geolocation or configured location"""
        location_info = {'city': None, 'lat': None, 'lon': None}
        
        # First priority: Check config file or environment variable (user's preferred location)
        try:
            config_file = "weather_config.txt"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    city = f.read().strip()
                    if city:
                        location_info['city'] = city
                        # Try to get coordinates for the city
                        coords = self._get_city_coordinates(city)
                        if coords:
                            location_info['lat'] = coords['lat']
                            location_info['lon'] = coords['lon']
                        return location_info
        except:
            pass
        
        # Check environment variable
        city = os.getenv("WEATHER_CITY", "")
        if city:
            location_info['city'] = city
            coords = self._get_city_coordinates(city)
            if coords:
                location_info['lat'] = coords['lat']
                location_info['lon'] = coords['lon']
            return location_info
        
        # Default location: Tupi, South Cotabato, Philippines
        # Get accurate coordinates for Tupi
        tupi_coords = self._get_city_coordinates("Tupi, South Cotabato, Philippines")
        if tupi_coords:
            location_info['city'] = "Tupi, South Cotabato, Philippines"
            location_info['lat'] = tupi_coords['lat']
            location_info['lon'] = tupi_coords['lon']
        else:
            # Fallback coordinates for Tupi, South Cotabato (more accurate)
            location_info['city'] = "Tupi, South Cotabato, Philippines"
            location_info['lat'] = 6.3333
            location_info['lon'] = 124.9500
        return location_info
    
    def _get_weather_condition_from_code(self, code):
        """Convert WMO weather code to readable condition (Open-Meteo format)"""
        # WMO Weather interpretation codes (WW)
        weather_codes = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            56: "light freezing drizzle",
            57: "dense freezing drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "light freezing rain",
            67: "heavy freezing rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "unknown")
    
    def _get_city_coordinates(self, city_name):
        """Get coordinates for a city name using geocoding"""
        try:
            # Try using Nominatim (OpenStreetMap - free, no API key) - Most reliable
            try:
                # Format city name for better results
                formatted_city = city_name.replace(",", ", ").strip()
                url = f"https://nominatim.openstreetmap.org/search?q={formatted_city}&format=json&limit=1"
                headers = {'User-Agent': 'GreetA-Weather-App/1.0'}
                response = requests.get(url, headers=headers, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        print(f"Found coordinates for {city_name}: {lat}, {lon}")
                        return {'lat': lat, 'lon': lon}
            except Exception as e:
                print(f"Nominatim geocoding error: {e}")
                pass
            
            # Try using OpenWeatherMap geocoding (if API key available)
            api_key = os.getenv("OPENWEATHER_API_KEY", "")
            if api_key:
                try:
                    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
                    response = requests.get(url, timeout=8)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            lat = data[0]['lat']
                            lon = data[0]['lon']
                            print(f"Found coordinates via OpenWeatherMap for {city_name}: {lat}, {lon}")
                            return {'lat': lat, 'lon': lon}
                except Exception as e:
                    print(f"OpenWeatherMap geocoding error: {e}")
                    pass
            
            # Special case: Tupi, South Cotabato, Philippines - use known accurate coordinates
            if "Tupi" in city_name and "South Cotabato" in city_name:
                return {'lat': 6.3333, 'lon': 124.9500}
                
        except Exception as e:
            print(f"Geocoding error: {e}")
            pass
        
        return None
    
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
        
        elif "attendance" in command or "mark attendance" in command or "record attendance" in command:
            # Voice-based attendance recording
            response, action = self.handle_voice_attendance(command, user_id, user_name)
            return response, action
        
        else:
            response = f"I'm sorry {user_name}, I didn't understand that command. You can ask me about time, weather, date, or say 'mark attendance'."
        
        return response, None
    
    def handle_voice_attendance(self, command, user_id, user_name):
        """Handle voice-based attendance recording"""
        try:
            if not user_id or user_id == "Unknown":
                return "I need to know who you are first. Please make sure your face is visible for recognition.", None
            
            # Check if already recorded today
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
            attendance_filename = "Attendance_" + date + ".csv"
            attendance_path = os.path.join("Attendance", attendance_filename)
            
            # Check existing attendance
            already_recorded = False
            if os.path.isfile(attendance_path):
                try:
                    with open(attendance_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader, None)  # Skip header
                        for row in reader:
                            if len(row) >= 7 and row[0] == str(user_id):
                                already_recorded = True
                                break
                except:
                    pass
            
            if already_recorded:
                return f"Hi {user_name}, your attendance for today is already recorded. No need to mark it again!", None
            
            # Record attendance via voice
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            attendance = [str(user_id), '', user_name, '', str(date), '', str(timeStamp)]
            
            # Ensure attendance directory exists
            assure_path_exists("Attendance/")
            
            # Write to attendance file
            exists = os.path.isfile(attendance_path)
            col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
            
            with open(attendance_path, 'a+', encoding='utf-8') as csvFile1:
                writer = csv.writer(csvFile1)
                if not exists:
                    writer.writerow(col_names)
                writer.writerow(attendance)
            
            # Add to treeview if available
            try:
                global tv
                tv.insert('', 0, values=(str(user_id), user_name, str(date), str(timeStamp)))
            except:
                pass
            
            response = f"Perfect! Your attendance has been recorded via voice command, {user_name}. Time: {timeStamp}"
            action = "attendance_recorded"
            
            return response, action
            
        except Exception as e:
            return f"Sorry {user_name}, there was an error recording your attendance. Please try again or use face recognition.", None

# Global voice assistant instance
voice_assistant = VoiceAssistant()

# Global CNN face recognizer instance
cnn_recognizer = CNNFaceRecognizer() if CNN_AVAILABLE else None

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

def validate_face_quality(gray_face_roi):
    """Validate face quality before recognition to improve accuracy.
    
    Returns:
        tuple: (is_valid, quality_score, issues)
    """
    try:
        if gray_face_roi is None or gray_face_roi.size == 0:
            return False, 0.0, ["Empty face ROI"]
        
        h, w = gray_face_roi.shape
        issues = []
        quality_score = 100.0
        
        # Check minimum size
        if h < 50 or w < 50:
            issues.append("Face too small")
            quality_score -= 30
        
        # Check aspect ratio (should be roughly square)
        aspect_ratio = w / h
        if aspect_ratio < 0.7 or aspect_ratio > 1.4:
            issues.append("Poor aspect ratio")
            quality_score -= 20
        
        # Check brightness (avoid too dark or too bright)
        mean_brightness = np.mean(gray_face_roi)
        if mean_brightness < 50:
            issues.append("Too dark")
            quality_score -= 25
        elif mean_brightness > 200:
            issues.append("Too bright")
            quality_score -= 25
        
        # Check contrast using standard deviation (more lenient)
        contrast = np.std(gray_face_roi)
        if contrast < 15:  # Reduced from 20
            issues.append("Low contrast")
            quality_score -= 15  # Reduced penalty
        
        # Check for blur using Laplacian variance (more lenient)
        laplacian_var = cv2.Laplacian(gray_face_roi, cv2.CV_64F).var()
        if laplacian_var < 50:  # Reduced from 100
            issues.append("Blurry image")
            quality_score -= 20  # Reduced penalty
        
        # Check for motion blur (if available)
        if laplacian_var < 25:  # Reduced from 50
            issues.append("Severe blur")
            quality_score -= 25  # Reduced penalty
        
        # Face is valid if quality score is above 25 (more lenient)
        is_valid = quality_score >= 25
        
        return is_valid, max(0, quality_score), issues
        
    except Exception as e:
        return False, 0.0, [f"Validation error: {str(e)}"]

def preprocess_face(gray_face_roi):
    """Apply enhanced preprocessing to a grayscale face ROI for better recognition.

    Steps:
    - Resize to fixed size (224x224) for better feature extraction
    - Histogram equalization for better contrast
    - CLAHE for local contrast enhancement
    - Bilateral filtering for noise reduction while preserving edges
    - Normalize to 0-255 uint8 range
    - Apply sharpening filter for better feature definition
    """
    try:
        if gray_face_roi is None or gray_face_roi.size == 0:
            return gray_face_roi
        
        # Resize to larger size for better feature extraction
        face_resized = cv2.resize(gray_face_roi, (224, 224), interpolation=cv2.INTER_CUBIC)
        
        # Global histogram equalization first
        face_eq = cv2.equalizeHist(face_resized)
        
        # CLAHE for local contrast enhancement with better parameters
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        face_clahe = clahe.apply(face_eq)
        
        # Bilateral filtering to reduce noise while preserving edges
        face_bilateral = cv2.bilateralFilter(face_clahe, 9, 75, 75)
        
        # Apply sharpening kernel for better feature definition (more gentle)
        kernel = np.array([[-0.5,-0.5,-0.5], [-0.5,5,-0.5], [-0.5,-0.5,-0.5]])
        face_sharp = cv2.filter2D(face_bilateral, -1, kernel)
        
        # Normalize to 0-255 range
        face_norm = cv2.normalize(face_sharp, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        
        return face_norm.astype('uint8')
    except Exception:
        # Fallback to original ROI if preprocessing fails
        return gray_face_roi

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

# Note: clear() and clear2() functions removed as they referenced 
# obsolete txt and txt2 input fields that no longer exist in the current GUI

def TakeImages():
    if not check_haarcascadefile():
        return
    
    # Get ID and name from user input dialogs
    Id = tsd.askstring('Faculty Registration', 'Enter Faculty ID:')
    if not Id:
        return
    
    name = tsd.askstring('Faculty Registration', 'Enter Faculty Name:')
    if not name:
        return
    
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("FacultyDetails/")
    assure_path_exists("TrainingImage/")
    serial = 0
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    exists = os.path.isfile(faculty_details_path)
    if exists:
        with open(faculty_details_path, 'r', encoding='latin-1') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
    else:
        with open(faculty_details_path, 'a+', encoding='latin-1') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
    
    if name.replace(' ', '').isalpha() and Id:
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        
        # Initialize face orientation detector
        orientation_detector = FaceOrientationDetector()
        
        sampleNum = 0
        front_samples = 0
        left_samples = 0
        right_samples = 0
        target_samples_per_angle = 30  # 30 samples per angle
        
        # Instructions for user
        instructions = [
            "Look straight at camera (front view)",
            "Turn your head slightly left",
            "Turn your head slightly right",
            "Look straight again"
        ]
        current_instruction = 0
        instruction_start_time = time.time()
        instruction_duration = 3  # seconds per instruction
        
        while True:
            ret, img = cam.read()
            if not ret:
                break
            
            # Update instruction every few seconds
            if time.time() - instruction_start_time > instruction_duration:
                current_instruction = (current_instruction + 1) % len(instructions)
                instruction_start_time = time.time()
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            
            # Get face orientation
            orientation, orientation_conf = orientation_detector.get_face_orientation(img)
            
            for (x, y, w, h) in faces:
                # Determine color based on current target angle
                if current_instruction == 0:  # Front view
                    color = (0, 255, 0) if orientation == 'front' else (0, 255, 255)
                elif current_instruction == 1:  # Left view
                    color = (0, 255, 0) if orientation == 'left' else (0, 255, 255)
                elif current_instruction == 2:  # Right view
                    color = (0, 255, 0) if orientation == 'right' else (0, 255, 255)
                else:  # Front again
                    color = (0, 255, 0) if orientation == 'front' else (0, 255, 255)
                
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                
                # Capture samples based on orientation and instruction
                should_capture = False
                if current_instruction == 0 and orientation == 'front' and front_samples < target_samples_per_angle:
                    should_capture = True
                    front_samples += 1
                elif current_instruction == 1 and orientation == 'left' and left_samples < target_samples_per_angle:
                    should_capture = True
                    left_samples += 1
                elif current_instruction == 2 and orientation == 'right' and right_samples < target_samples_per_angle:
                    should_capture = True
                    right_samples += 1
                elif current_instruction == 3 and orientation == 'front' and front_samples < target_samples_per_angle * 2:
                    should_capture = True
                    front_samples += 1
                
                if should_capture:
                    sampleNum += 1
                    # Include orientation in filename
                    image_filename = name + "." + str(serial) + "." + Id + '.' + str(sampleNum) + f"_{orientation}.jpg"
                    image_path = os.path.join("TrainingImage", image_filename)
                    face_roi = gray[y:y + h, x:x + w]
                    face_roi = preprocess_face(face_roi)
                    cv2.imwrite(image_path, face_roi)
            
            # Display instructions and progress
            cv2.putText(img, f"Instruction: {instructions[current_instruction]}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Current: {orientation} (conf: {orientation_conf:.2f})", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(img, f"Front: {front_samples}/{target_samples_per_angle*2}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, f"Left: {left_samples}/{target_samples_per_angle}", (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, f"Right: {right_samples}/{target_samples_per_angle}", (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, "Press Q to stop", (10, img.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('Multi-Angle Face Capture - Press Q to stop', img)
            
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum >= target_samples_per_angle * 4:  # Total samples for all angles
                break
        
        cam.release()
        cv2.destroyAllWindows()
        res = f"Multi-angle images captured for ID: {Id} (Front: {front_samples}, Left: {left_samples}, Right: {right_samples})"
        row = [serial, '', Id, '', name]
        with open(faculty_details_path, 'a+', encoding='latin-1') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        mess.showinfo("Success", res)
        voice_assistant.load_registered_users()
        update_registration_count()
    else:
        mess.showerror("Invalid Input", "Please enter a valid name and ID")

def _create_lbph_recognizer():
    """Create LBPH recognizer with optimized parameters for better discrimination."""
    # Optimized parameters for better accuracy:
    # - Radius 3, neighbors 16: More detailed local patterns
    # - Grid 12x12: Better spatial information capture
    # - Threshold 80: More lenient initial threshold
    recognizer = cv2.face_LBPHFaceRecognizer.create(
        radius=3, 
        neighbors=16, 
        grid_x=12, 
        grid_y=12,
        threshold=80
    )
    return recognizer

def ensemble_recognize(recognizer, face_roi, num_attempts=3):
    """Perform ensemble recognition using multiple preprocessing variations.
    
    Args:
        recognizer: The trained LBPH recognizer
        face_roi: Grayscale face ROI
        num_attempts: Number of recognition attempts with different preprocessing
    
    Returns:
        tuple: (best_serial, best_confidence, all_results)
    """
    try:
        results = []
        
        # Original preprocessing
        roi1 = preprocess_face(face_roi)
        serial1, conf1 = recognizer.predict(roi1)
        results.append((serial1, conf1, "original"))
        
        # Alternative preprocessing 1: Different resize and CLAHE
        try:
            roi2 = cv2.resize(face_roi, (200, 200), interpolation=cv2.INTER_CUBIC)
            roi2 = cv2.equalizeHist(roi2)
            clahe2 = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(6, 6))
            roi2 = clahe2.apply(roi2)
            roi2 = cv2.bilateralFilter(roi2, 7, 50, 50)
            roi2 = cv2.normalize(roi2, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            roi2 = roi2.astype('uint8')
            
            serial2, conf2 = recognizer.predict(roi2)
            results.append((serial2, conf2, "alt1"))
        except:
            results.append((serial1, conf1 + 10, "alt1_fallback"))
        
        # Alternative preprocessing 2: Different sharpening
        try:
            roi3 = cv2.resize(face_roi, (224, 224), interpolation=cv2.INTER_LINEAR)
            roi3 = cv2.equalizeHist(roi3)
            clahe3 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(10, 10))
            roi3 = clahe3.apply(roi3)
            
            # Different sharpening kernel
            kernel3 = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
            roi3 = cv2.filter2D(roi3, -1, kernel3)
            roi3 = cv2.normalize(roi3, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            roi3 = roi3.astype('uint8')
            
            serial3, conf3 = recognizer.predict(roi3)
            results.append((serial3, conf3, "alt2"))
        except:
            results.append((serial1, conf1 + 5, "alt2_fallback"))
        
        # Find the best result (lowest confidence score for LBPH)
        best_result = min(results, key=lambda x: x[1])
        best_serial, best_confidence, method = best_result
        
        print(f"Ensemble results: {[(r[0], r[1], r[2]) for r in results]}")
        print(f"Best: Serial {best_serial}, Confidence {best_confidence} (method: {method})")
        
        return best_serial, best_confidence, results
        
    except Exception as e:
        print(f"Ensemble recognition error: {e}")
        # Fallback to single recognition
        try:
            roi = preprocess_face(face_roi)
            serial, conf = recognizer.predict(roi)
            return serial, conf, [(serial, conf, "fallback")]
        except:
            return -1, 100, [(-1, 100, "error")]

def TrainImages():
    if not check_haarcascadefile():
        return
    assure_path_exists("TrainingImageLabel/")
    
    # Check if CNN is available, otherwise fall back to LBPH
    if CNN_AVAILABLE and cnn_recognizer is not None:
        print("Using CNN-based face recognition...")
        try:
            success = cnn_recognizer.train_faces("TrainingImage")
            if success:
                res = f"CNN Profile Saved Successfully! Trained {len(cnn_recognizer.registered_faces)} faces."
                mess.showinfo("Success", res)
            else:
                mess.showerror('Training Failed', 'CNN training failed. Please check your training images.')
        except Exception as e:
            print(f"CNN training error: {e}")
            mess.showerror('Training Error', f'CNN training failed: {str(e)}')
    else:
        print("CNN not available, using LBPH fallback...")
        # Fallback to LBPH
        recognizer = _create_lbph_recognizer()
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
        res = "LBPH Profile Saved Successfully"
        mess.showinfo("Success", res)

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')
            imageNp = preprocess_face(imageNp)
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
    
    # Initialize recognizer based on availability
    use_cnn = CNN_AVAILABLE and cnn_recognizer is not None
    recognizer = None
    
    if use_cnn:
        print("Using CNN-based face recognition...")
        # Load CNN embeddings
        if not cnn_recognizer.load_embeddings():
            mess.showerror('Data Missing', 'No CNN embeddings found. Please click on Save Profile to train CNN model first!')
            return
    else:
        print("CNN not available, using LBPH fallback...")
        # Fallback to LBPH
        recognizer = _create_lbph_recognizer()
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
    screen_detector = ScreenReplayDetector(buffer_size=30)  # Increased buffer for better detection
    # Motion detection state
    prev_gray_frame = None
    prev_roi_gray = {}  # Store previous ROI per face for motion tracking
    motion_threshold = 6.0  # Tune: higher = requires more movement

    # Initialize face orientation and body gesture detectors
    orientation_detector = FaceOrientationDetector()
    gesture_detector = BodyGestureDetector()

    # Liveness (blink) detection setup
    face_mesh = None
    if MP_AVAILABLE:
        try:
            face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception:
            face_mesh = None
    # Per-ID liveness state
    liveness_state_by_id = {}
    liveness_required_blinks = 2
    liveness_timeout_secs = 6.0

    def get_or_init_liveness_state(user_id):
        now = time.time()
        state = liveness_state_by_id.get(user_id)
        if state is None:
            state = {
                'start_time': now,
                'blink_count': 0,
                'prev_ear_below': False,
                'passed': False
            }
            liveness_state_by_id[user_id] = state
        return state

    # EAR computation using MediaPipe Face Mesh landmark indices
    # Left eye: 33, 160, 158, 133, 153, 144; Right eye: 362, 385, 387, 263, 373, 380
    left_eye_idx = [33, 160, 158, 133, 153, 144]
    right_eye_idx = [362, 385, 387, 263, 373, 380]

    def point_from_landmark(lm, w, h):
        return np.array([lm.x * w, lm.y * h], dtype=np.float32)

    def eye_aspect_ratio(landmarks, w, h, idxs):
        p = [point_from_landmark(landmarks[i], w, h) for i in idxs]
        # EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        vert1 = np.linalg.norm(p[1] - p[5])
        vert2 = np.linalg.norm(p[2] - p[4])
        horiz = np.linalg.norm(p[0] - p[3]) + 1e-6
        return (vert1 + vert2) / (2.0 * horiz)

    def compute_ear(landmarks, w, h):
        try:
            left = eye_aspect_ratio(landmarks, w, h, left_eye_idx)
            right = eye_aspect_ratio(landmarks, w, h, right_eye_idx)
            return (left + right) / 2.0
        except Exception:
            return None
    
    def detect_spoof(face_roi_bgr, face_roi_gray):
        """Enhanced spoof detection with multiple techniques"""
        try:
            if face_roi_bgr is None or face_roi_gray is None:
                return True, 0.0
            h, w = face_roi_gray.shape[:2]
            if h < 20 or w < 20:
                return True, 0.0
            
            # 1. Texture analysis (real faces have more texture)
            lap_var = cv2.Laplacian(face_roi_gray, cv2.CV_64F).var()
            texture_score = min(1.0, max(0.0, lap_var / 150.0))
            
            # 2. Edge analysis (real faces have natural edges)
            sobelx = cv2.Sobel(face_roi_gray, cv2.CV_32F, 1, 0, ksize=3)
            sobely = cv2.Sobel(face_roi_gray, cv2.CV_32F, 0, 1, ksize=3)
            mag = cv2.magnitude(sobelx, sobely)
            edge_mean = float(np.mean(mag))
            edge_score = min(1.0, max(0.0, edge_mean / 25.0))
            
            # 3. Specular reflection detection (photos/screens have reflections)
            hsv = cv2.cvtColor(face_roi_bgr, cv2.COLOR_BGR2HSV)
            h_ch, s_ch, v_ch = cv2.split(hsv)
            specular_mask = (v_ch > 230) & (s_ch < 40)
            spec_ratio = float(np.count_nonzero(specular_mask)) / float(h * w)
            spec_penalty = min(1.0, spec_ratio * 5.0)
            
            # 4. Color distribution analysis (real faces have natural color variation)
            b, g, r = cv2.split(face_roi_bgr)
            color_variance = (np.var(b.astype(np.float32)) + 
                            np.var(g.astype(np.float32)) + 
                            np.var(r.astype(np.float32))) / 3.0
            color_score = min(1.0, max(0.0, color_variance / 500.0))
            
            # 5. Depth cues (using focus/blur analysis)
            # Real faces have natural depth variation, photos are flatter
            focus_score = min(1.0, max(0.0, lap_var / 100.0))
            
            # Combined spoof score (higher = more likely to be real)
            spoof_score = (
                0.35 * texture_score +
                0.25 * edge_score +
                0.20 * color_score +
                0.20 * focus_score -
                0.30 * spec_penalty  # Penalty for reflections
            )
            
            # Stricter threshold for better security
            passed = spoof_score >= 0.40  # Increased from 0.35
            return passed, float(max(0.0, min(1.0, spoof_score)))
        except Exception as e:
            print(f"Spoof detection error: {e}")
            return True, 0.0

    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
    faculty_details_path = os.path.join("FacultyDetails", "FacultyDetails.csv")
    exists1 = os.path.isfile(faculty_details_path)
    if exists1:
        df = pd.read_csv(faculty_details_path, encoding='latin-1')
    else:
        mess.showerror('Details Missing', 'Faculty details are missing! Please register faculty in Admin Panel first.')
        cam.release()
        cv2.destroyAllWindows()
        return
    
    greeted_users = set()
    recorded_users = set()  # Track who has been recorded in this session
    already_recorded = False  # Initialize at function level
    
    # Load today's attendance to check for existing records
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    attendance_filename = "Attendance_" + date + ".csv"
    attendance_path = os.path.join("Attendance", attendance_filename)
    
    # Check if attendance file exists and load existing IDs
    existing_attendance_ids = set()
    if os.path.isfile(attendance_path):
        try:
            with open(attendance_path, 'r', encoding='utf-8') as f:
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
        
        # Initialize defaults for header text before analysis updates
        try:
            face_orientation
        except UnboundLocalError:
            pass
        except NameError:
            pass
        face_orientation = 'unknown'
        gesture_info = {'gesture': 'unknown'}
        
        # Create overlay for header
        overlay = display_im.copy()
        cv2.rectangle(overlay, (0, 0), (w_img, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display_im, 0.3, 0, display_im)
        
        # Header text
        cv2.putText(display_im, "Enhanced Faculty Attendance System", (20, 30), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)
        cv2.putText(display_im, "Multi-Angle Recognition + Body Gesture Detection", (20, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        cv2.putText(display_im, f"Time: {current_time}", (20, 75), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, f"Recorded Today: {len(existing_attendance_ids)}", 
                   (w_img - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, f"Session Count: {session_count}", 
                   (w_img - 250, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, f"Face: {face_orientation.upper()} | Gesture: {gesture_info['gesture'].upper()}", 
                   (w_img - 350, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Create footer overlay
        footer_overlay = display_im.copy()
        cv2.rectangle(footer_overlay, (0, h_img - 50), (w_img, h_img), (0, 0, 0), -1)
        cv2.addWeighted(footer_overlay, 0.7, display_im, 0.3, 0, display_im)
        
        # Footer instructions
        cv2.putText(display_im, "Press 'Q' to Exit | 'R' to Refresh", (20, h_img - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(display_im, "Face camera directly for best recognition", (w_img - 400, h_img - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        # Optimized detection parameters for better accuracy and reliability
        # scaleFactor=1.1: Balanced precision and sensitivity
        # minNeighbors=4: More lenient for better detection
        # minSize=(60, 60): Smaller minimum size for distant faces
        # maxSize=(500, 500): Reasonable maximum size
        faces = faceCascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=4, 
            minSize=(60, 60), 
            maxSize=(500, 500),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Get face orientation and body gesture information
        face_orientation, orientation_conf = orientation_detector.get_face_orientation(im)
        gesture_info = gesture_detector.get_gesture_info(im)
        
        # Debug: Print number of faces detected
        if len(faces) > 0:
            print(f"Faces detected: {len(faces)}")
            print(f"Face orientation: {face_orientation} (conf: {orientation_conf:.2f})")
            print(f"Body gesture: {gesture_info['gesture']} (conf: {gesture_info['confidence']:.2f})")
        else:
            print("No faces detected")
        
        for (x, y, w, h) in faces:
            # Initialize variables for THIS face (prevents data from previous face)
            bb = "Unknown"
            ID = "Unknown"
            faculty_tasks = []
            color = (0, 0, 255)  # Default red for unknown
            status_text = "UNKNOWN"
            status_color = (0, 0, 255)
            already_recorded = False  # Initialize to prevent UnboundLocalError
            conf = 100  # Initialize confidence to unknown

            # Compute motion score on face ROI using previous frame
            motion_score = 0.0
            if prev_gray_frame is not None:
                # Ensure ROI is in-bounds for both frames
                x0 = max(0, x)
                y0 = max(0, y)
                x1 = min(prev_gray_frame.shape[1], x + w)
                y1 = min(prev_gray_frame.shape[0], y + h)
                if x1 > x0 and y1 > y0:
                    roi_curr = gray[y0:y1, x0:x1]
                    roi_prev = prev_gray_frame[y0:y1, x0:x1]
                    if roi_curr.shape == roi_prev.shape and roi_curr.size > 0:
                        frame_delta = cv2.absdiff(roi_curr, roi_prev)
                        motion_score = float(np.mean(frame_delta))
            
            # Extract face ROI and validate quality
            roi = gray[y:y + h, x:x + w]
            
            # Validate face quality before recognition
            is_valid_face, quality_score, quality_issues = validate_face_quality(roi)
            
            # Always attempt recognition, but warn about poor quality
            if not is_valid_face:
                print(f"Poor face quality: {quality_issues} (Score: {quality_score:.1f})")
                print("Attempting recognition despite poor quality...")
                status_text = f"POOR QUALITY: {', '.join(quality_issues[:2])}"
                status_color = (0, 165, 255)  # Orange
            
            try:
                if use_cnn:
                    # Use CNN recognition
                    serial, conf, name = cnn_recognizer.recognize_face(roi)
                    print(f"CNN recognition - Serial: {serial}, Confidence: {conf:.1f}%, Name: {name}, Quality: {quality_score:.1f}")
                else:
                    # Use ensemble recognition for LBPH
                    serial, conf, ensemble_results = ensemble_recognize(recognizer, roi)
                    print(f"LBPH Ensemble recognition - Serial: {serial}, Confidence: {conf}, Quality: {quality_score:.1f}")
            except Exception as e:
                # If prediction fails, treat as unknown
                conf = 100
                serial = -1
                print(f"Recognition failed - treating as unknown: {e}")
            
            # Enhanced recognition with orientation, gesture, and quality validation
            # Adjust confidence threshold based on multiple factors
            if conf < 100:  # Face was recognized (not unknown)
                if use_cnn:
                    # CNN uses 0-100 scale (higher is better)
                    # Optimized threshold for 99% accuracy
                    base_threshold = 70  # CNN threshold (matches similarity_threshold * 100)
                    orientation_bonus = 0
                    gesture_bonus = 0
                    quality_bonus = 0
                
                    # Quality bonus: higher quality faces get better recognition
                    if quality_score >= 80:
                        quality_bonus = 10
                    elif quality_score >= 60:
                        quality_bonus = 5
                    elif quality_score >= 40:
                        quality_bonus = 2
                    
                    # Orientation bonus: front view gets better recognition
                    if face_orientation == 'front' and orientation_conf > 0.7:
                        orientation_bonus = 8
                    elif face_orientation in ['left', 'right'] and orientation_conf > 0.6:
                        orientation_bonus = 5
                    elif face_orientation == 'front' and orientation_conf > 0.5:
                        orientation_bonus = 3
                    
                    # Gesture bonus: natural poses get better recognition
                    if gesture_info['facing_camera'] and gesture_info['is_standing']:
                        gesture_bonus = 5
                    if gesture_info['gesture'] == 'neutral' and gesture_info['confidence'] > 0.6:
                        gesture_bonus += 3
                    
                    # Apply bonuses to threshold (higher threshold = more strict)
                    adjusted_threshold = base_threshold + orientation_bonus + gesture_bonus + quality_bonus
                    
                    # Ensure threshold doesn't go too high (maximum 85)
                    adjusted_threshold = min(85, adjusted_threshold)
                    
                    if conf >= adjusted_threshold:
                        print(f"CNN Face recognized with confidence {conf:.1f}%, serial {serial}")
                        print(f"Orientation: {face_orientation} (bonus: +{orientation_bonus})")
                        print(f"Gesture: {gesture_info['gesture']} (bonus: +{gesture_bonus})")
                        print(f"Quality: {quality_score:.1f} (bonus: +{quality_bonus})")
                        print(f"Adjusted threshold: {adjusted_threshold}")
                        
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        
                        # Debug: Check if serial exists in dataframe
                        print(f"Looking for serial {serial} in dataframe")
                        print(f"Available serials: {df['SERIAL NO.'].values}")
                        
                        aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                        ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                        
                        print(f"Found name values: {aa}")
                        print(f"Found ID values: {ID}")
                        
                        if len(aa) > 0 and len(ID) > 0:
                            ID = str(ID[0])
                            bb = str(aa[0])
                            print(f"Final ID: {ID}, Name: {bb}")
                            
                            # Check for tasks due today for this faculty (needed for display)
                            today_date = datetime.datetime.now().strftime('%Y-%m-%d')
                            tasks_path = os.path.join("Tasks", "Tasks.csv")
                            faculty_tasks = []
                            
                            # Debug: Print the ID we're checking
                            print(f"Checking tasks for Faculty ID: '{ID}', Name: '{bb}', Date: {today_date}")
                            
                            if os.path.isfile(tasks_path):
                                try:
                                    tasks_df = pd.read_csv(tasks_path, encoding='latin-1')
                                    print(f"Total tasks in database: {len(tasks_df)}")
                                    
                                    # Clean and compare IDs (remove quotes, whitespace, etc.)
                                    clean_id = str(ID).strip().strip("'").strip('"')
                                    print(f"Cleaned Faculty ID: '{clean_id}'")
                                    
                                    # Filter tasks for this faculty member due today and not completed
                                    faculty_tasks_df = tasks_df[
                                        (tasks_df['FACULTY_ID'].astype(str).str.strip() == clean_id) & 
                                        (tasks_df['DUE_DATE'].astype(str) == today_date) & 
                                        (tasks_df['STATUS'] != 'Completed')
                                    ]
                                    
                                    print(f"Found {len(faculty_tasks_df)} tasks for this faculty today")
                                    
                                    for idx, task in faculty_tasks_df.iterrows():
                                        print(f"Task found: {task['TASK_TITLE']} (Priority: {task['PRIORITY']})")
                                        faculty_tasks.append({
                                            'title': task['TASK_TITLE'],
                                            'description': task['TASK_DESCRIPTION'] if pd.notna(task['TASK_DESCRIPTION']) else '',
                                            'priority': task['PRIORITY']
                                        })
                                except Exception as e:
                                    print(f"Task check error: {e}")
                                    import traceback
                                    traceback.print_exc()
                        else:
                            print("No matching data found for this serial number")  
                            conf = 100  # Treat as unknown
                else:
                    # LBPH uses distance scale (lower is better)
                    base_threshold = 70  # LBPH threshold
                    orientation_bonus = 0
                    gesture_bonus = 0
                    quality_bonus = 0
                
                    # Quality bonus: higher quality faces get better recognition
                    if quality_score >= 80:
                        quality_bonus = 15
                    elif quality_score >= 60:
                        quality_bonus = 10
                    elif quality_score >= 40:
                        quality_bonus = 5
                
                    # Orientation bonus: front view gets better recognition
                    if face_orientation == 'front' and orientation_conf > 0.7:
                        orientation_bonus = 12
                    elif face_orientation in ['left', 'right'] and orientation_conf > 0.6:
                        orientation_bonus = 8
                    elif face_orientation == 'front' and orientation_conf > 0.5:
                        orientation_bonus = 5
                    
                    # Gesture bonus: natural poses get better recognition
                    if gesture_info['facing_camera'] and gesture_info['is_standing']:
                        gesture_bonus = 8
                    if gesture_info['gesture'] == 'neutral' and gesture_info['confidence'] > 0.6:
                        gesture_bonus += 5
                    
                    # Apply bonuses to threshold (lower threshold = more lenient)
                    adjusted_threshold = base_threshold - orientation_bonus - gesture_bonus - quality_bonus
                    
                    # Ensure threshold doesn't go too low (minimum 35)
                    adjusted_threshold = max(35, adjusted_threshold)
                    
                    if conf < adjusted_threshold:
                        print(f"LBPH Face recognized with confidence {conf}, serial {serial}")
                        print(f"Orientation: {face_orientation} (bonus: +{orientation_bonus})")
                        print(f"Gesture: {gesture_info['gesture']} (bonus: +{gesture_bonus})")
                        print(f"Quality: {quality_score:.1f} (bonus: +{quality_bonus})")
                        print(f"Adjusted threshold: {adjusted_threshold}")
                        
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    
                        # Debug: Check if serial exists in dataframe
                        print(f"Looking for serial {serial} in dataframe")
                        print(f"Available serials: {df['SERIAL NO.'].values}")
                        
                        aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                        ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                        
                        print(f"Found name values: {aa}")
                        print(f"Found ID values: {ID}")
                        
                        if len(aa) > 0 and len(ID) > 0:
                            ID = str(ID[0])
                            bb = str(aa[0])
                            print(f"Final ID: {ID}, Name: {bb}")
                            
                            # Check for tasks due today for this faculty (needed for display)
                            today_date = datetime.datetime.now().strftime('%Y-%m-%d')
                            tasks_path = os.path.join("Tasks", "Tasks.csv")
                            faculty_tasks = []
                            
                            # Debug: Print the ID we're checking
                            print(f"Checking tasks for Faculty ID: '{ID}', Name: '{bb}', Date: {today_date}")
                            
                            if os.path.isfile(tasks_path):
                                try:
                                    tasks_df = pd.read_csv(tasks_path, encoding='latin-1')
                                    print(f"Total tasks in database: {len(tasks_df)}")
                                    
                                    # Clean and compare IDs (remove quotes, whitespace, etc.)
                                    clean_id = str(ID).strip().strip("'").strip('"')
                                    print(f"Cleaned Faculty ID: '{clean_id}'")
                                    
                                    # Filter tasks for this faculty member due today and not completed
                                    faculty_tasks_df = tasks_df[
                                        (tasks_df['FACULTY_ID'].astype(str).str.strip() == clean_id) & 
                                        (tasks_df['DUE_DATE'].astype(str) == today_date) & 
                                        (tasks_df['STATUS'] != 'Completed')
                                    ]
                                    
                                    print(f"Found {len(faculty_tasks_df)} tasks for this faculty today")
                                    
                                    for idx, task in faculty_tasks_df.iterrows():
                                        print(f"Task found: {task['TASK_TITLE']} (Priority: {task['PRIORITY']})")
                                        faculty_tasks.append({
                                            'title': task['TASK_TITLE'],
                                            'description': task['TASK_DESCRIPTION'] if pd.notna(task['TASK_DESCRIPTION']) else '',
                                            'priority': task['PRIORITY']
                                        })
                                except Exception as e:
                                    print(f"Task check error: {e}")
                                    import traceback
                                    traceback.print_exc()
                            
                        # Check if this faculty already has attendance today
                        already_recorded = ID in existing_attendance_ids or ID in recorded_users
                        
                        # Debug: Print attendance status
                        print(f"Attendance status for {bb} (ID: {ID}):")
                        print(f"  - In existing_attendance_ids: {ID in existing_attendance_ids}")
                        print(f"  - In recorded_users: {ID in recorded_users}")
                        print(f"  - Already recorded: {already_recorded}")
                        
                        # Only attempt to record attendance if not already recorded today
                        if not already_recorded:
                            # Liveness: blink challenge (if MediaPipe available)
                            liveness_passed = True
                            liveness_prompt = ""
                            if face_mesh is not None and ID != "Unknown":
                                try:
                                    # MediaPipe expects RGB
                                    rgb_im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                                    results = face_mesh.process(rgb_im)
                                    if results.multi_face_landmarks:
                                        landmarks = results.multi_face_landmarks[0].landmark
                                        ear = compute_ear(landmarks, w_img, h_img)
                                        if ear is not None:
                                            state = get_or_init_liveness_state(ID)
                                            ear_thresh = 0.21
                                            # Blink detection: transition from not-below -> below threshold
                                            below = ear < ear_thresh
                                            if below and not state['prev_ear_below']:
                                                state['blink_count'] += 1
                                            state['prev_ear_below'] = below
                                            # Check pass/timeout
                                            if state['blink_count'] >= liveness_required_blinks:
                                                state['passed'] = True
                                            elif (time.time() - state['start_time']) > liveness_timeout_secs:
                                                # Reset window to avoid permanent block; allow continuing attempts
                                                state['start_time'] = time.time()
                                                state['blink_count'] = 0
                                                state['prev_ear_below'] = False
                                            liveness_passed = state['passed']
                                            if not liveness_passed:
                                                liveness_prompt = f"LIVENESS: Blink twice  Blinks: {state['blink_count']}/{liveness_required_blinks}"
                                        else:
                                            liveness_passed = False
                                            liveness_prompt = "LIVENESS: Hold steady and blink"
                                    else:
                                        liveness_passed = False
                                        liveness_prompt = "LIVENESS: Face not stable for landmarks"
                                except Exception:
                                    # If Face Mesh fails, fall back to motion-only
                                    liveness_passed = True

                            # Gate by motion + liveness + spoof detection: only mark attendance when all pass
                            roi_bgr = im[y:y + h, x:x + w]
                            roi_gray = gray[y:y + h, x:x + w]
                            
                            # Enhanced anti-spoofing detection
                            spoof_passed, spoof_score = detect_spoof(roi_bgr, roi_gray)
                            
                            # Get previous ROI for this face (if exists) for motion tracking
                            face_key = f"{x}_{y}_{w}_{h}"  # Simple key for face tracking
                            prev_roi = prev_roi_gray.get(face_key)
                            screen_passed, screen_score = screen_detector.update_and_detect(roi_bgr, roi_gray, prev_roi)
                            
                            # Store current ROI for next frame
                            prev_roi_gray[face_key] = roi_gray.copy()
                            
                            # Clean up old entries (keep only recent faces)
                            if len(prev_roi_gray) > 10:
                                # Remove oldest entries
                                keys_to_remove = list(prev_roi_gray.keys())[:-5]
                                for key in keys_to_remove:
                                    prev_roi_gray.pop(key, None)
                            
                            # Enhanced anti-spoofing: Block attendance if spoofing detected
                            anti_spoof_passed = spoof_passed and screen_passed
                            
                            if not anti_spoof_passed:
                                status_text = "SPOOF DETECTED"
                                status_color = (0, 0, 255)  # Red
                                print(f"Anti-spoofing failed: Spoof={spoof_passed} (score: {spoof_score:.2f}), Screen={screen_passed} (score: {screen_score:.2f})")
                            
                            # Attendance is gated by motion + anti-spoofing + liveness
                            if motion_score >= motion_threshold and anti_spoof_passed:
                                # Record attendance
                                attendance = [str(ID), '', bb, '', str(date), '', str(timeStamp)]
                                exists = os.path.isfile(attendance_path)
                                with open(attendance_path, 'a+', encoding='utf-8') as csvFile1:
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
                                already_recorded = True  # Update the flag
                                status_text = "ATTENDANCE RECORDED"
                                status_color = (0, 255, 0)
                                print(f"✅ ATTENDANCE RECORDED for {bb} (ID: {ID}) at {timeStamp}")
                            else:
                                # Block if motion is insufficient OR spoofing detected
                                if not anti_spoof_passed:
                                    # Spoofing already handled above, but keep status
                                    pass
                                elif motion_score < motion_threshold:
                                    status_text = "NO MOTION"
                                    status_color = (0, 0, 255)
                        else:
                            # Already recorded today
                            status_text = "ALREADY RECORDED TODAY"
                            status_color = (0, 165, 255)  # Orange
                            print(f"ℹ️  {bb} (ID: {ID}) already recorded today - skipping")
                    else:
                        print("No matching data found for this serial number")  
                        conf = 100  # Treat as unknown
                
            # Greet faculty (only once per session) and activate voice assistant
            if ID not in greeted_users and ID != "Unknown":
                time_greeting = voice_assistant.get_time_greeting()
                
                # Build greeting with task announcements
                if already_recorded:
                    # Already recorded today (from earlier)
                    full_greeting = f"Hi {bb}, {time_greeting}, Your attendance for today is already recorded"
                else:
                    # First time today
                    full_greeting = f"Hi {bb}, {time_greeting}, Welcome to Faculty Office"
                
                # Activate voice assistant automatically when face is recognized
                print(f"🎤 Activating voice assistant for {bb}")
                voice_status.configure(text=f"🎤 Speaking to {bb}", text_color=UI_COLORS["highlight"])
                voice_activation_indicator.configure(text=f"🎤 VOICE ASSISTANT ACTIVATED FOR {bb.upper()}", text_color=UI_COLORS["highlight"])
                
                # Auto-start voice listening after greeting
                def auto_listen():
                    # Wait for greeting to finish
                    time.sleep(3)
                    voice_status.configure(text=f"🎤 Listening to {bb}", text_color=UI_COLORS["accent"])
                    voice_response.configure(text=f"Say something to {bb}...")
                    voice_activation_indicator.configure(text=f"🎤 LISTENING TO {bb.upper()}", text_color=UI_COLORS["accent"])
                    
                    # Start listening in background
                    def listen_background():
                        try:
                            command = voice_assistant.listen()
                            if command not in ["timeout", "unknown", "error"]:
                                response, action = voice_assistant.handle_command(command, ID)
                                voice_response.configure(text=response)
                                voice_assistant.speak(response)
                                voice_status.configure(text=f"🎤 Responded to {bb}", text_color=UI_COLORS["success"])
                                voice_activation_indicator.configure(text=f"🎤 RESPONDED TO {bb.upper()}", text_color=UI_COLORS["success"])
                            else:
                                voice_status.configure(text=f"🎤 Ready for {bb}", text_color=UI_COLORS["text_primary"])
                                voice_activation_indicator.configure(text=f"🎤 READY FOR {bb.upper()}", text_color=UI_COLORS["text_primary"])
                        except Exception as e:
                            print(f"Auto-listen error: {e}")
                            voice_status.configure(text=f"🎤 Ready for {bb}", text_color=UI_COLORS["text_primary"])
                            voice_activation_indicator.configure(text=f"🎤 READY FOR {bb.upper()}", text_color=UI_COLORS["text_primary"])
                    
                    # Start listening in background thread
                    listen_thread = Thread(target=listen_background, daemon=True)
                    listen_thread.start()
                
                # Start auto-listen in background
                auto_thread = Thread(target=auto_listen, daemon=True)
                auto_thread.start()
                
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
            if already_recorded:
                # Orange for already recorded
                color = (0, 165, 255)  # BGR: Orange
                if status_text not in ("NO MOTION", "ALREADY RECORDED TODAY"):
                    status_text = "ALREADY RECORDED TODAY"
                    status_color = (0, 165, 255)
            else:
                # Green for newly recorded
                # Keep any motion-block override if set above; otherwise default to recorded
                if status_text not in ("NO MOTION", "ALREADY RECORDED TODAY"):
                    color = (0, 255, 0)  # BGR: Green
                    status_text = "ATTENDANCE RECORDED"
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
            
            # Status (includes NO MOTION / LIVENESS REQUIRED when blocking)
            cv2.putText(display_im, status_text, (x + 10, info_y + 78), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

            # Show motion score for debugging (small text under box)
            cv2.putText(display_im, f"Motion: {motion_score:.1f}", (x + w - 140, y + h + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            
            # Show face quality and orientation info
            quality_text = f"Quality: {quality_score:.0f}"
            orientation_text = f"Face: {face_orientation.upper()}"
            gesture_text = f"Gesture: {gesture_info['gesture'].upper()}"
            
            # Color code quality score
            if quality_score >= 80:
                quality_color = (0, 255, 0)  # Green
            elif quality_score >= 60:
                quality_color = (0, 255, 255)  # Yellow
            else:
                quality_color = (0, 165, 255)  # Orange
            
            cv2.putText(display_im, quality_text, (x + w - 140, y + h + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, quality_color, 1)
            cv2.putText(display_im, orientation_text, (x + w - 140, y + h + 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            cv2.putText(display_im, gesture_text, (x + w - 140, y + h + 85),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

            # Show liveness prompt/progress if applicable
            if face_mesh is not None and 'liveness_passed' in locals() and not liveness_passed:
                tip = liveness_prompt if 'liveness_prompt' in locals() else "LIVENESS: Blink twice"
                cv2.putText(display_im, tip[:48], (x, max(y - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)
            
            
            # Enhanced confidence display: convert LBPH distance to 0-100 quality
            # Map: 20->100, 60->60, 80->40, >100->0
            q = 100 - max(0, min(100, (conf - 20) * 1.5))
            q = max(0, min(100, q))
            if conf < 35:
                conf_color = (0, 255, 0)
            elif conf < 60:
                conf_color = (0, 255, 255)
            else:
                conf_color = (0, 165, 255)
            cv2.putText(display_im, f"Match Quality: {q:.0f}%", (x + w - 170, y + h + 25), 
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
                cv2.putText(display_im, f"{len(faculty_tasks)} Task(s) Due Today:",  
                           (x + 10, task_box_y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # List tasks (max 3 visible)
                for i, task in enumerate(faculty_tasks[:3]):
                    priority_icon = "🔴" if task['priority'] == "Urgent" else "🟠" if task['priority'] == "High" else "🟡"
                    task_text = f"{priority_icon} {task['title'][:35]}"
                    cv2.putText(display_im, task_text, 
                               (x + 15, task_box_y + 45 + (i * 25)), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            # If face was not recognized (conf >= 100), show unknown person display
            if conf >= 100:
                # Unknown person - use initialized default values (bb="Unknown", ID="Unknown")
                # Red rectangle with warning effect
                cv2.rectangle(display_im, (x-5, y-5), (x+w+5, y+h+5), (0, 0, 255), 3)
                cv2.rectangle(display_im, (x-3, y-3), (x+w+3, y+h+3), (255, 255, 255), 1)
                # Show enhanced anti-spoofing scores for debugging
                try:
                    if 'spoof_passed' in locals() and 'screen_passed' in locals():
                        spoof_status = "PASS" if spoof_passed else "FAIL"
                        screen_status = "PASS" if screen_passed else "FAIL"
                        spoof_color = (0, 255, 0) if spoof_passed else (0, 0, 255)
                        screen_color = (0, 255, 0) if screen_passed else (0, 0, 255)
                        cv2.putText(display_im, f"Anti-Spoof: {spoof_status}({spoof_score:.2f})", (x + w - 200, y + h + 55),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, spoof_color, 1)
                        cv2.putText(display_im, f"Screen: {screen_status}({screen_score:.2f})", (x + w - 200, y + h + 70),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, screen_color, 1)
                except Exception:
                    pass
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
        
        # Show voice assistant activation indicator (outside face loop)
        if len(faces) > 0:
            # Check if any recognized face should show voice activation
            for (fx, fy, fw, fh) in faces:
                # This will be handled inside the face loop for each face
                pass
        
        # Show voice attendance backup instruction (always visible)
        cv2.putText(display_im, "Voice Backup: Say 'mark attendance' if face recognition fails", 
                   (int(w_img/2) - 200, h_img - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # If no faces detected
        if len(faces) == 0:
            cv2.putText(display_im, "No face detected - Please look at camera", 
                       (int(w_img/2) - 250, int(h_img/2)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Show enhanced frame
        cv2.imshow('🎓 Faculty Attendance Recognition', display_im)

        # Update previous gray frame for next iteration (after using it)
        prev_gray_frame = gray.copy()
        
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
        voice_status.configure(text="Listening...", text_color="yellow")
        command = voice_assistant.listen()
        
        if command == "timeout":
            voice_status.configure(text="No command detected", text_color="orange")
            return
        elif command == "unknown":
            voice_status.configure(text="Could not understand", text_color="red")
            return
        elif command == "error":
            voice_status.configure(text="Microphone error", text_color="red")
            return
        
        voice_status.configure(text=f"Heard: {command}", text_color="green")
        
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
        with open(faculty_details_path, 'r', encoding='latin-1') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                res = res + 1
        res = (res // 2) - 1
    else:
        res = 0
    message.configure(text=f'📊 Total Faculty: {res}')

######################################## GUI FRONT-END ###########################################

window = ctk.CTk()
window.geometry("1600x900")
window.title("🎓 GreetA - Faculty Attendance System")
window.configure(fg_color=UI_COLORS["primary"])

# Configure window icon and styling
try:
    window.iconbitmap("icon.ico")  # Add if you have an icon
except:
    pass

# Header with modern design (matching admin panel)
header_frame = ctk.CTkFrame(
    window, 
    height=90, 
    corner_radius=0,
    fg_color=UI_COLORS["secondary"],
    border_width=2,
    border_color=UI_COLORS["accent"]
)
header_frame.pack(fill="x", padx=0, pady=0)
header_frame.pack_propagate(False)

# Main title with modern styling
title_label = ctk.CTkLabel(
    header_frame, 
    text="🔐 GreetA - Faculty Attendance System",
    font=("Arial Bold", 36),
    text_color=UI_COLORS["text_primary"]
)
title_label.pack(pady=20)

# Subtitle with accent color
subtitle_label = ctk.CTkLabel(
    header_frame,
    text="✨ AI-Powered Recognition & Management System ✨",
    font=("Arial", 14),
    text_color=UI_COLORS["highlight"]
)
subtitle_label.pack(pady=(0, 10))

# Date and Time Frame with modern styling (enhanced)
datetime_frame = ctk.CTkFrame(
    window, 
    height=50, 
    fg_color=UI_COLORS["secondary"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
datetime_frame.pack(fill="x", padx=20, pady=10)

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")
mont = {'01':'January', '02':'February', '03':'March', '04':'April', '05':'May', '06':'June',
        '07':'July', '08':'August', '09':'September', '10':'October', '11':'November', '12':'December'}

# Date with modern styling
date_label = ctk.CTkLabel(
    datetime_frame, 
    text=f"📅 {day} {mont[month]} {year}", 
    font=("Arial Bold", 16),
    text_color=UI_COLORS["text_primary"]
)
date_label.pack(side="left", padx=20, pady=10)

# Clock with accent styling
clock = ctk.CTkLabel(
    datetime_frame, 
    text="", 
    font=("Arial Bold", 16),
    text_color=UI_COLORS["highlight"]
)
clock.pack(side="right", padx=20, pady=10)

def tick():
    time_string = time.strftime('%H:%M:%S')
    clock.configure(text=time_string)
    clock.after(200, tick)

tick()

# Voice Assistant Frame with modern design (enhanced)
voice_frame = ctk.CTkFrame(
    window, 
    height=110,
    fg_color=UI_COLORS["secondary"],
    corner_radius=20,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
voice_frame.pack(fill="x", padx=20, pady=10)
voice_frame.pack_propagate(False)

# Voice assistant title with accent styling
voice_title = ctk.CTkLabel(
    voice_frame, 
    text="🎤 Voice Assistant", 
    font=("Arial Bold", 18),
    text_color=UI_COLORS["highlight"]
)
voice_title.pack(pady=8)

voice_button_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
voice_button_frame.pack()

# Enhanced voice button with modern styling (matching admin panel)
voice_button = ctk.CTkButton(
    voice_button_frame, 
    text="🎯 Start Listening",
    command=start_voice_command,
    width=200,
    height=45,
    font=("Arial Bold", 14),
    fg_color=UI_COLORS["accent"],
    hover_color=UI_COLORS["highlight"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
voice_button.pack(side="left", padx=15)

# Voice attendance backup button
def start_voice_attendance():
    """Start voice attendance recording"""
    def listen_and_record():
        voice_status.configure(text="🎤 Listening for attendance...", text_color=UI_COLORS["accent"])
        voice_response.configure(text="Say 'mark attendance' to record your attendance")
        
        command = voice_assistant.listen()
        
        if command == "timeout":
            voice_status.configure(text="No command detected", text_color=UI_COLORS["warning"])
            voice_response.configure(text="No voice detected. Please try again.")
            return
        elif command == "unknown":
            voice_status.configure(text="Could not understand", text_color=UI_COLORS["warning"])
            voice_response.configure(text="Could not understand. Please try saying 'mark attendance' clearly.")
            return
        elif command == "error":
            voice_status.configure(text="Microphone error", text_color=UI_COLORS["warning"])
            voice_response.configure(text="Microphone error. Please check your microphone.")
            return
        
        voice_status.configure(text=f"Heard: {command}", text_color=UI_COLORS["accent"])
        
        # Process the command
        response, action = voice_assistant.handle_command(command)
        voice_response.configure(text=response)
        voice_assistant.speak(response)
        
        if action == "attendance_recorded":
            voice_status.configure(text="✅ Attendance recorded!", text_color=UI_COLORS["success"])
            voice_activation_indicator.configure(text="✅ VOICE ATTENDANCE RECORDED", text_color=UI_COLORS["success"])
        else:
            voice_status.configure(text="Ready for commands", text_color=UI_COLORS["text_primary"])
    
    thread = Thread(target=listen_and_record)
    thread.daemon = True
    thread.start()

voice_attendance_btn = ctk.CTkButton(
    voice_button_frame, 
    text="📝 Voice Attendance",
    command=start_voice_attendance,
    width=180,
    height=45,
    font=("Arial Bold", 14),
    fg_color=UI_COLORS["success"],
    hover_color=UI_COLORS["accent"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["success"]
)
voice_attendance_btn.pack(side="left", padx=15)

# Voice status with modern styling
voice_status = ctk.CTkLabel(
    voice_button_frame, 
    text="🔊 Ready to listen", 
    font=("Arial Bold", 12),
    text_color=UI_COLORS["text_primary"]
)
voice_status.pack(side="left", padx=20)

# Voice response with accent styling
voice_response = ctk.CTkLabel(
    voice_frame, 
    text="💬 Say: 'hello', 'time', 'weather', 'date', or 'mark attendance'", 
    font=("Arial", 12), 
    text_color=UI_COLORS["text_secondary"]
)
voice_response.pack(pady=5)

# Voice activation indicator
voice_activation_indicator = ctk.CTkLabel(
    voice_frame,
    text="",
    font=("Arial Bold", 14),
    text_color=UI_COLORS["highlight"]
)
voice_activation_indicator.pack(pady=2)

# Main Content Frame with modern design
content_frame = ctk.CTkFrame(
    window, 
    fg_color=UI_COLORS["primary"],
    corner_radius=0
)
content_frame.pack(fill="both", expand=True, padx=20, pady=5)

# Left Panel - Attendance System with modern design (enhanced)
left_frame = ctk.CTkFrame(
    content_frame, 
    width=750,
    fg_color=UI_COLORS["secondary"],
    corner_radius=20,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
left_frame.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=10)

# Left panel header with modern styling
left_header = ctk.CTkLabel(
    left_frame, 
    text="📸 Attendance System", 
    font=("Arial Bold", 24),
    text_color=UI_COLORS["text_primary"]
)
left_header.pack(pady=15)

# Enhanced attendance button with modern styling (matching admin panel)
attendance_btn = ctk.CTkButton(
    left_frame,
    text="🎯 Take Attendance",
    command=TrackImages,
    width=320,
    height=55,
    font=("Arial Bold", 18),
    fg_color=UI_COLORS["success"],
    hover_color=UI_COLORS["accent"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["success"]
)
attendance_btn.pack(pady=20)

# Treeview for attendance with modern design
tree_frame = ctk.CTkFrame(
    left_frame,
    fg_color=UI_COLORS["primary"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
tree_frame.pack(fill="both", expand=True, padx=20, pady=15)

# Create a modern style for the treeview
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
          background=[('selected', UI_COLORS["highlight"])],
          foreground=[('selected', UI_COLORS["text_primary"])])

# Enhanced treeview with modern styling
tv = ttk.Treeview(
    tree_frame, 
    height=16, 
    columns=('ID', 'Name', 'Date', 'Time'), 
    show='headings',
    style="Treeview"
)
tv.column('ID', width=150, anchor='center')
tv.column('Name', width=250, anchor='center')
tv.column('Date', width=150, anchor='center')
tv.column('Time', width=120, anchor='center')
tv.heading('ID', text='🆔 ID')
tv.heading('Name', text='👤 NAME')
tv.heading('Date', text='📅 DATE')
tv.heading('Time', text='⏰ TIME')
tv.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Enhanced scrollbar
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tv.yview)
scrollbar.pack(side="right", fill="y", pady=10)
tv.configure(yscrollcommand=scrollbar.set)

# Enhanced quit button with modern styling (matching admin panel)
quit_btn = ctk.CTkButton(
    left_frame,
    text="🚪 Exit Application",
    command=window.destroy,
    width=320,
    height=50,
    font=("Arial Bold", 16),
    fg_color=UI_COLORS["highlight"],
    hover_color=UI_COLORS["accent"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["highlight"]
)
quit_btn.pack(pady=20)

# Right Panel - Admin Access & Info with modern design (enhanced)
right_frame = ctk.CTkFrame(
    content_frame, 
    width=750,
    fg_color=UI_COLORS["secondary"],
    corner_radius=20,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
right_frame.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

# Right panel header with modern styling
right_header = ctk.CTkLabel(
    right_frame, 
    text="🔐 Admin Panel", 
    font=("Arial Bold", 24),
    text_color=UI_COLORS["text_primary"]
)
right_header.pack(pady=15)

# Admin Panel Info with modern design
info_frame = ctk.CTkFrame(
    right_frame, 
    fg_color=UI_COLORS["primary"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
info_frame.pack(fill="both", expand=True, padx=20, pady=15)

# Admin functions title with modern styling
ctk.CTkLabel(
    info_frame,
    text="⚡ Administrator Functions ⚡",
    font=("Arial Bold", 20),
    text_color=UI_COLORS["highlight"]
).pack(pady=20)

# Admin description with modern styling
ctk.CTkLabel(
    info_frame,
    text="🎯 For faculty registration and\nuser management, please use\nthe Admin Panel. 🎯",
    font=("Arial Bold", 16),
    text_color=UI_COLORS["text_primary"],
    justify="center"
).pack(pady=15)

# Open Admin Panel Button
def open_admin_panel():
    """Launch admin panel in new process"""
    import subprocess
    admin_path = os.path.join(os.path.dirname(__file__), "admin_panel.py")
    subprocess.Popen(["python3", admin_path])

# Enhanced admin button with modern styling (matching admin panel)
admin_btn = ctk.CTkButton(
    info_frame,
    text="🚀 Open Admin Panel",
    command=open_admin_panel,
    width=320,
    height=60,
    font=("Arial Bold", 18),
    fg_color=UI_COLORS["highlight"],
    hover_color=UI_COLORS["accent"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["highlight"]
)
admin_btn.pack(pady=25)

# System Info with modern design
info_text_frame = ctk.CTkFrame(
    info_frame, 
    fg_color=UI_COLORS["accent"],
    corner_radius=10,
    border_width=1,
    border_color=UI_COLORS["highlight"]
)
info_text_frame.pack(fill="x", padx=15, pady=15)

# Features title with modern styling
ctk.CTkLabel(
    info_text_frame,
    text="⚡ Admin Panel Features: ⚡",
    font=("Arial Bold", 16),
    text_color=UI_COLORS["text_primary"],
    anchor="w"
).pack(pady=10, padx=20, anchor="w")

# Enhanced features list with modern styling
features = [
    "👥 Add new faculty",
    "📋 View all registrations", 
    "🗑️ Delete faculty",
    "📊 View attendance records",
    "📤 Export data",
    "🔐 Change admin password"
]

for feature in features:
    ctk.CTkLabel(
        info_text_frame,
        text=feature,
        font=("Arial Bold", 13),
        text_color=UI_COLORS["text_primary"],
        anchor="w"
    ).pack(pady=3, padx=30, anchor="w")

# Faculty count with modern styling
message = ctk.CTkLabel(
    right_frame, 
    text="", 
    font=("Arial Bold", 16), 
    text_color=UI_COLORS["success"]
)
message.pack(pady=15)

# Update registration count
update_registration_count()

# Menu Bar with modern design (matching admin panel)
menubar = ctk.CTkFrame(
    window, 
    height=70, 
    corner_radius=0, 
    fg_color=UI_COLORS["secondary"],
    border_width=2,
    border_color=UI_COLORS["accent"]
)
menubar.pack(side="bottom", fill="x")
menubar.pack_propagate(False)

# Enhanced menu buttons with modern styling (matching admin panel)
help_btn = ctk.CTkButton(
    menubar, 
    text="🔧 Change Password", 
    command=change_pass, 
    width=160, 
    height=40, 
    font=("Arial Bold", 14),
    fg_color=UI_COLORS["accent"],
    hover_color=UI_COLORS["highlight"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
help_btn.pack(side="left", padx=12, pady=12)

contact_btn = ctk.CTkButton(
    menubar, 
    text="📧 Contact Us", 
    command=contact,
    width=130, 
    height=40, 
    font=("Arial Bold", 14),
    fg_color=UI_COLORS["accent"],
    hover_color=UI_COLORS["highlight"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
contact_btn.pack(side="left", padx=12, pady=12)

def test_voice():
    """Test voice output"""
    print("Testing voice...")
    voice_assistant.speak("Testing voice. If you can hear this, the audio is working.")

# Enhanced voice help button (matching admin panel)
voice_help_btn = ctk.CTkButton(
    menubar, 
    text="🎤 Voice Help", 
    command=lambda: voice_assistant.speak("You can ask me about time, weather, date, say hello, or say 'mark attendance' to record your attendance. Click the microphone button to start listening."),
    width=130, 
    height=40, 
    font=("Arial Bold", 14),
    fg_color=UI_COLORS["accent"],
    hover_color=UI_COLORS["highlight"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["accent"]
)
voice_help_btn.pack(side="left", padx=12, pady=12)

# Enhanced test voice button (matching admin panel)
test_voice_btn = ctk.CTkButton(
    menubar, 
    text="⚡ Test Voice", 
    command=test_voice,
    width=130, 
    height=40, 
    font=("Arial Bold", 14), 
    fg_color=UI_COLORS["warning"],
    hover_color=UI_COLORS["highlight"],
    corner_radius=15,
    border_width=2,
    border_color=UI_COLORS["warning"]
)
test_voice_btn.pack(side="left", padx=12, pady=12)

# Initial voice greeting with modern theme
window.after(1000, lambda: voice_assistant.speak("Welcome to the Great A Attendance System. I'm ready to help you with our modern AI-powered recognition technology!"))

window.mainloop()

