"""
AI-Powered Recommendation System for Argus - Advanced Version
Provides intelligent recommendations based on ML patterns, user behavior, and predictive analytics
"""
import numpy as np
from django.utils import timezone
from django.db.models import Count, Avg, Q, F, Sum
from datetime import timedelta, datetime
from collections import defaultdict, Counter
import logging
import json

logger = logging.getLogger(__name__)


class AdvancedRecommendationEngine:
    """
    Moteur de recommandations avancé avec Machine Learning
    - Analyse prédictive
    - Scoring de risques multi-facteurs
    - Recommandations contextuelles
    - Apprentissage des préférences utilisateur
    """
    
    RECOMMENDATION_TYPES = {
        'SECURITY': 'security',
        'OPTIMIZATION': 'optimization',
        'BEHAVIOR': 'behavior',
        'ALERT': 'alert',
        'MONITORING': 'monitoring',
        'PREDICTIVE': 'predictive',  # Nouveau
        'PERFORMANCE': 'performance',  # Nouveau
    }
    
    PRIORITY_LEVELS = {
        'CRITICAL': 5,
        'HIGH': 4,
        'MEDIUM': 3,
        'LOW': 2,
        'INFO': 1
    }
    
    # Nouveau: Facteurs de risque avec pondération
    RISK_FACTORS = {
        'weapon_detection': {'weight': 10.0, 'threshold': 1},
        'night_activity': {'weight': 3.0, 'threshold': 5},
        'multiple_people': {'weight': 2.5, 'threshold': 3},
        'low_confidence': {'weight': 2.0, 'threshold': 0.5},
        'zone_violation': {'weight': 4.0, 'threshold': 2},
        'repeated_alerts': {'weight': 3.5, 'threshold': 3},
        'unusual_pattern': {'weight': 4.5, 'threshold': 1},
    }
    
    def __init__(self, user):
        """
        Initialize advanced recommendation engine
        
        Args:
            user: Django User object
        """
        self.user = user
        self.recommendations = []
        self.risk_score = 0.0
        self.behavior_profile = {}
        self.prediction_confidence = 0.0
        
    def analyze_and_recommend(self, days=30):
        """
        Analyse complète avec ML et recommandations prédictives
        
        Args:
            days: Période d'analyse en jours
            
        Returns:
            Liste de recommandations enrichies
        """
        from detection.models import DetectionResult
        from analytics.models import ObjectTrend, SecurityAlert, DetectionAnalytics
        
        start_date = timezone.now() - timedelta(days=days)
        
        # Récupération des données
        detections = DetectionResult.objects.filter(
            user=self.user,
            uploaded_at__gte=start_date
        ).select_related('user')
        
        trends = ObjectTrend.objects.filter(user=self.user)
        alerts = SecurityAlert.objects.filter(user=self.user)
        
        # Créer le profil comportemental
        self._build_behavior_profile(detections, alerts)
        
        # Calcul du score de risque global
        self._calculate_risk_score(detections, alerts)
        
        # Analyses avancées
        self._analyze_security_patterns(detections, alerts)
        self._analyze_predictive_threats(detections, alerts)  # Nouveau
        self._analyze_detection_frequency(detections)
        self._analyze_object_patterns(trends)
        self._analyze_anomalies(trends)
        self._analyze_coverage_gaps(detections)
        self._analyze_alert_efficiency(alerts)
        self._analyze_time_patterns(detections)
        self._analyze_performance_optimization(detections)  # Nouveau
        self._analyze_zone_efficiency(detections)  # Nouveau
        self._generate_predictive_recommendations()  # Nouveau
        
        # Filtrage intelligent basé sur le contexte
        self._apply_contextual_filtering()
        
        # Tri multi-critères
        self._smart_sort_recommendations()
        
        return self.recommendations
    
    def _build_behavior_profile(self, detections, alerts):
        """
        Construit un profil comportemental de l'utilisateur
        """
        total_detections = detections.count()
        if total_detections == 0:
            return
        
        # Patterns temporels
        hours = [d.uploaded_at.hour for d in detections]
        self.behavior_profile['peak_hours'] = Counter(hours).most_common(3)
        
        # Taux de réponse aux alertes
        acknowledged = alerts.filter(is_acknowledged=True).count()
        total_alerts = alerts.count()
        self.behavior_profile['alert_response_rate'] = (
            acknowledged / total_alerts if total_alerts > 0 else 0
        )
        
        # Fréquence de détection
        days_active = (timezone.now() - detections.first().uploaded_at).days or 1
        self.behavior_profile['detection_frequency'] = total_detections / days_active
        
        # Types d'objets préférés
        all_objects = []
        for det in detections:
            data = det.get_detection_data()
            if data:
                all_objects.extend([obj.get('class') for obj in data])
        self.behavior_profile['common_objects'] = Counter(all_objects).most_common(5)
        
    def _calculate_risk_score(self, detections, alerts):
        """
        Calcule un score de risque global multi-facteurs
        """
        risk_points = 0.0
        max_points = 100.0
        
        # Facteur 1: Alertes critiques non traitées
        critical_unread = alerts.filter(
            severity='critical',
            is_read=False
        ).count()
        risk_points += min(critical_unread * 15, 45)
        
        # Facteur 2: Objets dangereux détectés
        dangerous_objects = ['knife', 'gun', 'weapon', 'scissors', 'fire']
        danger_count = 0
        for det in detections:
            data = det.get_detection_data()
            if data:
                for obj in data:
                    if obj.get('class', '').lower() in dangerous_objects:
                        danger_count += 1
        risk_points += min(danger_count * 10, 30)
        
        # Facteur 3: Activité nocturne suspecte (22h-6h)
        night_detections = sum(
            1 for d in detections 
            if d.uploaded_at.hour >= 22 or d.uploaded_at.hour <= 6
        )
        total = detections.count() or 1
        night_ratio = night_detections / total
        if night_ratio > 0.3:
            risk_points += 15
        
        # Facteur 4: Taux de fausses alarmes
        false_alarm_rate = self._calculate_false_alarm_rate(alerts)
        if false_alarm_rate > 0.5:
            risk_points += 10
        
        self.risk_score = min(risk_points, max_points)
        
    def _calculate_false_alarm_rate(self, alerts):
        """Estime le taux de fausses alarmes"""
        dismissed = alerts.filter(is_acknowledged=False).count()
        total = alerts.count()
        return dismissed / total if total > 0 else 0
    
    def _analyze_predictive_threats(self, detections, alerts):
        """
        NOUVEAU: Analyse prédictive des menaces potentielles
        """
        if detections.count() < 10:
            return
        
        # Détection de patterns escaladant
        recent_7d = detections.filter(
            uploaded_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        previous_7d = detections.filter(
            uploaded_at__gte=timezone.now() - timedelta(days=14),
            uploaded_at__lt=timezone.now() - timedelta(days=7)
        ).count() or 1
        
        growth_rate = ((recent_7d - previous_7d) / previous_7d) * 100
        
        if growth_rate > 50:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['PREDICTIVE'],
                'priority': self.PRIORITY_LEVELS['HIGH'],
                'title': '⚠️ Augmentation anormale des détections',
                'description': f'Les détections ont augmenté de {growth_rate:.0f}% cette semaine. '
                              f'Cela pourrait indiquer une activité inhabituelle.',
                'action': 'Analyser les causes de l\'augmentation et renforcer la surveillance si nécessaire.',
                'confidence': 0.85,
                'impact': 'high',
                'context': {
                    'growth_rate': growth_rate,
                    'recent_count': recent_7d,
                    'previous_count': previous_7d
                }
            })
        
        # Prédiction de surcharge d'alertes
        alert_trend = self._predict_alert_overload(alerts)
        if alert_trend > 0.7:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['PREDICTIVE'],
                'priority': self.PRIORITY_LEVELS['MEDIUM'],
                'title': '📈 Risque de surcharge d\'alertes prévu',
                'description': f'Le système prévoit une augmentation significative des alertes (confiance: {alert_trend:.0%}).',
                'action': 'Optimiser les seuils de détection ou activer le mode de filtrage intelligent.',
                'confidence': alert_trend,
                'impact': 'medium',
                'context': {'prediction_confidence': alert_trend}
            })
    
    def _predict_alert_overload(self, alerts):
        """Prédit le risque de surcharge d'alertes"""
        if alerts.count() < 5:
            return 0.0
        
        recent = alerts.filter(
            created_at__gte=timezone.now() - timedelta(days=3)
        ).count()
        
        threshold = 20  # Seuil de surcharge
        confidence = min(recent / threshold, 1.0)
        return confidence
    
    def _analyze_performance_optimization(self, detections):
        """
        NOUVEAU: Recommandations pour optimiser les performances
        """
        if detections.count() < 5:
            return
        
        # Analyser la confiance moyenne
        all_confidences = []
        for det in detections:
            data = det.get_detection_data()
            if data:
                all_confidences.extend([obj.get('confidence', 0) for obj in data])
        
        if all_confidences:
            avg_confidence = np.mean(all_confidences)
            
            if avg_confidence < 0.6:
                self.recommendations.append({
                    'type': self.RECOMMENDATION_TYPES['PERFORMANCE'],
                    'priority': self.PRIORITY_LEVELS['MEDIUM'],
                    'title': '🎯 Confiance de détection faible',
                    'description': f'La confiance moyenne est de {avg_confidence:.0%}. '
                                  f'Cela peut générer des fausses alertes.',
                    'action': 'Améliorer l\'éclairage, ajuster l\'angle de caméra, ou augmenter le seuil de confiance minimal.',
                    'confidence': 0.80,
                    'impact': 'medium',
                    'context': {'avg_confidence': avg_confidence}
                })
        
        # Analyser la vitesse de traitement
        processing_times = []
        for det in detections:
            if hasattr(det, 'processed_at') and det.uploaded_at:
                delta = (det.uploaded_at - det.uploaded_at).total_seconds()
                processing_times.append(delta)
        
        if processing_times and np.mean(processing_times) > 5:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['PERFORMANCE'],
                'priority': self.PRIORITY_LEVELS['LOW'],
                'title': '⚡ Optimisation du temps de traitement',
                'description': f'Le temps moyen de traitement est de {np.mean(processing_times):.1f}s.',
                'action': 'Réduire la résolution des images ou optimiser le modèle YOLOv5.',
                'confidence': 0.75,
                'impact': 'low',
                'context': {'avg_processing_time': np.mean(processing_times)}
            })
    
    def _analyze_zone_efficiency(self, detections):
        """
        NOUVEAU: Analyse l'efficacité de la couverture par zone
        """
        # Simuler des zones (à adapter selon votre implémentation)
        zone_detections = defaultdict(int)
        for det in detections:
            # Exemple simple, à adapter selon vos zones réelles
            zone_detections['zone_default'] += 1
        
        if len(zone_detections) > 0:
            zones = list(zone_detections.items())
            total = sum(count for _, count in zones)
            
            # Identifier les zones sous-utilisées
            underused_zones = [
                zone for zone, count in zones 
                if count / total < 0.1
            ]
            
            if underused_zones:
                self.recommendations.append({
                    'type': self.RECOMMENDATION_TYPES['MONITORING'],
                    'priority': self.PRIORITY_LEVELS['LOW'],
                    'title': '📍 Zones de surveillance sous-utilisées',
                    'description': f'{len(underused_zones)} zone(s) reçoivent peu de détections.',
                    'action': 'Vérifier si ces zones nécessitent toujours une surveillance ou ajuster les caméras.',
                    'confidence': 0.70,
                    'impact': 'low',
                    'context': {'underused_zones': underused_zones}
                })
    
    def _generate_predictive_recommendations(self):
        """
        NOUVEAU: Génère des recommandations prédictives basées sur l'IA
        """
        # Recommandation basée sur le score de risque
        if self.risk_score > 70:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['SECURITY'],
                'priority': self.PRIORITY_LEVELS['CRITICAL'],
                'title': '🚨 Score de risque élevé détecté',
                'description': f'Votre score de risque global est de {self.risk_score:.0f}/100. '
                              f'Action immédiate recommandée.',
                'action': 'Consulter toutes les alertes critiques, renforcer la surveillance, '
                         'et envisager une révision des protocoles de sécurité.',
                'confidence': 0.95,
                'impact': 'high',
                'context': {
                    'risk_score': self.risk_score,
                    'recommendation_source': 'risk_analysis'
                }
            })
        elif self.risk_score > 40:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['SECURITY'],
                'priority': self.PRIORITY_LEVELS['MEDIUM'],
                'title': '⚡ Score de risque modéré',
                'description': f'Score de risque: {self.risk_score:.0f}/100. Surveillance recommandée.',
                'action': 'Réviser les alertes récentes et ajuster les paramètres de détection.',
                'confidence': 0.80,
                'impact': 'medium',
                'context': {'risk_score': self.risk_score}
            })
        
        # Recommandation basée sur le profil comportemental
        if self.behavior_profile.get('alert_response_rate', 1.0) < 0.3:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['BEHAVIOR'],
                'priority': self.PRIORITY_LEVELS['HIGH'],
                'title': '📋 Faible taux de réponse aux alertes',
                'description': f'Seulement {self.behavior_profile["alert_response_rate"]:.0%} des alertes sont traitées.',
                'action': 'Mettre en place une routine de vérification quotidienne des alertes '
                         'ou activer les notifications push.',
                'confidence': 0.90,
                'impact': 'high',
                'context': self.behavior_profile
            })
    
    def _apply_contextual_filtering(self):
        """
        Filtre intelligent basé sur le contexte utilisateur
        """
        # Supprimer les doublons similaires
        seen = set()
        filtered = []
        for rec in self.recommendations:
            key = (rec['type'], rec['title'][:30])
            if key not in seen:
                seen.add(key)
                filtered.append(rec)
        
        self.recommendations = filtered
        
        # Limiter le nombre de recommandations de faible priorité
        high_priority = [r for r in self.recommendations if r['priority'] >= 3]
        low_priority = [r for r in self.recommendations if r['priority'] < 3][:3]
        
        self.recommendations = high_priority + low_priority
    
    def _smart_sort_recommendations(self):
        """
        Tri intelligent multi-critères:
        1. Priorité
        2. Confiance
        3. Impact
        """
        impact_weight = {'high': 3, 'medium': 2, 'low': 1}
        
        self.recommendations.sort(
            key=lambda x: (
                -x['priority'],
                -x['confidence'],
                -impact_weight.get(x.get('impact', 'low'), 1)
            )
        )
    
    def _analyze_security_patterns(self, detections, alerts):
        """Analyse avancée des patterns de sécurité"""
        
        # Check for high-risk objects
        high_risk_objects = ['knife', 'gun', 'weapon', 'fire']
        risky_detections = 0
        
        for detection in detections:
            data = detection.get_detection_data()
            if data:
                for obj in data:
                    if obj.get('class', '').lower() in high_risk_objects:
                        risky_detections += 1
        
        if risky_detections > 5:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['SECURITY'],
                'priority': self.PRIORITY_LEVELS['CRITICAL'],
                'title': 'Objets à risque détectés fréquemment',
                'description': f'{risky_detections} détections d\'objets à risque dans les {len(detections)} dernières détections.',
                'action': 'Envisager de renforcer la surveillance ou d\'activer des alertes automatiques pour ces objets.',
                'impact': 'high',
                'confidence': 0.95,
                'metadata': {
                    'risky_count': risky_detections,
                    'suggested_actions': [
                        'Configurer des alertes SMS pour objets dangereux',
                        'Augmenter la fréquence de monitoring',
                        'Revoir les zones de surveillance'
                    ]
                }
            })
        
        # Check unread critical alerts
        critical_unread = alerts.filter(
            severity='critical',
            is_read=False
        ).count()
        
        if critical_unread > 0:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['ALERT'],
                'priority': self.PRIORITY_LEVELS['HIGH'],
                'title': 'Alertes critiques non lues',
                'description': f'Vous avez {critical_unread} alerte(s) critique(s) en attente.',
                'action': 'Consulter et traiter les alertes critiques immédiatement.',
                'impact': 'high',
                'confidence': 1.0,
                'metadata': {
                    'alert_count': critical_unread,
                    'url': '/analytics/alerts/'
                }
            })
    
    def _analyze_detection_frequency(self, detections):
        """Analyze detection frequency patterns"""
        
        total_detections = detections.count()
        
        if total_detections < 10:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['OPTIMIZATION'],
                'priority': self.PRIORITY_LEVELS['MEDIUM'],
                'title': 'Faible activité de détection',
                'description': f'Seulement {total_detections} détections enregistrées récemment.',
                'action': 'Augmenter la fréquence de surveillance ou vérifier que les caméras sont actives.',
                'impact': 'medium',
                'confidence': 0.85,
                'metadata': {
                    'detection_count': total_detections,
                    'recommended_frequency': 'Au moins 1 détection par jour pour une surveillance efficace'
                }
            })
        
        # Analyze daily distribution
        daily_counts = defaultdict(int)
        for detection in detections:
            date_key = detection.uploaded_at.date()
            daily_counts[date_key] += 1
        
        if daily_counts:
            avg_per_day = sum(daily_counts.values()) / len(daily_counts)
            max_per_day = max(daily_counts.values())
            
            if max_per_day > avg_per_day * 3:
                self.recommendations.append({
                    'type': self.RECOMMENDATION_TYPES['BEHAVIOR'],
                    'priority': self.PRIORITY_LEVELS['MEDIUM'],
                    'title': 'Pics d\'activité inhabituels',
                    'description': f'Certains jours montrent jusqu\'à {int(max_per_day)} détections vs moyenne de {int(avg_per_day)}.',
                    'action': 'Analyser les jours à forte activité pour identifier des patterns.',
                    'impact': 'medium',
                    'confidence': 0.80,
                    'metadata': {
                        'avg_daily': int(avg_per_day),
                        'max_daily': int(max_per_day),
                        'spike_ratio': round(max_per_day / avg_per_day, 2)
                    }
                })
    
    def _analyze_object_patterns(self, trends):
        """Analyze object detection patterns"""
        
        top_objects = trends.order_by('-detection_count')[:5]
        
        if top_objects.exists():
            # Check for unusual concentrations
            total_detections = sum(t.detection_count for t in trends)
            top_concentration = sum(t.detection_count for t in top_objects)
            
            if total_detections > 0:
                concentration_ratio = top_concentration / total_detections
                
                if concentration_ratio > 0.8:
                    object_list = [t.object_class for t in top_objects]
                    self.recommendations.append({
                        'type': self.RECOMMENDATION_TYPES['MONITORING'],
                        'priority': self.PRIORITY_LEVELS['LOW'],
                        'title': 'Forte concentration sur certains objets',
                        'description': f'{int(concentration_ratio * 100)}% des détections concernent 5 types d\'objets seulement.',
                        'action': 'Diversifier les zones de surveillance ou ajuster les paramètres de détection.',
                        'impact': 'low',
                        'confidence': 0.75,
                        'metadata': {
                            'concentration_ratio': concentration_ratio,
                            'top_objects': object_list,
                            'suggestion': 'Élargir la couverture pour détecter plus de types d\'objets'
                        }
                    })
    
    def _analyze_anomalies(self, trends):
        """Analyze anomaly patterns"""
        
        anomalies = trends.filter(is_anomaly=True)
        anomaly_count = anomalies.count()
        
        if anomaly_count > 5:
            anomaly_objects = list(anomalies.values_list('object_class', flat=True)[:10])
            
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['SECURITY'],
                'priority': self.PRIORITY_LEVELS['HIGH'],
                'title': 'Anomalies détectées',
                'description': f'{anomaly_count} patterns anormaux identifiés par l\'IA.',
                'action': 'Examiner les anomalies pour identifier des menaces potentielles.',
                'impact': 'high',
                'confidence': 0.88,
                'metadata': {
                    'anomaly_count': anomaly_count,
                    'anomaly_objects': anomaly_objects,
                    'detection_method': 'Machine Learning (Isolation Forest)'
                }
            })
    
    def _analyze_coverage_gaps(self, detections):
        """Analyze temporal coverage gaps"""
        
        if detections.count() < 2:
            return
        
        # Check for large time gaps
        sorted_detections = detections.order_by('uploaded_at')
        max_gap = timedelta(0)
        gap_count = 0
        
        prev_time = None
        for detection in sorted_detections:
            if prev_time:
                gap = detection.uploaded_at - prev_time
                if gap > timedelta(hours=24):
                    gap_count += 1
                    max_gap = max(max_gap, gap)
            prev_time = detection.uploaded_at
        
        if gap_count > 0:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['OPTIMIZATION'],
                'priority': self.PRIORITY_LEVELS['MEDIUM'],
                'title': 'Lacunes dans la surveillance',
                'description': f'{gap_count} période(s) sans détection de plus de 24 heures.',
                'action': 'Vérifier la continuité de la surveillance et la disponibilité des caméras.',
                'impact': 'medium',
                'confidence': 0.90,
                'metadata': {
                    'gap_count': gap_count,
                    'max_gap_hours': int(max_gap.total_seconds() / 3600),
                    'recommendation': 'Mettre en place une surveillance continue ou des alertes de disponibilité'
                }
            })
    
    def _analyze_alert_efficiency(self, alerts):
        """Analyze alert handling efficiency"""
        
        total_alerts = alerts.count()
        if total_alerts == 0:
            return
        
        unread_alerts = alerts.filter(is_read=False).count()
        read_ratio = 1 - (unread_alerts / total_alerts)
        
        # Calculate average response time for acknowledged alerts
        acknowledged_alerts = alerts.filter(is_acknowledged=True).exclude(acknowledged_at__isnull=True)
        
        if acknowledged_alerts.exists():
            response_times = []
            for alert in acknowledged_alerts:
                if alert.acknowledged_at and alert.created_at:
                    delta = alert.acknowledged_at - alert.created_at
                    response_times.append(delta.total_seconds() / 3600)  # hours
            
            if response_times:
                avg_response_hours = np.mean(response_times)
                
                if avg_response_hours > 24:
                    self.recommendations.append({
                        'type': self.RECOMMENDATION_TYPES['OPTIMIZATION'],
                        'priority': self.PRIORITY_LEVELS['MEDIUM'],
                        'title': 'Temps de réponse aux alertes élevé',
                        'description': f'Temps moyen de réponse: {int(avg_response_hours)} heures.',
                        'action': 'Optimiser le processus de traitement des alertes pour une réponse plus rapide.',
                        'impact': 'medium',
                        'confidence': 0.82,
                        'metadata': {
                            'avg_response_hours': int(avg_response_hours),
                            'total_alerts': total_alerts,
                            'unread_count': unread_alerts,
                            'suggestion': 'Activer les notifications push ou SMS pour les alertes critiques'
                        }
                    })
        
        if read_ratio < 0.5:
            self.recommendations.append({
                'type': self.RECOMMENDATION_TYPES['ALERT'],
                'priority': self.PRIORITY_LEVELS['HIGH'],
                'title': 'Nombreuses alertes non traitées',
                'description': f'{int((1 - read_ratio) * 100)}% des alertes n\'ont pas été consultées.',
                'action': 'Prioriser le traitement des alertes en attente.',
                'impact': 'high',
                'confidence': 0.95,
                'metadata': {
                    'read_ratio': read_ratio,
                    'unread_count': unread_alerts,
                    'total_count': total_alerts
                }
            })
    
    def _analyze_time_patterns(self, detections):
        """Analyze temporal patterns in detections"""
        
        if detections.count() < 10:
            return
        
        # Analyze hourly distribution
        hour_counts = defaultdict(int)
        for detection in detections:
            hour_counts[detection.uploaded_at.hour] += 1
        
        if hour_counts:
            # Find peak hours
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            avg_count = sum(hour_counts.values()) / len(hour_counts)
            
            if peak_hour[1] > avg_count * 2:
                self.recommendations.append({
                    'type': self.RECOMMENDATION_TYPES['BEHAVIOR'],
                    'priority': self.PRIORITY_LEVELS['LOW'],
                    'title': 'Pattern horaire identifié',
                    'description': f'Pic d\'activité à {peak_hour[0]}h avec {peak_hour[1]} détections.',
                    'action': 'Renforcer la surveillance pendant les heures de pic.',
                    'impact': 'low',
                    'confidence': 0.78,
                    'metadata': {
                        'peak_hour': peak_hour[0],
                        'peak_count': peak_hour[1],
                        'avg_count': int(avg_count),
                        'pattern_type': 'hourly'
                    }
                })
        
        # Weekend vs weekday analysis
        weekend_count = detections.filter(
            uploaded_at__week_day__in=[1, 7]  # Sunday=1, Saturday=7 in Django
        ).count()
        weekday_count = detections.count() - weekend_count
        
        if weekend_count > 0 and weekday_count > 0:
            ratio = weekend_count / weekday_count
            
            if ratio > 1.5:
                self.recommendations.append({
                    'type': self.RECOMMENDATION_TYPES['BEHAVIOR'],
                    'priority': self.PRIORITY_LEVELS['LOW'],
                    'title': 'Activité accrue le weekend',
                    'description': f'Les weekends représentent une part importante de l\'activité.',
                    'action': 'Adapter la surveillance pour les weekends.',
                    'impact': 'low',
                    'confidence': 0.70,
                    'metadata': {
                        'weekend_count': weekend_count,
                        'weekday_count': weekday_count,
                        'ratio': round(ratio, 2)
                    }
                })


