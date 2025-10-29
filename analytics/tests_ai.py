"""
Tests pour l'API IA et le système de recommandations
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

from analytics.models import AIRecommendation, ObjectTrend, SecurityAlert
from analytics.ai_recommendation_system import RecommendationEngine, SmartRecommendationFilter
from detection.models import DetectionResult

User = get_user_model()


class RecommendationEngineTestCase(TestCase):
    """Tests pour le moteur de recommandations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_recommendation_engine_initialization(self):
        """Test l'initialisation du moteur"""
        engine = RecommendationEngine(self.user)
        self.assertEqual(engine.user, self.user)
        self.assertEqual(len(engine.recommendations), 0)
    
    def test_analyze_and_recommend(self):
        """Test la génération de recommandations"""
        engine = RecommendationEngine(self.user)
        recommendations = engine.analyze_and_recommend(days=30)
        
        # Should return a list
        self.assertIsInstance(recommendations, list)
        
        # Each recommendation should have required fields
        if recommendations:
            rec = recommendations[0]
            self.assertIn('type', rec)
            self.assertIn('priority', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('action', rec)
            self.assertIn('confidence', rec)
    
    def test_smart_filter(self):
        """Test le filtrage intelligent"""
        recommendations = [
            {
                'type': 'security',
                'priority': 5,
                'title': 'Test 1',
                'confidence': 0.9,
                'description': 'Test',
                'action': 'Test action'
            },
            {
                'type': 'optimization',
                'priority': 3,
                'title': 'Test 2',
                'confidence': 0.5,  # Below threshold
                'description': 'Test',
                'action': 'Test action'
            }
        ]
        
        filtered = SmartRecommendationFilter.filter_recommendations(
            recommendations,
            max_count=10,
            min_confidence=0.6
        )
        
        # Should filter out low confidence
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['title'], 'Test 1')
    
    def test_group_by_type(self):
        """Test le groupement par type"""
        recommendations = [
            {'type': 'security', 'title': 'Security 1'},
            {'type': 'security', 'title': 'Security 2'},
            {'type': 'optimization', 'title': 'Optimization 1'}
        ]
        
        grouped = SmartRecommendationFilter.group_by_type(recommendations)
        
        self.assertEqual(len(grouped['security']), 2)
        self.assertEqual(len(grouped['optimization']), 1)


class AIRecommendationModelTestCase(TestCase):
    """Tests pour le modèle AIRecommendation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_recommendation(self):
        """Test la création d'une recommandation"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test Recommendation',
            description='Test description',
            action='Test action',
            confidence=0.95,
            impact='high'
        )
        
        self.assertEqual(rec.user, self.user)
        self.assertEqual(rec.status, 'pending')
        self.assertEqual(rec.confidence, 0.95)
    
    def test_mark_viewed(self):
        """Test le marquage comme vu"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test',
            description='Test',
            action='Test',
            confidence=0.9
        )
        
        rec.mark_viewed()
        self.assertEqual(rec.status, 'viewed')
        self.assertIsNotNone(rec.viewed_at)
    
    def test_mark_acted(self):
        """Test le marquage comme traité"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test',
            description='Test',
            action='Test',
            confidence=0.9
        )
        
        rec.mark_acted()
        self.assertEqual(rec.status, 'acted')
        self.assertIsNotNone(rec.acted_at)
    
    def test_set_feedback(self):
        """Test l'enregistrement du feedback"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test',
            description='Test',
            action='Test',
            confidence=0.9
        )
        
        rec.set_feedback(True, 'Very helpful!')
        self.assertTrue(rec.was_helpful)
        self.assertEqual(rec.user_feedback, 'Very helpful!')
    
    def test_metadata_json(self):
        """Test la gestion des métadonnées JSON"""
        rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test',
            description='Test',
            action='Test',
            confidence=0.9
        )
        
        metadata = {
            'key1': 'value1',
            'key2': 'value2',
            'nested': {'key3': 'value3'}
        }
        
        rec.set_metadata(metadata)
        retrieved = rec.get_metadata()
        
        self.assertEqual(retrieved, metadata)


class AIAPITestCase(TestCase):
    """Tests pour l'API IA"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_ai_recommendations_endpoint(self):
        """Test l'endpoint de recommandations"""
        url = reverse('analytics:ai_recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('recommendations', data['data'])
    
    def test_ai_dashboard_endpoint(self):
        """Test l'endpoint du dashboard IA"""
        url = reverse('analytics:ai_dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('health', data['data'])
        self.assertIn('score', data['data']['health'])
    
    def test_save_recommendation_endpoint(self):
        """Test l'enregistrement d'une recommandation"""
        url = reverse('analytics:ai_save_recommendation')
        
        payload = {
            'recommendation_type': 'security',
            'priority': 5,
            'title': 'Test Recommendation',
            'description': 'Test description',
            'action': 'Test action',
            'confidence': 0.95,
            'impact': 'high',
            'metadata': {'test': 'data'}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        # Verify it was created
        self.assertTrue(
            AIRecommendation.objects.filter(
                user=self.user,
                title='Test Recommendation'
            ).exists()
        )
    
    def test_list_saved_recommendations(self):
        """Test la liste des recommandations sauvegardées"""
        # Create test recommendations
        AIRecommendation.objects.create(
            user=self.user,
            recommendation_type='security',
            priority=5,
            title='Test 1',
            description='Test',
            action='Test',
            confidence=0.9
        )
        
        url = reverse('analytics:ai_list_saved_recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertGreater(len(data['data']['recommendations']), 0)
    
    def test_risk_assessment_endpoint(self):
        """Test l'endpoint d'évaluation des risques"""
        url = reverse('analytics:ai_risk_assessment')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('risk_score', data['data'])
        self.assertIn('risk_level', data['data'])
    
    def test_unauthorized_access(self):
        """Test l'accès non autorisé"""
        self.client.logout()
        
        url = reverse('analytics:ai_recommendations')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["analytics.tests_ai"])
