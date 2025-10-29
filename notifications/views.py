from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import (
    Notification,
    NotificationPreference,
    NotificationRule,
    PredictiveAlert
)
from .services import NotificationService, PredictiveAnalyticsService


@login_required
def notifications_dashboard(request):
    """
    Main notifications dashboard
    """
    user = request.user
    
    # Récupérer les notifications non lues
    unread_notifications = NotificationService.get_unread_notifications(user, limit=20)
    
    # Récupérer les notifications agrégées
    aggregated = NotificationService.get_aggregated_notifications(user)
    
    # Statistiques
    total_count = Notification.objects.filter(user=user).count()
    unread_count = Notification.objects.filter(user=user, read_at__isnull=True).count()
    
    context = {
        'unread_notifications': unread_notifications,
        'aggregated_notifications': aggregated,
        'total_count': total_count,
        'unread_count': unread_count,
    }
    
    return render(request, 'notifications/dashboard.html', context)


@login_required
def notification_detail(request, pk):
    """
    View notification details
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    # Marquer comme lu
    notification.mark_as_read()
    
    context = {
        'notification': notification,
        'metadata': notification.metadata,
    }
    
    return render(request, 'notifications/detail.html', context)


@login_required
def mark_all_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(
        user=request.user,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    messages.success(request, "✅ Toutes les notifications ont été marquées comme lues.")
    return redirect('notifications:dashboard')


@login_required
def preferences_view(request):
    """
    View and edit notification preferences
    """
    user = request.user
    preferences, created = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={
            'enabled_methods': ['web'],
            'min_severity_web': 'low',
            'min_severity_email': 'high',
            'min_severity_sms': 'critical',
        }
    )
    
    if request.method == 'POST':
        # Mettre à jour les préférences
        preferences.enabled_methods = request.POST.getlist('enabled_methods')
        preferences.min_severity_web = request.POST.get('min_severity_web', 'low')
        preferences.min_severity_email = request.POST.get('min_severity_email', 'high')
        preferences.min_severity_sms = request.POST.get('min_severity_sms', 'critical')
        
        preferences.quiet_hours_enabled = request.POST.get('quiet_hours_enabled') == 'on'
        preferences.quiet_hours_start = request.POST.get('quiet_hours_start') or None
        preferences.quiet_hours_end = request.POST.get('quiet_hours_end') or None
        
        preferences.enable_aggregation = request.POST.get('enable_aggregation') == 'on'
        preferences.aggregation_window_minutes = int(request.POST.get('aggregation_window_minutes', 30))
        
        preferences.max_notifications_per_hour = int(request.POST.get('max_notifications_per_hour', 10))
        
        preferences.notify_suspicious_objects = request.POST.get('notify_suspicious_objects') == 'on'
        preferences.notify_anomalies = request.POST.get('notify_anomalies') == 'on'
        preferences.notify_high_frequency = request.POST.get('notify_high_frequency') == 'on'
        preferences.notify_unusual_time = request.POST.get('notify_unusual_time') == 'on'
        
        preferences.save()
        
        messages.success(request, "✅ Préférences mises à jour avec succès.")
        return redirect('notifications:preferences')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'notifications/preferences.html', context)


@login_required
def rules_view(request):
    """
    View and manage notification rules
    """
    user = request.user
    rules = NotificationRule.objects.filter(user=user).order_by('-priority', 'name')
    
    context = {
        'rules': rules,
    }
    
    return render(request, 'notifications/rules.html', context)


@login_required
def create_rule(request):
    """
    Create a new notification rule
    """
    if request.method == 'POST':
        rule = NotificationRule.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            condition_type=request.POST.get('condition_type'),
            condition_value={},  # À compléter selon le type de condition
            action=request.POST.get('action'),
            action_parameters={},
            priority=int(request.POST.get('priority', 0))
        )
        
        messages.success(request, f"✅ Règle '{rule.name}' créée avec succès.")
        return redirect('notifications:rules')
    
    return render(request, 'notifications/create_rule.html')


@login_required
def toggle_rule(request, pk):
    """
    Toggle rule active status
    """
    rule = get_object_or_404(NotificationRule, pk=pk, user=request.user)
    rule.is_active = not rule.is_active
    rule.save()
    
    status = "activée" if rule.is_active else "désactivée"
    messages.success(request, f"✅ Règle '{rule.name}' {status}.")
    return redirect('notifications:rules')


@login_required
def delete_rule(request, pk):
    """
    Delete a notification rule
    """
    rule = get_object_or_404(NotificationRule, pk=pk, user=request.user)
    name = rule.name
    rule.delete()
    
    messages.success(request, f"✅ Règle '{name}' supprimée.")
    return redirect('notifications:rules')


@login_required
def predictive_alerts_view(request):
    """
    View predictive alerts
    """
    user = request.user
    
    # Générer de nouvelles prédictions
    PredictiveAnalyticsService.generate_trend_predictions(user)
    PredictiveAnalyticsService.generate_anomaly_forecast(user)
    risk_assessment = PredictiveAnalyticsService.assess_security_risk(user)
    
    # Récupérer les prédictions actives
    predictions = PredictiveAlert.objects.filter(
        user=user,
        is_active=True
    ).order_by('-confidence_score', '-created_at')
    
    context = {
        'predictions': predictions,
        'risk_assessment': risk_assessment,
    }
    
    return render(request, 'notifications/predictive.html', context)


@login_required
def notifications_api(request):
    """
    API endpoint for real-time notifications
    """
    user = request.user
    
    # Récupérer les nouvelles notifications
    last_check = request.GET.get('since')
    
    notifications = Notification.objects.filter(
        user=user,
        status='sent',
        read_at__isnull=True
    )
    
    if last_check:
        try:
            from datetime import datetime
            last_check_time = datetime.fromisoformat(last_check)
            notifications = notifications.filter(created_at__gt=last_check_time)
        except:
            pass
    
    notifications = notifications.order_by('-created_at')[:10]
    
    data = {
        'count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'severity': n.severity,
                'type': n.notification_type,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications
        ]
    }
    
    return JsonResponse(data)
