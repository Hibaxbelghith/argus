"""
Interactive Visualizations with Plotly
Charts, heatmaps, and advanced data visualizations
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Conditional imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pandas as pd
    import numpy as np
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.warning("Plotly not installed. Interactive visualizations disabled.")


class ChartGenerator:
    """
    Génère des graphiques interactifs avec Plotly
    """
    
    @staticmethod
    def create_timeline_chart(detections):
        """
        Graphique temporel des détections
        
        Args:
            detections: QuerySet de DetectionResult
            
        Returns:
            JSON Plotly chart or None
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        if not detections.exists():
            return None
        
        # Préparer les données
        dates = [d.uploaded_at for d in detections]
        counts = [d.objects_detected for d in detections]
        
        # Créer le graphique
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='Objects Detected',
            line=dict(color='#4CAF50', width=2),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Detection Timeline',
            xaxis_title='Time',
            yaxis_title='Objects Count',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_hourly_heatmap(analytics_data_list):
        """
        Heatmap de l'activité par heure et jour
        
        Args:
            analytics_data_list: List de DetectionAnalytics
            
        Returns:
            JSON Plotly heatmap
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        # Créer une matrice jour x heure
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = list(range(24))
        
        # Initialiser la matrice
        matrix = np.zeros((7, 24))
        
        for analytics in analytics_data_list:
            day_idx = analytics.period_start.weekday()
            hourly_data = analytics.get_detections_by_hour()
            
            for hour_str, count in hourly_data.items():
                try:
                    hour = int(hour_str)
                    matrix[day_idx][hour] += count
                except (ValueError, IndexError):
                    continue
        
        # Créer le heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=[f'{h:02d}:00' for h in hours],
            y=days,
            colorscale='YlOrRd',
            hoverongaps=False,
            hovertemplate='%{y}<br>%{x}<br>Detections: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Activity Heatmap (Day x Hour)',
            xaxis_title='Hour of Day',
            yaxis_title='Day of Week',
            height=400,
            template='plotly_white'
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_object_distribution_pie(analytics_data):
        """
        Graphique circulaire de la distribution des objets
        
        Args:
            analytics_data: DetectionAnalytics instance
            
        Returns:
            JSON Plotly pie chart
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        objects_by_class = analytics_data.get_objects_by_class()
        
        if not objects_by_class:
            return None
        
        # Trier et limiter aux top 10
        sorted_objects = sorted(objects_by_class.items(), key=lambda x: x[1], reverse=True)[:10]
        
        labels = [obj[0] for obj in sorted_objects]
        values = [obj[1] for obj in sorted_objects]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            hovertemplate='%{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Object Distribution (Top 10)',
            height=400,
            template='plotly_white'
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_trend_chart(object_trends):
        """
        Graphique des tendances d'objets
        
        Args:
            object_trends: QuerySet de ObjectTrend
            
        Returns:
            JSON Plotly bar chart
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        if not object_trends.exists():
            return None
        
        # Top 15 objets
        top_trends = object_trends.order_by('-detection_count')[:15]
        
        objects = [t.object_class for t in top_trends]
        counts = [t.detection_count for t in top_trends]
        
        # Couleurs selon la tendance
        colors = []
        for t in top_trends:
            if t.trend_direction == 'increasing':
                colors.append('#f44336')  # Rouge
            elif t.trend_direction == 'decreasing':
                colors.append('#4CAF50')  # Vert
            else:
                colors.append('#2196F3')  # Bleu
        
        fig = go.Figure(data=[go.Bar(
            x=objects,
            y=counts,
            marker_color=colors,
            hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Object Detection Trends',
            xaxis_title='Object Class',
            yaxis_title='Detection Count',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_anomaly_scatter(detections, anomalies):
        """
        Scatter plot avec anomalies mises en évidence
        
        Args:
            detections: List de détections
            anomalies: List d'anomalies (from AnomalyDetector)
            
        Returns:
            JSON Plotly scatter plot
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        anomaly_ids = set(a['detection_id'] for a in anomalies)
        
        # Séparer normales et anomalies
        normal_times = []
        normal_counts = []
        anomaly_times = []
        anomaly_counts = []
        
        for detection in detections:
            if detection.id in anomaly_ids:
                anomaly_times.append(detection.uploaded_at)
                anomaly_counts.append(detection.objects_detected)
            else:
                normal_times.append(detection.uploaded_at)
                normal_counts.append(detection.objects_detected)
        
        fig = go.Figure()
        
        # Points normaux
        fig.add_trace(go.Scatter(
            x=normal_times,
            y=normal_counts,
            mode='markers',
            name='Normal',
            marker=dict(color='#4CAF50', size=8, opacity=0.6)
        ))
        
        # Anomalies
        fig.add_trace(go.Scatter(
            x=anomaly_times,
            y=anomaly_counts,
            mode='markers',
            name='Anomaly',
            marker=dict(
                color='#f44336',
                size=12,
                symbol='x',
                line=dict(color='darkred', width=2)
            )
        ))
        
        fig.update_layout(
            title='Detection Pattern with Anomalies',
            xaxis_title='Time',
            yaxis_title='Objects Detected',
            height=400,
            template='plotly_white',
            hovermode='closest'
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_prediction_chart(predictions):
        """
        Graphique de prédictions futures
        
        Args:
            predictions: List de prédictions (from TimeSeriesPredictor)
            
        Returns:
            JSON Plotly chart
        """
        if not PLOTLY_AVAILABLE or not predictions:
            return None
        
        dates = [p['date'] for p in predictions]
        predicted = [p['predicted_detections'] for p in predictions]
        lower = [p['lower_bound'] for p in predictions]
        upper = [p['upper_bound'] for p in predictions]
        
        fig = go.Figure()
        
        # Bande de confiance
        fig.add_trace(go.Scatter(
            x=dates + dates[::-1],
            y=upper + lower[::-1],
            fill='toself',
            fillcolor='rgba(0,100,200,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Interval',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # Prédiction
        fig.add_trace(go.Scatter(
            x=dates,
            y=predicted,
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#2196F3', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Activity Forecast (Next 7 Days)',
            xaxis_title='Date',
            yaxis_title='Predicted Detections',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_kpi_dashboard(analytics_data, anomalies=None, trends=None):
        """
        Dashboard multi-graphique avec KPIs
        
        Args:
            analytics_data: DetectionAnalytics
            anomalies: Anomalies détectées
            trends: Tendances
            
        Returns:
            JSON Plotly dashboard avec subplots
        """
        if not PLOTLY_AVAILABLE:
            return None
        
        # Créer des subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Total Detections',
                'Objects per Detection',
                'Security Score',
                'Activity Level'
            ),
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}],
                [{"type": "indicator"}, {"type": "indicator"}]
            ]
        )
        
        # KPI 1: Total Detections
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=analytics_data.total_detections,
            title={'text': "Total Detections"},
            delta={'reference': analytics_data.total_detections * 0.9, 'relative': True},
            domain={'x': [0, 1], 'y': [0, 1]}
        ), row=1, col=1)
        
        # KPI 2: Avg Objects per Detection
        fig.add_trace(go.Indicator(
            mode="number",
            value=analytics_data.avg_objects_per_detection,
            title={'text': "Avg Objects/Detection"},
            number={'suffix': " obj"}
        ), row=1, col=2)
        
        # KPI 3: Security Score (basé sur objets suspects)
        security_score = max(0, 100 - (analytics_data.suspicious_objects_count * 5))
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=security_score,
            title={'text': "Security Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen" if security_score > 80 else "orange" if security_score > 50 else "red"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ), row=2, col=1)
        
        # KPI 4: Anomaly Score
        anomaly_rate = anomalies.get('anomaly_rate', 0) * 100 if anomalies else 0
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=anomaly_rate,
            title={'text': "Anomaly Rate"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "red" if anomaly_rate > 20 else "orange" if anomaly_rate > 10 else "green"}
            }
        ), row=2, col=2)
        
        fig.update_layout(
            height=600,
            template='plotly_white',
            title_text="Analytics Dashboard - Key Performance Indicators"
        )
        
        return fig.to_json()


