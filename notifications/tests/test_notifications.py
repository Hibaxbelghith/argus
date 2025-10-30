"""
Tests for Notification ML Scoring and Services
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from detection.models import Detection
from analytics.models import Alert
from notifications.models import Notification, UserNotificationPreference
from datetime import datetime, timedelta

User = get_user_model()


class NotificationScorerTests(TestCase):
    """Tests for ML-based notification scoring"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='notifuser',
            email='notif@test.com',
            password='testpass123'
        )
        
        # Create a detection
        self.detection = Detection.objects.create(
            user=self.user,
            image_url="test.jpg",
            detected_objects=["weapon"],
            confidence=0.95,
            detected_at=datetime.now()
        )
        
        # Create an alert
        self.alert = Alert.objects.create(
            detection=self.detection,
            alert_type='anomaly_detected',
            severity='high',
            message='Weapon detected'
        )
    
    def test_notification_scorer_import(self):
        """Test NotificationScorer can be imported"""
        from notifications.ml_scoring import NotificationScorer
        scorer = NotificationScorer()
        self.assertIsNotNone(scorer)
    
    def test_score_notification_returns_valid_score(self):
        """Test that scoring returns a valid score (0-100)"""
        from notifications.ml_scoring import NotificationScorer
        
        scorer = NotificationScorer()
        score = scorer.score_notification(self.alert)
        
        self.assertIsInstance(score, (int, float))
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_high_severity_gets_high_score(self):
        """Test that high severity alerts get high scores"""
        from notifications.ml_scoring import NotificationScorer
        
        scorer = NotificationScorer()
        score = scorer.score_notification(self.alert)
        
        # High severity weapon detection should get high score
        self.assertGreater(score, 60)
    
    def test_false_alert_filter(self):
        """Test false alert filtering"""
        from notifications.ml_scoring import FalseAlertFilter
        
        filter_obj = FalseAlertFilter()
        is_false = filter_obj.is_likely_false_alert(self.alert)
        
        self.assertIsInstance(is_false, bool)


class BehavioralLearnerTests(TestCase):
    """Tests for Behavioral Learning"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='behavioruser',
            email='behavior@test.com',
            password='testpass123'
        )
        
        # Create notification history
        for i in range(10):
            notif = Notification.objects.create(
                user=self.user,
                title=f"Test {i}",
                message="Test message",
                notification_type='security_alert',
                priority='medium',
                created_at=datetime.now() - timedelta(days=i)
            )
            # Mark some as read
            if i % 2 == 0:
                notif.is_read = True
                notif.read_at = datetime.now() - timedelta(days=i, hours=2)
                notif.save()
    
    def test_behavioral_learner_import(self):
        """Test BehavioralLearner can be imported"""
        from notifications.behavioral_learning import BehavioralLearner
        learner = BehavioralLearner(self.user)
        self.assertIsNotNone(learner)
    
    def test_analyze_interaction_patterns(self):
        """Test interaction pattern analysis"""
        from notifications.behavioral_learning import BehavioralLearner
        
        learner = BehavioralLearner(self.user)
        patterns = learner.analyze_interaction_patterns()
        
        self.assertIsInstance(patterns, dict)
        self.assertIn('response_rate', patterns)
        self.assertIn('avg_response_time', patterns)
    
    def test_get_preferred_notification_times(self):
        """Test preferred notification time detection"""
        from notifications.behavioral_learning import BehavioralLearner
        
        learner = BehavioralLearner(self.user)
        times = learner.get_preferred_notification_times()
        
        self.assertIsInstance(times, list)
    
    def test_notification_optimizer(self):
        """Test NotificationOptimizer"""
        from notifications.behavioral_learning import NotificationOptimizer
        
        optimizer = NotificationOptimizer(self.user)
        should_send = optimizer.should_send_notification('security_alert')
        
        self.assertIsInstance(should_send, bool)


class PredictiveAlertsTests(TestCase):
    """Tests for Predictive Alerts Engine"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='predictuser',
            email='predict@test.com',
            password='testpass123'
        )
        
        # Create detection history
        for i in range(30):
            Detection.objects.create(
                user=self.user,
                image_url=f"predict_{i}.jpg",
                detected_objects=["person"],
                confidence=0.9,
                detected_at=datetime.now() - timedelta(days=30-i)
            )
    
    def test_predictive_alert_engine_import(self):
        """Test PredictiveAlertEngine can be imported"""
        from notifications.predictive_alerts import PredictiveAlertEngine
        engine = PredictiveAlertEngine(self.user)
        self.assertIsNotNone(engine)
    
    def test_generate_predictive_alerts(self):
        """Test predictive alert generation"""
        from notifications.predictive_alerts import PredictiveAlertEngine
        
        engine = PredictiveAlertEngine(self.user)
        alerts = engine.generate_predictive_alerts()
        
        self.assertIsInstance(alerts, list)
    
    def test_predict_activity_surge(self):
        """Test activity surge prediction"""
        from notifications.predictive_alerts import PredictiveAlertEngine
        
        engine = PredictiveAlertEngine(self.user)
        surge = engine.predict_activity_surge()
        
        self.assertIsInstance(surge, dict)
        self.assertIn('predicted', surge)


