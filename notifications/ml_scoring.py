"""
ML-based Notification Scoring and Priority System
Uses XGBoost for intelligent alert prioritization
"""
from django.utils import timezone
from datetime import timedelta
import logging
import pickle
import os

logger = logging.getLogger(__name__)

# Conditional imports
try:
    import xgboost as xgb
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import LabelEncoder
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost or sklearn not installed. ML scoring disabled.")


class NotificationScorer:
    """
    Score les notifications de 0-100 selon critères multiples
    """
    
    # Poids des facteurs de scoring
    WEIGHTS = {
        'severity': 0.30,           # Sévérité de l'alerte
        'time_context': 0.15,       # Heure de la journée
        'object_risk': 0.25,        # Risque de l'objet détecté
        'frequency': 0.10,          # Fréquence de détection
        'confidence': 0.10,         # Confiance de détection
        'user_history': 0.10,       # Historique utilisateur
    }
    
    # Objets à haut risque
    HIGH_RISK_OBJECTS = ['gun', 'weapon', 'knife', 'fire', 'person_unknown']
    MEDIUM_RISK_OBJECTS = ['person', 'scissors', 'broken_glass', 'crowbar']
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle XGBoost pré-entraîné (si disponible)"""
        model_path = os.path.join('notifications', 'models', 'xgb_scorer.pkl')
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("XGBoost scoring model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
                self.model = None
        else:
            logger.info("No pre-trained model found. Using rule-based scoring.")
    
    def score_notification(self, alert, detection=None, user_preferences=None):
        """
        Calcule un score de priorité (0-100) pour une notification
        
        Args:
            alert: SecurityAlert instance
            detection: DetectionResult instance (optional)
            user_preferences: NotificationPreference instance (optional)
            
        Returns:
            Dict avec score et détails
        """
        # Si modèle ML disponible, l'utiliser
        if XGBOOST_AVAILABLE and self.model is not None:
            return self._ml_score(alert, detection, user_preferences)
        
        # Sinon, scoring basé sur règles
        return self._rule_based_score(alert, detection, user_preferences)
    
    def _rule_based_score(self, alert, detection, user_preferences):
        """Scoring basé sur règles (fallback)"""
        scores = {}
        
        # 1. Score de sévérité (0-30 points)
        severity_scores = {
            'low': 5,
            'medium': 15,
            'high': 25,
            'critical': 30
        }
        scores['severity'] = severity_scores.get(alert.severity, 10)
        
        # 2. Score de contexte temporel (0-15 points)
        now = timezone.now()
        hour = now.hour
        
        # Nuit = plus de points
        if hour < 6 or hour > 22:
            scores['time_context'] = 15
        elif 6 <= hour < 9 or 18 <= hour <= 22:
            scores['time_context'] = 10
        else:
            scores['time_context'] = 5
        
        # 3. Score de risque d'objet (0-25 points)
        scores['object_risk'] = self._calculate_object_risk(alert, detection)
        
        # 4. Score de fréquence (0-10 points)
        scores['frequency'] = self._calculate_frequency_score(alert)
        
        # 5. Score de confiance (0-10 points)
        if detection:
            detection_data = detection.get_detection_data()
            if detection_data:
                avg_confidence = sum(obj.get('confidence', 0) for obj in detection_data) / len(detection_data)
                scores['confidence'] = int(avg_confidence * 10)
            else:
                scores['confidence'] = 5
        else:
            scores['confidence'] = 5
        
        # 6. Score basé sur historique utilisateur (0-10 points)
        scores['user_history'] = self._calculate_user_history_score(alert, user_preferences)
        
        # Score total
        total_score = sum(scores.values())
        
        # Normaliser à 0-100
        final_score = min(100, max(0, total_score))
        
        return {
            'score': final_score,
            'priority_level': self._score_to_priority(final_score),
            'breakdown': scores,
            'method': 'rule_based',
            'explanation': self._generate_explanation(scores, final_score)
        }
    
    def _ml_score(self, alert, detection, user_preferences):
        """Scoring avec modèle XGBoost (si disponible)"""
        try:
            # Préparer les features
            features = self._prepare_features(alert, detection, user_preferences)
            
            # Prédire le score
            X = pd.DataFrame([features])
            predicted_score = self.model.predict(X)[0]
            
            # Normaliser à 0-100
            final_score = min(100, max(0, int(predicted_score)))
            
            return {
                'score': final_score,
                'priority_level': self._score_to_priority(final_score),
                'method': 'xgboost_ml',
                'explanation': f"ML model predicted score: {final_score}/100"
            }
        
        except Exception as e:
            logger.error(f"ML scoring failed: {e}. Falling back to rule-based.")
            return self._rule_based_score(alert, detection, user_preferences)
    
    def _prepare_features(self, alert, detection, user_preferences):
        """Prépare les features pour le modèle ML"""
        features = {}
        
        # Features temporelles
        now = timezone.now()
        features['hour'] = now.hour
        features['day_of_week'] = now.weekday()
        features['is_weekend'] = 1 if now.weekday() >= 5 else 0
        features['is_night'] = 1 if now.hour < 6 or now.hour > 22 else 0
        
        # Features de l'alerte
        features['severity_encoded'] = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}.get(alert.severity, 1)
        features['alert_type_encoded'] = {
            'suspicious_object': 3,
            'anomaly': 2,
            'high_frequency': 1,
            'unusual_time': 2,
            'trend_change': 1
        }.get(alert.alert_type, 1)
        
        # Features de détection
        if detection:
            features['objects_count'] = detection.objects_detected
            detection_data = detection.get_detection_data()
            if detection_data:
                features['avg_confidence'] = sum(obj.get('confidence', 0) for obj in detection_data) / len(detection_data)
            else:
                features['avg_confidence'] = 0.5
        else:
            features['objects_count'] = 0
            features['avg_confidence'] = 0.5
        
        # Features utilisateur
        if user_preferences:
            features['quiet_hours'] = 1 if user_preferences.is_in_quiet_hours() else 0
        else:
            features['quiet_hours'] = 0
        
        return features
    
    def _calculate_object_risk(self, alert, detection):
        """Calcule le score de risque basé sur les objets détectés"""
        if not detection:
            # Basé sur le type d'alerte
            if alert.alert_type == 'suspicious_object':
                return 25
            elif alert.alert_type == 'anomaly':
                return 20
            else:
                return 10
        
        detection_data = detection.get_detection_data()
        if not detection_data:
            return 10
        
        max_risk = 0
        
        for obj in detection_data:
            obj_class = obj.get('class', '').lower()
            
            if any(risk_obj in obj_class for risk_obj in self.HIGH_RISK_OBJECTS):
                max_risk = max(max_risk, 25)
            elif any(risk_obj in obj_class for risk_obj in self.MEDIUM_RISK_OBJECTS):
                max_risk = max(max_risk, 15)
            else:
                max_risk = max(max_risk, 5)
        
        return max_risk
    
    def _calculate_frequency_score(self, alert):
        """Score basé sur la fréquence de détections similaires"""
        from analytics.models import SecurityAlert
        
        # Compter les alertes similaires dans les dernières 24h
        similar_alerts = SecurityAlert.objects.filter(
            user=alert.user,
            alert_type=alert.alert_type,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Plus d'alertes similaires = score plus élevé (pattern suspect)
        if similar_alerts > 10:
            return 10
        elif similar_alerts > 5:
            return 7
        elif similar_alerts > 2:
            return 5
        else:
            return 3
    
    def _calculate_user_history_score(self, alert, user_preferences):
        """Score basé sur l'historique et préférences utilisateur"""
        if not user_preferences:
            return 5
        
        score = 5
        
        # Si l'utilisateur a activé les notifications pour ce type
        if alert.alert_type == 'suspicious_object' and user_preferences.notify_suspicious_objects:
            score += 3
        elif alert.alert_type == 'anomaly' and user_preferences.notify_anomalies:
            score += 3
        elif alert.alert_type == 'high_frequency' and user_preferences.notify_high_frequency:
            score += 3
        elif alert.alert_type == 'unusual_time' and user_preferences.notify_unusual_time:
            score += 3
        
        # Pénaliser si en heures silencieuses (mais pas bloquer complètement)
        if user_preferences.is_in_quiet_hours():
            score -= 2
        
        return max(0, score)
    
    def _score_to_priority(self, score):
        """Convertit un score en niveau de priorité"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _generate_explanation(self, scores, final_score):
        """Génère une explication textuelle du score"""
        explanations = []
        
        if scores.get('severity', 0) >= 25:
            explanations.append("High severity alert")
        
        if scores.get('time_context', 0) >= 10:
            explanations.append("Detected during unusual hours")
        
        if scores.get('object_risk', 0) >= 20:
            explanations.append("High-risk object detected")
        
        if scores.get('frequency', 0) >= 7:
            explanations.append("Frequent similar detections")
        
        if not explanations:
            explanations.append("Standard priority alert")
        
        return f"{self._score_to_priority(final_score).upper()}: {', '.join(explanations)}"


class FalseAlertFilter:
    """
    Filtre les fausses alertes en apprenant des patterns
    """
    
    def __init__(self):
        self.false_positive_patterns = self._load_false_positive_patterns()
    
    def _load_false_positive_patterns(self):
        """Charge les patterns de fausses alertes connus"""
        # En production, ceci serait chargé depuis la base de données
        return {
            'frequent_objects': ['car', 'bird', 'cat', 'dog'],  # Objets courants
            'normal_hours': range(8, 20),  # Heures normales
        }
    
    def is_likely_false_positive(self, alert, detection=None, user_history=None):
        """
        Détermine si une alerte est probablement un faux positif
        
        Args:
            alert: SecurityAlert instance
            detection: DetectionResult instance
            user_history: Historique de détections similaires
            
        Returns:
            Dict avec probabilité de faux positif et raison
        """
        false_positive_score = 0
        reasons = []
        
        # 1. Vérifier si objet commun pendant heures normales
        if detection:
            hour = detection.uploaded_at.hour
            detection_data = detection.get_detection_data()
            
            if detection_data:
                for obj in detection_data:
                    obj_class = obj.get('class', '').lower()
                    
                    if obj_class in self.false_positive_patterns['frequent_objects']:
                        if hour in self.false_positive_patterns['normal_hours']:
                            false_positive_score += 30
                            reasons.append(f"Common object ({obj_class}) during normal hours")
        
        # 2. Vérifier si l'utilisateur a déjà marqué des alertes similaires comme fausses
        if user_history:
            # Cette logique nécessiterait un modèle de tracking des feedbacks utilisateur
            pass
        
        # 3. Sévérité faible + aucun objet à risque
        if alert.severity == 'low' and alert.alert_type not in ['suspicious_object', 'anomaly']:
            false_positive_score += 20
            reasons.append("Low severity, non-critical type")
        
        # 4. Confiance de détection faible
        if detection:
            detection_data = detection.get_detection_data()
            if detection_data:
                avg_confidence = sum(obj.get('confidence', 0) for obj in detection_data) / len(detection_data)
                if avg_confidence < 0.5:
                    false_positive_score += 25
                    reasons.append(f"Low detection confidence ({avg_confidence:.2f})")
        
        is_false_positive = false_positive_score >= 50
        
        return {
            'is_likely_false_positive': is_false_positive,
            'confidence': false_positive_score / 100,
            'reasons': reasons,
            'recommendation': 'suppress' if is_false_positive else 'send',
            'score': false_positive_score
        }
    
    def train_from_feedback(self, user, feedback_data):
        """
        Entraîne le filtre à partir des feedbacks utilisateur
        
        Args:
            user: User instance
            feedback_data: List de {'alert_id': ..., 'is_false_positive': bool}
        """
        # En production, ceci mettrait à jour un modèle ML
        # Pour l'instant, on log simplement
        logger.info(f"Received {len(feedback_data)} feedback entries from user {user.username}")
        
        # Compter les patterns de faux positifs
        false_positive_patterns = {
            'alert_types': {},
            'object_classes': {},
            'hours': {}
        }
        
        for feedback in feedback_data:
            if feedback.get('is_false_positive'):
                # Extraire le pattern
                alert_type = feedback.get('alert_type')
                if alert_type:
                    false_positive_patterns['alert_types'][alert_type] = \
                        false_positive_patterns['alert_types'].get(alert_type, 0) + 1
        
        logger.info(f"False positive patterns: {false_positive_patterns}")
        
        return {
            'patterns_learned': len(false_positive_patterns),
            'message': 'Feedback processed successfully'
        }
