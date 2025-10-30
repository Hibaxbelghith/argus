"""
Analytics Services - Business logic for detection analytics
"""
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
from detection.models import DetectionResult
from .models import (
    DetectionAnalytics, 
    ObjectTrend, 
    SecurityAlert, 
    AnalyticsInsight
)
import json


# Objets considérés comme suspects/à risque
SUSPICIOUS_OBJECTS = [
    'knife', 'scissors', 'gun', 'weapon', 'fire',
    'broken glass', 'crowbar', 'bat'
]

HIGH_RISK_OBJECTS = [
    'gun', 'weapon', 'fire', 'knife'
]

# Objets de surveillance (sévérité MEDIUM pour SMS)
MONITORED_OBJECTS = [
    'person', 'car', 'dog', 'cat', 'motorcycle', 'truck'
]

# Heures normales d'activité (8h-22h)
NORMAL_ACTIVITY_HOURS = range(8, 22)


class AnalyticsEngine:
    """
    Core analytics engine for processing detection data
    """
    
    @staticmethod
    def generate_period_analytics(user, period_type='daily', period_start=None):
        """
        Generate analytics for a specific period
        
        Args:
            user: User instance
            period_type: 'daily', 'weekly', 'monthly'
            period_start: Start of period (defaults to current period)
        
        Returns:
            DetectionAnalytics instance
        """
        if period_start is None:
            period_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculer la fin de période
        if period_type == 'daily':
            period_end = period_start + timedelta(days=1)
        elif period_type == 'weekly':
            period_end = period_start + timedelta(weeks=1)
        elif period_type == 'monthly':
            period_end = period_start + timedelta(days=30)
        else:
            raise ValueError(f"Invalid period type: {period_type}")
        
        # Récupérer les détections de la période
        detections = DetectionResult.objects.filter(
            user=user,
            uploaded_at__gte=period_start,
            uploaded_at__lt=period_end
        )
        
        # Calculer les statistiques
        total_detections = detections.count()
        total_objects = sum(d.objects_detected for d in detections)
        avg_objects = total_objects / total_detections if total_detections > 0 else 0
        
        # Analyser les objets par classe
        objects_by_class = defaultdict(int)
        detections_by_hour = defaultdict(int)
        suspicious_count = 0
        high_risk_count = 0
        
        for detection in detections:
            # Heure de détection
            hour = detection.uploaded_at.hour
            detections_by_hour[str(hour)] += 1
            
            # Analyser les objets détectés
            detection_data = detection.get_detection_data()
            for obj in detection_data:
                obj_class = obj.get('class', 'unknown').lower()
                objects_by_class[obj_class] += 1
                
                # Vérifier si l'objet est suspect
                if any(suspect in obj_class for suspect in SUSPICIOUS_OBJECTS):
                    suspicious_count += 1
                
                # Vérifier si l'objet est à haut risque
                if any(risk in obj_class for risk in HIGH_RISK_OBJECTS):
                    high_risk_count += 1
        
        # Créer ou mettre à jour l'analytics
        analytics, created = DetectionAnalytics.objects.update_or_create(
            user=user,
            period_type=period_type,
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'total_detections': total_detections,
                'total_objects_detected': total_objects,
                'avg_objects_per_detection': round(avg_objects, 2),
                'objects_by_class': json.dumps(dict(objects_by_class)),
                'detections_by_hour': json.dumps(dict(detections_by_hour)),
                'suspicious_objects_count': suspicious_count,
                'high_risk_detections': high_risk_count,
            }
        )
        
        return analytics
    
    @staticmethod
    def update_object_trends(user):
        """
        Update object trends based on recent detections
        """
        # Analyser les 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_detections = DetectionResult.objects.filter(
            user=user,
            uploaded_at__gte=thirty_days_ago
        )
        
        # Compter les occurrences par classe
        object_counts = defaultdict(lambda: {
            'count': 0,
            'first': None,
            'last': None,
            'timestamps': []
        })
        
        for detection in recent_detections:
            detection_data = detection.get_detection_data()
            for obj in detection_data:
                obj_class = obj.get('class', 'unknown')
                object_counts[obj_class]['count'] += 1
                object_counts[obj_class]['timestamps'].append(detection.uploaded_at)
                
                if object_counts[obj_class]['first'] is None:
                    object_counts[obj_class]['first'] = detection.uploaded_at
                object_counts[obj_class]['last'] = detection.uploaded_at
        
        # Mettre à jour les tendances
        for obj_class, data in object_counts.items():
            if data['count'] == 0:
                continue
            
            # Calculer la tendance
            trend_direction = AnalyticsEngine._calculate_trend(data['timestamps'])
            
            # Détecter les anomalies
            is_anomaly, anomaly_score = AnalyticsEngine._detect_anomaly(
                obj_class, data['count'], data['timestamps']
            )
            
            # Créer ou mettre à jour la tendance
            ObjectTrend.objects.update_or_create(
                user=user,
                object_class=obj_class,
                defaults={
                    'detection_count': data['count'],
                    'first_detected': data['first'],
                    'last_detected': data['last'],
                    'trend_direction': trend_direction,
                    'is_anomaly': is_anomaly,
                    'anomaly_score': anomaly_score,
                }
            )
    
    @staticmethod
    def _calculate_trend(timestamps):
        """
        Calculate trend direction based on timestamps
        """
        if len(timestamps) < 3:
            return 'stable'
        
        # Diviser en deux périodes
        mid_point = len(timestamps) // 2
        first_half_count = mid_point
        second_half_count = len(timestamps) - mid_point
        
        # Comparer les deux périodes
        if second_half_count > first_half_count * 1.5:
            return 'increasing'
        elif second_half_count < first_half_count * 0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _detect_anomaly(obj_class, count, timestamps):
        """
        Detect anomalies in detection patterns
        """
        # Anomalie si objet à haut risque détecté
        if any(risk in obj_class.lower() for risk in HIGH_RISK_OBJECTS):
            return True, 0.9
        
        # Anomalie si détection fréquente inhabituelle
        if count > 20:  # Plus de 20 détections en 30 jours
            return True, 0.7
        
        # Anomalie si détections à des heures inhabituelles
        unusual_hours = sum(1 for ts in timestamps if ts.hour not in NORMAL_ACTIVITY_HOURS)
        if unusual_hours > len(timestamps) * 0.5:
            return True, 0.6
        
        return False, 0.0
    
    @staticmethod
    def generate_insights(user):
        """
        Generate AI insights from analytics data
        """
        insights = []
        
        # Analyser les tendances récentes
        trends = ObjectTrend.objects.filter(user=user, is_anomaly=True).order_by('-anomaly_score')[:5]
        
        for trend in trends:
            insight = AnalyticsInsight.objects.create(
                user=user,
                insight_type='pattern',
                title=f"Anomalie détectée: {trend.object_class}",
                description=f"Détection inhabituelle de '{trend.object_class}' avec {trend.detection_count} occurrences. "
                            f"Tendance: {trend.get_trend_direction_display()}.",
                confidence_score=trend.anomaly_score,
                data=json.dumps({
                    'object_class': trend.object_class,
                    'count': trend.detection_count,
                    'trend': trend.trend_direction,
                })
            )
            insights.append(insight)
        
        # Analyser les patterns temporels
        recent_analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_type='daily'
        ).order_by('-period_start')[:7]
        
        if recent_analytics.exists():
            total_suspicious = sum(a.suspicious_objects_count for a in recent_analytics)
            if total_suspicious > 0:
                insight = AnalyticsInsight.objects.create(
                    user=user,
                    insight_type='summary',
                    title="Objets suspects détectés cette semaine",
                    description=f"{total_suspicious} objets suspects ont été détectés au cours des 7 derniers jours.",
                    confidence_score=0.8,
                    data=json.dumps({
                        'total_suspicious': total_suspicious,
                        'period': '7 days'
                    })
                )
                insights.append(insight)
        
        return insights


