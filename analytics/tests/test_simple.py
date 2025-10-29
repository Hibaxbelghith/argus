"""
Tests Simples pour Analytics ML Models
Adaptés aux modèles réels du projet
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from detection.models import DetectionResult
from analytics.models import DetectionAnalytics
from datetime import datetime, timedelta
import json

User = get_user_model()


class MLModelsImportTests(TestCase):
    """Tests d'import des modules ML"""
    
    def test_anomaly_detector_import(self):
        """Test que AnomalyDetector peut être importé"""
        from analytics.ml_models import AnomalyDetector
        detector = AnomalyDetector()
        self.assertIsNotNone(detector)
    
    def test_trend_analyzer_import(self):
        """Test que TrendAnalyzer peut être importé"""
        from analytics.ml_models import TrendAnalyzer
        analyzer = TrendAnalyzer()
        self.assertIsNotNone(analyzer)
    
    def test_pattern_recognizer_import(self):
        """Test que PatternRecognizer peut être importé"""
        from analytics.pattern_recognition import PatternRecognizer
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test123')
        recognizer = PatternRecognizer(user)
        self.assertIsNotNone(recognizer)
    
    def test_chart_generator_import(self):
        """Test que ChartGenerator peut être importé"""
        from analytics.visualizations import ChartGenerator
        generator = ChartGenerator()
        self.assertIsNotNone(generator)


class BasicFunctionalityTests(TestCase):
    """Tests de fonctionnalité de base"""
    
    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def create_detection(self, objects_list, confidence=0.9):
        """Helper pour créer une détection"""
        # Créer une fausse image
        image = SimpleUploadedFile(
            "test.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        
        detection_data = [{
            'class': obj,
            'confidence': confidence,
            'box': [0, 0, 100, 100]
        } for obj in objects_list]
        
        detection = DetectionResult.objects.create(
            user=self.user,
            original_image=image,
            objects_detected=len(objects_list),
            detection_data=json.dumps(detection_data),
            uploaded_at=datetime.now()
        )
        return detection
    
    def test_create_detection(self):
        """Test création d'une détection"""
        detection = self.create_detection(['person', 'chair'])
        self.assertIsNotNone(detection)
        self.assertEqual(detection.objects_detected, 2)
    
    def test_detection_data_parsing(self):
        """Test parsing des données de détection"""
        detection = self.create_detection(['person'])
        data = detection.get_detection_data()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


class AnalyticsAPITests(TestCase):
    """Tests des endpoints API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_stats_summary_endpoint(self):
        """Test endpoint statistiques"""
        response = self.client.get('/analytics/api/stats/summary/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)


# Run tests with: py manage.py test analytics.tests.test_simple
