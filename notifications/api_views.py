"""
API REST pour le module Notifications
Fournit des endpoints JSON pour la gestion des notifications
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
import json

from .models import (
    Notification,
    NotificationPreference,
    NotificationRule,
    NotificationLog,
    PredictiveAlert
)
from .services import NotificationService, PredictiveAnalyticsService


@login_required
@require_http_methods(["GET"])
def api_notifications_list(request):
    """
    GET /notifications/api/list/
    Retourne la liste des notifications
    Paramètres:
        - unread_only: true/false
        - limit: nombre de résultats
        - type: alert/insight/report/system
        - severity: low/medium/high/critical
    """
    user = request.user
    
    # Filtres
    unread_only = request.GET.get('unread_only', 'false') == 'true'
    limit = int(request.GET.get('limit', 50))
    notif_type = request.GET.get('type')
    severity = request.GET.get('severity')
    
    # Query
    notifications = Notification.objects.filter(user=user)
    
    if unread_only:
        notifications = notifications.filter(read_at__isnull=True)
    
    if notif_type:
        notifications = notifications.filter(notification_type=notif_type)
    
    if severity:
        notifications = notifications.filter(severity=severity)
    
    notifications = notifications.order_by('-created_at')[:limit]
    
    # Sérialiser
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'severity': notif.severity,
            'delivery_method': notif.delivery_method,
            'status': notif.status,
            'is_read': notif.read_at is not None,
            'is_aggregated': notif.is_aggregated,
            'created_at': notif.created_at.isoformat(),
            'read_at': notif.read_at.isoformat() if notif.read_at else None,
            'metadata': notif.get_metadata(),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def api_notification_mark_read(request, notification_id):
    """
    POST /notifications/api/<id>/mark-read/
    Marque une notification comme lue
    """
    user = request.user
    
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        
        if not notification.read_at:
            notification.read_at = timezone.now()
            notification.save()
            
            # Logger l'action
            NotificationLog.objects.create(
                notification=notification,
                event='marked_read',
                details='Notification marquée comme lue via API'
            )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification marquée comme lue',
            'notification_id': notification.id,
            'timestamp': timezone.now().isoformat()
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Notification non trouvée'
        }, status=404)


@login_required
@require_http_methods(["POST"])
def api_mark_all_read(request):
    """
    POST /notifications/api/mark-all-read/
    Marque toutes les notifications comme lues
    """
    user = request.user
    
    # Marquer toutes les notifications non lues
    updated = Notification.objects.filter(
        user=user,
        read_at__isnull=True
    ).update(read_at=timezone.now())
    
    return JsonResponse({
        'status': 'success',
        'message': f'{updated} notification(s) marquée(s) comme lue(s)',
        'count': updated,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_notifications_stats(request):
    """
    GET /notifications/api/stats/
    Retourne les statistiques des notifications
    """
    user = request.user
    
    # Statistiques globales
    stats = Notification.objects.filter(user=user).aggregate(
        total=Count('id'),
        unread=Count('id', filter=Q(read_at__isnull=True)),
        by_severity_critical=Count('id', filter=Q(severity='critical')),
        by_severity_high=Count('id', filter=Q(severity='high')),
        by_severity_medium=Count('id', filter=Q(severity='medium')),
        by_severity_low=Count('id', filter=Q(severity='low')),
        sent=Count('id', filter=Q(status='sent')),
        pending=Count('id', filter=Q(status='pending')),
        failed=Count('id', filter=Q(status='failed')),
    )
    
    # Stats par type
    by_type = {}
    for notif_type in ['alert', 'insight', 'report', 'system']:
        by_type[notif_type] = Notification.objects.filter(
            user=user,
            notification_type=notif_type
        ).count()
    
    # Stats dernière semaine
    week_ago = timezone.now() - timedelta(days=7)
    weekly_count = Notification.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).count()
    
    return JsonResponse({
        'status': 'success',
        'stats': {
            'global': stats,
            'by_type': by_type,
            'weekly_count': weekly_count,
        },
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["GET"])
def api_preferences_get(request):
    """
    GET /notifications/api/preferences/
    Retourne les préférences de notification de l'utilisateur
    """
    user = request.user
    
    try:
        prefs = NotificationPreference.objects.get(user=user)
        
        return JsonResponse({
            'status': 'success',
            'preferences': {
                'enabled_methods': prefs.get_enabled_methods(),
                'min_severity_web': prefs.min_severity_web,
                'min_severity_email': prefs.min_severity_email,
                'min_severity_sms': prefs.min_severity_sms,
                'quiet_hours_enabled': prefs.quiet_hours_enabled,
                'quiet_hours_start': prefs.quiet_hours_start.isoformat() if prefs.quiet_hours_start else None,
                'quiet_hours_end': prefs.quiet_hours_end.isoformat() if prefs.quiet_hours_end else None,
                'enable_aggregation': prefs.enable_aggregation,
                'aggregation_window_minutes': prefs.aggregation_window_minutes,
                'max_notifications_per_hour': prefs.max_notifications_per_hour,
                'notify_suspicious_objects': prefs.notify_suspicious_objects,
                'notify_anomalies': prefs.notify_anomalies,
                'notify_high_frequency': prefs.notify_high_frequency,
                'notify_unusual_time': prefs.notify_unusual_time,
            },
            'timestamp': timezone.now().isoformat()
        })
    except NotificationPreference.DoesNotExist:
        # Créer des préférences par défaut
        prefs = NotificationPreference.objects.create(user=user)
        return api_preferences_get(request)


@login_required
@require_http_methods(["POST"])
def api_preferences_update(request):
    """
    POST /notifications/api/preferences/update/
    Met à jour les préférences de notification
    Body JSON: {
        "enabled_methods": ["web", "email"],
        "min_severity_email": "high",
        ...
    }
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        prefs, created = NotificationPreference.objects.get_or_create(user=user)
        
        # Mettre à jour les champs fournis
        if 'enabled_methods' in data:
            prefs.set_enabled_methods(data['enabled_methods'])
        
        for field in ['min_severity_web', 'min_severity_email', 'min_severity_sms',
                      'quiet_hours_enabled', 'enable_aggregation',
                      'aggregation_window_minutes', 'max_notifications_per_hour',
                      'notify_suspicious_objects', 'notify_anomalies',
                      'notify_high_frequency', 'notify_unusual_time']:
            if field in data:
                setattr(prefs, field, data[field])
        
        prefs.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Préférences mises à jour avec succès',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_rules_list(request):
    """
    GET /notifications/api/rules/
    Retourne la liste des règles de notification
    Paramètres:
        - active_only: true/false
    """
    user = request.user
    
    active_only = request.GET.get('active_only', 'false') == 'true'
    
    rules = NotificationRule.objects.filter(user=user)
    
    if active_only:
        rules = rules.filter(is_active=True)
    
    rules = rules.order_by('-priority', '-created_at')
    
    # Sérialiser
    data = []
    for rule in rules:
        data.append({
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'condition_type': rule.condition_type,
            'condition_value': rule.get_condition_value(),
            'action': rule.action,
            'action_parameters': rule.get_action_parameters(),
            'is_active': rule.is_active,
            'priority': rule.priority,
            'created_at': rule.created_at.isoformat(),
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'data': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def api_rule_create(request):
    """
    POST /notifications/api/rules/create/
    Crée une nouvelle règle de notification
    Body JSON: {
        "name": "Alerte armes",
        "condition_type": "object_class",
        "condition_value": {"classes": ["knife", "gun"]},
        "action": "notify",
        "priority": 10
    }
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        
        rule = NotificationRule.objects.create(
            user=user,
            name=data.get('name'),
            description=data.get('description', ''),
            condition_type=data.get('condition_type'),
            action=data.get('action', 'notify'),
            priority=data.get('priority', 0),
            is_active=data.get('is_active', True)
        )
        
        # Définir les valeurs JSON
        if 'condition_value' in data:
            rule.set_condition_value(data['condition_value'])
        
        if 'action_parameters' in data:
            rule.set_action_parameters(data['action_parameters'])
        
        rule.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Règle créée avec succès',
            'rule_id': rule.id,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def api_rule_toggle(request, rule_id):
    """
    POST /notifications/api/rules/<id>/toggle/
    Active/désactive une règle
    """
    user = request.user
    
    try:
        rule = NotificationRule.objects.get(id=rule_id, user=user)
        rule.is_active = not rule.is_active
        rule.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Règle {"activée" if rule.is_active else "désactivée"}',
            'rule_id': rule.id,
            'is_active': rule.is_active,
            'timestamp': timezone.now().isoformat()
        })
    except NotificationRule.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Règle non trouvée'
        }, status=404)


@login_required
@require_http_methods(["DELETE"])
def api_rule_delete(request, rule_id):
    """
    DELETE /notifications/api/rules/<id>/delete/
    Supprime une règle
    """
    user = request.user
    
    try:
        rule = NotificationRule.objects.get(id=rule_id, user=user)
        rule.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Règle supprimée avec succès',
            'timestamp': timezone.now().isoformat()
        })
    except NotificationRule.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Règle non trouvée'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def api_predictive_alerts(request):
    """
    GET /notifications/api/predictive/
    Génère et retourne les alertes prédictives
    """
    user = request.user
    
    # Générer les prédictions
    predictions = PredictiveAnalyticsService.generate_predictions(user)
    
    # Sérialiser
    data = []
    for pred in predictions:
        data.append({
            'id': pred.id,
            'prediction_type': pred.prediction_type,
            'title': pred.title,
            'description': pred.description,
            'predicted_event': pred.predicted_event,
            'confidence_score': float(pred.confidence_score),
            'timeframe_start': pred.predicted_timeframe_start.isoformat(),
            'timeframe_end': pred.predicted_timeframe_end.isoformat(),
            'recommendations': pred.recommendations,
            'supporting_data': pred.get_supporting_data(),
            'is_active': pred.is_active,
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'predictions': data,
        'timestamp': timezone.now().isoformat()
    })


@login_required
@require_http_methods(["POST"])
def api_test_notification(request):
    """
    POST /notifications/api/test/
    Envoie une notification de test
    Body JSON: {
        "method": "web|email|sms",
        "message": "Test message"
    }
    """
    user = request.user
    
    try:
        data = json.loads(request.body)
        method = data.get('method', 'web')
        message = data.get('message', 'Ceci est une notification de test')
        
        # Créer notification de test
        notification = Notification.objects.create(
            user=user,
            notification_type='system',
            title='Test de Notification',
            message=message,
            severity='low',
            delivery_method=method,
            status='sent',
            sent_at=timezone.now()
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Notification de test envoyée via {method}',
            'notification_id': notification.id,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def api_notification_logs(request, notification_id):
    """
    GET /notifications/api/<id>/logs/
    Retourne l'historique d'une notification
    """
    user = request.user
    
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        logs = NotificationLog.objects.filter(notification=notification).order_by('-timestamp')
        
        data = []
        for log in logs:
            data.append({
                'event': log.event,
                'details': log.details,
                'timestamp': log.timestamp.isoformat(),
            })
        
        return JsonResponse({
            'status': 'success',
            'notification_id': notification.id,
            'logs': data,
            'timestamp': timezone.now().isoformat()
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Notification non trouvée'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def api_health_check(request):
    """
    GET /notifications/api/health/
    Vérifie l'état du module notifications
    """
    user = request.user
    
    # Compter les éléments
    stats = {
        'notifications_count': Notification.objects.filter(user=user).count(),
        'unread_count': Notification.objects.filter(user=user, read_at__isnull=True).count(),
        'rules_count': NotificationRule.objects.filter(user=user).count(),
        'active_rules_count': NotificationRule.objects.filter(user=user, is_active=True).count(),
        'predictive_alerts_count': PredictiveAlert.objects.filter(user=user, is_active=True).count(),
    }
    
    # Vérifier préférences
    has_preferences = NotificationPreference.objects.filter(user=user).exists()
    
    return JsonResponse({
        'status': 'healthy',
        'module': 'notifications',
        'stats': stats,
        'has_preferences': has_preferences,
        'timestamp': timezone.now().isoformat()
    })
