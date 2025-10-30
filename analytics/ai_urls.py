"""
URL Configuration for AI-Powered Analytics API
Routes pour l'intelligence artificielle et les recommandations
"""
from django.urls import path
from . import ai_api_views as ai_api

app_name = 'analytics_ai'

urlpatterns = [
    # ============ AI RECOMMENDATION SYSTEM ============
    
    # Recommandations intelligentes
    path('api/ai/recommendations/', ai_api.api_ai_recommendations, name='ai_recommendations'),
    
    # Insights IA
    path('api/ai/insights/', ai_api.api_ai_insights, name='ai_insights'),
    
    # Prédictions d'activité
    path('api/ai/predict-activity/', ai_api.api_ai_predict_activity, name='ai_predict_activity'),
    
    # Recherche intelligente avec NLP
    path('api/ai/smart-search/', ai_api.api_ai_smart_search, name='ai_smart_search'),
    
    # Évaluation des risques
    path('api/ai/risk-assessment/', ai_api.api_ai_risk_assessment, name='ai_risk_assessment'),
    
    # Suggestions d'optimisation
    path('api/ai/optimization/', ai_api.api_ai_optimization_suggestions, name='ai_optimization'),
    
    # Dashboard IA résumé
    path('api/ai/dashboard/', ai_api.api_ai_dashboard_summary, name='ai_dashboard'),
]
