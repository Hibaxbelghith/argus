"""
Service de génération de rapports AI pour Analytics
Utilise l'IA pour créer des rapports narratifs intelligents
"""

from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json
from typing import Dict, List, Tuple, Optional
from detection.models import DetectionResult
from .models import DetectionAnalytics, ObjectTrend, SecurityAlert, AnalyticsInsight


class AIReportGenerator:
    """
    Générateur de rapports intelligents avec analyse narrative
    """
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()
    
    def generate_comprehensive_report(self, period='week') -> Dict:
        """
        Génère un rapport complet avec analyse AI
        
        Args:
            period: 'day', 'week', 'month', 'year'
            
        Returns:
            Dict avec toutes les analyses et narratives
        """
        # Déterminer la période
        start_date = self._get_period_start(period)
        
        # Collecter les données
        detections = DetectionResult.objects.filter(
            user=self.user,
            uploaded_at__gte=start_date
        ).order_by('uploaded_at')
        
        if not detections.exists():
            return self._generate_empty_report(period)
        
        # Analyses principales
        summary = self._analyze_summary(detections, period)
        trends = self._analyze_trends(detections)
        patterns = self._analyze_patterns(detections)
        security = self._analyze_security(detections)
        predictions = self._generate_predictions(detections)
        recommendations = self._generate_recommendations(detections, security)
        narrative = self._generate_narrative(summary, trends, patterns, security)
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': self.now,
            'summary': summary,
            'trends': trends,
            'patterns': patterns,
            'security': security,
            'predictions': predictions,
            'recommendations': recommendations,
            'narrative': narrative,
            'generated_at': self.now,
        }
    
    def _get_period_start(self, period: str) -> datetime:
        """Calcule la date de début selon la période"""
        if period == 'day':
            return self.now - timedelta(days=1)
        elif period == 'week':
            return self.now - timedelta(days=7)
        elif period == 'month':
            return self.now - timedelta(days=30)
        elif period == 'year':
            return self.now - timedelta(days=365)
        else:
            return self.now - timedelta(days=7)
    
    def _analyze_summary(self, detections, period: str) -> Dict:
        """Analyse résumée des métriques principales"""
        total_detections = detections.count()
        
        # Extraire les objets de detection_data
        all_objects = []
        confidence_scores = []
        suspicious_count = 0
        
        for det in detections:
            det_data = det.get_detection_data()
            if det_data:
                for obj in det_data:
                    all_objects.append(obj.get('class', 'unknown'))
                    confidence_scores.append(obj.get('confidence', 0))
                    if obj.get('is_suspicious', False):
                        suspicious_count += 1
        
        total_objects = len(all_objects)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        unique_objects = len(set(all_objects))
        
        # Calculer les tendances
        period_mapping = {'day': 24, 'week': 7, 'month': 30, 'year': 12}
        comparison_period = period_mapping.get(period, 7)
        
        previous_start = self._get_period_start(period) - timedelta(days=comparison_period)
        previous_end = self._get_period_start(period)
        
        previous_detections = DetectionResult.objects.filter(
            user=self.user,
            uploaded_at__gte=previous_start,
            uploaded_at__lt=previous_end
        ).count()
        
        if previous_detections > 0:
            change_percent = ((total_detections - previous_detections) / previous_detections) * 100
        else:
            change_percent = 100 if total_detections > 0 else 0
        
        return {
            'total_detections': total_detections,
            'total_objects': total_objects,
            'unique_objects': unique_objects,
            'avg_confidence': round(avg_confidence, 2),
            'suspicious_detections': suspicious_count,
            'change_percent': round(change_percent, 1),
            'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable',
            'most_active_hour': self._find_most_active_hour(detections),
            'detection_rate': round(total_detections / comparison_period, 2),
        }
    
    def _analyze_trends(self, detections) -> Dict:
        """Analyse des tendances temporelles"""
        # Grouper par objet
        object_counts = defaultdict(int)
        object_confidences = defaultdict(list)
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for det in detections:
            det_data = det.get_detection_data()
            hour = det.uploaded_at.hour
            day = det.uploaded_at.strftime('%Y-%m-%d')
            
            hourly_counts[hour] += 1
            daily_counts[day] += 1
            
            if det_data:
                for obj in det_data:
                    obj_class = obj.get('class', 'unknown')
                    object_counts[obj_class] += 1
                    object_confidences[obj_class].append(obj.get('confidence', 0))
        
        # Top objets
        top_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Objets en croissance
        growing_objects = self._identify_growing_trends(object_counts)
        
        # Heures de pointe
        peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'top_objects': [
                {
                    'name': obj,
                    'count': count,
                    'avg_confidence': round(sum(object_confidences[obj]) / len(object_confidences[obj]), 2) if object_confidences[obj] else 0,
                    'percentage': round((count / sum(object_counts.values())) * 100, 1) if object_counts else 0
                }
                for obj, count in top_objects
            ],
            'growing_trends': growing_objects,
            'peak_hours': [{'hour': h, 'count': c} for h, c in peak_hours],
            'daily_distribution': dict(daily_counts),
            'hourly_distribution': dict(hourly_counts),
        }
    
    def _analyze_patterns(self, detections) -> Dict:
        """Détecte les patterns et anomalies"""
        patterns = []
        
        # Pattern 1: Détections nocturnes
        night_detections = sum(
            1 for det in detections 
            if det.uploaded_at.hour >= 22 or det.uploaded_at.hour <= 6
        )
        
        if night_detections > 0:
            night_percent = (night_detections / detections.count()) * 100
            if night_percent > 30:
                patterns.append({
                    'type': 'nocturnal_activity',
                    'severity': 'high' if night_percent > 50 else 'medium',
                    'description': f'{night_percent:.1f}% des détections ont lieu la nuit',
                    'recommendation': 'Renforcez la surveillance nocturne',
                    'count': night_detections
                })
        
        # Pattern 2: Objets suspects récurrents
        suspicious_objects = []
        for det in detections:
            det_data = det.get_detection_data()
            if det_data:
                for obj in det_data:
                    if obj.get('is_suspicious', False):
                        suspicious_objects.append(obj.get('class', 'unknown'))
        
        if suspicious_objects:
            from collections import Counter
            sus_counter = Counter(suspicious_objects)
            for obj, count in sus_counter.most_common(3):
                if count >= 3:
                    patterns.append({
                        'type': 'recurring_suspicious',
                        'severity': 'high',
                        'description': f'Objet suspect récurrent: {obj} ({count} fois)',
                        'recommendation': f'Enquêter sur les détections de {obj}',
                        'count': count
                    })
        
        # Pattern 3: Pics d'activité
        hourly_dist = defaultdict(int)
        for det in detections:
            hourly_dist[det.uploaded_at.hour] += 1
        
        if hourly_dist:
            max_hour = max(hourly_dist.items(), key=lambda x: x[1])
            avg_hourly = sum(hourly_dist.values()) / len(hourly_dist)
            
            if max_hour[1] > avg_hourly * 2:
                patterns.append({
                    'type': 'activity_spike',
                    'severity': 'medium',
                    'description': f'Pic d\'activité à {max_hour[0]}h ({max_hour[1]} détections)',
                    'recommendation': 'Analyser les causes du pic d\'activité',
                    'count': max_hour[1]
                })
        
        return {
            'detected_patterns': patterns,
            'pattern_count': len(patterns),
            'anomaly_score': self._calculate_anomaly_score(detections),
        }
    
    def _analyze_security(self, detections) -> Dict:
        """Analyse de sécurité approfondie"""
        security_score = 100
        risks = []
        
        # Risque 1: Taux de détections suspectes
        suspicious_count = 0
        for det in detections:
            det_data = det.get_detection_data()
            if det_data:
                for obj in det_data:
                    if obj.get('is_suspicious', False):
                        suspicious_count += 1
        
        if detections.count() > 0:
            suspicious_rate = (suspicious_count / detections.count()) * 100
            
            if suspicious_rate > 50:
                security_score -= 30
                risks.append({
                    'type': 'high_suspicious_rate',
                    'severity': 'critical',
                    'description': f'Taux élevé de détections suspectes ({suspicious_rate:.1f}%)',
                    'impact': 30
                })
            elif suspicious_rate > 25:
                security_score -= 15
                risks.append({
                    'type': 'medium_suspicious_rate',
                    'severity': 'high',
                    'description': f'Taux modéré de détections suspectes ({suspicious_rate:.1f}%)',
                    'impact': 15
                })
        
        # Risque 2: Activité nocturne
        night_count = sum(
            1 for det in detections 
            if det.uploaded_at.hour >= 22 or det.uploaded_at.hour <= 6
        )
        
        if night_count > detections.count() * 0.4:
            security_score -= 20
            risks.append({
                'type': 'excessive_night_activity',
                'severity': 'high',
                'description': f'Activité nocturne importante ({night_count} détections)',
                'impact': 20
            })
        
        # Risque 3: Zones à risque
        zones = defaultdict(int)
        for det in detections:
            det_data = det.get_detection_data()
            if det_data:
                for obj in det_data:
                    zone = obj.get('metadata', {}).get('zone', 'unknown')
                    if 'restricted' in zone.lower():
                        zones[zone] += 1
        
        if zones:
            security_score -= 25
            risks.append({
                'type': 'restricted_zone_access',
                'severity': 'critical',
                'description': f'Accès à zones restreintes détecté ({sum(zones.values())} fois)',
                'impact': 25
            })
        
        # Niveau de sécurité
        if security_score >= 80:
            level = 'excellent'
            level_color = 'success'
        elif security_score >= 60:
            level = 'good'
            level_color = 'info'
        elif security_score >= 40:
            level = 'moderate'
            level_color = 'warning'
        else:
            level = 'critical'
            level_color = 'danger'
        
        return {
            'security_score': max(0, security_score),
            'level': level,
            'level_color': level_color,
            'risks': risks,
            'risk_count': len(risks),
            'suspicious_rate': round((suspicious_count / detections.count() * 100), 1) if detections.count() > 0 else 0,
        }
    
    def _generate_predictions(self, detections) -> Dict:
        """Génère des prédictions basées sur les données historiques"""
        if detections.count() < 7:
            return {
                'available': False,
                'reason': 'Données insuffisantes (minimum 7 jours requis)'
            }
        
        # Prédiction du nombre de détections
        daily_counts = defaultdict(int)
        for det in detections:
            day = det.uploaded_at.date()
            daily_counts[day] += 1
        
        avg_daily = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
        
        # Tendance
        if len(daily_counts) >= 3:
            recent_avg = sum(list(daily_counts.values())[-3:]) / 3
            trend_direction = 'increasing' if recent_avg > avg_daily else 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Prédiction pour les 7 prochains jours
        if trend_direction == 'increasing':
            next_week_prediction = int(avg_daily * 1.15 * 7)
        elif trend_direction == 'decreasing':
            next_week_prediction = int(avg_daily * 0.85 * 7)
        else:
            next_week_prediction = int(avg_daily * 7)
        
        return {
            'available': True,
            'next_week_detections': next_week_prediction,
            'avg_daily_detections': round(avg_daily, 1),
            'trend_direction': trend_direction,
            'confidence': 75 if len(daily_counts) >= 14 else 60,
            'peak_day_prediction': self._predict_peak_day(detections),
        }
    
    def _generate_recommendations(self, detections, security_analysis: Dict) -> List[Dict]:
        """Génère des recommandations personnalisées"""
        recommendations = []
        
        # Recommandation basée sur le score de sécurité
        if security_analysis['security_score'] < 60:
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'title': 'Améliorer la sécurité globale',
                'description': 'Votre score de sécurité est faible. Passez en revue les alertes et renforcez la surveillance.',
                'actions': [
                    'Vérifier toutes les alertes de sécurité',
                    'Augmenter la surveillance des zones à risque',
                    'Configurer des notifications SMS pour les alertes critiques'
                ]
            })
        
        # Recommandation basée sur les patterns
        night_count = sum(
            1 for det in detections 
            if det.uploaded_at.hour >= 22 or det.uploaded_at.hour <= 6
        )
        
        if night_count > detections.count() * 0.3:
            recommendations.append({
                'priority': 'medium',
                'category': 'monitoring',
                'title': 'Optimiser la surveillance nocturne',
                'description': f'{night_count} détections nocturnes enregistrées.',
                'actions': [
                    'Installer un éclairage infrarouge',
                    'Activer l\'enregistrement vidéo nocturne',
                    'Configurer des alertes spécifiques pour la nuit'
                ]
            })
        
        # Recommandation basée sur la fréquence
        if detections.count() > 100:
            recommendations.append({
                'priority': 'low',
                'category': 'optimization',
                'title': 'Optimiser les performances',
                'description': 'Volume élevé de détections. Envisagez des optimisations.',
                'actions': [
                    'Ajuster la sensibilité de détection',
                    'Créer des zones d\'exclusion',
                    'Programmer des horaires de détection'
                ]
            })
        
        # Recommandation analytics
        if detections.count() >= 7:
            recommendations.append({
                'priority': 'low',
                'category': 'analytics',
                'title': 'Explorer les analytics avancées',
                'description': 'Vous avez suffisamment de données pour des analyses prédictives.',
                'actions': [
                    'Activer les prédictions ML',
                    'Générer des rapports hebdomadaires',
                    'Configurer des tableaux de bord personnalisés'
                ]
            })
        
        return sorted(recommendations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
    
    def _generate_narrative(self, summary: Dict, trends: Dict, patterns: Dict, security: Dict) -> str:
        """Génère une narrative AI en français"""
        narrative_parts = []
        
        # Introduction
        period_text = {
            'day': 'dernières 24 heures',
            'week': '7 derniers jours',
            'month': '30 derniers jours',
            'year': 'dernière année'
        }
        
        narrative_parts.append(
            f"📊 **Analyse de Période**: Durant les {period_text.get('week', '7 derniers jours')}, "
            f"votre système de surveillance a enregistré **{summary['total_detections']} détections** "
            f"avec un total de **{summary['total_objects']} objets identifiés**."
        )
        
        # Tendance
        if summary['change_percent'] > 10:
            narrative_parts.append(
                f"📈 **Tendance à la Hausse**: L'activité a augmenté de **{summary['change_percent']:.1f}%** "
                f"par rapport à la période précédente, indiquant une augmentation notable du trafic."
            )
        elif summary['change_percent'] < -10:
            narrative_parts.append(
                f"📉 **Tendance à la Baisse**: L'activité a diminué de **{abs(summary['change_percent']):.1f}%** "
                f"par rapport à la période précédente."
            )
        else:
            narrative_parts.append(
                f"➡️ **Activité Stable**: L'activité reste relativement stable avec une variation de {summary['change_percent']:.1f}%."
            )
        
        # Objets principaux
        if trends['top_objects']:
            top_obj = trends['top_objects'][0]
            narrative_parts.append(
                f"🎯 **Détection Principale**: L'objet le plus fréquemment détecté est **{top_obj['name']}** "
                f"avec **{top_obj['count']} occurrences** ({top_obj['percentage']:.1f}% du total) "
                f"et une confiance moyenne de {top_obj['avg_confidence']:.0%}."
            )
        
        # Sécurité
        security_emoji = {
            'excellent': '🛡️',
            'good': '✅',
            'moderate': '⚠️',
            'critical': '🚨'
        }
        
        narrative_parts.append(
            f"{security_emoji.get(security['level'], '📊')} **Évaluation Sécurité**: "
            f"Score de sécurité de **{security['security_score']}/100** ({security['level'].upper()}). "
        )
        
        if security['risks']:
            narrative_parts.append(
                f"⚠️ **Alertes**: {security['risk_count']} risque(s) de sécurité identifié(s) nécessitant attention."
            )
        else:
            narrative_parts.append(
                f"✅ **Aucune alerte**: Aucun risque majeur détecté durant cette période."
            )
        
        # Patterns
        if patterns['detected_patterns']:
            high_severity = sum(1 for p in patterns['detected_patterns'] if p['severity'] == 'high')
            if high_severity > 0:
                narrative_parts.append(
                    f"🔍 **Patterns Détectés**: {patterns['pattern_count']} pattern(s) anormaux identifiés, "
                    f"dont {high_severity} de haute priorité."
                )
        
        # Confiance et qualité
        if summary['avg_confidence'] >= 0.8:
            narrative_parts.append(
                f"🎯 **Haute Précision**: Confiance moyenne de détection de {summary['avg_confidence']:.0%}, "
                f"garantissant une fiabilité optimale des résultats."
            )
        
        return "\n\n".join(narrative_parts)
    
    def _generate_empty_report(self, period: str) -> Dict:
        """Génère un rapport vide pour les périodes sans données"""
        return {
            'period': period,
            'start_date': self._get_period_start(period),
            'end_date': self.now,
            'summary': {
                'total_detections': 0,
                'total_objects': 0,
                'unique_objects': 0,
                'avg_confidence': 0,
                'suspicious_detections': 0,
                'change_percent': 0,
                'trend': 'stable',
            },
            'trends': {'top_objects': [], 'growing_trends': [], 'peak_hours': []},
            'patterns': {'detected_patterns': [], 'pattern_count': 0, 'anomaly_score': 0},
            'security': {'security_score': 100, 'level': 'excellent', 'risks': []},
            'predictions': {'available': False, 'reason': 'Aucune donnée disponible'},
            'recommendations': [],
            'narrative': f"Aucune détection enregistrée durant cette période.",
            'generated_at': self.now,
        }
    
    # Méthodes utilitaires
    
    def _find_most_active_hour(self, detections) -> int:
        """Trouve l'heure la plus active"""
        hourly_counts = defaultdict(int)
        for det in detections:
            hourly_counts[det.uploaded_at.hour] += 1
        
        if hourly_counts:
            return max(hourly_counts.items(), key=lambda x: x[1])[0]
        return 0
    
    def _identify_growing_trends(self, object_counts: Dict) -> List[str]:
        """Identifie les objets en tendance croissante"""
        # Simple heuristique: objets avec plus de 5 détections
        return [obj for obj, count in object_counts.items() if count >= 5]
    
    def _calculate_anomaly_score(self, detections) -> float:
        """Calcule un score d'anomalie (0-100)"""
        score = 0
        
        # Détections nocturnes
        night_count = sum(
            1 for det in detections 
            if det.uploaded_at.hour >= 22 or det.uploaded_at.hour <= 6
        )
        
        if detections.count() > 0:
            night_rate = night_count / detections.count()
            score += min(night_rate * 50, 30)
        
        # Détections suspectes
        suspicious_count = 0
        for det in detections:
            det_data = det.get_detection_data()
            if det_data:
                for obj in det_data:
                    if obj.get('is_suspicious', False):
                        suspicious_count += 1
        
        if detections.count() > 0:
            suspicious_rate = suspicious_count / detections.count()
            score += min(suspicious_rate * 70, 40)
        
        return round(min(score, 100), 1)
    
    def _predict_peak_day(self, detections) -> str:
        """Prédit le jour de la semaine le plus actif"""
        weekday_counts = defaultdict(int)
        for det in detections:
            weekday = det.uploaded_at.strftime('%A')
            weekday_counts[weekday] += 1
        
        if weekday_counts:
            return max(weekday_counts.items(), key=lambda x: x[1])[0]
        return 'Unknown'
