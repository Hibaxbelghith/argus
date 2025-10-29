"""
Django signals for analytics module
Automatically process detections when they are created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from detection.models import DetectionResult
from .services import AnalyticsEngine, SecurityAlertService


@receiver(post_save, sender=DetectionResult)
def process_detection_analytics(sender, instance, created, **kwargs):
    """
    Process analytics and alerts when a new detection is created
    """
    if created and instance.objects_detected > 0:
        # Analyser la détection pour les alertes de sécurité
        SecurityAlertService.analyze_detection(instance)
        
        # Mettre à jour les tendances d'objets
        try:
            AnalyticsEngine.update_object_trends(instance.user)
        except Exception as e:
            print(f"Error updating object trends: {e}")
        
        # Générer les analytics quotidiens
        try:
            AnalyticsEngine.generate_period_analytics(
                instance.user, 
                period_type='daily'
            )
        except Exception as e:
            print(f"Error generating analytics: {e}")