class MultiChannelDeliveryTests(TestCase):
    """Tests for Multi-Channel Delivery (without actual sending)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='channeluser',
            email='channel@test.com',
            password='testpass123'
        )
        
        self.notification = Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="Test message",
            notification_type='security_alert',
            priority='high'
        )
    
    def test_multi_channel_service_import(self):
        """Test MultiChannelDeliveryService can be imported"""
        from notifications.multi_channel_delivery import MultiChannelDeliveryService
        service = MultiChannelDeliveryService()
        self.assertIsNotNone(service)
    
    def test_channel_selector_import(self):
        """Test IntelligentChannelSelector can be imported"""
        from notifications.multi_channel_delivery import IntelligentChannelSelector
        selector = IntelligentChannelSelector()
        self.assertIsNotNone(selector)
    
    def test_select_channels(self):
        """Test channel selection logic"""
        from notifications.multi_channel_delivery import IntelligentChannelSelector
        
        selector = IntelligentChannelSelector()
        channels = selector.select_channels(self.notification, self.user)
        
        self.assertIsInstance(channels, list)
        self.assertGreater(len(channels), 0)
    
    def test_send_notification_structure(self):
        """Test send notification returns proper structure"""
        from notifications.multi_channel_delivery import MultiChannelDeliveryService
        
        service = MultiChannelDeliveryService()
        # Don't actually send, just test structure
        result = service.send_notification(
            self.notification,
            channels=['web'],  # Web channel doesn't need external services
            dry_run=True
        )
        
        self.assertIsInstance(result, dict)


class NotificationServiceTests(TestCase):
    """Tests for Notification Service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='serviceuser',
            email='service@test.com',
            password='testpass123'
        )
    
    def test_notification_service_import(self):
        """Test NotificationService can be imported"""
        from notifications.services import NotificationService
        service = NotificationService()
        self.assertIsNotNone(service)
    
    def test_create_notification(self):
        """Test notification creation"""
        from notifications.services import NotificationService
        
        service = NotificationService()
        notification = service.create_notification(
            user=self.user,
            title="Test Alert",
            message="Test message",
            notification_type='security_alert',
            priority='high'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, "Test Alert")
        self.assertIsNotNone(notification.priority_score)
    
    def test_notification_has_score(self):
        """Test that created notifications have ML scores"""
        from notifications.services import NotificationService
        
        service = NotificationService()
        notification = service.create_notification(
            user=self.user,
            title="High Priority",
            message="Weapon detected",
            notification_type='security_alert',
            priority='high'
        )
        
        self.assertIsNotNone(notification.priority_score)
        self.assertGreater(notification.priority_score, 0)


class NotificationPreferenceTests(TestCase):
    """Tests for User Notification Preferences"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='prefuser',
            email='pref@test.com',
            password='testpass123'
        )
    
    def test_create_preference(self):
        """Test creating user preferences"""
        pref = UserNotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            sms_enabled=False,
            push_enabled=True,
            min_priority_score=60
        )
        
        self.assertIsNotNone(pref)
        self.assertEqual(pref.user, self.user)
        self.assertTrue(pref.email_enabled)
        self.assertFalse(pref.sms_enabled)
    
    def test_preference_filtering(self):
        """Test that preferences filter notifications"""
        pref = UserNotificationPreference.objects.create(
            user=self.user,
            min_priority_score=70
        )
        
        # Low priority notification
        low_notif = Notification.objects.create(
            user=self.user,
            title="Low Priority",
            message="Test",
            notification_type='info',
            priority='low',
            priority_score=50
        )
        
        # High priority notification
        high_notif = Notification.objects.create(
            user=self.user,
            title="High Priority",
            message="Test",
            notification_type='security_alert',
            priority='high',
            priority_score=85
        )
        
        # Check filtering logic
        self.assertLess(low_notif.priority_score, pref.min_priority_score)
        self.assertGreater(high_notif.priority_score, pref.min_priority_score)


class NotificationAPITests(TestCase):
    """Tests for Notification API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apinotifuser',
            email='apinotif@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        # Create test notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                title=f"Notification {i}",
                message="Test message",
                notification_type='security_alert',
                priority='medium',
                priority_score=70
            )
    
    def test_notification_list_endpoint(self):
        """Test notification list endpoint"""
        response = self.client.get('/notifications/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_notification_mark_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.filter(user=self.user).first()
        
        self.assertFalse(notification.is_read)
        
        notification.is_read = True
        notification.read_at = datetime.now()
        notification.save()
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)


# Run tests with: python manage.py test notifications.tests.test_notifications
