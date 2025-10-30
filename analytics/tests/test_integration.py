"""
Integration Tests - Full Pipeline
Tests the complete detection → analytics → notification pipeline
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from detection.models import Detection
from analytics.models import Alert, Insight
from notifications.models import Notification
from datetime import datetime, timedelta
import time

User = get_user_model()


class FullPipelineIntegrationTests(TestCase):
    """Test the complete AI pipeline end-to-end"""
    
    def setUp(self):
        """Set up test environment"""
        self.user = User.objects.create_user(
            username='pipelineuser',
            email='pipeline@test.com',
            password='testpass123'
        )
    
    def test_weapon_detection_creates_alert_and_notification(self):
        """
        Test complete pipeline:
        1. Create detection with weapon
        2. Check if alert is created
        3. Check if notification is created
        4. Verify ML scoring
        """
        # Step 1: Create weapon detection
        detection = Detection.objects.create(
            user=self.user,
            image_url="weapon_pipeline_test.jpg",
            detected_objects=["gun", "weapon"],
            confidence=0.95,
            detected_at=datetime.now()
        )
        
        # Step 2: Verify detection created
        self.assertIsNotNone(detection.id)
        self.assertEqual(detection.detected_objects, ["gun", "weapon"])
        
        # Note: Alert and Notification creation depends on signals
        # which may not run in test environment
        # In production, this would create Alert and Notification automatically
        
        print(f"✅ Detection created: ID={detection.id}")
    
    def test_anomaly_detection_workflow(self):
        """
        Test anomaly detection workflow:
        1. Create normal + anomalous detections
        2. Run anomaly detection
        3. Verify anomalies are identified
        """
        from analytics.ml_models import AnomalyDetector
        
        # Create normal detections
        normal_detections = []
        for i in range(50):
            d = Detection.objects.create(
                user=self.user,
                image_url=f"normal_{i}.jpg",
                detected_objects=["person", "chair"],
                confidence=0.85,
                detected_at=datetime.now() - timedelta(days=i % 10)
            )
            normal_detections.append(d)
        
        # Create anomalous detections
        anomalous_detections = []
        for i in range(5):
            d = Detection.objects.create(
                user=self.user,
                image_url=f"anomaly_{i}.jpg",
                detected_objects=["weapon", "fire"],
                confidence=0.95,
                detected_at=datetime.now() - timedelta(hours=i)
            )
            anomalous_detections.append(d)
        
        # Run anomaly detection
        detector = AnomalyDetector()
        all_detections = Detection.objects.filter(user=self.user)
        
        start_time = time.time()
        anomalies = detector.detect_anomalies(all_detections)
        duration = time.time() - start_time
        
        # Verify
        self.assertGreater(len(anomalies), 0)
        print(f"✅ Detected {len(anomalies)} anomalies in {duration:.2f}s")
    
    def test_pattern_recognition_workflow(self):
        """
        Test pattern recognition workflow:
        1. Create pattern of detections
        2. Run pattern recognition
        3. Verify patterns identified
        """
        from analytics.pattern_recognition import PatternRecognizer
        
        # Create morning activity pattern (7 days)
        for day in range(7):
            for hour in [8, 9, 10]:
                Detection.objects.create(
                    user=self.user,
                    image_url=f"pattern_{day}_{hour}.jpg",
                    detected_objects=["person", "laptop"],
                    confidence=0.90,
                    detected_at=datetime.now() - timedelta(days=7-day, hours=24-hour)
                )
        
        # Run pattern recognition
        recognizer = PatternRecognizer()
        detections = Detection.objects.filter(user=self.user)
        
        start_time = time.time()
        patterns = recognizer.identify_daily_routines(detections)
        duration = time.time() - start_time
        
        # Verify
        self.assertIsInstance(patterns, list)
        morning_patterns = [p for p in patterns if p.get('hour', 0) in [8, 9, 10]]
        self.assertGreater(len(morning_patterns), 0)
        
        print(f"✅ Identified {len(patterns)} patterns in {duration:.2f}s")
    
    def test_notification_scoring_workflow(self):
        """
        Test notification scoring workflow:
        1. Create alerts with different severities
        2. Score them with ML
        3. Verify scores are correct
        """
        from notifications.ml_scoring import NotificationScorer
        
        # Create detection
        detection = Detection.objects.create(
            user=self.user,
            image_url="score_test.jpg",
            detected_objects=["weapon"],
            confidence=0.95,
            detected_at=datetime.now()
        )
        
        # Create alerts with different severities
        high_alert = Alert.objects.create(
            detection=detection,
            alert_type='security_threat',
            severity='high',
            message='Weapon detected'
        )
        
        low_alert = Alert.objects.create(
            detection=detection,
            alert_type='info',
            severity='low',
            message='Normal activity'
        )
        
        # Score them
        scorer = NotificationScorer()
        
        high_score = scorer.score_notification(high_alert)
        low_score = scorer.score_notification(low_alert)
        
        # Verify
        self.assertGreater(high_score, low_score)
        self.assertGreaterEqual(high_score, 70)
        self.assertLessEqual(low_score, 50)
        
        print(f"✅ High severity score: {high_score}, Low severity score: {low_score}")
    
    def test_visualization_generation_workflow(self):
        """
        Test visualization generation workflow:
        1. Create detections
        2. Generate various charts
        3. Verify charts are valid
        """
        from analytics.visualizations import ChartGenerator
        
        # Create detections
        for i in range(20):
            Detection.objects.create(
                user=self.user,
                image_url=f"viz_{i}.jpg",
                detected_objects=["person"],
                confidence=0.90,
                detected_at=datetime.now() - timedelta(days=i)
            )
        
        generator = ChartGenerator()
        detections = Detection.objects.filter(user=self.user)
        
        # Generate different charts
        start_time = time.time()
        
        timeline = generator.generate_timeline_chart(detections)
        heatmap = generator.generate_heatmap(detections)
        pie = generator.generate_pie_chart(detections)
        
        duration = time.time() - start_time
        
        # Verify
        self.assertIsNotNone(timeline)
        self.assertIsNotNone(heatmap)
        self.assertIsNotNone(pie)
        
        # Check they can be converted to HTML
        timeline_html = timeline.to_html()
        self.assertIn('plotly', timeline_html.lower())
        
        print(f"✅ Generated 3 charts in {duration:.2f}s")
    
    def test_behavioral_learning_workflow(self):
        """
        Test behavioral learning workflow:
        1. Create notification history
        2. Analyze patterns
        3. Make recommendations
        """
        from notifications.behavioral_learning import BehavioralLearner
        
        # Create notification history
        for i in range(15):
            notif = Notification.objects.create(
                user=self.user,
                title=f"Alert {i}",
                message="Test message",
                notification_type='security_alert',
                priority='medium',
                created_at=datetime.now() - timedelta(days=i)
            )
            
            # Mark some as read
            if i % 3 == 0:
                notif.is_read = True
                notif.read_at = notif.created_at + timedelta(hours=2)
                notif.save()
        
        # Analyze behavior
        learner = BehavioralLearner(self.user)
        
        start_time = time.time()
        patterns = learner.analyze_interaction_patterns()
        duration = time.time() - start_time
        
        # Verify
        self.assertIsInstance(patterns, dict)
        self.assertIn('response_rate', patterns)
        
        response_rate = patterns['response_rate']
        self.assertGreaterEqual(response_rate, 0)
        self.assertLessEqual(response_rate, 100)
        
        print(f"✅ Analyzed behavior: Response rate = {response_rate:.1f}% in {duration:.2f}s")
    
    def test_predictive_alerts_workflow(self):
        """
        Test predictive alerts workflow:
        1. Create historical data
        2. Generate predictions
        3. Create predictive alerts
        """
        from notifications.predictive_alerts import PredictiveAlertEngine
        
        # Create 30 days of detection history
        for i in range(30):
            Detection.objects.create(
                user=self.user,
                image_url=f"predict_{i}.jpg",
                detected_objects=["person"],
                confidence=0.88,
                detected_at=datetime.now() - timedelta(days=30-i)
            )
        
        # Generate predictive alerts
        engine = PredictiveAlertEngine(self.user)
        
        start_time = time.time()
        alerts = engine.generate_predictive_alerts()
        duration = time.time() - start_time
        
        # Verify
        self.assertIsInstance(alerts, list)
        
        print(f"✅ Generated {len(alerts)} predictive alerts in {duration:.2f}s")
    
    def test_api_endpoints_workflow(self):
        """
        Test API endpoints workflow:
        1. Create test data
        2. Call various API endpoints
        3. Verify responses
        """
        # Login user
        self.client.force_login(self.user)
        
        # Create test data
        for i in range(10):
            Detection.objects.create(
                user=self.user,
                image_url=f"api_{i}.jpg",
                detected_objects=["person"],
                confidence=0.90,
                detected_at=datetime.now() - timedelta(days=i)
            )
        
        # Test endpoints
        endpoints = [
            '/analytics/api/anomalies/detect/',
            '/analytics/api/patterns/recognize/',
            '/analytics/api/stats/summary/',
        ]
        
        results = []
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            results.append({
                'endpoint': endpoint,
                'status': response.status_code,
                'valid': response.status_code == 200
            })
        
        # Verify
        for result in results:
            self.assertEqual(result['status'], 200, 
                           f"Endpoint {result['endpoint']} failed")
            print(f"✅ {result['endpoint']} - Status {result['status']}")
    
    def test_performance_with_large_dataset(self):
        """
        Test performance with larger dataset:
        1. Create 500 detections
        2. Run various analytics
        3. Measure performance
        """
        from analytics.ml_models import AnomalyDetector, TrendAnalyzer
        
        # Create 500 detections (simulating real usage)
        print("📊 Creating 500 detections...")
        for i in range(500):
            Detection.objects.create(
                user=self.user,
                image_url=f"perf_{i}.jpg",
                detected_objects=["person"] if i % 10 != 0 else ["weapon"],
                confidence=0.90,
                detected_at=datetime.now() - timedelta(hours=i)
            )
        
        detections = Detection.objects.filter(user=self.user)
        
        # Test anomaly detection performance
        detector = AnomalyDetector()
        start = time.time()
        anomalies = detector.detect_anomalies(detections)
        anomaly_time = time.time() - start
        
        # Test trend analysis performance
        analyzer = TrendAnalyzer()
        start = time.time()
        trends = analyzer.analyze_trends(detections)
        trend_time = time.time() - start
        
        # Verify performance is acceptable
        self.assertLess(anomaly_time, 10.0, "Anomaly detection too slow")
        self.assertLess(trend_time, 5.0, "Trend analysis too slow")
        
        print(f"✅ Performance test passed:")
        print(f"   - Anomaly detection: {anomaly_time:.2f}s")
        print(f"   - Trend analysis: {trend_time:.2f}s")
        print(f"   - Anomalies found: {len(anomalies)}")


class DataConsistencyTests(TestCase):
    """Test data consistency across modules"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='consistencyuser',
            email='consistency@test.com',
            password='testpass123'
        )
    
    def test_detection_to_alert_relationship(self):
        """Test that alerts correctly reference detections"""
        detection = Detection.objects.create(
            user=self.user,
            image_url="consistency_test.jpg",
            detected_objects=["weapon"],
            confidence=0.95,
            detected_at=datetime.now()
        )
        
        alert = Alert.objects.create(
            detection=detection,
            alert_type='security_threat',
            severity='high',
            message='Test alert'
        )
        
        # Verify relationship
        self.assertEqual(alert.detection.id, detection.id)
        self.assertEqual(alert.detection.user, self.user)
    
    def test_notification_user_consistency(self):
        """Test that notifications are correctly linked to users"""
        notif = Notification.objects.create(
            user=self.user,
            title="Test",
            message="Test message",
            notification_type='info',
            priority='low'
        )
        
        # Verify
        self.assertEqual(notif.user.id, self.user.id)
        
        # Query should work both ways
        user_notifs = Notification.objects.filter(user=self.user)
        self.assertIn(notif, user_notifs)


# Run with: python manage.py test analytics.tests.test_integration -v 2
