"""
URL Configuration for Advanced Analytics & Notifications APIs
"""
from django.urls import path
from . import advanced_api_views as api

app_name = 'analytics_advanced'

urlpatterns = [
    # ============ ANALYTICS AI ENDPOINTS ============
    # Natural Language Processing
    path('api/nlp-query/', api.api_nlp_query, name='nlp_query'),
    
    # Machine Learning & Predictions
    path('api/anomalies/', api.api_anomaly_detection, name='anomaly_detection'),
    path('api/predictions/', api.api_predictions_forecast, name='predictions'),
    path('api/patterns/', api.api_pattern_recognition, name='patterns'),
    
    # Recommendations & Insights
    path('api/recommendations/', api.api_recommendations, name='recommendations'),
    path('api/narrative-report/', api.api_generate_narrative_report, name='narrative_report'),
    
    # Visualizations
    path('api/visualizations/', api.api_visualizations, name='visualizations'),
    
    # Real-time Stats
    path('api/realtime-stats/', api.api_realtime_stats, name='realtime_stats'),
    
    # ============ NOTIFICATIONS AI ENDPOINTS ============
    # Notification Scoring & Intelligence
    path('api/notifications/score/', api.api_notification_score, name='notification_score'),
    path('api/notifications/behavioral-insights/', api.api_behavioral_insights, name='behavioral_insights'),
    path('api/notifications/adapt-preferences/', api.api_adapt_preferences, name='adapt_preferences'),
    
    # Predictive Alerts
    path('api/notifications/predictive-alerts/', api.api_predictive_alerts, name='predictive_alerts'),
    path('api/notifications/generate-predictive/', api.api_generate_predictive_alerts, name='generate_predictive'),
    
    # Notification Actions
    path('api/notifications/mark-read/', api.api_mark_notification_read, name='mark_read'),
    path('api/notifications/feedback/', api.api_notification_feedback, name='notification_feedback'),
]
