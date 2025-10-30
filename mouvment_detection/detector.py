import cv2
import numpy as np
import threading
import time
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from .models import DetectionEvent, CameraSettings


class MotionDetector:
    """
    Classe pour gérer la détection de mouvement et de visages en temps réel
    avec la caméra du laptop
    """
    
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None
        self.is_running = False
        self.frame = None
        self.previous_frame = None
        self.lock = threading.Lock()
        
        # Paramètres de détection
        self.motion_threshold = 25
        self.min_contour_area = 500
        self.enable_motion_detection = True
        self.enable_face_detection = True
        self.save_images = True
        self.detection_interval = 1
        self.last_detection_time = 0
        
        # Chargement du classificateur de visages Haar Cascade (gratuit et local)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Statistiques
        self.motion_detected = False
        self.faces_detected = 0
        self.last_motion_intensity = 0.0
        
    def initialize_camera(self):
        """Initialise la connexion à la caméra"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                raise Exception(f"Impossible d'ouvrir la caméra {self.camera_index}")
            
            # Configuration de la caméra
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la caméra: {e}")
            return False
    
    def release_camera(self):
        """Libère les ressources de la caméra"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def load_settings(self):
        """Charge les paramètres depuis la base de données"""
        try:
            settings = CameraSettings.objects.filter(is_active=True).first()
            if settings:
                self.camera_index = settings.camera_index
                self.enable_motion_detection = settings.enable_motion_detection
                self.enable_face_detection = settings.enable_face_detection
                self.motion_threshold = settings.motion_threshold
                self.min_contour_area = settings.min_contour_area
                self.save_images = settings.save_images
                self.detection_interval = settings.detection_interval
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")
    
    def detect_motion(self, frame):
        """
        Détecte le mouvement dans la frame actuelle
        Retourne: (motion_detected, motion_intensity, processed_frame)
        """
        if self.previous_frame is None:
            self.previous_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.previous_frame = cv2.GaussianBlur(self.previous_frame, (21, 21), 0)
            return False, 0.0, frame
        
        # Conversion en niveaux de gris et flou
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Calcul de la différence entre les frames
        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, self.motion_threshold, 255, cv2.THRESH_BINARY)[1]
        
        # Dilatation pour combler les trous
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Détection des contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        motion_intensity = 0.0
        
        for contour in contours:
            if cv2.contourArea(contour) < self.min_contour_area:
                continue
            
            motion_detected = True
            motion_intensity += cv2.contourArea(contour)
            
            # Dessiner un rectangle autour de la zone de mouvement
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Normaliser l'intensité du mouvement
        motion_intensity = min(motion_intensity / 100000, 1.0)
        
        # Mise à jour de la frame précédente
        self.previous_frame = gray
        
        return motion_detected, motion_intensity, frame
    
    def detect_faces(self, frame):
        """
        Détecte les visages dans la frame actuelle
        Retourne: (faces_count, processed_frame)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détection des visages
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Dessiner des rectangles autour des visages détectés
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, 'Visage', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        return len(faces), frame
    
    def save_detection_event(self, detection_type, faces_count=0, motion_intensity=0.0, frame=None):
        """Enregistre un événement de détection dans la base de données"""
        try:
            event = DetectionEvent(
                detection_type=detection_type,
                faces_count=faces_count,
                motion_intensity=motion_intensity,
                confidence=0.85  # Confiance par défaut
            )
            
            # Sauvegarder l'image si activé
            if self.save_images and frame is not None:
                # Convertir la frame OpenCV en image PIL
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Sauvegarder dans un buffer
                buffer = BytesIO()
                pil_image.save(buffer, format='JPEG')
                buffer.seek(0)
                
                # Créer le nom de fichier
                filename = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                event.image.save(filename, ContentFile(buffer.read()), save=False)
            
            event.save()
            return event
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'événement: {e}")
            return None
    
    def process_frame(self):
        """Traite une frame et effectue les détections"""
        if self.camera is None or not self.camera.isOpened():
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            return None
        
        original_frame = frame.copy()
        motion_detected = False
        faces_count = 0
        motion_intensity = 0.0
        
        # Détection de mouvement
        if self.enable_motion_detection:
            motion_detected, motion_intensity, frame = self.detect_motion(frame)
            self.motion_detected = motion_detected
            self.last_motion_intensity = motion_intensity
        
        # Détection de visages
        if self.enable_face_detection:
            faces_count, frame = self.detect_faces(frame)
            self.faces_detected = faces_count
        
        # Ajouter les informations sur la frame
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(frame, f'Heure: {current_time}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if self.enable_motion_detection:
            status = 'MOUVEMENT DETECTE' if motion_detected else 'Aucun mouvement'
            color = (0, 0, 255) if motion_detected else (0, 255, 0)
            cv2.putText(frame, status, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, f'Intensite: {motion_intensity:.2f}', (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if self.enable_face_detection:
            cv2.putText(frame, f'Visages: {faces_count}', (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Enregistrer l'événement si nécessaire
        current_timestamp = time.time()
        if (current_timestamp - self.last_detection_time) >= self.detection_interval:
            if motion_detected or faces_count > 0:
                detection_type = 'both' if (motion_detected and faces_count > 0) else \
                                ('motion' if motion_detected else 'face')
                self.save_detection_event(
                    detection_type=detection_type,
                    faces_count=faces_count,
                    motion_intensity=motion_intensity,
                    frame=original_frame
                )
                self.last_detection_time = current_timestamp
        
        with self.lock:
            self.frame = frame
        
        return frame
    
    def get_frame(self):
        """Retourne la dernière frame traitée"""
        with self.lock:
            return self.frame
    
    def generate_frames(self):
        """Générateur de frames pour le streaming vidéo"""
        while self.is_running:
            frame = self.process_frame()
            if frame is not None:
                # Encoder la frame en JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03)  # ~30 FPS
    
    def start(self):
        """Démarre la détection"""
        if not self.is_running:
            self.load_settings()
            if self.initialize_camera():
                self.is_running = True
                return True
        return False
    
    def stop(self):
        """Arrête la détection"""
        self.is_running = False
        self.release_camera()
        self.previous_frame = None


# Instance globale du détecteur
detector = MotionDetector()
