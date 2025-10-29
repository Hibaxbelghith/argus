from django.urls import path, include
from . import views
from . import api_views
from . import ai_api_views

app_name = 'analytics'

urlpatterns = [
    # Dashboard principal
    path('', views.analytics_dashboard, name='dashboard'),
    
    # Dashboard IA avec recommandations
    path('ai-dashboard/', views.ai_dashboard_view, name='ai_dashboard_view'),
    
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
    path('ai-report/', views.ai_report_view, name='ai_report'),
    path('download-report/', views.download_report_json, name='download_report'),
    
    # === API REST COMPLÈTE ===
    
    # Stats et résumés
    path('api/stats/summary/', api_views.api_stats_summary, name='api_stats_summary'),
    path('api/quick-insights/', api_views.api_quick_insights, name='api_quick_insights'),
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
    
    # ============ AI-POWERED API ============
    
    # Recommandations IA
    path('api/ai/recommendations/', ai_api_views.api_ai_recommendations, name='ai_recommendations'),
    path('api/ai/insights/', ai_api_views.api_ai_insights, name='ai_insights'),
    path('api/ai/dashboard/', ai_api_views.api_ai_dashboard_summary, name='ai_dashboard'),
    
    # Prédictions et analyse
    path('api/ai/predict-activity/', ai_api_views.api_ai_predict_activity, name='ai_predict_activity'),
    path('api/ai/risk-assessment/', ai_api_views.api_ai_risk_assessment, name='ai_risk_assessment'),
    
    # Recherche et optimisation
    path('api/ai/smart-search/', ai_api_views.api_ai_smart_search, name='ai_smart_search'),
    path('api/ai/optimization/', ai_api_views.api_ai_optimization_suggestions, name='ai_optimization'),
    
    # Gestion des recommandations sauvegardées
    path('api/ai/recommendations/save/', ai_api_views.api_save_recommendation, name='ai_save_recommendation'),
    path('api/ai/recommendations/saved/', ai_api_views.api_list_saved_recommendations, name='ai_list_saved_recommendations'),
    path('api/ai/recommendations/<int:rec_id>/status/', ai_api_views.api_update_recommendation_status, name='ai_update_recommendation_status'),
    path('api/ai/recommendations/<int:rec_id>/feedback/', ai_api_views.api_recommendation_feedback, name='ai_recommendation_feedback'),
    path('api/ai/recommendations/generate-save/', ai_api_views.api_generate_and_save_recommendations, name='ai_generate_save_recommendations'),
]
