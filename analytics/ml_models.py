"""
ML Models for Advanced Analytics
Anomaly Detection, Prediction, and Pattern Recognition
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Conditional imports for optional dependencies
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed. Time series forecasting disabled.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost not installed. Advanced predictions disabled.")


class AnomalyDetector:
    """
    Détection d'anomalies dans les patterns de détection
    Utilise Isolation Forest et DBSCAN
    """
    
    def __init__(self, contamination=0.1):
        """
        Args:
            contamination: Proportion attendue d'anomalies (0.1 = 10%)
        """
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
    def prepare_features(self, detections):
        """
        Prépare les features pour la détection d'anomalies
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            DataFrame avec features extraites
        """
        features = []
        
        for detection in detections:
            # Extraction de features temporelles et contextuelles
            dt = detection.uploaded_at
            
            feature_dict = {
                'hour': dt.hour,
                'day_of_week': dt.weekday(),
                'objects_count': detection.objects_detected,
                'is_weekend': 1 if dt.weekday() >= 5 else 0,
                'is_night': 1 if dt.hour < 6 or dt.hour > 22 else 0,
            }
            
            # Analyse des objets détectés
            detection_data = detection.get_detection_data()
            if detection_data:
                # Nombre d'objets par classe
                classes_count = {}
                confidences = []
                
                for obj in detection_data:
                    obj_class = obj.get('class', 'unknown')
                    confidence = obj.get('confidence', 0)
                    
                    classes_count[obj_class] = classes_count.get(obj_class, 0) + 1
                    confidences.append(confidence)
                
                feature_dict['avg_confidence'] = np.mean(confidences) if confidences else 0
                feature_dict['unique_classes'] = len(classes_count)
                feature_dict['max_class_count'] = max(classes_count.values()) if classes_count else 0
            else:
                feature_dict['avg_confidence'] = 0
                feature_dict['unique_classes'] = 0
                feature_dict['max_class_count'] = 0
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)
    
    def detect_anomalies(self, detections):
        """
        Détecte les anomalies dans les détections
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            Dict avec anomalies détectées et scores
        """
        if len(detections) < 10:
            return {
                'anomalies': [],
                'anomaly_rate': 0,
                'message': 'Insufficient data for anomaly detection (minimum 10 samples required)'
            }
        
        # Préparer les features
        df = self.prepare_features(detections)
        
        if df.empty:
            return {'anomalies': [], 'anomaly_rate': 0, 'message': 'No features extracted'}
        
        # Normaliser les features
        X = self.scaler.fit_transform(df)
        
        # Détecter les anomalies avec Isolation Forest
        predictions = self.isolation_forest.fit_predict(X)
        anomaly_scores = self.isolation_forest.score_samples(X)
        
        # Identifier les anomalies (-1 = anomalie, 1 = normal)
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            detection = detections[idx]
            anomalies.append({
                'detection_id': detection.id,
                'timestamp': detection.uploaded_at,
                'anomaly_score': abs(anomaly_scores[idx]),
                'features': df.iloc[idx].to_dict(),
                'reason': self._explain_anomaly(df.iloc[idx])
            })
        
        return {
            'anomalies': anomalies,
            'anomaly_rate': len(anomalies) / len(detections),
            'total_detections': len(detections),
            'anomaly_count': len(anomalies),
            'message': f'Detected {len(anomalies)} anomalies out of {len(detections)} detections'
        }
    
    def _explain_anomaly(self, features):
        """Génère une explication pour l'anomalie"""
        reasons = []
        
        if features['is_night'] == 1:
            reasons.append('Detection during unusual hours (night)')
        
        if features['objects_count'] > 10:
            reasons.append(f'Unusually high object count ({features["objects_count"]})')
        
        if features['unique_classes'] > 5:
            reasons.append(f'High diversity of objects ({features["unique_classes"]} classes)')
        
        if features['avg_confidence'] < 0.5:
            reasons.append(f'Low confidence score ({features["avg_confidence"]:.2f})')
        
        return ' | '.join(reasons) if reasons else 'Pattern deviation from normal behavior'
    
    def cluster_detections(self, detections, eps=0.5, min_samples=5):
        """
        Groupe les détections similaires avec DBSCAN
        
        Args:
            detections: QuerySet de DetectionResult
            eps: Distance maximale entre deux échantillons
            min_samples: Nombre minimum d'échantillons pour un cluster
            
        Returns:
            Dict avec clusters identifiés
        """
        if len(detections) < min_samples:
            return {'clusters': [], 'noise_points': 0, 'message': 'Insufficient data for clustering'}
        
        df = self.prepare_features(detections)
        X = self.scaler.fit_transform(df)
        
        # Clustering DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(X)
        
        # Analyser les clusters
        unique_clusters = set(clusters)
        cluster_info = []
        
        for cluster_id in unique_clusters:
            if cluster_id == -1:  # Bruit
                continue
            
            cluster_indices = np.where(clusters == cluster_id)[0]
            cluster_detections = [detections[i] for i in cluster_indices]
            
            cluster_info.append({
                'cluster_id': cluster_id,
                'size': len(cluster_indices),
                'detections': [d.id for d in cluster_detections],
                'pattern_summary': self._summarize_cluster(df.iloc[cluster_indices])
            })
        
        noise_count = np.sum(clusters == -1)
        
        return {
            'clusters': cluster_info,
            'cluster_count': len(cluster_info),
            'noise_points': noise_count,
            'message': f'Identified {len(cluster_info)} behavior patterns'
        }
    
    def _summarize_cluster(self, cluster_df):
        """Résume les caractéristiques d'un cluster"""
        return {
            'avg_hour': cluster_df['hour'].mean(),
            'avg_objects': cluster_df['objects_count'].mean(),
            'dominant_day': cluster_df['day_of_week'].mode()[0] if len(cluster_df) > 0 else None,
            'night_detections': cluster_df['is_night'].sum(),
            'weekend_detections': cluster_df['is_weekend'].sum(),
        }


