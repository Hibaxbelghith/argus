"""
Advanced API Views for AI-Powered Analytics & Notifications
NLP Queries, ML Predictions, Recommendations, Real-time Analytics
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)


# ============ ANALYTICS AI ENDPOINTS ============

@login_required
@require_http_methods(["POST"])
def api_nlp_query(request):
    """
    POST /analytics/api/nlp-query/
    Process natural language queries
    Body: {"query": "show me detections from today"}
    """
    try:
        data = json.loads(request.body)
        query_text = data.get('query', '')
        
        from analytics.nlp_service import NaturalLanguageQueryProcessor
        
        processor = NaturalLanguageQueryProcessor()
        result = processor.process_query(query_text, request.user)
        
        return JsonResponse({
            'status': 'success',
            'query': result['query'],
            'intent': result['intent'],
            'results': result['results'],
            'summary': result['summary']
        })
    
    except Exception as e:
        logger.error(f"NLP query failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_anomaly_detection(request):
    """
    GET /analytics/api/anomalies/
    Detect anomalies in recent detections
    Params: ?days=7
    """
    try:
        days = int(request.GET.get('days', 7))
        
        from detection.models import DetectionResult
        from analytics.ml_models import AnomalyDetector
        
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=timezone.now() - timedelta(days=days)
        ).order_by('uploaded_at')
        
        detector = AnomalyDetector()
        result = detector.detect_anomalies(detections)
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'period_days': days
        })
    
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_predictions_forecast(request):
    """
    GET /analytics/api/predictions/
    Generate activity forecasts
    Params: ?periods=7
    """
    try:
        periods = int(request.GET.get('periods', 7))
        
        from detection.models import DetectionResult
        from analytics.ml_models import TimeSeriesPredictor
        
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('uploaded_at')
        
        predictor = TimeSeriesPredictor()
        forecast = predictor.forecast(detections, periods=periods)
        
        return JsonResponse({
            'status': 'success',
            'data': forecast
        })
    
    except Exception as e:
        logger.error(f"Forecast failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_pattern_recognition(request):
    """
    GET /analytics/api/patterns/
    Identify behavioral patterns and routines
    """
    try:
        from detection.models import DetectionResult
        from analytics.pattern_recognition import PatternRecognizer
        
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=timezone.now() - timedelta(days=30)
        )
        
        recognizer = PatternRecognizer(request.user)
        routines = recognizer.identify_routines(detections)
        behavior_profile = recognizer.classify_behavior_profile(detections)
        
        return JsonResponse({
            'status': 'success',
            'routines': routines,
            'behavior_profile': behavior_profile
        })
    
    except Exception as e:
        logger.error(f"Pattern recognition failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_recommendations(request):
    """
    GET /analytics/api/recommendations/
    Get intelligent system recommendations
    """
    try:
        from analytics.models import DetectionAnalytics
        from analytics.pattern_recognition import RecommendationEngine, PatternRecognizer
        from detection.models import DetectionResult
        
        # Get latest analytics
        analytics = DetectionAnalytics.objects.filter(
            user=request.user
        ).order_by('-period_start').first()
        
        if not analytics:
            return JsonResponse({
                'status': 'success',
                'recommendations': [],
                'message': 'No analytics data available'
            })
        
        # Get patterns
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=timezone.now() - timedelta(days=30)
        )
        
        recognizer = PatternRecognizer(request.user)
        patterns = recognizer.identify_routines(detections)
        
        # Generate recommendations
        recommendations = RecommendationEngine.generate_system_recommendations(
            request.user,
            analytics,
            patterns
        )
        
        return JsonResponse({
            'status': 'success',
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    
    except Exception as e:
        logger.error(f"Recommendations failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_generate_narrative_report(request):
    """
    POST /analytics/api/narrative-report/
    Generate AI narrative reports
    Body: {"period": "daily"|"weekly", "date": "2025-01-01"}
    """
    try:
        data = json.loads(request.body)
        period = data.get('period', 'daily')
        
        from analytics.nlp_service import NarrativeReportGenerator
        from analytics.models import DetectionAnalytics
        from detection.models import DetectionResult
        
        if period == 'daily':
            date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            analytics = DetectionAnalytics.objects.filter(
                user=request.user,
                period_type='daily',
                period_start=date
            ).first()
            
            detections = DetectionResult.objects.filter(
                user=request.user,
                uploaded_at__gte=date
            )
            
            if analytics:
                narrative = NarrativeReportGenerator.generate_daily_summary(
                    request.user, analytics, detections
                )
            else:
                narrative = "No data available for today"
        
        elif period == 'weekly':
            week_ago = timezone.now() - timedelta(days=7)
            weekly_analytics = DetectionAnalytics.objects.filter(
                user=request.user,
                period_type='daily',
                period_start__gte=week_ago
            ).order_by('period_start')
            
            narrative = NarrativeReportGenerator.generate_weekly_report(
                request.user, list(weekly_analytics)
            )
        
        else:
            narrative = "Invalid period"
        
        return JsonResponse({
            'status': 'success',
            'period': period,
            'narrative': narrative
        })
    
    except Exception as e:
        logger.error(f"Narrative report generation failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_visualizations(request):
    """
    GET /analytics/api/visualizations/
    Get all interactive visualizations data
    Params: ?period=weekly
    """
    try:
        period = request.GET.get('period', 'weekly')
        
        from analytics.visualizations import ReportVisualizer
        
        report = ReportVisualizer.generate_comprehensive_report(
            request.user, period
        )
        
        return JsonResponse({
            'status': 'success',
            'report': report
        })
    
    except Exception as e:
        logger.error(f"Visualization generation failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============ NOTIFICATIONS AI ENDPOINTS ============

@login_required
@require_http_methods(["POST"])
def api_notification_score(request):
    """
    POST /notifications/api/score/
    Score a potential notification
    Body: {"alert_id": 123}
    """
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        
        from analytics.models import SecurityAlert
        from notifications.ml_scoring import NotificationScorer
        from notifications.models import NotificationPreference
        
        alert = SecurityAlert.objects.get(id=alert_id, user=request.user)
        preferences = NotificationPreference.objects.get(user=request.user)
        
        scorer = NotificationScorer()
        score_result = scorer.score_notification(alert, alert.detection, preferences)
        
        return JsonResponse({
            'status': 'success',
            'score': score_result
        })
    
    except Exception as e:
        logger.error(f"Notification scoring failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_behavioral_insights(request):
    """
    GET /notifications/api/behavioral-insights/
    Get behavioral learning insights
    """
    try:
        from notifications.behavioral_learning import BehavioralLearner
        
        learner = BehavioralLearner(request.user)
        patterns = learner.analyze_interaction_patterns()
        
        return JsonResponse({
            'status': 'success',
            'patterns': patterns
        })
    
    except Exception as e:
        logger.error(f"Behavioral insights failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_adapt_preferences(request):
    """
    POST /notifications/api/adapt-preferences/
    Auto-adapt notification preferences
    Body: {"auto_apply": true}
    """
    try:
        data = json.loads(request.body)
        auto_apply = data.get('auto_apply', False)
        
        from notifications.behavioral_learning import BehavioralLearner
        
        learner = BehavioralLearner(request.user)
        result = learner.adapt_preferences(auto_apply=auto_apply)
        
        return JsonResponse({
            'status': 'success',
            'adaptation_result': result
        })
    
    except Exception as e:
        logger.error(f"Preference adaptation failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_predictive_alerts(request):
    """
    GET /notifications/api/predictive-alerts/
    Get predictive alerts
    """
    try:
        from notifications.models import PredictiveAlert
        
        alerts = PredictiveAlert.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-confidence_score')[:10]
        
        data = []
        for alert in alerts:
            data.append({
                'id': alert.id,
                'type': alert.prediction_type,
                'title': alert.title,
                'description': alert.description,
                'predicted_event': alert.predicted_event,
                'confidence': alert.confidence_score,
                'timeframe_start': alert.predicted_timeframe_start.isoformat(),
                'timeframe_end': alert.predicted_timeframe_end.isoformat(),
                'recommendations': alert.recommendations
            })
        
        return JsonResponse({
            'status': 'success',
            'predictive_alerts': data,
            'total': len(data)
        })
    
    except Exception as e:
        logger.error(f"Predictive alerts retrieval failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_generate_predictive_alerts(request):
    """
    POST /notifications/api/generate-predictive-alerts/
    Manually trigger predictive alert generation
    """
    try:
        from notifications.predictive_alerts import PredictiveAlertEngine
        
        engine = PredictiveAlertEngine(request.user)
        alerts_data = engine.generate_predictive_alerts()
        created_alerts = engine.save_predictive_alerts(alerts_data)
        
        return JsonResponse({
            'status': 'success',
            'generated_alerts': len(created_alerts),
            'alerts': [
                {
                    'title': a.title,
                    'confidence': a.confidence_score,
                    'predicted_event': a.predicted_event
                }
                for a in created_alerts
            ]
        })
    
    except Exception as e:
        logger.error(f"Predictive alert generation failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request):
    """
    POST /notifications/api/mark-read/
    Mark notification(s) as read
    Body: {"notification_ids": [1, 2, 3]}
    """
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
        
        from notifications.models import Notification
        
        notifications = Notification.objects.filter(
            user=request.user,
            id__in=notification_ids
        )
        
        for notif in notifications:
            notif.mark_as_read()
        
        return JsonResponse({
            'status': 'success',
            'marked_read': notifications.count()
        })
    
    except Exception as e:
        logger.error(f"Mark as read failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_notification_feedback(request):
    """
    POST /notifications/api/feedback/
    Submit feedback for notification learning
    Body: {"notification_id": 123, "is_false_positive": true}
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        is_false_positive = data.get('is_false_positive', False)
        
        from notifications.ml_scoring import FalseAlertFilter
        
        # Store feedback (you'd need a model for this)
        # For now, just log it
        logger.info(f"Feedback received: notification {notification_id}, false_positive: {is_false_positive}")
        
        filter = FalseAlertFilter()
        # In a real implementation, you'd save this to train the model
        
        return JsonResponse({
            'status': 'success',
            'message': 'Feedback recorded'
        })
    
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============ REAL-TIME STATS ============

@login_required
@require_http_methods(["GET"])
def api_realtime_stats(request):
    """
    GET /analytics/api/realtime-stats/
    Get real-time analytics dashboard data
    """
    try:
        from analytics.models import DetectionAnalytics, SecurityAlert
        from notifications.models import Notification
        from detection.models import DetectionResult
        
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Today's stats
        today_analytics = DetectionAnalytics.objects.filter(
            user=request.user,
            period_start=today
        ).first()
        
        # Recent detections
        recent_detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Unread notifications
        unread_notifs = Notification.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).count()
        
        # Recent alerts
        recent_alerts = SecurityAlert.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(hours=24),
            is_read=False
        ).count()
        
        return JsonResponse({
            'status': 'success',
            'realtime_data': {
                'today_total_detections': today_analytics.total_detections if today_analytics else 0,
                'today_total_objects': today_analytics.total_objects_detected if today_analytics else 0,
                'last_24h_detections': recent_detections,
                'unread_notifications': unread_notifs,
                'recent_alerts': recent_alerts,
                'timestamp': timezone.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Realtime stats failed: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
