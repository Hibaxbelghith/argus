from django.urls import path
from . import views
from . import api_views

app_name = 'notifications'

urlpatterns = [
    # Dashboard principal
    path('', views.notifications_dashboard, name='dashboard'),
    
    # Notifications individuelles
    path('<int:pk>/', views.notification_detail, name='detail'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # Préférences
    path('preferences/', views.preferences_view, name='preferences'),
    
    # Règles de notification
    path('rules/', views.rules_view, name='rules'),
    path('rules/create/', views.create_rule, name='create_rule'),
    path('rules/<int:pk>/toggle/', views.toggle_rule, name='toggle_rule'),
    path('rules/<int:pk>/delete/', views.delete_rule, name='delete_rule'),
    
    # Alertes prédictives
    path('predictive/', views.predictive_alerts_view, name='predictive'),
    
    # API (legacy)
    path('api/updates/', views.notifications_api, name='api_updates'),
    
    # === API REST COMPLÈTE ===
    
    # Notifications
    path('api/list/', api_views.api_notifications_list, name='api_list'),
    path('api/<int:notification_id>/mark-read/', api_views.api_notification_mark_read, name='api_mark_read'),
    path('api/mark-all-read/', api_views.api_mark_all_read, name='api_mark_all_read'),
    path('api/stats/', api_views.api_notifications_stats, name='api_stats'),
    path('api/<int:notification_id>/logs/', api_views.api_notification_logs, name='api_logs'),
    
    # Préférences
    path('api/preferences/', api_views.api_preferences_get, name='api_preferences_get'),
    path('api/preferences/update/', api_views.api_preferences_update, name='api_preferences_update'),
    
    # Règles
    path('api/rules/', api_views.api_rules_list, name='api_rules_list'),
    path('api/rules/create/', api_views.api_rule_create, name='api_rule_create'),
    path('api/rules/<int:rule_id>/toggle/', api_views.api_rule_toggle, name='api_rule_toggle'),
    path('api/rules/<int:rule_id>/delete/', api_views.api_rule_delete, name='api_rule_delete'),
    
    # Prédictif
    path('api/predictive/', api_views.api_predictive_alerts, name='api_predictive'),
    
    # Utilitaires
    path('api/test/', api_views.api_test_notification, name='api_test'),
    path('api/health/', api_views.api_health_check, name='api_health'),
]
