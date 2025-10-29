"""
YOLOv5 Object Detection Module
Handles image upload, object detection, and annotated image generation
Enhanced with real-time security monitoring capabilities
"""
import torch
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import os
import json
from datetime import datetime
from threading import Thread, Lock
import time


class ObjectDetector:
    """
    YOLOv5-based object detector for Django application
    """
    
    def __init__(self, model_name='yolov5s', confidence_threshold=0.25):
        """
        Initialize the YOLOv5 model
        
        Args:
            model_name (str): YOLOv5 model variant (yolov5s, yolov5m, yolov5l, yolov5x)
            confidence_threshold (float): Confidence threshold for detections (0.0 to 1.0)
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLOv5 model from torch hub"""
        try:
            # Load YOLOv5 model from ultralytics repository
            self.model = torch.hub.load('ultralytics/yolov5', self.model_name, pretrained=True)
            self.model.conf = self.confidence_threshold
            print(f"✅ YOLOv5 model '{self.model_name}' loaded successfully")
        except Exception as e:
            print(f"❌ Error loading YOLOv5 model: {str(e)}")
            raise
    
    def detect_objects(self, image_path):
        """
        Perform object detection on an image
        
        Args:
            image_path (str): Path to the input image
            
        Returns:
            dict: Detection results containing:
                - detections: List of detected objects with coordinates and confidence
                - count: Total number of objects detected
                - image_shape: Original image dimensions
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Run inference
        results = self.model(image_path)
        
        # Extract detection data
        detections = []
        df = results.pandas().xyxy[0]  # Pandas DataFrame with detection results
        
        for _, row in df.iterrows():
            detection = {
                'class': row['name'],
                'confidence': float(row['confidence']),
                'bbox': {
                    'xmin': int(row['xmin']),
                    'ymin': int(row['ymin']),
                    'xmax': int(row['xmax']),
                    'ymax': int(row['ymax'])
                }
            }
            detections.append(detection)
        
        # Get image shape
        img = Image.open(image_path)
        image_shape = {'width': img.width, 'height': img.height}
        
        return {
            'detections': detections,
            'count': len(detections),
            'image_shape': image_shape
        }
    
    def draw_annotations(self, image_path, detections, output_path):
        """
        Draw bounding boxes and labels on the image
        
        Args:
            image_path (str): Path to input image
            detections (list): List of detection dictionaries
            output_path (str): Path to save annotated image
            
        Returns:
            str: Path to the annotated image
        """
        # Read image with OpenCV
        img = cv2.imread(str(image_path))
        
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        # Define colors for different classes (BGR format)
        colors = [
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
        ]
        
        # Draw each detection
        for idx, det in enumerate(detections):
            bbox = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Get color for this detection
            color = colors[idx % len(colors)]
            
            # Draw bounding box
            cv2.rectangle(
                img,
                (bbox['xmin'], bbox['ymin']),
                (bbox['xmax'], bbox['ymax']),
                color,
                2
            )
            
            # Prepare label text
            label = f"{class_name}: {confidence:.2f}"
            
            # Get text size for background rectangle
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Draw background rectangle for text
            cv2.rectangle(
                img,
                (bbox['xmin'], bbox['ymin'] - text_height - 10),
                (bbox['xmin'] + text_width, bbox['ymin']),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                img,
                label,
                (bbox['xmin'], bbox['ymin'] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save annotated image
        cv2.imwrite(str(output_path), img)
        
        return output_path
    
    def process_image(self, image_path, output_path):
        """
        Complete pipeline: detect objects and create annotated image
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path to save annotated image
            
        Returns:
            dict: Detection results with annotated image path
        """
        # Perform detection
        results = self.detect_objects(image_path)
        
        # Draw annotations if objects were detected
        if results['count'] > 0:
            annotated_path = self.draw_annotations(
                image_path, 
                results['detections'], 
                output_path
            )
            results['annotated_image'] = annotated_path
        else:
            results['annotated_image'] = None
        
        return results


# Singleton instance for reuse across requests
_detector_instance = None

def get_detector(model_name='yolov5s', confidence_threshold=0.25):
    """
    Get or create a singleton ObjectDetector instance
    
    Args:
        model_name (str): YOLOv5 model variant
        confidence_threshold (float): Confidence threshold for detections
        
    Returns:
        ObjectDetector: Singleton detector instance
    """
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = ObjectDetector(model_name, confidence_threshold)
    return _detector_instance


# ==================== REAL-TIME SECURITY MONITORING ====================

class SecurityCamera:
    """
    Real-time security camera monitoring with YOLOv5 object detection
    Captures frames, detects objects, and logs security events
    """
    
    def __init__(self, camera_source=0, detector=None, target_classes=None, 
                 snapshot_dir='media/security/snapshots', log_file='media/security/detection_log.json'):
        """
        Initialize security camera system
        
        Args:
            camera_source (int or str): Camera index (0 for default webcam) or IP camera URL
            detector (ObjectDetector): Pre-initialized detector instance
            target_classes (list): List of object classes to detect (e.g., ['person', 'car', 'dog'])
            snapshot_dir (str): Directory to save security snapshots
            log_file (str): Path to detection log file
        """
        self.camera_source = camera_source
        self.detector = detector or get_detector()
        
        # Target classes for security monitoring
        self.target_classes = target_classes or ['person', 'car', 'dog', 'cat', 'truck', 'motorcycle']
        
        # File paths
        self.snapshot_dir = snapshot_dir
        self.log_file = log_file
        
        # Ensure directories exist
        os.makedirs(snapshot_dir, exist_ok=True)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Camera and detection state
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.annotated_frame = None
        self.latest_detections = []
        self.frame_lock = Lock()
        
        # Statistics
        self.total_detections = 0
        self.person_count = 0
        
    def connect_camera(self):
        """
        Connect to camera source (webcam, IP camera, or video file)
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Determine if source is a file path
            is_file = isinstance(self.camera_source, str) and (
                self.camera_source.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))
            )
            
            self.camera = cv2.VideoCapture(self.camera_source)
            
            # Set camera properties (only for live cameras, not files)
            if not is_file:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.camera.isOpened():
                print(f"Failed to open source: {self.camera_source}")
                return False
            
            source_type = "video file" if is_file else "camera"
            print(f"Connected to {source_type}: {self.camera_source}")
            return True
            
        except Exception as e:
            print(f"Error connecting to camera: {str(e)}")
            return False
    
    def disconnect_camera(self):
        """Release camera resources"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("📹 Camera disconnected")
    
    def detect_frame(self, frame):
        """
        Run object detection on a single frame
        
        Args:
            frame (numpy.ndarray): Video frame from camera
            
        Returns:
            dict: Detection results with filtered target classes
        """
        if self.detector.model is None:
            return {'detections': [], 'count': 0}
        
        # Run inference on frame
        results = self.detector.model(frame)
        
        # Extract detections
        detections = []
        df = results.pandas().xyxy[0]
        
        for _, row in df.iterrows():
            class_name = row['name']
            
            # Filter by target classes for security monitoring
            if class_name in self.target_classes:
                detection = {
                    'class': class_name,
                    'confidence': float(row['confidence']),
                    'bbox': {
                        'xmin': int(row['xmin']),
                        'ymin': int(row['ymin']),
                        'xmax': int(row['xmax']),
                        'ymax': int(row['ymax'])
                    },
                    'timestamp': datetime.now().isoformat()
                }
                detections.append(detection)
        
        return {
            'detections': detections,
            'count': len(detections),
            'timestamp': datetime.now().isoformat()
        }
    
    def annotate_frame(self, frame, detections):
        """
        Draw bounding boxes and labels on video frame
        
        Args:
            frame (numpy.ndarray): Original frame
            detections (list): List of detection dictionaries
            
        Returns:
            numpy.ndarray: Annotated frame
        """
        annotated = frame.copy()
        
        # Color mapping for different classes
        class_colors = {
            'person': (0, 255, 0),      # Green - High priority
            'car': (255, 0, 0),         # Blue
            'dog': (0, 255, 255),       # Yellow
            'cat': (255, 255, 0),       # Cyan
            'truck': (255, 0, 255),     # Magenta
            'motorcycle': (0, 165, 255) # Orange
        }
        
        for det in detections:
            bbox = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Get color for this class
            color = class_colors.get(class_name, (0, 255, 0))
            
            # Draw bounding box (thicker for person detection)
            thickness = 3 if class_name == 'person' else 2
            cv2.rectangle(
                annotated,
                (bbox['xmin'], bbox['ymin']),
                (bbox['xmax'], bbox['ymax']),
                color,
                thickness
            )
            
            # Prepare label
            label = f"{class_name.upper()}: {confidence:.2f}"
            
            # Draw label background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            cv2.rectangle(
                annotated,
                (bbox['xmin'], bbox['ymin'] - text_height - 10),
                (bbox['xmin'] + text_width, bbox['ymin']),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (bbox['xmin'], bbox['ymin'] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )
        
        # Add timestamp and statistics overlay
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            annotated,
            f"Security Monitor | {timestamp}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        # Detection count
        cv2.putText(
            annotated,
            f"Detections: {len(detections)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        return annotated
    
    def save_snapshot(self, frame, detections):
        """
        Save snapshot when security event detected
        
        Args:
            frame (numpy.ndarray): Frame to save
            detections (list): Detection information
            
        Returns:
            str: Path to saved snapshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filename with detection info
        detected_classes = "_".join([d['class'] for d in detections[:3]])
        filename = f"snapshot_{timestamp}_{detected_classes}.jpg"
        filepath = os.path.join(self.snapshot_dir, filename)
        
        # Save annotated frame
        cv2.imwrite(filepath, frame)
        print(f"📸 Snapshot saved: {filename}")
        
        return filepath
    
    def log_detection(self, detections, snapshot_path=None):
        """
        Log detection event to JSON file
        
        Args:
            detections (list): Detection information
            snapshot_path (str): Path to saved snapshot (if any)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'detection_count': len(detections),
            'detections': detections,
            'snapshot': snapshot_path,
            'camera_source': str(self.camera_source)
        }
        
        # Read existing log
        log_data = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
        
        # Append new entry
        log_data.append(log_entry)
        
        # Keep only last 1000 entries to prevent file bloat
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        # Write back to file
        with open(self.log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def process_frame(self, frame):
        """
        Process a single frame: detect, annotate, log, and save if needed
        
        Args:
            frame (numpy.ndarray): Video frame
            
        Returns:
            dict: Processing results
        """
        # Detect objects in frame
        results = self.detect_frame(frame)
        detections = results['detections']
        
        # Annotate frame with bounding boxes
        annotated = self.annotate_frame(frame, detections)
        
        # Update shared state (thread-safe)
        with self.frame_lock:
            self.current_frame = frame.copy()
            self.annotated_frame = annotated.copy()
            self.latest_detections = detections
        
        # Auto-save snapshot if person detected
        snapshot_path = None
        if any(d['class'] == 'person' for d in detections):
            snapshot_path = self.save_snapshot(annotated, detections)
            self.person_count += 1
        
        # Log detection event
        if len(detections) > 0:
            self.log_detection(detections, snapshot_path)
            self.total_detections += len(detections)
        
        return {
            'detections': detections,
            'count': len(detections),
            'snapshot': snapshot_path,
            'timestamp': results['timestamp']
        }
    
    def get_frame_for_streaming(self):
        """
        Get current annotated frame for web streaming
        
        Returns:
            bytes: JPEG encoded frame for HTTP response
        """
        with self.frame_lock:
            if self.annotated_frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', self.annotated_frame)
                if ret:
                    return buffer.tobytes()
        return None
    
    def get_latest_detections(self):
        """
        Get latest detection results in structured format
        
        Returns:
            dict: Detection data for frontend display
        """
        with self.frame_lock:
            return {
                'detections': self.latest_detections,
                'count': len(self.latest_detections),
                'total_detections': self.total_detections,
                'person_count': self.person_count,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_monitoring(self, frame_skip=2):
        """
        Main monitoring loop - runs continuously
        
        Args:
            frame_skip (int): Process every Nth frame for performance
        """
        self.is_running = True
        frame_count = 0
        
        print("🔒 Security monitoring started")
        
        while self.is_running:
            if self.camera is None or not self.camera.isOpened():
                print("⚠️ Camera not available")
                break
            
            # Read frame from camera
            ret, frame = self.camera.read()
            
            if not ret:
                print("⚠️ Failed to read frame")
                time.sleep(0.1)
                continue
            
            # Process frame (skip frames for performance)
            if frame_count % frame_skip == 0:
                self.process_frame(frame)
            else:
                # Still update current frame for streaming
                with self.frame_lock:
                    self.current_frame = frame.copy()
                    if self.annotated_frame is None:
                        self.annotated_frame = frame.copy()
            
            frame_count += 1
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
        
        print("🔒 Security monitoring stopped")
    
    def start_monitoring_thread(self):
        """Start monitoring in background thread"""
        if not self.connect_camera():
            return False
        
        self.is_running = True
        monitor_thread = Thread(target=self.run_monitoring, daemon=True)
        monitor_thread.start()
        
        return True
    
    def stop_monitoring(self):
        """Stop monitoring and release resources"""
        self.is_running = False
        time.sleep(0.5)  # Allow thread to finish
        self.disconnect_camera()


# Global security camera instance
_security_camera = None

def get_security_camera(camera_source=0, target_classes=None):
    """
    Get or create singleton SecurityCamera instance
    
    Args:
        camera_source (int or str): Camera source
        target_classes (list): Target object classes
        
    Returns:
        SecurityCamera: Security camera instance
    """
    global _security_camera
    if _security_camera is None:
        detector = get_detector()
        _security_camera = SecurityCamera(
            camera_source=camera_source,
            detector=detector,
            target_classes=target_classes
        )
    return _security_camera