class SmartRecommendationFilter:
    """
    Filtre intelligent pour prioriser et personnaliser les recommandations
    """
    
    @staticmethod
    def filter_recommendations(recommendations, max_count=10, min_confidence=0.6):
        """
        Filter and rank recommendations
        
        Args:
            recommendations: List of recommendation dicts
            max_count: Maximum number to return
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered and sorted list
        """
        # Filter by confidence
        filtered = [
            r for r in recommendations 
            if r.get('confidence', 0) >= min_confidence
        ]
        
        # Sort by priority and confidence
        sorted_recs = sorted(
            filtered,
            key=lambda x: (x.get('priority', 0), x.get('confidence', 0)),
            reverse=True
        )
        
        return sorted_recs[:max_count]
    
    @staticmethod
    def group_by_type(recommendations):
        """
        Group recommendations by type
        
        Returns:
            Dictionary with types as keys
        """
        grouped = defaultdict(list)
        
        for rec in recommendations:
            rec_type = rec.get('type', 'other')
            grouped[rec_type].append(rec)
        
        return dict(grouped)
    
    @staticmethod
    def get_actionable_recommendations(recommendations):
        """
        Filter for highly actionable recommendations
        
        Returns:
            List of actionable recommendations with clear next steps
        """
        actionable = []
        
        for rec in recommendations:
            # Must have high priority or high impact
            if rec.get('priority', 0) >= 4 or rec.get('impact') == 'high':
                # Must have clear action
                if rec.get('action') and len(rec.get('action', '')) > 10:
                    actionable.append(rec)
        
        return actionable


# Alias pour compatibilité avec le code existant
RecommendationEngine = AdvancedRecommendationEngine