class TimeSeriesPredictor:
    """
    Prédiction de séries temporelles avec Prophet
    Prévoit l'activité future et les tendances
    """
    
    def __init__(self):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet is required for time series prediction. Install with: pip install prophet")
        self.model = None
        
    def prepare_timeseries_data(self, detections):
        """
        Prépare les données pour Prophet (format: ds, y)
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            DataFrame au format Prophet
        """
        # Agréger par jour
        daily_counts = {}
        
        for detection in detections:
            date = detection.uploaded_at.date()
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        # Créer DataFrame
        df = pd.DataFrame([
            {'ds': date, 'y': count}
            for date, count in sorted(daily_counts.items())
        ])
        
        return df
    
    def forecast(self, detections, periods=7):
        """
        Génère des prévisions pour les prochains jours
        
        Args:
            detections: QuerySet de DetectionResult
            periods: Nombre de jours à prédire
            
        Returns:
            Dict avec prédictions et tendances
        """
        if not PROPHET_AVAILABLE:
            return {'error': 'Prophet not available', 'predictions': []}
        
        df = self.prepare_timeseries_data(detections)
        
        if len(df) < 2:
            return {
                'error': 'Insufficient data',
                'message': 'Need at least 2 days of data for forecasting',
                'predictions': []
            }
        
        # Entraîner le modèle Prophet
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05
        )
        
        self.model.fit(df)
        
        # Générer les prédictions futures
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        
        # Extraire les prédictions futures
        predictions = []
        for _, row in forecast.tail(periods).iterrows():
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_detections': max(0, int(row['yhat'])),
                'lower_bound': max(0, int(row['yhat_lower'])),
                'upper_bound': max(0, int(row['yhat_upper'])),
                'trend': row['trend']
            })
        
        # Analyser la tendance globale
        trend_direction = 'stable'
        if len(forecast) > 1:
            trend_change = forecast['trend'].iloc[-1] - forecast['trend'].iloc[0]
            if trend_change > 0.5:
                trend_direction = 'increasing'
            elif trend_change < -0.5:
                trend_direction = 'decreasing'
        
        return {
            'predictions': predictions,
            'trend_direction': trend_direction,
            'current_activity': int(df['y'].tail(7).mean()),
            'predicted_activity': int(np.mean([p['predicted_detections'] for p in predictions])),
            'message': f'Generated {periods}-day forecast with {trend_direction} trend'
        }
    
    def detect_changepoints(self, detections):
        """
        Détecte les points de changement dans les tendances
        
        Returns:
            Liste des dates où des changements significatifs sont détectés
        """
        if not PROPHET_AVAILABLE or self.model is None:
            return []
        
        df = self.prepare_timeseries_data(detections)
        
        if len(df) < 2:
            return []
        
        # Réentraîner si nécessaire
        if self.model is None:
            self.model = Prophet()
            self.model.fit(df)
        
        # Récupérer les changepoints
        changepoints = []
        if hasattr(self.model, 'changepoints'):
            for cp in self.model.changepoints:
                changepoints.append({
                    'date': cp.strftime('%Y-%m-%d'),
                    'significance': 'high'  # Simplified
                })
        
        return changepoints


class TrendAnalyzer:
    """
    Analyse avancée des tendances avec XGBoost
    """
    
    def __init__(self):
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available. Advanced trend analysis disabled.")
        self.model = None
    
    def analyze_object_trends(self, object_trends):
        """
        Analyse les tendances des objets détectés
        
        Args:
            object_trends: QuerySet de ObjectTrend
            
        Returns:
            Insights sur les tendances
        """
        if not object_trends.exists():
            return {'trends': [], 'message': 'No trend data available'}
        
        trends = []
        
        for trend in object_trends:
            # Calculer le taux de croissance
            days_active = (trend.last_detected - trend.first_detected).days + 1
            detection_rate = trend.detection_count / max(days_active, 1)
            
            # Classifier la tendance
            if trend.trend_direction == 'increasing' and detection_rate > 1:
                urgency = 'high'
            elif trend.trend_direction == 'stable':
                urgency = 'low'
            else:
                urgency = 'medium'
            
            trends.append({
                'object_class': trend.object_class,
                'trend_direction': trend.trend_direction,
                'detection_count': trend.detection_count,
                'detection_rate': round(detection_rate, 2),
                'is_anomaly': trend.is_anomaly,
                'anomaly_score': trend.anomaly_score,
                'urgency': urgency,
                'days_active': days_active
            })
        
        # Trier par urgence et score d'anomalie
        trends.sort(key=lambda x: (x['urgency'] == 'high', x['anomaly_score']), reverse=True)
        
        return {
            'trends': trends,
            'total_objects': len(trends),
            'anomalous_objects': sum(1 for t in trends if t['is_anomaly']),
            'message': f'Analyzed {len(trends)} object trends'
        }
