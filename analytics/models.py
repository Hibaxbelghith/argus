from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import json


class DetectionAnalytics(models.Model):
    """
    Stores aggregated analytics data for detections
    Generated daily/weekly/monthly for each user
    """
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Statistiques de base
    total_detections = models.IntegerField(default=0)
    total_objects_detected = models.IntegerField(default=0)
    avg_objects_per_detection = models.FloatField(default=0.0)
    
    # Détection par catégorie (JSON: {classe: count})
    objects_by_class = models.TextField(default='{}', help_text="JSON: object classes and their counts")
    
    # Tendances temporelles (JSON: {heure: count})
    detections_by_hour = models.TextField(default='{}', help_text="JSON: detections per hour")
    
    # Objets suspects détectés
    suspicious_objects_count = models.IntegerField(default=0)
    
    # Métriques de sécurité
    high_risk_detections = models.IntegerField(default=0, help_text="Detections with high-risk objects")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        verbose_name = 'Detection Analytics'
        verbose_name_plural = 'Detection Analytics'
        unique_together = ['user', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['user', 'period_type', 'period_start']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.period_type} - {self.period_start.date()}"
    
    def get_objects_by_class(self):
        """Parse JSON objects by class"""
        try:
            return json.loads(self.objects_by_class)
        except json.JSONDecodeError:
            return {}
    
    def set_objects_by_class(self, data):
        """Store objects by class as JSON"""
        self.objects_by_class = json.dumps(data)
    
    def get_detections_by_hour(self):
        """Parse JSON detections by hour"""
        try:
            return json.loads(self.detections_by_hour)
        except json.JSONDecodeError:
            return {}
    
    def set_detections_by_hour(self, data):
        """Store detections by hour as JSON"""
        self.detections_by_hour = json.dumps(data)


class ObjectTrend(models.Model):
    """
    Tracks trends for specific object classes over time
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='object_trends'
    )
    object_class = models.CharField(max_length=100, db_index=True)
    
    # Statistiques de tendance
    detection_count = models.IntegerField(default=0)
    first_detected = models.DateTimeField()
    last_detected = models.DateTimeField()
    
    # Tendance (increasing, stable, decreasing)
    trend_direction = models.CharField(
        max_length=20,
        choices=[
            ('increasing', 'Increasing'),
            ('stable', 'Stable'),
            ('decreasing', 'Decreasing'),
        ],
        default='stable'
    )
    
    # Anomalie détectée
    is_anomaly = models.BooleanField(default=False, help_text="Unusual detection pattern")
    anomaly_score = models.FloatField(default=0.0, help_text="Anomaly severity (0-1)")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-detection_count', '-last_detected']
        verbose_name = 'Object Trend'
        verbose_name_plural = 'Object Trends'
        unique_together = ['user', 'object_class']
        indexes = [
            models.Index(fields=['user', 'object_class']),
            models.Index(fields=['is_anomaly', 'anomaly_score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.object_class} ({self.detection_count}x)"


class SecurityAlert(models.Model):
    """
    Generated security alerts based on detection analytics
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    ALERT_TYPE_CHOICES = [
        ('suspicious_object', 'Suspicious Object'),
        ('anomaly', 'Anomaly Detected'),
        ('trend_change', 'Trend Change'),
        ('high_frequency', 'High Frequency Detection'),
        ('unusual_time', 'Unusual Time Detection'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_alerts'
    )
    detection = models.ForeignKey(
        'detection.DetectionResult',
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Données contextuelles (JSON)
    context_data = models.TextField(default='{}', help_text="JSON: additional context")
    
    # État de l'alerte
    is_read = models.BooleanField(default=False)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Security Alert'
        verbose_name_plural = 'Security Alerts'
        indexes = [
            models.Index(fields=['user', 'is_read', 'severity']),
            models.Index(fields=['created_at', 'severity']),
        ]
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
    
    def get_context_data(self):
        """Parse JSON context data"""
        try:
            return json.loads(self.context_data)
        except json.JSONDecodeError:
            return {}
    
    def set_context_data(self, data):
        """Store context data as JSON"""
        self.context_data = json.dumps(data)
    
    def acknowledge(self):
        """Mark alert as acknowledged"""
        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        self.save()


class AnalyticsInsight(models.Model):
    """
    AI-generated insights from detection patterns
    """
    INSIGHT_TYPE_CHOICES = [
        ('pattern', 'Pattern Recognition'),
        ('prediction', 'Predictive Insight'),
        ('recommendation', 'Recommendation'),
        ('summary', 'Summary'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='insights'
    )
    
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Score de confiance (0-1)
    confidence_score = models.FloatField(default=0.0)
    
    # Données associées (JSON)
    data = models.TextField(default='{}', help_text="JSON: supporting data")
    
    # Validité
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
        verbose_name = 'Analytics Insight'
        verbose_name_plural = 'Analytics Insights'
    
    def __str__(self):
        return f"{self.title} ({self.confidence_score:.2f})"
    
    def get_data(self):
        """Parse JSON data"""
        try:
            return json.loads(self.data)
        except json.JSONDecodeError:
            return {}
    
    def set_data(self, data):
        """Store data as JSON"""
        self.data = json.dumps(data)
