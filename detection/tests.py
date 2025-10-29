from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import DetectionResult

User = get_user_model()


class DetectionResultModelTest(TestCase):
    """Test cases for DetectionResult model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_detection_result_creation(self):
        """Test creating a detection result"""
        detection = DetectionResult.objects.create(
            user=self.user,
            objects_detected=3
        )
        self.assertEqual(detection.user, self.user)
        self.assertEqual(detection.objects_detected, 3)
    
    def test_detection_data_methods(self):
        """Test JSON data storage and retrieval"""
        detection = DetectionResult.objects.create(user=self.user)
        test_data = [
            {'class': 'person', 'confidence': 0.95},
            {'class': 'car', 'confidence': 0.87}
        ]
        detection.set_detection_data(test_data)
        detection.save()
        
        retrieved_data = detection.get_detection_data()
        self.assertEqual(len(retrieved_data), 2)
        self.assertEqual(retrieved_data[0]['class'], 'person')
