from django.urls import path
from . import views
from . import api_views

app_name = 'analytics'

urlpatterns = [
    # Dashboard principal
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Tendances d'objets
    path('trends/', views.object_trends_view, name='trends'),
    
    # Alertes de sécurité
    path('alerts/', views.security_alerts_view, name='alerts'),
    path('alerts/<int:pk>/', views.alert_detail_view, name='alert_detail'),
    path('alerts/<int:pk>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    
    # Insights
    path('insights/', views.insights_view, name='insights'),
    
    # API endpoints (legacy)
    path('api/data/', views.analytics_api, name='api_data'),
    
    # Rapports
    path('report/', views.generate_report, name='report'),
    
    # === API REST COMPLÈTE ===
    
    # Stats et résumés
    path('api/stats/summary/', api_views.api_stats_summary, name='api_stats_summary'),
    path('api/health/', api_views.api_health_check, name='api_health'),
    
    # Tendances
    path('api/trends/', api_views.api_trends_list, name='api_trends_list'),
    
    # Alertes
    path('api/alerts/', api_views.api_alerts_list, name='api_alerts_list'),
    path('api/alerts/<int:alert_id>/acknowledge/', api_views.api_alert_acknowledge, name='api_alert_acknowledge'),
    
    # Insights
    path('api/insights/', api_views.api_insights_list, name='api_insights_list'),
    
    # Analytics périodiques
    path('api/analytics/period/', api_views.api_period_analytics, name='api_period_analytics'),
    path('api/analytics/generate/', api_views.api_generate_analytics, name='api_generate_analytics'),
    
    # Graphiques
    path('api/charts/detections/', api_views.api_chart_data, name='api_chart_data'),
    
    # Anomalies
    path('api/anomalies/detect/', api_views.api_detect_anomalies, name='api_detect_anomalies'),
]
