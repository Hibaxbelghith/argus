from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import timedelta, datetime
from .models import (
    DetectionAnalytics, 
    ObjectTrend, 
    SecurityAlert, 
    AnalyticsInsight
)
from .services import AnalyticsEngine, SecurityAlertService
from detection.models import DetectionResult
import json
from collections import defaultdict


@login_required
def analytics_dashboard(request):
    """
    Dashboard Analytics principal avec rapports AI
    """
    user = request.user
    
    # Générer le rapport AI complet
    from .ai_reports import AIReportGenerator
    
    period = request.GET.get('period', 'week')
    report_generator = AIReportGenerator(user)
    ai_report = report_generator.generate_comprehensive_report(period)
    
    # Récupérer les détections récentes
    recent_detections = DetectionResult.objects.filter(user=user).order_by('-uploaded_at')[:10]
    
    # Alertes de sécurité actives
    active_alerts = SecurityAlert.objects.filter(
        user=user,
        is_acknowledged=False
    ).order_by('-created_at')[:5]
    
    # Insights récents
    recent_insights = AnalyticsInsight.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score', '-created_at')[:5]
    
    # Préparer les données pour les graphiques
    if ai_report['trends']['daily_distribution']:
        chart_labels = list(ai_report['trends']['daily_distribution'].keys())
        chart_values = list(ai_report['trends']['daily_distribution'].values())
    else:
        chart_labels = []
        chart_values = []
    
    # Statistiques d'alertes pour le template
    alert_summary = {
        'total': SecurityAlert.objects.filter(user=user).count(),
        'unread': SecurityAlert.objects.filter(user=user, is_read=False).count(),
        'critical': SecurityAlert.objects.filter(user=user, severity='critical', is_acknowledged=False).count(),
        'high': SecurityAlert.objects.filter(user=user, severity='high', is_acknowledged=False).count(),
        'medium': SecurityAlert.objects.filter(user=user, severity='medium', is_acknowledged=False).count(),
        'low': SecurityAlert.objects.filter(user=user, severity='low', is_acknowledged=False).count(),
    }
    
    # Préparer les données pour le graphique horaire
    hourly_dist = ai_report['trends'].get('hourly_distribution', {})
    hourly_labels = [f"{h}h" for h in range(24)]
    hourly_values = [hourly_dist.get(h, 0) for h in range(24)]
    
    # Récupérer les tendances d'objets pour l'affichage
    top_trends = ObjectTrend.objects.filter(user=user).order_by('-detection_count')[:10]
    
    context = {
        'ai_report': ai_report,
        'period': period,
        'recent_detections': recent_detections,
        'active_alerts': active_alerts,
        'recent_insights': recent_insights,
        'alert_summary': alert_summary,
        'top_trends': top_trends,
        'chart_data': {
            'labels': chart_labels,
            'values': chart_values
        },
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'hourly_labels': json.dumps(hourly_labels),
        'hourly_values': json.dumps(hourly_values),
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


@login_required
def ai_report_view(request):
    """
    Génère et affiche un rapport AI détaillé
    """
    from .ai_reports import AIReportGenerator
    
    user = request.user
    period = request.GET.get('period', 'week')
    
    # Générer le rapport AI
    report_generator = AIReportGenerator(user)
    ai_report = report_generator.generate_comprehensive_report(period)
    
    context = {
        'ai_report': ai_report,
        'period': period,
        'user': user,
    }
    
    return render(request, 'analytics/ai_report.html', context)


@login_required
def download_report_json(request):
    """
    Télécharge le rapport au format JSON
    """
    from .ai_reports import AIReportGenerator
    import json
    from django.http import JsonResponse
    
    user = request.user
    period = request.GET.get('period', 'week')
    
    # Générer le rapport
    report_generator = AIReportGenerator(user)
    ai_report = report_generator.generate_comprehensive_report(period)
    
    # Convertir les dates en strings pour JSON
    ai_report['start_date'] = ai_report['start_date'].isoformat()
    ai_report['end_date'] = ai_report['end_date'].isoformat()
    ai_report['generated_at'] = ai_report['generated_at'].isoformat()
    
    return JsonResponse(ai_report, json_dumps_params={'indent': 2})


@login_required
def ai_dashboard_view(request):
    """
    Dashboard IA avec recommandations intelligentes
    """
    from .ai_recommendation_system import RecommendationEngine, SmartRecommendationFilter
    from .models import AIRecommendation
    
    user = request.user
    
    # Générer des recommandations si demandé
    if request.GET.get('generate') == 'true':
        engine = RecommendationEngine(user)
        recommendations = engine.analyze_and_recommend(days=30)
        
        # Sauvegarder les recommandations haute priorité
        saved_count = 0
        for rec in recommendations:
            if rec['priority'] >= 4:  # High et Critical uniquement
                # Vérifier si existe déjà
                exists = AIRecommendation.objects.filter(
                    user=user,
                    title=rec['title'],
                    status__in=['pending', 'viewed']
                ).exists()
                
                if not exists:
                    AIRecommendation.objects.create(
                        user=user,
                        recommendation_type=rec.get('type', 'optimization'),
                        priority=rec.get('priority', 3),
                        impact=rec.get('impact', 'medium'),
                        title=rec.get('title', ''),
                        description=rec.get('description', ''),
                        action=rec.get('action', ''),
                        confidence=rec.get('confidence', 0.0),
                        metadata=json.dumps(rec.get('metadata', {})),
                        expires_at=timezone.now() + timedelta(days=30)
                    )
                    saved_count += 1
    
    # Récupérer les recommandations sauvegardées
    saved_recommendations = AIRecommendation.objects.filter(
        user=user,
        status__in=['pending', 'viewed']
    ).order_by('-priority', '-confidence')[:10]
    
    # Statistiques des recommandations
    rec_stats = {
        'total': AIRecommendation.objects.filter(user=user).count(),
        'pending': AIRecommendation.objects.filter(user=user, status='pending').count(),
        'acted': AIRecommendation.objects.filter(user=user, status='acted').count(),
        'by_type': {},
        'by_priority': {}
    }
    
    # Count by type
    from django.db.models import Count
    by_type = AIRecommendation.objects.filter(user=user).values('recommendation_type').annotate(count=Count('id'))
    for item in by_type:
        rec_stats['by_type'][item['recommendation_type']] = item['count']
    
    # Count by priority
    by_priority = AIRecommendation.objects.filter(user=user).values('priority').annotate(count=Count('id'))
    for item in by_priority:
        rec_stats['by_priority'][item['priority']] = item['count']
    
    # Score de santé
    week_ago = timezone.now() - timedelta(days=7)
    detections_week = DetectionResult.objects.filter(
        user=user,
        uploaded_at__gte=week_ago
    ).count()
    
    alerts_unread = SecurityAlert.objects.filter(
        user=user,
        is_read=False
    ).count()
    
    alerts_critical = SecurityAlert.objects.filter(
        user=user,
        severity='critical',
        is_read=False
    ).count()
    
    # Calculer le score de santé
    health_score = 100
    if alerts_critical > 0:
        health_score -= min(alerts_critical * 20, 40)
    if alerts_unread > 5:
        health_score -= min((alerts_unread - 5) * 5, 30)
    if detections_week < 7:
        health_score -= 20
    
    health_score = max(health_score, 0)
    
    # Statut de santé
    if health_score >= 80:
        health_status = 'excellent'
        health_label = 'Excellent'
        health_color = 'success'
    elif health_score >= 60:
        health_status = 'good'
        health_label = 'Bon'
        health_color = 'info'
    elif health_score >= 40:
        health_status = 'fair'
        health_label = 'Acceptable'
        health_color = 'warning'
    else:
        health_status = 'poor'
        health_label = 'Attention requise'
        health_color = 'danger'
    
    # Statistiques rapides
    quick_stats = {
        'detections_week': detections_week,
        'alerts_unread': alerts_unread,
        'alerts_critical': alerts_critical,
        'recommendations_pending': rec_stats['pending']
    }
    
    # Récupérer les insights récents
    recent_insights = AnalyticsInsight.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score', '-created_at')[:5]
    
    # Récupérer les alertes récentes
    recent_alerts = SecurityAlert.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    # Tendances d'objets
    top_trends = ObjectTrend.objects.filter(user=user).order_by('-detection_count')[:5]
    
    context = {
        'saved_recommendations': saved_recommendations,
        'rec_stats': rec_stats,
        'health': {
            'score': health_score,
            'status': health_status,
            'label': health_label,
            'color': health_color
        },
        'quick_stats': quick_stats,
        'recent_insights': recent_insights,
        'recent_alerts': recent_alerts,
        'top_trends': top_trends,
        'page_title': 'Dashboard IA - Recommandations'
    }
    
    return render(request, 'analytics/ai_dashboard.html', context)
