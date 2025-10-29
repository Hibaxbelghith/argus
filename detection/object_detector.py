"""
YOLOv5 Object Detection Module
Handles image upload, object detection, and annotated image generation
"""
import torch
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import os


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
