from django.urls import path
from . import views

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
    
    # API
    path('api/updates/', views.notifications_api, name='api_updates'),
]
