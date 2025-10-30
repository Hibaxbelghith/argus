"""
API REST pour le module Analytics
Fournit des endpoints JSON pour l'intégration externe
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import timedelta
import json

from .models import (
    DetectionAnalytics,
    ObjectTrend,
    SecurityAlert,
    AnalyticsInsight
)
from .services import AnalyticsEngine, SecurityAlertService
from detection.models import DetectionResult


@login_required
@require_http_methods(["GET"])
def api_stats_summary(request):
    """
    GET /analytics/api/stats/summary/
    Retourne un résumé des statistiques globales
    """
    user = request.user
    
    # Statistiques globales
    total_detections = DetectionResult.objects.filter(user=user).count()
    total_objects = sum(d.objects_detected for d in DetectionResult.objects.filter(user=user))
    
    # Dernière semaine
    week_ago = timezone.now() - timedelta(days=7)
    weekly_detections = DetectionResult.objects.filter(
        user=user,
        uploaded_at__gte=week_ago
    ).count()
    
    # Alertes
    alert_counts = SecurityAlert.objects.filter(user=user).aggregate(
        total=Count('id'),
        unread=Count('id', filter=Q(is_read=False)),
        critical=Count('id', filter=Q(severity='critical')),
        high=Count('id', filter=Q(severity='high'))
    )
    
    # Top objets
    top_objects = list(
        ObjectTrend.objects.filter(user=user)
        .order_by('-detection_count')[:5]
        .values('object_class', 'detection_count', 'is_anomaly')
    )
    
    return JsonResponse({
        'status': 'success',
        'data': {
            'total_detections': total_detections,
            'total_objects': total_objects,
            'weekly_detections': weekly_detections,
            'alerts': alert_counts,
            'top_objects': top_objects,
        },
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_trends_list(request):
    """
    GET /analytics/api/trends/
    Retourne la liste des tendances d'objets
    Paramètres:
        - anomalies_only: true/false
        - limit: nombre de résultats
    """
    user = request.user
    
    # Filtres
    anomalies_only = request.GET.get('anomalies_only', 'false') == 'true'
    limit = int(request.GET.get('limit', 50))
    
    # Query
    trends = ObjectTrend.objects.filter(user=user)
    
    if anomalies_only:
        trends = trends.filter(is_anomaly=True)
    
    trends = trends.order_by('-detection_count')[:limit]
    
    # Sérialiser
    data = []
    for trend in trends:
        data.append({
            'id': trend.id,
            'object_class': trend.object_class,
            'detection_count': trend.detection_count,
            'first_detected': trend.first_detected.isoformat(),
            'last_detected': trend.last_detected.isoformat(),
            'trend_direction': trend.trend_direction,
            'is_anomaly': trend.is_anomaly,
            'anomaly_score': float(trend.anomaly_score),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_alerts_list(request):
    """
    GET /analytics/api/alerts/
    Retourne la liste des alertes de sécurité
    Paramètres:
        - severity: low/medium/high/critical
        - unread_only: true/false
        - limit: nombre de résultats
    """
    user = request.user
    
    # Filtres
    severity = request.GET.get('severity')
    unread_only = request.GET.get('unread_only', 'false') == 'true'
    limit = int(request.GET.get('limit', 50))
    
    # Query
    alerts = SecurityAlert.objects.filter(user=user)
    
    if severity:
        alerts = alerts.filter(severity=severity)
    
    if unread_only:
        alerts = alerts.filter(is_read=False)
    
    alerts = alerts.order_by('-created_at')[:limit]
    
    # Sérialiser
    data = []
    for alert in alerts:
        data.append({
            'id': alert.id,
            'alert_type': alert.alert_type,
            'severity': alert.severity,
            'title': alert.title,
            'message': alert.message,
            'is_read': alert.is_read,
            'is_acknowledged': alert.is_acknowledged,
            'created_at': alert.created_at.isoformat(),
            'context_data': alert.get_context_data(),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def api_alert_acknowledge(request, alert_id):
    """
    POST /analytics/api/alerts/<id>/acknowledge/
    Marque une alerte comme acquittée
    """
    user = request.user
    
    try:
        alert = SecurityAlert.objects.get(id=alert_id, user=user)
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Alerte acquittée avec succès',
            'alert_id': alert.id,
            'timestamp': timezone.now().isoformat()
        })
    except SecurityAlert.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Alerte non trouvée'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def api_insights_list(request):
    """
    GET /analytics/api/insights/
    Retourne les insights générés
    Paramètres:
        - type: pattern/prediction/recommendation/summary
        - active_only: true/false
    """
    user = request.user
    
    # Filtres
    insight_type = request.GET.get('type')
    active_only = request.GET.get('active_only', 'true') == 'true'
    
    # Query
    insights = AnalyticsInsight.objects.filter(user=user)
    
    if insight_type:
        insights = insights.filter(insight_type=insight_type)
    
    if active_only:
        insights = insights.filter(is_active=True)
    
    insights = insights.order_by('-confidence_score', '-created_at')[:20]
    
    # Sérialiser
    data = []
    for insight in insights:
        data.append({
            'id': insight.id,
            'insight_type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'confidence_score': float(insight.confidence_score),
            'is_active': insight.is_active,
            'created_at': insight.created_at.isoformat(),
            'data': insight.get_data(),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_period_analytics(request):
    """
    GET /analytics/api/analytics/period/
    Retourne les analytics pour une période donnée
    Paramètres:
        - period: daily/weekly/monthly
        - days: nombre de jours à récupérer (défaut: 7)
    """
    user = request.user
    
    # Paramètres
    period_type = request.GET.get('period', 'daily')
    days = int(request.GET.get('days', 7))
    
    # Query
    analytics = DetectionAnalytics.objects.filter(
        user=user,
        period_type=period_type
    ).order_by('-period_start')[:days]
    
    # Sérialiser
    data = []
    for analytic in analytics:
        data.append({
            'id': analytic.id,
            'period_type': analytic.period_type,
            'period_start': analytic.period_start.isoformat(),
            'period_end': analytic.period_end.isoformat(),
            'total_detections': analytic.total_detections,
            'total_objects_detected': analytic.total_objects_detected,
            'avg_objects_per_detection': float(analytic.avg_objects_per_detection),
            'suspicious_objects_count': analytic.suspicious_objects_count,
            'high_risk_detections': analytic.high_risk_detections,
            'objects_by_class': analytic.get_objects_by_class(),
            'detections_by_hour': analytic.get_detections_by_hour(),
        })
    
    return JsonResponse({
        'status': 'success',
        'period': period_type,
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_chart_data(request):
    """
    GET /analytics/api/charts/detections/
    Retourne les données formatées pour Chart.js
    Paramètres:
        - days: nombre de jours (défaut: 7)
        - period: daily/weekly
    """
    user = request.user
    
    # Paramètres
    days = int(request.GET.get('days', 7))
    period_type = request.GET.get('period', 'daily')
    
    # Query
    analytics = DetectionAnalytics.objects.filter(
        user=user,
        period_type=period_type
    ).order_by('-period_start')[:days]
    
    # Préparer données pour Chart.js
    analytics_reversed = list(reversed(analytics))
    
    chart_data = {
        'labels': [a.period_start.strftime('%d/%m') for a in analytics_reversed],
        'datasets': {
            'detections': [a.total_detections for a in analytics_reversed],
            'objects': [a.total_objects_detected for a in analytics_reversed],
            'suspicious': [a.suspicious_objects_count for a in analytics_reversed],
        }
    }
    
    return JsonResponse({
        'status': 'success',
        'chart_data': chart_data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def api_generate_analytics(request):
    """
    POST /analytics/api/analytics/generate/
    Force la génération des analytics
    Body JSON: {"period": "daily|weekly|monthly"}
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        period_type = data.get('period', 'daily')
        
        # Générer analytics
        analytics = AnalyticsEngine.generate_period_analytics(user, period_type)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Analytics {period_type} générées avec succès',
            'analytics': {
                'total_detections': analytics.total_detections,
                'total_objects': analytics.total_objects_detected,
                'period_start': analytics.period_start.isoformat(),
                'period_end': analytics.period_end.isoformat(),
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_detect_anomalies(request):
    """
    GET /analytics/api/anomalies/detect/
    Détecte et retourne les anomalies actuelles
    """
    user = request.user
    
    # Mettre à jour les tendances pour détecter les anomalies
    AnalyticsEngine.update_object_trends(user)
    
    # Récupérer les anomalies
    anomalies = ObjectTrend.objects.filter(
        user=user,
        is_anomaly=True
    ).order_by('-anomaly_score')
    
    data = []
    for anomaly in anomalies:
        data.append({
            'object_class': anomaly.object_class,
            'detection_count': anomaly.detection_count,
            'anomaly_score': float(anomaly.anomaly_score),
            'trend_direction': anomaly.trend_direction,
            'last_detected': anomaly.last_detected.isoformat(),
        })
    
    return JsonResponse({
        'status': 'success',
        'anomalies_count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_health_check(request):
    """
    GET /analytics/api/health/
    Vérifie l'état du module analytics
    """
    user = request.user
    
    # Compter les éléments
    stats = {
        'analytics_count': DetectionAnalytics.objects.filter(user=user).count(),
        'trends_count': ObjectTrend.objects.filter(user=user).count(),
        'alerts_count': SecurityAlert.objects.filter(user=user).count(),
        'insights_count': AnalyticsInsight.objects.filter(user=user).count(),
        'unread_alerts': SecurityAlert.objects.filter(user=user, is_read=False).count(),
    }
    
    return JsonResponse({
        'status': 'healthy',
        'module': 'analytics',
        'stats': stats,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_quick_insights(request):
    """
    GET /analytics/api/quick-insights/
    Retourne un résumé rapide des insights AI pour le dashboard
    """
    from .ai_reports import AIReportGenerator
    
    user = request.user
    period = request.GET.get('period', 'day')
    
    try:
        # Générer le rapport AI
        generator = AIReportGenerator(user)
        report = generator.generate_comprehensive_report(period)
        
        # Créer un résumé compact pour le dashboard
        quick_insights = {
            'security': {
                'score': report['security']['score'],
                'level': report['security']['level'],
                'risks_count': len(report['security']['risks'])
            },
            'summary': {
                'total_detections': report['summary']['total_detections'],
                'suspicious_count': report['summary']['suspicious_detections'],
                'trend': report['summary']['trend'],
                'change_percent': report['summary']['change_percent']
            },
            'top_objects': report['trends']['top_objects'][:5] if report['trends']['top_objects'] else [],
            'top_recommendation': report['recommendations'][0] if report['recommendations'] else None,
            'patterns_count': len(report['patterns']['anomalies']) if report['patterns']['anomalies'] else 0,
            'has_predictions': report['predictions'] is not None
        }
        
        return JsonResponse({
            'success': True,
            'data': quick_insights,
            'period': period,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Erreur lors de la génération des insights AI'
        }, status=500)
