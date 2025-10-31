"""
AI API Views - Intelligence Artificielle pour Analytics
Fournit des endpoints avancés avec recommandations IA et analyses prédictives
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)


# ============ AI RECOMMENDATION SYSTEM ============

@login_required
@require_http_methods(["GET"])
def api_ai_recommendations(request):
    """
    GET /analytics/api/ai/recommendations/
    Génère des recommandations intelligentes basées sur l'IA
    
    Params:
        - days: période d'analyse (défaut: 30)
        - max_count: nombre max de recommandations (défaut: 10)
        - min_confidence: confiance minimale 0-1 (défaut: 0.6)
        - types: filtrer par types (security,optimization,behavior,alert,monitoring)
        - actionable_only: true pour ne retourner que les recommandations actionnables
    """
    try:
        from analytics.ai_recommendation_system import RecommendationEngine, SmartRecommendationFilter
        
        # Paramètres
        days = int(request.GET.get('days', 30))
        max_count = int(request.GET.get('max_count', 10))
        min_confidence = float(request.GET.get('min_confidence', 0.6))
        filter_types = request.GET.get('types', '').split(',') if request.GET.get('types') else None
        actionable_only = request.GET.get('actionable_only', 'false').lower() == 'true'
        
        # Générer recommandations
        engine = RecommendationEngine(request.user)
        recommendations = engine.analyze_and_recommend(days=days)
        
        # Filtrer par type si demandé
        if filter_types:
            recommendations = [r for r in recommendations if r.get('type') in filter_types]
        
        # Filtrer les recommandations
        if actionable_only:
            recommendations = SmartRecommendationFilter.get_actionable_recommendations(recommendations)
        else:
            recommendations = SmartRecommendationFilter.filter_recommendations(
                recommendations,
                max_count=max_count,
                min_confidence=min_confidence
            )
        
        # Grouper par type
        grouped = SmartRecommendationFilter.group_by_type(recommendations)
        
        # Statistiques
        stats = {
            'total_recommendations': len(recommendations),
            'by_priority': {},
            'by_type': {k: len(v) for k, v in grouped.items()},
            'average_confidence': sum(r.get('confidence', 0) for r in recommendations) / len(recommendations) if recommendations else 0
        }
        
        # Count by priority
        for rec in recommendations:
            priority = rec.get('priority', 0)
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'grouped': grouped,
                'statistics': stats,
                'analysis_period_days': days,
                'filters_applied': {
                    'max_count': max_count,
                    'min_confidence': min_confidence,
                    'types': filter_types,
                    'actionable_only': actionable_only
                }
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI Recommendations failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_ai_insights(request):
    """
    GET /analytics/api/ai/insights/
    Génère des insights intelligents sur les données de détection
    """
    try:
        from detection.models import DetectionResult
        from analytics.models import ObjectTrend, SecurityAlert
        from analytics.ml_models import AnomalyDetector
        
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Collecter les données
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=start_date
        )
        
        trends = ObjectTrend.objects.filter(user=request.user)
        alerts = SecurityAlert.objects.filter(
            user=request.user,
            created_at__gte=start_date
        )
        
        # Analyse des anomalies
        anomaly_insights = []
        if detections.exists():
            detector = AnomalyDetector()
            try:
                anomaly_result = detector.detect_anomalies(detections)
                if anomaly_result.get('anomalies'):
                    anomaly_insights.append({
                        'type': 'anomaly',
                        'title': 'Anomalies détectées',
                        'description': f"{anomaly_result.get('anomaly_count', 0)} anomalies identifiées par l'IA",
                        'severity': 'high' if anomaly_result.get('anomaly_count', 0) > 5 else 'medium',
                        'data': anomaly_result
                    })
            except Exception as e:
                logger.warning(f"Anomaly detection failed: {e}")
        
        # Insights sur les tendances
        trend_insights = []
        if trends.exists():
            top_trend = trends.order_by('-detection_count').first()
            anomaly_trends = trends.filter(is_anomaly=True).count()
            
            trend_insights.append({
                'type': 'trend',
                'title': 'Objet le plus détecté',
                'description': f"{top_trend.object_class} avec {top_trend.detection_count} détections",
                'severity': 'info',
                'data': {
                    'object_class': top_trend.object_class,
                    'count': top_trend.detection_count,
                    'is_anomaly': top_trend.is_anomaly
                }
            })
            
            if anomaly_trends > 0:
                trend_insights.append({
                    'type': 'trend_anomaly',
                    'title': 'Tendances anormales',
                    'description': f"{anomaly_trends} types d'objets avec patterns inhabituels",
                    'severity': 'medium',
                    'data': {'anomaly_count': anomaly_trends}
                })
        
        # Insights sur les alertes
        alert_insights = []
        if alerts.exists():
            critical_count = alerts.filter(severity='critical').count()
            unread_count = alerts.filter(is_read=False).count()
            
            if critical_count > 0:
                alert_insights.append({
                    'type': 'alert',
                    'title': 'Alertes critiques',
                    'description': f"{critical_count} alertes critiques générées",
                    'severity': 'critical',
                    'data': {
                        'critical_count': critical_count,
                        'unread_count': unread_count
                    }
                })
        
        # Combiner tous les insights
        all_insights = anomaly_insights + trend_insights + alert_insights
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'insights': all_insights,
                'summary': {
                    'total_insights': len(all_insights),
                    'period_days': days,
                    'categories': {
                        'anomalies': len(anomaly_insights),
                        'trends': len(trend_insights),
                        'alerts': len(alert_insights)
                    }
                }
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI Insights generation failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_ai_predict_activity(request):
    """
    GET /analytics/api/ai/predict-activity/
    Prédit l'activité future basée sur les patterns historiques
    
    Params:
        - periods: nombre de périodes à prédire (défaut: 7)
        - interval: hour/day/week (défaut: day)
    """
    try:
        from detection.models import DetectionResult
        from analytics.ml_models import TimeSeriesPredictor
        
        periods = int(request.GET.get('periods', 7))
        interval = request.GET.get('interval', 'day')
        
        # Collecter les données historiques
        detections = DetectionResult.objects.filter(
            user=request.user
        ).order_by('uploaded_at')
        
        if detections.count() < 10:
            return JsonResponse({
                'status': 'error',
                'message': 'Données insuffisantes pour la prédiction (minimum 10 détections requises)'
            }, status=400)
        
        # Prédiction
        predictor = TimeSeriesPredictor()
        result = predictor.predict_activity(detections, periods=periods, interval=interval)
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'parameters': {
                'periods': periods,
                'interval': interval
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Activity prediction failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_ai_smart_search(request):
    """
    POST /analytics/api/ai/smart-search/
    Recherche intelligente avec NLP
    
    Body:
        {
            "query": "show me suspicious detections from last week",
            "context": "security" (optional)
        }
    """
    try:
        from analytics.nlp_service import NaturalLanguageQueryProcessor
        
        data = json.loads(request.body)
        query = data.get('query', '')
        context = data.get('context', None)
        
        if not query:
            return JsonResponse({
                'status': 'error',
                'message': 'Query parameter is required'
            }, status=400)
        
        # Process NLP query
        processor = NaturalLanguageQueryProcessor()
        result = processor.process_query(query, request.user, context=context)
        
        return JsonResponse({
            'status': 'success',
            'data': result,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Smart search failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_ai_risk_assessment(request):
    """
    GET /analytics/api/ai/risk-assessment/
    Évalue le niveau de risque global basé sur l'IA
    """
    try:
        from detection.models import DetectionResult
        from analytics.models import SecurityAlert, ObjectTrend
        
        days = int(request.GET.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Collecter les données
        detections = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=start_date
        )
        
        alerts = SecurityAlert.objects.filter(
            user=request.user,
            created_at__gte=start_date
        )
        
        trends = ObjectTrend.objects.filter(
            user=request.user,
            is_anomaly=True
        )
        
        # Calcul du score de risque (0-100)
        risk_score = 0
        risk_factors = []
        
        # Facteur 1: Alertes critiques non lues
        critical_unread = alerts.filter(severity='critical', is_read=False).count()
        if critical_unread > 0:
            risk_score += min(critical_unread * 15, 40)
            risk_factors.append({
                'factor': 'critical_alerts',
                'weight': min(critical_unread * 15, 40),
                'description': f'{critical_unread} alertes critiques non traitées'
            })
        
        # Facteur 2: Objets dangereux détectés
        dangerous_objects = ['knife', 'gun', 'weapon', 'fire']
        dangerous_count = 0
        
        for detection in detections:
            data = detection.get_detection_data()
            if data:
                for obj in data:
                    if obj.get('class', '').lower() in dangerous_objects:
                        dangerous_count += 1
        
        if dangerous_count > 0:
            risk_score += min(dangerous_count * 10, 30)
            risk_factors.append({
                'factor': 'dangerous_objects',
                'weight': min(dangerous_count * 10, 30),
                'description': f'{dangerous_count} objets dangereux détectés'
            })
        
        # Facteur 3: Anomalies
        anomaly_count = trends.count()
        if anomaly_count > 0:
            risk_score += min(anomaly_count * 5, 20)
            risk_factors.append({
                'factor': 'anomalies',
                'weight': min(anomaly_count * 5, 20),
                'description': f'{anomaly_count} patterns anormaux détectés'
            })
        
        # Facteur 4: Taux d'alertes
        if detections.count() > 0:
            alert_rate = alerts.count() / detections.count()
            if alert_rate > 0.3:
                risk_score += 10
                risk_factors.append({
                    'factor': 'high_alert_rate',
                    'weight': 10,
                    'description': f'Taux d\'alerte élevé: {int(alert_rate * 100)}%'
                })
        
        # Normaliser le score (0-100)
        risk_score = min(risk_score, 100)
        
        # Déterminer le niveau de risque
        if risk_score >= 70:
            risk_level = 'critical'
            risk_label = 'Critique'
            color = 'red'
        elif risk_score >= 50:
            risk_level = 'high'
            risk_label = 'Élevé'
            color = 'orange'
        elif risk_score >= 30:
            risk_level = 'medium'
            risk_label = 'Moyen'
            color = 'yellow'
        else:
            risk_level = 'low'
            risk_label = 'Faible'
            color = 'green'
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_label': risk_label,
                'color': color,
                'factors': risk_factors,
                'recommendations': [
                    f for f in risk_factors if f['weight'] >= 10
                ],
                'period_days': days,
                'metrics': {
                    'total_detections': detections.count(),
                    'total_alerts': alerts.count(),
                    'critical_alerts': critical_unread,
                    'anomalies': anomaly_count,
                    'dangerous_objects': dangerous_count
                }
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_ai_optimization_suggestions(request):
    """
    GET /analytics/api/ai/optimization/
    Suggestions d'optimisation basées sur l'analyse IA
    """
    try:
        from analytics.ai_recommendation_system import RecommendationEngine
        
        # Générer recommandations d'optimisation uniquement
        engine = RecommendationEngine(request.user)
        all_recommendations = engine.analyze_and_recommend(days=30)
        
        # Filtrer pour optimisation uniquement
        optimization_recs = [
            r for r in all_recommendations 
            if r.get('type') == 'optimization'
        ]
        
        # Grouper par catégorie
        categories = {
            'surveillance': [],
            'performance': [],
            'coverage': [],
            'alerts': []
        }
        
        for rec in optimization_recs:
            title_lower = rec.get('title', '').lower()
            
            if 'surveillance' in title_lower or 'monitoring' in title_lower:
                categories['surveillance'].append(rec)
            elif 'performance' in title_lower or 'efficacité' in title_lower:
                categories['performance'].append(rec)
            elif 'coverage' in title_lower or 'lacune' in title_lower or 'gap' in title_lower:
                categories['coverage'].append(rec)
            else:
                categories['alerts'].append(rec)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'total_suggestions': len(optimization_recs),
                'by_category': categories,
                'all_suggestions': optimization_recs,
                'priority_actions': [
                    r for r in optimization_recs 
                    if r.get('priority', 0) >= 4
                ]
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Optimization suggestions failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_ai_dashboard_summary(request):
    """
    GET /analytics/api/ai/dashboard/
    Résumé complet IA pour le dashboard
    Combine recommandations, insights, risques et prédictions
    """
    try:
        from analytics.ai_recommendation_system import RecommendationEngine, SmartRecommendationFilter
        from detection.models import DetectionResult
        from analytics.models import SecurityAlert
        
        # Recommandations top priorité
        engine = RecommendationEngine(request.user)
        recommendations = engine.analyze_and_recommend(days=30)
        top_recommendations = SmartRecommendationFilter.get_actionable_recommendations(recommendations)[:5]
        
        # Statistiques rapides
        week_ago = timezone.now() - timedelta(days=7)
        detections_week = DetectionResult.objects.filter(
            user=request.user,
            uploaded_at__gte=week_ago
        ).count()
        
        alerts_unread = SecurityAlert.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        alerts_critical = SecurityAlert.objects.filter(
            user=request.user,
            severity='critical',
            is_read=False
        ).count()
        
        # Score de santé global (0-100)
        health_score = 100
        
        # Pénalités
        if alerts_critical > 0:
            health_score -= min(alerts_critical * 20, 40)
        if alerts_unread > 5:
            health_score -= min((alerts_unread - 5) * 5, 30)
        if detections_week < 7:
            health_score -= 20
        
        health_score = max(health_score, 0)
        
        # Déterminer le statut
        if health_score >= 80:
            health_status = 'excellent'
            health_label = 'Excellent'
        elif health_score >= 60:
            health_status = 'good'
            health_label = 'Bon'
        elif health_score >= 40:
            health_status = 'fair'
            health_label = 'Acceptable'
        else:
            health_status = 'poor'
            health_label = 'Attention requise'
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'health': {
                    'score': health_score,
                    'status': health_status,
                    'label': health_label
                },
                'quick_stats': {
                    'detections_week': detections_week,
                    'alerts_unread': alerts_unread,
                    'alerts_critical': alerts_critical,
                    'recommendations_count': len(top_recommendations)
                },
                'top_recommendations': top_recommendations,
                'alerts': {
                    'has_critical': alerts_critical > 0,
                    'needs_attention': alerts_unread > 5
                }
            },
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI Dashboard summary failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ============ SAVED RECOMMENDATIONS MANAGEMENT ============

@login_required
@require_http_methods(["POST"])
def api_save_recommendation(request):
    """
    POST /analytics/api/ai/recommendations/save/
    Save a recommendation to database
    
    Body:
        {
            "recommendation_type": "security",
            "priority": 5,
            "title": "...",
            "description": "...",
            "action": "...",
            "confidence": 0.95,
            "impact": "high",
            "metadata": {...}
        }
    """
    try:
        from analytics.models import AIRecommendation
        
        data = json.loads(request.body)
        
        # Create recommendation
        recommendation = AIRecommendation.objects.create(
            user=request.user,
            recommendation_type=data.get('recommendation_type', 'optimization'),
            priority=data.get('priority', 3),
            impact=data.get('impact', 'medium'),
            title=data.get('title', ''),
            description=data.get('description', ''),
            action=data.get('action', ''),
            confidence=data.get('confidence', 0.0),
            metadata=json.dumps(data.get('metadata', {}))
        )
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': recommendation.id,
                'message': 'Recommandation enregistrée avec succès'
            }
        }, status=201)
        
    except Exception as e:
        logger.error(f"Save recommendation failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_list_saved_recommendations(request):
    """
    GET /analytics/api/ai/recommendations/saved/
    List saved recommendations
    
    Params:
        - status: filter by status (pending, viewed, acted, dismissed)
        - type: filter by recommendation_type
        - priority_min: minimum priority level
        - limit: number of results
    """
    try:
        from analytics.models import AIRecommendation
        
        # Base query
        recommendations = AIRecommendation.objects.filter(user=request.user)
        
        # Filters
        status = request.GET.get('status')
        if status:
            recommendations = recommendations.filter(status=status)
        
        rec_type = request.GET.get('type')
        if rec_type:
            recommendations = recommendations.filter(recommendation_type=rec_type)
        
        priority_min = request.GET.get('priority_min')
        if priority_min:
            recommendations = recommendations.filter(priority__gte=int(priority_min))
        
        limit = int(request.GET.get('limit', 50))
        recommendations = recommendations[:limit]
        
        # Serialize
        data = []
        for rec in recommendations:
            data.append({
                'id': rec.id,
                'type': rec.recommendation_type,
                'priority': rec.priority,
                'priority_label': rec.get_priority_display(),
                'title': rec.title,
                'description': rec.description,
                'action': rec.action,
                'confidence': rec.confidence,
                'impact': rec.impact,
                'status': rec.status,
                'metadata': rec.get_metadata(),
                'was_helpful': rec.was_helpful,
                'created_at': rec.created_at.isoformat(),
                'expires_at': rec.expires_at.isoformat() if rec.expires_at else None,
                'is_expired': rec.is_expired()
            })
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'recommendations': data,
                'total': len(data)
            }
        })
        
    except Exception as e:
        logger.error(f"List saved recommendations failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_update_recommendation_status(request, rec_id):
    """
    POST /analytics/api/ai/recommendations/<id>/status/
    Update recommendation status
    
    Body:
        {
            "action": "view" | "act" | "dismiss"
        }
    """
    try:
        from analytics.models import AIRecommendation
        
        recommendation = get_object_or_404(
            AIRecommendation,
            id=rec_id,
            user=request.user
        )
        
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'view':
            recommendation.mark_viewed()
            message = 'Recommandation marquée comme vue'
        elif action == 'act':
            recommendation.mark_acted()
            message = 'Recommandation marquée comme traitée'
        elif action == 'dismiss':
            recommendation.dismiss()
            message = 'Recommandation rejetée'
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Action invalide. Utilisez: view, act, ou dismiss'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': recommendation.id,
                'new_status': recommendation.status,
                'message': message
            }
        })
        
    except Exception as e:
        logger.error(f"Update recommendation status failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_recommendation_feedback(request, rec_id):
    """
    POST /analytics/api/ai/recommendations/<id>/feedback/
    Provide feedback on recommendation
    
    Body:
        {
            "was_helpful": true | false,
            "feedback_text": "optional feedback text"
        }
    """
    try:
        from analytics.models import AIRecommendation
        
        recommendation = get_object_or_404(
            AIRecommendation,
            id=rec_id,
            user=request.user
        )
        
        data = json.loads(request.body)
        was_helpful = data.get('was_helpful')
        feedback_text = data.get('feedback_text', '')
        
        if was_helpful is None:
            return JsonResponse({
                'status': 'error',
                'message': 'was_helpful est requis (true/false)'
            }, status=400)
        
        recommendation.set_feedback(was_helpful, feedback_text)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': recommendation.id,
                'message': 'Feedback enregistré avec succès'
            }
        })
        
    except Exception as e:
        logger.error(f"Recommendation feedback failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_generate_and_save_recommendations(request):
    """
    POST /analytics/api/ai/recommendations/generate-save/
    Generate recommendations and save them to database
    
    Body:
        {
            "days": 30,
            "min_confidence": 0.7,
            "auto_save": true
        }
    """
    try:
        from analytics.ai_recommendation_system import RecommendationEngine, SmartRecommendationFilter
        from analytics.models import AIRecommendation
        
        data = json.loads(request.body) if request.body else {}
        
        days = data.get('days', 30)
        min_confidence = data.get('min_confidence', 0.7)
        auto_save = data.get('auto_save', True)
        
        # Generate recommendations
        engine = RecommendationEngine(request.user)
        recommendations = engine.analyze_and_recommend(days=days)
        
        # Filter
        filtered = SmartRecommendationFilter.filter_recommendations(
            recommendations,
            max_count=20,
            min_confidence=min_confidence
        )
        
        saved_count = 0
        
        if auto_save:
            # Save to database
            for rec in filtered:
                # Check if similar recommendation already exists
                exists = AIRecommendation.objects.filter(
                    user=request.user,
                    title=rec['title'],
                    status__in=['pending', 'viewed']
                ).exists()
                
                if not exists:
                    AIRecommendation.objects.create(
                        user=request.user,
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
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'generated_count': len(filtered),
                'saved_count': saved_count,
                'recommendations': filtered if not auto_save else None,
                'message': f'{saved_count} recommandations sauvegardées' if auto_save else 'Recommandations générées'
            }
        })
        
    except Exception as e:
        logger.error(f"Generate and save recommendations failed: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
