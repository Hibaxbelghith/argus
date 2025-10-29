from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from .models import (
    DetectionAnalytics, 
    ObjectTrend, 
    SecurityAlert, 
    AnalyticsInsight
)
from .services import AnalyticsEngine, SecurityAlertService
from detection.models import DetectionResult
import json


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard with overview and insights
    """
    user = request.user
    
    # Générer les analytics du jour si nécessaire
    today_analytics = AnalyticsEngine.generate_period_analytics(user, 'daily')
    
    # Analytics de la semaine
    week_start = timezone.now() - timedelta(days=7)
    weekly_detections = DetectionResult.objects.filter(
        user=user,
        uploaded_at__gte=week_start
    )
    
    # Statistiques générales
    total_detections = DetectionResult.objects.filter(user=user).count()
    total_objects = sum(d.objects_detected for d in DetectionResult.objects.filter(user=user))
    
    # Top objets détectés
    top_trends = ObjectTrend.objects.filter(user=user).order_by('-detection_count')[:10]
    
    # Alertes de sécurité
    alert_summary = SecurityAlertService.get_alert_summary(user)
    
    # Insights récents
    recent_insights = AnalyticsInsight.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score', '-created_at')[:5]
    
    # Analytics des 7 derniers jours
    daily_analytics = DetectionAnalytics.objects.filter(
        user=user,
        period_type='daily'
    ).order_by('-period_start')[:7]
    
    # Préparer les données pour les graphiques
    chart_data = {
        'labels': [a.period_start.strftime('%d/%m') for a in reversed(daily_analytics)],
        'detections': [a.total_detections for a in reversed(daily_analytics)],
        'objects': [a.total_objects_detected for a in reversed(daily_analytics)],
    }
    
    context = {
        'today_analytics': today_analytics,
        'total_detections': total_detections,
        'total_objects': total_objects,
        'weekly_count': weekly_detections.count(),
        'top_trends': top_trends,
        'alert_summary': alert_summary,
        'recent_insights': recent_insights,
        'chart_data': json.dumps(chart_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def object_trends_view(request):
    """
    View to display object detection trends
    """
    user = request.user
    
    # Mettre à jour les tendances
    AnalyticsEngine.update_object_trends(user)
    
    # Récupérer toutes les tendances
    trends = ObjectTrend.objects.filter(user=user).order_by('-detection_count')
    
    # Filtrer par anomalie si demandé
    show_anomalies = request.GET.get('anomalies', 'false') == 'true'
    if show_anomalies:
        trends = trends.filter(is_anomaly=True)
    
    context = {
        'trends': trends,
        'show_anomalies': show_anomalies,
    }
    
    return render(request, 'analytics/trends.html', context)


@login_required
def security_alerts_view(request):
    """
    View to display and manage security alerts
    """
    user = request.user
    
    # Filtrer par sévérité si demandé
    severity = request.GET.get('severity', None)
    
    if severity:
        alerts = SecurityAlert.objects.filter(user=user, severity=severity)
    else:
        alerts = SecurityAlert.objects.filter(user=user)
    
    alerts = alerts.order_by('-created_at')
    
    # Statistiques
    alert_stats = {
        'total': SecurityAlert.objects.filter(user=user).count(),
        'unread': SecurityAlert.objects.filter(user=user, is_read=False).count(),
        'critical': SecurityAlert.objects.filter(user=user, severity='critical').count(),
        'high': SecurityAlert.objects.filter(user=user, severity='high').count(),
        'medium': SecurityAlert.objects.filter(user=user, severity='medium').count(),
        'low': SecurityAlert.objects.filter(user=user, severity='low').count(),
    }
    
    context = {
        'alerts': alerts,
        'alert_stats': alert_stats,
        'current_severity': severity,
    }
    
    return render(request, 'analytics/alerts.html', context)


@login_required
def alert_detail_view(request, pk):
    """
    View alert details
    """
    alert = get_object_or_404(SecurityAlert, pk=pk, user=request.user)
    
    # Marquer comme lu
    if not alert.is_read:
        alert.is_read = True
        alert.save()
    
    context = {
        'alert': alert,
        'context_data': alert.get_context_data(),
    }
    
    return render(request, 'analytics/alert_detail.html', context)


@login_required
def acknowledge_alert(request, pk):
    """
    Acknowledge an alert
    """
    alert = get_object_or_404(SecurityAlert, pk=pk, user=request.user)
    alert.acknowledge()
    
    return redirect('analytics:alerts')


@login_required
def insights_view(request):
    """
    View AI-generated insights
    """
    user = request.user
    
    # Générer de nouveaux insights
    AnalyticsEngine.generate_insights(user)
    
    # Récupérer les insights actifs
    insights = AnalyticsInsight.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score', '-created_at')
    
    context = {
        'insights': insights,
    }
    
    return render(request, 'analytics/insights.html', context)


@login_required
def analytics_api(request):
    """
    API endpoint for analytics data (for AJAX requests)
    """
    user = request.user
    period_type = request.GET.get('period', 'daily')
    
    # Récupérer les analytics
    if period_type == 'daily':
        analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_type='daily'
        ).order_by('-period_start')[:30]
    elif period_type == 'weekly':
        analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_type='weekly'
        ).order_by('-period_start')[:12]
    else:
        analytics = DetectionAnalytics.objects.filter(
            user=user,
            period_type='monthly'
        ).order_by('-period_start')[:12]
    
    # Formater les données
    data = {
        'labels': [a.period_start.strftime('%d/%m/%Y') for a in reversed(analytics)],
        'detections': [a.total_detections for a in reversed(analytics)],
        'objects': [a.total_objects_detected for a in reversed(analytics)],
        'suspicious': [a.suspicious_objects_count for a in reversed(analytics)],
    }
    
    return JsonResponse(data)


@login_required
def generate_report(request):
    """
    Generate analytics report
    """
    user = request.user
    period = request.GET.get('period', 'weekly')
    
    if period == 'weekly':
        period_start = timezone.now() - timedelta(days=7)
    elif period == 'monthly':
        period_start = timezone.now() - timedelta(days=30)
    else:
        period_start = timezone.now() - timedelta(days=1)
    
    # Récupérer les données
    detections = DetectionResult.objects.filter(
        user=user,
        uploaded_at__gte=period_start
    )
    
    analytics = DetectionAnalytics.objects.filter(
        user=user,
        period_start__gte=period_start
    )
    
    alerts = SecurityAlert.objects.filter(
        user=user,
        created_at__gte=period_start
    )
    
    trends = ObjectTrend.objects.filter(user=user).order_by('-detection_count')[:10]
    
    context = {
        'period': period,
        'period_start': period_start,
        'detections': detections,
        'analytics': analytics,
        'alerts': alerts,
        'trends': trends,
        'total_detections': detections.count(),
        'total_objects': sum(d.objects_detected for d in detections),
        'critical_alerts': alerts.filter(severity='critical').count(),
    }
    
    return render(request, 'analytics/report.html', context)
