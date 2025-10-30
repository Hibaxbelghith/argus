"""
Pattern Recognition Module
Identify user routines, habits, and behavioral patterns
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, time
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """
    Identifie les patterns et routines dans les détections
    """
    
    def __init__(self, user):
        self.user = user
    
    def identify_routines(self, detections, min_occurrences=3):
        """
        Identifie les routines récurrentes
        
        Args:
            detections: QuerySet de DetectionResult
            min_occurrences: Nombre minimum d'occurrences pour considérer comme routine
            
        Returns:
            Dict avec routines identifiées
        """
        # Analyser les patterns temporels
        time_patterns = defaultdict(list)
        day_patterns = defaultdict(int)
        hourly_patterns = defaultdict(int)
        
        for detection in detections:
            dt = detection.uploaded_at
            
            # Pattern jour de la semaine + heure
            day_hour_key = f"{dt.strftime('%A')}_{dt.hour:02d}:00"
            time_patterns[day_hour_key].append(detection)
            
            # Pattern jour seul
            day_patterns[dt.strftime('%A')] += 1
            
            # Pattern heure seule
            hourly_patterns[dt.hour] += 1
        
        # Identifier les routines (patterns récurrents)
        routines = []
        
        for pattern, detections_list in time_patterns.items():
            if len(detections_list) >= min_occurrences:
                day, hour = pattern.split('_')
                routines.append({
                    'type': 'time_routine',
                    'pattern': f"Every {day} around {hour}",
                    'occurrences': len(detections_list),
                    'confidence': min(len(detections_list) / 10, 1.0),  # Max 100% à 10 occurrences
                    'description': f"Regular activity detected on {day}s at {hour}",
                    'detections': [d.id for d in detections_list]
                })
        
        # Identifier les jours favoris
        if day_patterns:
            favorite_day = max(day_patterns.items(), key=lambda x: x[1])
            if favorite_day[1] >= min_occurrences:
                routines.append({
                    'type': 'day_preference',
                    'pattern': f"Most active on {favorite_day[0]}",
                    'occurrences': favorite_day[1],
                    'confidence': favorite_day[1] / sum(day_patterns.values()),
                    'description': f"{favorite_day[0]} is the most active day ({favorite_day[1]} detections)",
                    'data': dict(day_patterns)
                })
        
        # Identifier les heures de pointe régulières
        if hourly_patterns:
            peak_hour = max(hourly_patterns.items(), key=lambda x: x[1])
            if peak_hour[1] >= min_occurrences:
                routines.append({
                    'type': 'peak_hour_routine',
                    'pattern': f"Peak activity at {peak_hour[0]:02d}:00",
                    'occurrences': peak_hour[1],
                    'confidence': peak_hour[1] / sum(hourly_patterns.values()),
                    'description': f"Regular peak activity around {peak_hour[0]:02d}:00 ({peak_hour[1]} detections)",
                    'data': dict(hourly_patterns)
                })
        
        return {
            'routines': sorted(routines, key=lambda x: x['confidence'], reverse=True),
            'total_patterns': len(routines),
            'message': f"Identified {len(routines)} behavioral patterns"
        }
    
    def detect_habit_changes(self, recent_detections, historical_detections):
        """
        Détecte les changements dans les habitudes
        
        Args:
            recent_detections: Détections récentes (7 derniers jours)
            historical_detections: Détections historiques (30 jours avant)
            
        Returns:
            Dict avec changements détectés
        """
        changes = []
        
        # Comparer les patterns horaires
        recent_hours = Counter(d.uploaded_at.hour for d in recent_detections)
        historical_hours = Counter(d.uploaded_at.hour for d in historical_detections)
        
        # Normaliser par le nombre de jours
        recent_days = 7
        historical_days = 30
        
        for hour in range(24):
            recent_rate = recent_hours.get(hour, 0) / recent_days
            historical_rate = historical_hours.get(hour, 0) / historical_days
            
            # Détecter changements significatifs (>50% différence)
            if historical_rate > 0:
                change_pct = (recent_rate - historical_rate) / historical_rate
                
                if abs(change_pct) > 0.5:  # 50% de changement
                    changes.append({
                        'type': 'hourly_change',
                        'hour': hour,
                        'change_direction': 'increase' if change_pct > 0 else 'decrease',
                        'change_percentage': abs(change_pct) * 100,
                        'recent_rate': round(recent_rate, 2),
                        'historical_rate': round(historical_rate, 2),
                        'description': f"{'Increase' if change_pct > 0 else 'Decrease'} in activity at {hour:02d}:00 ({abs(change_pct)*100:.0f}%)"
                    })
        
        # Comparer les jours de la semaine
        recent_days_count = Counter(d.uploaded_at.strftime('%A') for d in recent_detections)
        historical_days_count = Counter(d.uploaded_at.strftime('%A') for d in historical_detections)
        
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            recent_count = recent_days_count.get(day, 0)
            historical_avg = historical_days_count.get(day, 0) / 4  # ~4 semaines
            
            if historical_avg > 0:
                change_pct = (recent_count - historical_avg) / historical_avg
                
                if abs(change_pct) > 0.5:
                    changes.append({
                        'type': 'daily_change',
                        'day': day,
                        'change_direction': 'increase' if change_pct > 0 else 'decrease',
                        'change_percentage': abs(change_pct) * 100,
                        'description': f"{day} activity {'increased' if change_pct > 0 else 'decreased'} by {abs(change_pct)*100:.0f}%"
                    })
        
        # Comparer le nombre moyen d'objets détectés
        recent_avg_objects = sum(d.objects_detected for d in recent_detections) / len(recent_detections) if recent_detections else 0
        historical_avg_objects = sum(d.objects_detected for d in historical_detections) / len(historical_detections) if historical_detections else 0
        
        if historical_avg_objects > 0:
            objects_change = (recent_avg_objects - historical_avg_objects) / historical_avg_objects
            
            if abs(objects_change) > 0.3:
                changes.append({
                    'type': 'detection_density_change',
                    'change_direction': 'increase' if objects_change > 0 else 'decrease',
                    'change_percentage': abs(objects_change) * 100,
                    'recent_avg': round(recent_avg_objects, 1),
                    'historical_avg': round(historical_avg_objects, 1),
                    'description': f"Average objects per detection {'increased' if objects_change > 0 else 'decreased'} from {historical_avg_objects:.1f} to {recent_avg_objects:.1f}"
                })
        
        return {
            'changes': sorted(changes, key=lambda x: x['change_percentage'], reverse=True),
            'total_changes': len(changes),
            'significant_changes': len([c for c in changes if c['change_percentage'] > 100]),
            'message': f"Detected {len(changes)} behavioral changes"
        }
    
    def identify_object_associations(self, detections):
        """
        Identifie les objets fréquemment détectés ensemble
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            Dict avec associations d'objets
        """
        # Compter les co-occurrences d'objets
        cooccurrences = defaultdict(int)
        object_counts = defaultdict(int)
        
        for detection in detections:
            detection_data = detection.get_detection_data()
            if not detection_data:
                continue
            
            # Extraire les classes d'objets
            objects = [obj.get('class', 'unknown') for obj in detection_data]
            object_set = set(objects)
            
            # Compter chaque objet
            for obj in object_set:
                object_counts[obj] += 1
            
            # Compter les paires d'objets
            for obj1 in object_set:
                for obj2 in object_set:
                    if obj1 < obj2:  # Éviter les duplicatas
                        cooccurrences[(obj1, obj2)] += 1
        
        # Calculer les associations fortes
        associations = []
        
        for (obj1, obj2), count in cooccurrences.items():
            # Calculer la confiance de l'association
            confidence1 = count / object_counts[obj1] if object_counts[obj1] > 0 else 0
            confidence2 = count / object_counts[obj2] if object_counts[obj2] > 0 else 0
            
            # Moyenne des confidences
            avg_confidence = (confidence1 + confidence2) / 2
            
            if count >= 3 and avg_confidence >= 0.3:  # Au moins 3 occurrences et 30% de confiance
                associations.append({
                    'object_1': obj1,
                    'object_2': obj2,
                    'cooccurrence_count': count,
                    'confidence': round(avg_confidence, 2),
                    'description': f"{obj1} and {obj2} detected together {count} times ({avg_confidence*100:.0f}% association)"
                })
        
        return {
            'associations': sorted(associations, key=lambda x: x['confidence'], reverse=True),
            'total_associations': len(associations),
            'message': f"Found {len(associations)} object associations"
        }
    
    def classify_behavior_profile(self, detections):
        """
        Classe le profil comportemental de l'utilisateur
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            Dict avec profil comportemental
        """
        if not detections.exists():
            return {
                'profile_type': 'unknown',
                'characteristics': [],
                'message': 'Insufficient data for behavior profiling'
            }
        
        total = detections.count()
        
        # Analyser les patterns temporels
        hours = [d.uploaded_at.hour for d in detections]
        
        day_count = sum(1 for h in hours if 6 <= h < 18)
        night_count = total - day_count
        
        weekday_count = sum(1 for d in detections if d.uploaded_at.weekday() < 5)
        weekend_count = total - weekday_count
        
        # Déterminer le profil
        characteristics = []
        
        # Pattern jour/nuit
        if day_count / total > 0.8:
            characteristics.append('predominantly_daytime_activity')
        elif night_count / total > 0.8:
            characteristics.append('predominantly_nighttime_activity')
        else:
            characteristics.append('balanced_day_night_activity')
        
        # Pattern semaine/weekend
        if weekday_count / total > 0.8:
            characteristics.append('weekday_focused')
        elif weekend_count / total > 0.8:
            characteristics.append('weekend_focused')
        else:
            characteristics.append('balanced_weekly_activity')
        
        # Régularité
        routines = self.identify_routines(detections, min_occurrences=2)
        if routines['total_patterns'] > 5:
            characteristics.append('highly_routine_based')
            profile_type = 'predictable'
        elif routines['total_patterns'] > 2:
            characteristics.append('moderately_routine_based')
            profile_type = 'semi_predictable'
        else:
            characteristics.append('irregular_patterns')
            profile_type = 'unpredictable'
        
        # Niveau d'activité
        if total > 100:
            characteristics.append('high_activity')
        elif total > 30:
            characteristics.append('moderate_activity')
        else:
            characteristics.append('low_activity')
        
        return {
            'profile_type': profile_type,
            'characteristics': characteristics,
            'activity_level': 'high' if total > 100 else 'moderate' if total > 30 else 'low',
            'day_night_ratio': round(day_count / total, 2),
            'weekday_weekend_ratio': round(weekday_count / total, 2),
            'routine_count': routines['total_patterns'],
            'description': self._describe_profile(profile_type, characteristics),
            'message': 'Behavior profile generated successfully'
        }
    
    def _describe_profile(self, profile_type, characteristics):
        """Génère une description textuelle du profil"""
        descriptions = {
            'predictable': "User exhibits highly predictable behavior with consistent routines.",
            'semi_predictable': "User shows moderate consistency with some routine patterns.",
            'unpredictable': "User behavior is irregular with few consistent patterns."
        }
        
        base = descriptions.get(profile_type, "User behavior profile generated.")
        
        # Ajouter des détails
        details = []
        if 'predominantly_daytime_activity' in characteristics:
            details.append("mostly active during daytime")
        elif 'predominantly_nighttime_activity' in characteristics:
            details.append("mostly active at night")
        
        if 'weekday_focused' in characteristics:
            details.append("focused on weekdays")
        elif 'weekend_focused' in characteristics:
            details.append("focused on weekends")
        
        if details:
            base += f" Activity is {', '.join(details)}."
        
        return base


class RecommendationEngine:
    """
    Génère des recommandations intelligentes basées sur les patterns
    """
    
    @staticmethod
    def generate_system_recommendations(user, analytics_data, patterns):
        """
        Génère des recommandations pour optimiser le système
        
        Args:
            user: User instance
            analytics_data: DetectionAnalytics
            patterns: Dict de patterns identifiés
            
        Returns:
            List de recommandations
        """
        recommendations = []
        
        # Recommandations basées sur les routines
        routines = patterns.get('routines', [])
        if routines:
            for routine in routines[:3]:
                if routine['type'] == 'peak_hour_routine':
                    recommendations.append({
                        'category': 'optimization',
                        'priority': 'medium',
                        'title': 'Optimize Peak Hour Monitoring',
                        'description': f"Increase sensitivity during peak hours ({routine['pattern']})",
                        'action': 'adjust_sensitivity',
                        'parameters': {'peak_hours': routine.get('data', {})}
                    })
        
        # Recommandations basées sur les anomalies
        if analytics_data.suspicious_objects_count > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'high',
                'title': 'Review Suspicious Object Detections',
                'description': f"Detected {analytics_data.suspicious_objects_count} suspicious objects",
                'action': 'review_alerts',
                'parameters': {'alert_type': 'suspicious_object'}
            })
        
        # Recommandations basées sur l'activité
        if analytics_data.total_detections < 5:
            recommendations.append({
                'category': 'configuration',
                'priority': 'low',
                'title': 'Low Detection Activity',
                'description': 'Consider adjusting camera angles or detection sensitivity',
                'action': 'check_configuration',
                'parameters': {'detection_count': analytics_data.total_detections}
            })
        elif analytics_data.total_detections > 100:
            recommendations.append({
                'category': 'optimization',
                'priority': 'medium',
                'title': 'High Detection Volume',
                'description': 'Consider filtering common objects to reduce noise',
                'action': 'configure_filters',
                'parameters': {'detection_count': analytics_data.total_detections}
            })
        
        # Recommandations de sécurité
        if analytics_data.high_risk_detections > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'critical',
                'title': 'High-Risk Objects Detected',
                'description': f"{analytics_data.high_risk_detections} high-risk detections require immediate attention",
                'action': 'urgent_review',
                'parameters': {'risk_level': 'high', 'count': analytics_data.high_risk_detections}
            })
        
        return sorted(recommendations, key=lambda x: ['low', 'medium', 'high', 'critical'].index(x['priority']), reverse=True)