class ReportVisualizer:
    """
    Génère des rapports visuels complets
    """
    
    @staticmethod
    def generate_comprehensive_report(user, period='weekly'):
        """
        Génère un rapport visuel complet
        
        Args:
            user: User instance
            period: 'daily', 'weekly', 'monthly'
            
        Returns:
            Dict avec tous les graphiques
        """
        from analytics.models import DetectionAnalytics, ObjectTrend
        from detection.models import DetectionResult
        from django.utils import timezone
        from datetime import timedelta
        
        # Récupérer les données
        if period == 'daily':
            days = 1
        elif period == 'weekly':
            days = 7
        else:
            days = 30
        
        start_date = timezone.now() - timedelta(days=days)
        
        analytics_list = DetectionAnalytics.objects.filter(
            user=user,
            period_start__gte=start_date
        ).order_by('period_start')
        
        detections = DetectionResult.objects.filter(
            user=user,
            uploaded_at__gte=start_date
        )
        
        object_trends = ObjectTrend.objects.filter(user=user)
        
        # Générer les graphiques
        charts = {
            'timeline': ChartGenerator.create_timeline_chart(detections),
            'heatmap': ChartGenerator.create_hourly_heatmap(analytics_list),
            'object_distribution': ChartGenerator.create_object_distribution_pie(analytics_list.last()) if analytics_list.exists() else None,
            'trends': ChartGenerator.create_trend_chart(object_trends),
        }
        
        # Ajouter KPI dashboard si data disponible
        if analytics_list.exists():
            charts['kpi_dashboard'] = ChartGenerator.create_kpi_dashboard(analytics_list.last())
        
        return {
            'period': period,
            'charts': charts,
            'generated_at': timezone.now().isoformat(),
            'total_charts': len([c for c in charts.values() if c is not None])
        }