class SecurityAlertService:
    """
    Service for generating and managing security alerts
    """
    
    @staticmethod
    def analyze_detection(detection):
        """
        Analyze a detection and create alerts if necessary
        
        Args:
            detection: DetectionResult instance
        
        Returns:
            List of created SecurityAlert instances
        """
        alerts = []
        detection_data = detection.get_detection_data()
        
        # Vérifier les objets à haut risque
        high_risk_objects = []
        suspicious_objects = []
        monitored_objects = []
        
        for obj in detection_data:
            obj_class = obj.get('class', 'unknown').lower()
            confidence = obj.get('confidence', 0)
            
            # Objet à haut risque
            if any(risk in obj_class for risk in HIGH_RISK_OBJECTS):
                high_risk_objects.append({
                    'class': obj_class,
                    'confidence': confidence
                })
            
            # Objet suspect
            elif any(suspect in obj_class for suspect in SUSPICIOUS_OBJECTS):
                suspicious_objects.append({
                    'class': obj_class,
                    'confidence': confidence
                })
            
            # Objet sous surveillance
            elif any(monitor in obj_class for monitor in MONITORED_OBJECTS):
                monitored_objects.append({
                    'class': obj_class,
                    'confidence': confidence
                })
        
        # Créer alerte pour objets à haut risque
        if high_risk_objects:
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='suspicious_object',
                severity='critical',
                title=f"⚠️ ALERTE CRITIQUE: Objet dangereux détecté",
                message=f"{len(high_risk_objects)} objet(s) dangereux détecté(s): {', '.join(o['class'] for o in high_risk_objects)}",
                context_data=json.dumps({
                    'objects': high_risk_objects,
                    'detection_id': detection.id,
                    'timestamp': detection.uploaded_at.isoformat()
                })
            )
            alerts.append(alert)
        
        # Créer alerte pour objets suspects
        elif suspicious_objects:
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='suspicious_object',
                severity='high',
                title=f"⚠️ Objet suspect détecté",
                message=f"{len(suspicious_objects)} objet(s) suspect(s) détecté(s): {', '.join(o['class'] for o in suspicious_objects)}",
                context_data=json.dumps({
                    'objects': suspicious_objects,
                    'detection_id': detection.id,
                    'timestamp': detection.uploaded_at.isoformat()
                })
            )
            alerts.append(alert)
        
        # Créer alerte pour objets sous surveillance (person, car, dog, etc.)
        if monitored_objects:
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='suspicious_object',
                severity='medium',
                title=f"👁️ Détection surveillance: {', '.join(set(o['class'] for o in monitored_objects))}",
                message=f"{len(monitored_objects)} objet(s) surveillé(s) détecté(s): {', '.join(o['class'] for o in monitored_objects)}",
                context_data=json.dumps({
                    'objects': monitored_objects,
                    'detection_id': detection.id,
                    'timestamp': detection.uploaded_at.isoformat()
                })
            )
            alerts.append(alert)
        
        # Vérifier l'heure de détection
        if detection.uploaded_at.hour not in NORMAL_ACTIVITY_HOURS:
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='unusual_time',
                severity='medium',
                title=f"🕐 Détection à heure inhabituelle",
                message=f"Détection effectuée à {detection.uploaded_at.strftime('%H:%M')} (heure inhabituelle)",
                context_data=json.dumps({
                    'hour': detection.uploaded_at.hour,
                    'detection_id': detection.id,
                })
            )
            alerts.append(alert)
        
        # Vérifier la fréquence des détections
        recent_count = DetectionResult.objects.filter(
            user=detection.user,
            uploaded_at__gte=timezone.now() - timedelta(hours=1)
        ).count()
        
        if recent_count > 10:
            alert = SecurityAlert.objects.create(
                user=detection.user,
                detection=detection,
                alert_type='high_frequency',
                severity='medium',
                title=f"📊 Fréquence de détection élevée",
                message=f"{recent_count} détections au cours de la dernière heure",
                context_data=json.dumps({
                    'count': recent_count,
                    'period': '1 hour',
                })
            )
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def get_unread_alerts(user, severity=None):
        """
        Get unread alerts for a user
        """
        alerts = SecurityAlert.objects.filter(user=user, is_read=False)
        
        if severity:
            alerts = alerts.filter(severity=severity)
        
        return alerts.order_by('-created_at')
    
    @staticmethod
    def get_alert_summary(user):
        """
        Get summary of alerts for dashboard
        """
        alerts = SecurityAlert.objects.filter(user=user)
        
        summary = {
            'total': alerts.count(),
            'unread': alerts.filter(is_read=False).count(),
            'critical': alerts.filter(severity='critical').count(),
            'high': alerts.filter(severity='high').count(),
            'medium': alerts.filter(severity='medium').count(),
            'low': alerts.filter(severity='low').count(),
            'recent': alerts.order_by('-created_at')[:5],
        }
        
        return summary
