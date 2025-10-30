"""
Celery Configuration for Periodic Tasks
Compatible with or without Celery - can run manually
"""
from django.utils import timezone
from datetime import timedelta
import logging

# Conditional Celery import - works even without Celery installed
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    # Fallback decorator if Celery not installed
    def shared_task(func):
        func.delay = lambda *args, **kwargs: func(*args, **kwargs)
        return func
    CELERY_AVAILABLE = False

logger = logging.getLogger(__name__)


@shared_task
def generate_daily_analytics():
    """
    Generate daily analytics for all active users
    Run daily at midnight
    """
    from analytics.services import AnalyticsEngine
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        try:
            AnalyticsEngine.generate_period_analytics(user, 'daily')
            logger.info(f"Daily analytics generated for {user.username}")
        except Exception as e:
            logger.error(f"Failed to generate analytics for {user.username}: {e}")


@shared_task
def generate_weekly_analytics():
    """
    Generate weekly analytics for all active users
    Run weekly on Mondays
    """
    from analytics.services import AnalyticsEngine
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        try:
            AnalyticsEngine.generate_period_analytics(user, 'weekly')
            logger.info(f"Weekly analytics generated for {user.username}")
        except Exception as e:
            logger.error(f"Failed to generate weekly analytics for {user.username}: {e}")


@shared_task
def generate_predictive_alerts_task():
    """
    Generate predictive alerts for all active users
    Run daily at 6 AM
    """
    from notifications.predictive_alerts import PredictiveAlertEngine
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        try:
            engine = PredictiveAlertEngine(user)
            alerts_data = engine.generate_predictive_alerts()
            created_alerts = engine.save_predictive_alerts(alerts_data)
            
            logger.info(f"Generated {len(created_alerts)} predictive alerts for {user.username}")
        except Exception as e:
            logger.error(f"Failed to generate predictive alerts for {user.username}: {e}")


@shared_task
def send_daily_digest():
    """
    Send daily notification digest to users
    Run daily at 9 AM
    """
    from notifications.behavioral_learning import NotificationOptimizer
    from notifications.models import Notification
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    yesterday = timezone.now() - timedelta(days=1)
    
    for user in User.objects.filter(is_active=True):
        try:
            # Get unread notifications from yesterday
            notifications = Notification.objects.filter(
                user=user,
                created_at__gte=yesterday,
                read_at__isnull=True
            )
            
            if notifications.count() > 0:
                digest = NotificationOptimizer.create_digest(user, list(notifications))
                
                # TODO: Send digest via email
                logger.info(f"Daily digest created for {user.username}: {digest['total_notifications']} notifications")
        
        except Exception as e:
            logger.error(f"Failed to send digest for {user.username}: {e}")


@shared_task
def cleanup_old_notifications():
    """
    Clean up old read notifications
    Run weekly
    """
    from notifications.models import Notification
    
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Notification.objects.filter(
        read_at__isnull=False,
        created_at__lt=cutoff_date,
        severity='low'
    ).delete()[0]
    
    logger.info(f"Deleted {deleted_count} old notifications")


@shared_task
def evaluate_prediction_accuracy():
    """
    Evaluate accuracy of past predictions
    Run daily
    """
    from notifications.predictive_alerts import PredictiveAlertEngine
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        try:
            engine = PredictiveAlertEngine(user)
            accuracy = engine.evaluate_prediction_accuracy()
            
            if accuracy['total_predictions'] > 0:
                logger.info(f"Prediction accuracy for {user.username}: {accuracy['accuracy_rate']*100:.1f}%")
        
        except Exception as e:
            logger.error(f"Failed to evaluate predictions for {user.username}: {e}")
