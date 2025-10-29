from django.urls import path
from . import views

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
    
    # API endpoints
    path('api/data/', views.analytics_api, name='api_data'),
    
    # Rapports
    path('report/', views.generate_report, name='report'),
]
