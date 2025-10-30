from django.test import TestCase, Client
from django.urls import reverse
from .models import DetectionEvent, CameraSettings
from datetime import datetime


class DetectionModelsTestCase(TestCase):
    """Tests pour les modèles de détection"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.camera_settings = CameraSettings.objects.create(
            name='Test Camera',
            camera_index=0,
            enable_motion_detection=True,
            enable_face_detection=True,
            motion_threshold=25,
            min_contour_area=500,
            save_images=True,
            detection_interval=1,
            is_active=True
        )
        
        self.detection_event = DetectionEvent.objects.create(
            detection_type='motion',
            confidence=0.85,
            faces_count=0,
            motion_intensity=0.75,
            location='Test Location',
            is_active=True
        )
    
    def test_camera_settings_creation(self):
        """Test de création des paramètres de caméra"""
        self.assertEqual(self.camera_settings.name, 'Test Camera')
        self.assertTrue(self.camera_settings.enable_motion_detection)
        self.assertTrue(self.camera_settings.enable_face_detection)
    
    def test_detection_event_creation(self):
        """Test de création d'un événement de détection"""
        self.assertEqual(self.detection_event.detection_type, 'motion')
        self.assertEqual(self.detection_event.faces_count, 0)
        self.assertAlmostEqual(self.detection_event.motion_intensity, 0.75)
    
    def test_detection_event_str(self):
        """Test de la représentation string d'un événement"""
        self.assertIn('Détection de Mouvement', str(self.detection_event))


class DetectionViewsTestCase(TestCase):
    """Tests pour les vues de détection"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = Client()
    
    def test_index_view(self):
        """Test de la page d'accueil"""
        response = self.client.get(reverse('detection:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Détection en Temps Réel')
    
    def test_events_list_view(self):
        """Test de la page d'historique"""
        response = self.client.get(reverse('detection:events_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_statistics_view(self):
        """Test de la page de statistiques"""
        response = self.client.get(reverse('detection:statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Statistiques')
    
    def test_settings_view(self):
        """Test de la page de paramètres"""
        response = self.client.get(reverse('detection:settings'))
        self.assertEqual(response.status_code, 200)
    
    def test_detection_status_api(self):
        """Test de l'API de statut"""
        response = self.client.get(reverse('detection:detection_status'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('is_running', data)
        self.assertIn('motion_detected', data)
        self.assertIn('faces_detected', data)
    
    def test_events_api(self):
        """Test de l'API des événements"""
        # Créer quelques événements
        DetectionEvent.objects.create(
            detection_type='face',
            faces_count=2,
            motion_intensity=0.5
        )
        
        response = self.client.get(reverse('detection:events_api'))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('events', data)
    
    def test_update_settings(self):
        """Test de mise à jour des paramètres"""
        response = self.client.post(
            reverse('detection:update_settings'),
            {
                'enable_motion': 'true',
                'enable_face': 'false'
            }
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')


class DetectionDetectorTestCase(TestCase):
    """Tests pour le détecteur de mouvement"""
    
    def test_detector_initialization(self):
        """Test d'initialisation du détecteur"""
        from .detector import MotionDetector
        
        detector = MotionDetector(camera_index=0)
        self.assertEqual(detector.camera_index, 0)
        self.assertIsNotNone(detector.face_cascade)
        self.assertTrue(detector.enable_motion_detection)
        self.assertTrue(detector.enable_face_detection)
    
    def test_detector_settings(self):
        """Test de chargement des paramètres"""
        from .detector import MotionDetector
        
        # Créer des paramètres
        CameraSettings.objects.create(
            name='Test',
            camera_index=1,
            enable_motion_detection=False,
            enable_face_detection=True,
            motion_threshold=30,
            is_active=True
        )
        
        detector = MotionDetector()
        detector.load_settings()
        
        self.assertEqual(detector.camera_index, 1)
        self.assertFalse(detector.enable_motion_detection)
        self.assertTrue(detector.enable_face_detection)
        self.assertEqual(detector.motion_threshold, 30)
