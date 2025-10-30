"""
Predictive Alert System
Generates preventive notifications based on predictions and patterns
"""
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class PredictiveAlertEngine:
    """
    Génère des alertes prédictives basées sur l'analyse de patterns
    """
    
    def __init__(self, user):
        self.user = user
    
    def generate_predictive_alerts(self):
        """
        Génère des alertes prédictives pour l'utilisateur
        
        Returns:
            List de PredictiveAlert à créer
        """
        from notifications.models import PredictiveAlert
        from analytics.ml_models import TimeSeriesPredictor, AnomalyDetector
        from analytics.pattern_recognition import PatternRecognizer
        from detection.models import DetectionResult
        
        alerts_to_create = []
        
        # 1. Prédictions de tendances
        trend_alerts = self._generate_trend_predictions()
        alerts_to_create.extend(trend_alerts)
        
        # 2. Prédictions d'anomalies
        anomaly_alerts = self._generate_anomaly_forecasts()
        alerts_to_create.extend(anomaly_alerts)
        
        # 3. Évaluations de risque
        risk_alerts = self._generate_risk_assessments()
        alerts_to_create.extend(risk_alerts)
        
        # 4. Alertes de maintenance prédictive
        maintenance_alerts = self._generate_maintenance_predictions()
        alerts_to_create.extend(maintenance_alerts)
        
        return alerts_to_create
    
    def _generate_trend_predictions(self):
        """Génère des alertes basées sur les prédictions de tendances"""
        from analytics.ml_models import TimeSeriesPredictor
        from detection.models import DetectionResult
        
        alerts = []
        
        try:
            # Récupérer les détections des 30 derniers jours
            detections = DetectionResult.objects.filter(
                user=self.user,
                uploaded_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('uploaded_at')
            
            if detections.count() < 7:
                return alerts  # Pas assez de données
            
            # Générer des prédictions
            predictor = TimeSeriesPredictor()
            forecast = predictor.forecast(detections, periods=7)
            
            if 'error' in forecast:
                return alerts
            
            # Analyser les prédictions
            predictions = forecast.get('predictions', [])
            current_activity = forecast.get('current_activity', 0)
            predicted_activity = forecast.get('predicted_activity', 0)
            trend_direction = forecast.get('trend_direction', 'stable')
            
            # Créer une alerte si augmentation significative prévue
            if predicted_activity > current_activity * 1.5:  # +50%
                alerts.append({
                    'prediction_type': 'trend',
                    'title': 'Activity Surge Predicted',
                    'description': f"Detection activity expected to increase by {((predicted_activity/current_activity - 1) * 100):.0f}% in the next 7 days",
                    'predicted_event': 'activity_increase',
                    'confidence_score': 0.75,
                    'predicted_timeframe_start': timezone.now() + timedelta(days=1),
                    'predicted_timeframe_end': timezone.now() + timedelta(days=7),
                    'supporting_data': {
                        'current_daily_avg': current_activity,
                        'predicted_daily_avg': predicted_activity,
                        'trend': trend_direction,
                        'predictions': predictions[:3]  # Premier 3 jours
                    },
                    'recommendations': 'Consider reviewing system capacity and alert thresholds.'
                })
            
            # Alerte si diminution significative (potentiel dysfonctionnement)
            elif predicted_activity < current_activity * 0.5 and current_activity > 10:  # -50%
                alerts.append({
                    'prediction_type': 'trend',
                    'title': 'Activity Drop Predicted',
                    'description': f"Detection activity expected to decrease by {((1 - predicted_activity/current_activity) * 100):.0f}%. This might indicate a system issue.",
                    'predicted_event': 'activity_decrease',
                    'confidence_score': 0.70,
                    'predicted_timeframe_start': timezone.now() + timedelta(days=1),
                    'predicted_timeframe_end': timezone.now() + timedelta(days=7),
                    'supporting_data': {
                        'current_daily_avg': current_activity,
                        'predicted_daily_avg': predicted_activity,
                        'trend': trend_direction
                    },
                    'recommendations': 'Check camera connectivity and system health.'
                })
        
        except Exception as e:
            logger.error(f"Trend prediction failed: {e}")
        
        return alerts
    
    def _generate_anomaly_forecasts(self):
        """Prévoit les périodes à haut risque d'anomalies"""
        from analytics.pattern_recognition import PatternRecognizer
        from detection.models import DetectionResult
        
        alerts = []
        
        try:
            # Analyser les patterns historiques
            detections = DetectionResult.objects.filter(
                user=self.user,
                uploaded_at__gte=timezone.now() - timedelta(days=30)
            )
            
            if not detections.exists():
                return alerts
            
            recognizer = PatternRecognizer(self.user)
            routines = recognizer.identify_routines(detections)
            
            # Identifier les routines nocturnes (potentiellement suspectes)
            night_routines = [
                r for r in routines.get('routines', [])
                if 'night' in r.get('description', '').lower() or
                any(hour in r.get('pattern', '') for hour in ['22', '23', '00', '01', '02', '03', '04', '05'])
            ]
            
            if night_routines:
                alerts.append({
                    'prediction_type': 'anomaly_forecast',
                    'title': 'Unusual Activity Pattern Detected',
                    'description': f"Detected {len(night_routines)} recurring nighttime activity patterns. Monitor for security concerns.",
                    'predicted_event': 'nighttime_activity',
                    'confidence_score': 0.65,
                    'predicted_timeframe_start': timezone.now(),
                    'predicted_timeframe_end': timezone.now() + timedelta(days=7),
                    'supporting_data': {
                        'routines': night_routines[:3],
                        'frequency': 'recurring'
                    },
                    'recommendations': 'Review nighttime detections and consider increasing alert sensitivity during these hours.'
                })
        
        except Exception as e:
            logger.error(f"Anomaly forecast failed: {e}")
        
        return alerts
    
    def _generate_risk_assessments(self):
        """Évalue et prédit les risques de sécurité"""
        from analytics.models import SecurityAlert, ObjectTrend
        
        alerts = []
        
        try:
            # Analyser les alertes récentes
            recent_alerts = SecurityAlert.objects.filter(
                user=self.user,
                created_at__gte=timezone.now() - timedelta(days=7),
                severity__in=['high', 'critical']
            )
            
            high_risk_count = recent_alerts.count()
            
            if high_risk_count >= 5:
                # Risque élevé détecté
                alerts.append({
                    'prediction_type': 'risk_assessment',
                    'title': 'Elevated Security Risk',
                    'description': f"{high_risk_count} high-severity alerts in the past week indicate increased security risk.",
                    'predicted_event': 'continued_high_risk',
                    'confidence_score': 0.80,
                    'predicted_timeframe_start': timezone.now(),
                    'predicted_timeframe_end': timezone.now() + timedelta(days=3),
                    'supporting_data': {
                        'recent_high_severity_alerts': high_risk_count,
                        'alert_types': list(recent_alerts.values_list('alert_type', flat=True).distinct())
                    },
                    'recommendations': 'Review security protocols. Consider increasing monitoring frequency and response readiness.'
                })
            
            # Analyser les tendances d'objets suspects
            suspicious_trends = ObjectTrend.objects.filter(
                user=self.user,
                is_anomaly=True,
                trend_direction='increasing'
            )
            
            if suspicious_trends.exists():
                top_suspicious = suspicious_trends.order_by('-anomaly_score').first()
                
                alerts.append({
                    'prediction_type': 'risk_assessment',
                    'title': f'Increasing Detection of {top_suspicious.object_class}',
                    'description': f"Detection frequency of '{top_suspicious.object_class}' is increasing abnormally.",
                    'predicted_event': 'object_trend_escalation',
                    'confidence_score': top_suspicious.anomaly_score,
                    'predicted_timeframe_start': timezone.now(),
                    'predicted_timeframe_end': timezone.now() + timedelta(days=5),
                    'supporting_data': {
                        'object_class': top_suspicious.object_class,
                        'detection_count': top_suspicious.detection_count,
                        'anomaly_score': top_suspicious.anomaly_score
                    },
                    'recommendations': f"Investigate the increasing detections of {top_suspicious.object_class}. Verify if legitimate or concerning."
                })
        
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
        
        return alerts
    
    def _generate_maintenance_predictions(self):
        """Prévoit les besoins de maintenance système"""
        from detection.models import DetectionResult
        
        alerts = []
        
        try:
            # Analyser la fréquence de détection récente
            now = timezone.now()
            
            # Comparer activité des 7 derniers jours vs 7 jours précédents
            recent_week = DetectionResult.objects.filter(
                user=self.user,
                uploaded_at__gte=now - timedelta(days=7)
            ).count()
            
            previous_week = DetectionResult.objects.filter(
                user=self.user,
                uploaded_at__gte=now - timedelta(days=14),
                uploaded_at__lt=now - timedelta(days=7)
            ).count()
            
            # Si activité récente < 25% de l'activité précédente
            if previous_week > 10 and recent_week < previous_week * 0.25:
                alerts.append({
                    'prediction_type': 'risk_assessment',
                    'title': 'Potential System Malfunction',
                    'description': f"Detection activity dropped by {((1 - recent_week/previous_week) * 100):.0f}%. System may need maintenance.",
                    'predicted_event': 'system_issue',
                    'confidence_score': 0.85,
                    'predicted_timeframe_start': now,
                    'predicted_timeframe_end': now + timedelta(days=1),
                    'supporting_data': {
                        'recent_detections': recent_week,
                        'previous_detections': previous_week,
                        'drop_percentage': ((1 - recent_week/previous_week) * 100)
                    },
                    'recommendations': 'Check camera power, connectivity, and lens cleanliness. Verify system logs for errors.'
                })
            
            # Vérifier l'ancienneté de la dernière détection
            last_detection = DetectionResult.objects.filter(user=self.user).order_by('-uploaded_at').first()
            
            if last_detection:
                hours_since_last = (now - last_detection.uploaded_at).total_seconds() / 3600
                
                if hours_since_last > 24:  # Pas de détection depuis 24h
                    alerts.append({
                        'prediction_type': 'risk_assessment',
                        'title': 'No Recent Detections',
                        'description': f"No detections recorded for {hours_since_last:.0f} hours. System may be offline.",
                        'predicted_event': 'system_offline',
                        'confidence_score': 0.90,
                        'predicted_timeframe_start': now,
                        'predicted_timeframe_end': now + timedelta(hours=1),
                        'supporting_data': {
                            'last_detection': last_detection.uploaded_at.isoformat(),
                            'hours_elapsed': hours_since_last
                        },
                        'recommendations': 'Immediately check system status and camera connectivity.'
                    })
        
        except Exception as e:
            logger.error(f"Maintenance prediction failed: {e}")
        
        return alerts
    
    def save_predictive_alerts(self, alerts_data):
        """
        Sauvegarde les alertes prédictives en base de données
        
        Args:
            alerts_data: List de dict avec données d'alertes
            
        Returns:
            List de PredictiveAlert créées
        """
        from notifications.models import PredictiveAlert
        
        created_alerts = []
        
        for alert_data in alerts_data:
            try:
                # Vérifier si une alerte similaire existe déjà
                existing = PredictiveAlert.objects.filter(
                    user=self.user,
                    predicted_event=alert_data['predicted_event'],
                    is_active=True,
                    created_at__gte=timezone.now() - timedelta(days=1)
                ).first()
                
                if existing:
                    logger.info(f"Similar predictive alert already exists: {alert_data['title']}")
                    continue
                
                # Créer l'alerte
                alert = PredictiveAlert.objects.create(
                    user=self.user,
                    prediction_type=alert_data['prediction_type'],
                    title=alert_data['title'],
                    description=alert_data['description'],
                    predicted_event=alert_data['predicted_event'],
                    confidence_score=alert_data['confidence_score'],
                    predicted_timeframe_start=alert_data['predicted_timeframe_start'],
                    predicted_timeframe_end=alert_data['predicted_timeframe_end'],
                    supporting_data=alert_data.get('supporting_data', {}),
                    recommendations=alert_data.get('recommendations', ''),
                    is_active=True
                )
                
                created_alerts.append(alert)
                logger.info(f"Created predictive alert: {alert.title}")
            
            except Exception as e:
                logger.error(f"Failed to create predictive alert: {e}")
        
        return created_alerts
    
    def evaluate_prediction_accuracy(self):
        """
        Évalue la précision des prédictions passées
        
        Returns:
            Dict avec métriques de précision
        """
        from notifications.models import PredictiveAlert
        
        # Récupérer les alertes prédictives expirées
        past_alerts = PredictiveAlert.objects.filter(
            user=self.user,
            predicted_timeframe_end__lt=timezone.now(),
            was_accurate__isnull=False
        )
        
        if not past_alerts.exists():
            return {
                'total_predictions': 0,
                'accuracy': None,
                'message': 'No historical predictions to evaluate'
            }
        
        total = past_alerts.count()
        accurate = past_alerts.filter(was_accurate=True).count()
        
        accuracy_rate = accurate / total if total > 0 else 0
        
        # Analyser par type de prédiction
        by_type = {}
        for pred_type in ['trend', 'anomaly_forecast', 'risk_assessment']:
            type_alerts = past_alerts.filter(prediction_type=pred_type)
            type_total = type_alerts.count()
            
            if type_total > 0:
                type_accurate = type_alerts.filter(was_accurate=True).count()
                by_type[pred_type] = {
                    'total': type_total,
                    'accurate': type_accurate,
                    'accuracy_rate': type_accurate / type_total
                }
        
        return {
            'total_predictions': total,
            'accurate_predictions': accurate,
            'accuracy_rate': round(accuracy_rate, 2),
            'by_type': by_type,
            'message': f"Overall prediction accuracy: {accuracy_rate*100:.0f}%"
        }
