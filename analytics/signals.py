"""
Django Signals for Automatic Integration
Detection -> Analytics -> Notifications Pipeline
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from detection.models import DetectionResult
from .services import AnalyticsEngine, SecurityAlertService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DetectionResult)
def process_detection_analytics(sender, instance, created, **kwargs):
    """
    Process analytics and alerts when a new detection is created
    Enhanced with ML anomaly detection and intelligent notifications
    """
    print(f"🔔 SIGNAL TRIGGERED - Detection #{instance.id}, created={created}, objects={instance.objects_detected}")
    
    # Accepter si c'est une nouvelle détection OU si des objets viennent d'être détectés
    if instance.objects_detected == 0:
        print(f"❌ SIGNAL SKIPPED - No objects detected")
        return
    
    # Éviter de traiter plusieurs fois la même détection
    if not created and hasattr(instance, '_analytics_processed'):
        print(f"❌ SIGNAL SKIPPED - Already processed")
        return
    
    # Marquer comme traité
    instance._analytics_processed = True
    
    logger.info(f"Processing new detection: {instance.id}")
    
    try:
        # 1. Mettre à jour les analytics quotidiennes
        _update_analytics(instance)
        
        # 2. Analyser pour alertes de sécurité
        SecurityAlertService.analyze_detection(instance)
        
        # 3. Vérifier les anomalies ML
        _check_for_anomalies(instance)
        
        # 4. Analyser les objets suspects
        _analyze_suspicious_objects(instance)
        
        # 5. Mettre à jour les tendances
        _update_object_trends(instance)
        
    except Exception as e:
        logger.error(f"Error processing detection {instance.id}: {e}")


def _update_analytics(detection):
    """Met à jour les analytics quotidiennes"""
    from analytics.models import DetectionAnalytics
    
    try:
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        analytics, created = DetectionAnalytics.objects.get_or_create(
            user=detection.user,
            period_type='daily',
            period_start=today,
            defaults={
                'period_end': today + timedelta(days=1),
                'total_detections': 0,
                'total_objects_detected': 0,
                'avg_objects_per_detection': 0.0,
            }
        )
        
        # Mettre à jour les compteurs
        analytics.total_detections += 1
        analytics.total_objects_detected += detection.objects_detected
        analytics.avg_objects_per_detection = analytics.total_objects_detected / analytics.total_detections
        
        # Mettre à jour les détections par heure
        hour = detection.uploaded_at.hour
        detections_by_hour = analytics.get_detections_by_hour()
        detections_by_hour[str(hour)] = detections_by_hour.get(str(hour), 0) + 1
        analytics.set_detections_by_hour(detections_by_hour)
        
        # Mettre à jour les objets par classe
        objects_by_class = analytics.get_objects_by_class()
        detection_data = detection.get_detection_data()
        
        for obj in detection_data:
            obj_class = obj.get('class', 'unknown')
            objects_by_class[obj_class] = objects_by_class.get(obj_class, 0) + 1
        
        analytics.set_objects_by_class(objects_by_class)
        analytics.save()
        
        logger.info(f"Analytics updated for detection {detection.id}")
        
    except Exception as e:
        logger.error(f"Failed to update analytics: {e}")


def _check_for_anomalies(detection):
    """Vérifie si la détection est une anomalie"""
    from analytics.models import SecurityAlert
    from analytics.ml_models import AnomalyDetector
    
    try:
        recent_detections = DetectionResult.objects.filter(
            user=detection.user,
            uploaded_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('uploaded_at')
        
        if recent_detections.count() < 10:
            return
        
        detector = AnomalyDetector()
        result = detector.detect_anomalies(recent_detections)
        
        detection_ids = [a['detection_id'] for a in result.get('anomalies', [])]
        
        if detection.id in detection_ids:
            anomaly_info = next(a for a in result['anomalies'] if a['detection_id'] == detection.id)
            
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='anomaly',
                severity='high' if anomaly_info['anomaly_score'] > 0.8 else 'medium',
                title='Anomalous Detection Pattern',
                message=f"Unusual detection pattern: {anomaly_info['reason']}",
            )
            alert.set_context_data({
                'anomaly_score': anomaly_info['anomaly_score'],
                'features': anomaly_info['features'],
                'reason': anomaly_info['reason']
            })
            alert.save()
            
            logger.info(f"Anomaly alert created for detection {detection.id}")
            # Notification envoyée automatiquement via le signal post_save
    
    except Exception as e:
        logger.error(f"Anomaly check failed: {e}")


def _analyze_suspicious_objects(detection):
    """Analyse les objets suspects"""
    from analytics.models import SecurityAlert
    
    SUSPICIOUS_OBJECTS = ['gun', 'weapon', 'knife', 'fire', 'scissors', 'crowbar']
    HIGH_RISK_OBJECTS = ['gun', 'weapon', 'fire']
    
    try:
        detection_data = detection.get_detection_data()
        suspicious_objects = []
        
        for obj in detection_data:
            obj_class = obj.get('class', '').lower()
            if any(suspect in obj_class for suspect in SUSPICIOUS_OBJECTS):
                suspicious_objects.append(obj)
        
        if suspicious_objects:
            has_high_risk = any(
                any(risk in obj.get('class', '').lower() for risk in HIGH_RISK_OBJECTS)
                for obj in suspicious_objects
            )
            
            severity = 'critical' if has_high_risk else 'high'
            
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='suspicious_object',
                severity=severity,
                title=f'Suspicious Object: {suspicious_objects[0]["class"]}',
                message=f'Detected {len(suspicious_objects)} suspicious object(s).',
            )
            alert.set_context_data({'suspicious_objects': suspicious_objects})
            alert.save()
            
            # Notification envoyée automatiquement via le signal post_save
    
    except Exception as e:
        logger.error(f"Suspicious object analysis failed: {e}")


def _update_object_trends(detection):
    """Met à jour les tendances d'objets"""
    from analytics.models import ObjectTrend
    
    try:
        detection_data = detection.get_detection_data()
        
        for obj in detection_data:
            obj_class = obj.get('class', 'unknown')
            
            trend, created = ObjectTrend.objects.get_or_create(
                user=detection.user,
                object_class=obj_class,
                defaults={
                    'first_detected': detection.uploaded_at,
                    'last_detected': detection.uploaded_at,
                    'detection_count': 1,
                }
            )
            
            if not created:
                trend.last_detected = detection.uploaded_at
                trend.detection_count += 1
                
                days_active = (trend.last_detected - trend.first_detected).days + 1
                avg_per_day = trend.detection_count / max(days_active, 1)
                
                if avg_per_day > 5:
                    trend.trend_direction = 'increasing'
                elif avg_per_day < 1:
                    trend.trend_direction = 'decreasing'
                else:
                    trend.trend_direction = 'stable'
                
                trend.save()
    
    except Exception as e:
        logger.error(f"Trend update failed: {e}")


def _create_notification_from_alert(alert):
    """Crée et envoie une notification"""
    from notifications.services import NotificationService
    
    try:
        # Utiliser le service simplifié
        notifications = NotificationService.create_notification_from_alert(alert)
        logger.info(f"Created {len(notifications)} notifications for alert {alert.id}")
    
    except Exception as e:
        logger.error(f"Notification creation failed: {e}")


# DÉSACTIVÉ - Le signal dans notifications/signals.py gère déjà ceci
# Pour éviter les doublons de notifications SMS
# @receiver(post_save, sender='analytics.SecurityAlert')
# def send_notification_on_alert(sender, instance, created, **kwargs):
#     """Envoie notification quand alerte créée"""
#     print(f"🚨 ALERT SIGNAL - Alert #{instance.id}, created={created}, severity={instance.severity}")
#     
#     if created:
#         print(f"✅ Creating notifications for alert #{instance.id}")
#         _create_notification_from_alert(instance)
#     else:
#         print(f"❌ Alert signal skipped - not created")
