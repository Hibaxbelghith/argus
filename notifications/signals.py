"""
Django signals for notifications module
Automatically create notifications from security alerts
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from analytics.models import SecurityAlert
from .services import NotificationService


@receiver(post_save, sender=SecurityAlert)
def create_notification_from_alert(sender, instance, created, **kwargs):
    """
    Automatically create notification when a security alert is created
    """
    if created:
        try:
            NotificationService.create_notification_from_alert(instance)
        except Exception as e:
            print(f"Error creating notification from alert: {e}")
