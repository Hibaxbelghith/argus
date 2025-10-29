"""
Notification Services - Smart notification delivery and filtering
"""
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from collections import defaultdict
import hashlib
import json

from .models import (
    Notification,
    NotificationPreference,
    NotificationRule,
    NotificationLog,
    PredictiveAlert
)
from analytics.models import SecurityAlert, ObjectTrend, DetectionAnalytics


# Mapping de sévérité en valeurs numériques
SEVERITY_LEVELS = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4,
}


class NotificationService:
    """
    Core service for intelligent notification delivery
    """
    
    @staticmethod
    def create_notification_from_alert(alert):
        """
        Create notification(s) from a security alert
        
        Args:
            alert: SecurityAlert instance
        
        Returns:
            List of created Notification instances
        """
        print(f"📧 NotificationService.create_notification_from_alert - Alert #{alert.id}")
        
        user = alert.user
        preferences = NotificationService._get_or_create_preferences(user)
        
        print(f"   User: {user.username}, Methods: {preferences.enabled_methods}")
        
        # Vérifier si l'utilisateur veut ce type d'alerte
        if not NotificationService._should_notify(alert, preferences):
            print(f"   ❌ Should not notify")
            return []
        
        print(f"   ✅ Should notify")
        
        # Vérifier les heures silencieuses
        if preferences.is_in_quiet_hours() and alert.severity != 'critical':
            print(f"   ❌ Quiet hours")
            return []
        
        # Vérifier la fréquence maximale
        if not NotificationService._check_rate_limit(user, preferences):
            print(f"   ❌ Rate limit exceeded")
            return []
        
        # Appliquer les règles personnalisées
        action = NotificationService._apply_rules(alert, user)
        if action == 'suppress':
            print(f"   ❌ Suppressed by rules")
            return []
        
        print(f"   ✅ Creating notifications...")
        
        # Créer les notifications selon les méthodes activées
        notifications = []
        
        for method in preferences.enabled_methods:
            # Vérifier la sévérité minimale pour cette méthode
            min_severity = getattr(preferences, f'min_severity_{method}', 'low')
            
            print(f"   Method: {method}, min_severity: {min_severity}, alert: {alert.severity}")
            
            if SEVERITY_LEVELS[alert.severity] < SEVERITY_LEVELS[min_severity]:
                print(f"      ❌ Severity too low")
                continue
            
            print(f"      ✅ Creating {method} notification...")
            
            # Créer la notification
            notification = Notification.objects.create(
                user=user,
                notification_type='alert',
                title=alert.title,
                message=alert.message,
                severity=alert.severity,
                delivery_method=method,
                related_alert_id=alert.id,
                metadata={
                    'alert_type': alert.alert_type,
                    'detection_id': alert.detection_id if alert.detection else None,
                }
            )
            
            print(f"      ✅ Notification #{notification.id} created")
            
            # Gérer l'agrégation si activée
            if preferences.enable_aggregation:
                NotificationService._handle_aggregation(notification, preferences)
            
            notifications.append(notification)
        
        print(f"   📦 Total notifications created: {len(notifications)}")
        
        # Envoyer les notifications
        for notification in notifications:
            print(f"   📤 Sending {notification.delivery_method} notification #{notification.id}...")
            NotificationService._send_notification(notification)
        
        print(f"   ✅ Done! {len(notifications)} notifications sent")
        
        return notifications
    
    @staticmethod
    def _get_or_create_preferences(user):
        """Get or create notification preferences for user"""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'enabled_methods': ['web'],
                'min_severity_web': 'low',
                'min_severity_email': 'high',
                'min_severity_sms': 'critical',
            }
        )
        return preferences
    
    @staticmethod
    def _should_notify(alert, preferences):
        """Check if alert should trigger notification based on preferences"""
        # Vérifier les filtres spécifiques
        if alert.alert_type == 'suspicious_object' and not preferences.notify_suspicious_objects:
            return False
        
        if alert.alert_type == 'anomaly' and not preferences.notify_anomalies:
            return False
        
        if alert.alert_type == 'high_frequency' and not preferences.notify_high_frequency:
            return False
        
        if alert.alert_type == 'unusual_time' and not preferences.notify_unusual_time:
            return False
        
        return True
    
    @staticmethod
    def _check_rate_limit(user, preferences):
        """Check if rate limit is exceeded"""
        if preferences.max_notifications_per_hour == 0:
            return True
        
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_count = Notification.objects.filter(
            user=user,
            created_at__gte=one_hour_ago,
            status='sent'
        ).count()
        
        return recent_count < preferences.max_notifications_per_hour
    
    @staticmethod
    def _apply_rules(alert, user):
        """Apply custom notification rules"""
        rules = NotificationRule.objects.filter(
            user=user,
            is_active=True
        ).order_by('-priority')
        
        for rule in rules:
            if NotificationService._evaluate_rule(rule, alert):
                return rule.action
        
        return 'notify'
    
    @staticmethod
    def _evaluate_rule(rule, alert):
        """Evaluate if a rule matches an alert"""
        condition_value = rule.condition_value
        
        if rule.condition_type == 'object_class':
            # Vérifier si l'alerte concerne une classe d'objet spécifique
            context = alert.get_context_data()
            objects = context.get('objects', [])
            target_classes = condition_value.get('classes', [])
            
            for obj in objects:
                if obj.get('class') in target_classes:
                    return True
        
        elif rule.condition_type == 'detection_count':
            # Vérifier le nombre de détections
            threshold = condition_value.get('threshold', 0)
            context = alert.get_context_data()
            count = context.get('count', 0)
            
            return count >= threshold
        
        elif rule.condition_type == 'time_range':
            # Vérifier la plage horaire
            start_hour = condition_value.get('start_hour', 0)
            end_hour = condition_value.get('end_hour', 24)
            current_hour = timezone.now().hour
            
            return start_hour <= current_hour < end_hour
        
        return False
    
    @staticmethod
    def _handle_aggregation(notification, preferences):
        """Handle notification aggregation"""
        window = timedelta(minutes=preferences.aggregation_window_minutes)
        window_start = timezone.now() - window
        
        # Créer un ID de groupe basé sur le type et la sévérité
        group_key = f"{notification.notification_type}_{notification.severity}"
        group_hash = hashlib.md5(group_key.encode()).hexdigest()[:16]
        
        # Vérifier s'il y a des notifications similaires récentes
        similar_notifications = Notification.objects.filter(
            user=notification.user,
            notification_type=notification.notification_type,
            severity=notification.severity,
            created_at__gte=window_start,
            is_aggregated=False
        ).exclude(id=notification.id)
        
        if similar_notifications.exists():
            # Marquer comme agrégée
            notification.is_aggregated = True
            notification.aggregation_group_id = group_hash
            notification.save()
            
            # Marquer les autres aussi
            similar_notifications.update(
                is_aggregated=True,
                aggregation_group_id=group_hash
            )
    
    @staticmethod
    def _send_notification(notification):
        """Send notification via the specified method"""
        try:
            if notification.delivery_method == 'web':
                # Notification web (déjà enregistrée en DB)
                notification.mark_as_sent()
                NotificationService._log_event(notification, 'sent_web', 'Displayed in web dashboard')
            
            elif notification.delivery_method == 'email':
                # Envoyer par email
                NotificationService._send_email(notification)
                notification.mark_as_sent()
                NotificationService._log_event(notification, 'sent_email', f'Sent to {notification.user.email}')
            
            elif notification.delivery_method == 'sms':
                # Envoyer par SMS via Twilio
                sms_sid = NotificationService._send_sms(notification)
                notification.mark_as_sent()
                NotificationService._log_event(notification, 'sent_sms', f'Sent SMS to {notification.user.phone_number} (SID: {sms_sid})')
            
            elif notification.delivery_method == 'push':
                # Placeholder pour push notifications
                NotificationService._log_event(notification, 'push_not_implemented', 'Push notifications not configured')
                notification.status = 'failed'
                notification.save()
        
        except Exception as e:
            print(f"      ❌ EXCEPTION in _send_notification: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            notification.status = 'failed'
            notification.save()
            NotificationService._log_event(notification, 'failed', str(e))
    
    @staticmethod
    def _send_email(notification):
        """Send email notification"""
        subject = f"[{notification.severity.upper()}] {notification.title}"
        message = f"""
{notification.message}

---
Severity: {notification.get_severity_display()}
Type: {notification.get_notification_type_display()}
Time: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}

View details: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'}/analytics/alerts/

---
Argus Security Platform
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [notification.user.email],
            fail_silently=False,
        )
    
    @staticmethod
    def _send_sms(notification):
        """Send SMS notification via Twilio"""
        try:
            from twilio.rest import Client
            
            print(f"      🔵 _send_sms called for notification #{notification.id}")
            
            # Vérifier la configuration Twilio
            if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
                raise ValueError("Twilio credentials not configured in settings")
            
            print(f"      ✅ Twilio credentials OK")
            
            # Récupérer le numéro de téléphone de l'utilisateur
            phone_number = notification.user.phone_number
            
            if not phone_number:
                raise ValueError(f"No phone number configured for user {notification.user.username}")
            
            print(f"      ✅ Phone number: {phone_number}")
            
            # Créer le message SMS
            sms_body = f"[{notification.severity.upper()}] {notification.title}\n\n{notification.message[:140]}"
            
            print(f"      ✅ SMS body: {sms_body[:50]}...")
            
            # Initialiser le client Twilio
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            print(f"      ✅ Twilio client initialized")
            
            # Envoyer le SMS
            message = client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            print(f"      ✅ SMS sent! SID: {message.sid}")
            
            return message.sid
            
        except Exception as e:
            print(f"      ❌ SMS FAILED: {str(e)}")
            raise Exception(f"Failed to send SMS: {str(e)}")
    
    @staticmethod
    def _log_event(notification, event, details=''):
        """Log notification event"""
        NotificationLog.objects.create(
            notification=notification,
            event=event,
            details=details
        )
    
    @staticmethod
    def get_unread_notifications(user, limit=None):
        """Get unread notifications for user"""
        notifications = Notification.objects.filter(
            user=user,
            read_at__isnull=True,
            status='sent'
        ).order_by('-created_at')
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    @staticmethod
    def get_aggregated_notifications(user):
        """Get aggregated notifications grouped by aggregation_group_id"""
        notifications = Notification.objects.filter(
            user=user,
            is_aggregated=True,
            read_at__isnull=True
        ).order_by('aggregation_group_id', '-created_at')
        
        # Grouper par aggregation_group_id
        grouped = defaultdict(list)
        for notif in notifications:
            grouped[notif.aggregation_group_id].append(notif)
        
        return grouped


class PredictiveAnalyticsService:
    """
    Service for predictive analytics and alerts
    """
    
    @staticmethod
    def generate_trend_predictions(user):
        """
        Generate predictions based on detection trends
        """
        predictions = []
        
        # Analyser les tendances d'objets
        increasing_trends = ObjectTrend.objects.filter(
            user=user,
            trend_direction='increasing'
        ).order_by('-detection_count')[:5]
        
        for trend in increasing_trends:
            # Prédire une continuation de la tendance
            confidence = min(0.7 + (trend.detection_count / 100), 0.95)
            
            prediction = PredictiveAlert.objects.create(
                user=user,
                prediction_type='trend',
                title=f"Tendance croissante: {trend.object_class}",
                description=f"Basé sur {trend.detection_count} détections récentes, "
                            f"nous prévoyons une augmentation continue de '{trend.object_class}'.",
                predicted_event=f"increase_{trend.object_class}",
                confidence_score=confidence,
                predicted_timeframe_start=timezone.now(),
                predicted_timeframe_end=timezone.now() + timedelta(days=7),
                supporting_data={
                    'object_class': trend.object_class,
                    'detection_count': trend.detection_count,
                    'trend': trend.trend_direction,
                },
                recommendations=f"Surveillez les détections de '{trend.object_class}' et envisagez des mesures préventives."
            )
            predictions.append(prediction)
        
        return predictions
    
    @staticmethod
    def generate_anomaly_forecast(user):
        """
        Forecast potential anomalies based on patterns
        """
        predictions = []
        
        # Analyser les anomalies récentes
        recent_anomalies = ObjectTrend.objects.filter(
            user=user,
            is_anomaly=True,
            updated_at__gte=timezone.now() - timedelta(days=7)
        )
        
        if recent_anomalies.count() > 3:
            # Prévoir une possible anomalie future
            prediction = PredictiveAlert.objects.create(
                user=user,
                prediction_type='anomaly_forecast',
                title="Risque d'anomalie accru",
                description=f"{recent_anomalies.count()} anomalies détectées cette semaine. "
                            f"Risque accru d'anomalies futures.",
                predicted_event='anomaly_spike',
                confidence_score=0.65,
                predicted_timeframe_start=timezone.now(),
                predicted_timeframe_end=timezone.now() + timedelta(days=3),
                supporting_data={
                    'recent_anomaly_count': recent_anomalies.count(),
                },
                recommendations="Augmentez la surveillance et vérifiez la configuration de sécurité."
            )
            predictions.append(prediction)
        
        return predictions
    
    @staticmethod
    def assess_security_risk(user):
        """
        Assess overall security risk level
        """
        # Analyser les 7 derniers jours
        week_ago = timezone.now() - timedelta(days=7)
        
        # Compter les alertes critiques
        critical_alerts = SecurityAlert.objects.filter(
            user=user,
            severity='critical',
            created_at__gte=week_ago
        ).count()
        
        # Compter les objets suspects
        analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_start__gte=week_ago
        )
        
        total_suspicious = sum(a.suspicious_objects_count for a in analytics)
        
        # Calculer le score de risque
        risk_score = min((critical_alerts * 0.3 + total_suspicious * 0.1), 1.0)
        
        if risk_score > 0.7:
            risk_level = 'high'
            message = "Niveau de risque élevé détecté. Plusieurs incidents de sécurité cette semaine."
        elif risk_score > 0.4:
            risk_level = 'medium'
            message = "Niveau de risque modéré. Surveillez l'évolution de la situation."
        else:
            risk_level = 'low'
            message = "Niveau de risque faible. Situation sous contrôle."
        
        prediction = PredictiveAlert.objects.create(
            user=user,
            prediction_type='risk_assessment',
            title=f"Évaluation du risque: {risk_level.upper()}",
            description=message,
            predicted_event=f'risk_{risk_level}',
            confidence_score=0.85,
            predicted_timeframe_start=timezone.now(),
            predicted_timeframe_end=timezone.now() + timedelta(days=7),
            supporting_data={
                'risk_score': risk_score,
                'critical_alerts': critical_alerts,
                'suspicious_objects': total_suspicious,
            },
            recommendations="Maintenez une surveillance active et répondez rapidement aux alertes."
        )
        
        return prediction
