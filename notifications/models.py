from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json


class NotificationPreference(models.Model):
    """
    User preferences for notifications
    """
    NOTIFICATION_METHODS = [
        ('web', 'Web Dashboard'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    # Contact information for SMS
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number for SMS notifications (E.164 format: +33612345678)"
    )
    phone_verified = models.BooleanField(
        default=False,
        help_text="Whether phone number has been verified"
    )
    phone_verification_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    phone_verification_expires = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Canaux de notification activés
    enabled_methods = models.JSONField(
        default=list,
        help_text="List of enabled notification methods"
    )
    
    # Filtres de sévérité minimale
    min_severity_web = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='low'
    )
    min_severity_email = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='high'
    )
    min_severity_sms = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='critical'
    )
    min_severity_push = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium'
    )
    
    # Heures silencieuses (Do Not Disturb)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True, help_text="Start of quiet hours (e.g., 22:00)")
    quiet_hours_end = models.TimeField(null=True, blank=True, help_text="End of quiet hours (e.g., 08:00)")
    
    # Agrégation des notifications
    enable_aggregation = models.BooleanField(
        default=True,
        help_text="Group similar notifications together"
    )
    aggregation_window_minutes = models.IntegerField(
        default=30,
        help_text="Time window for grouping notifications (minutes)"
    )
    
    # Fréquence maximale
    max_notifications_per_hour = models.IntegerField(
        default=10,
        help_text="Maximum notifications per hour (0 = unlimited)"
    )
    
    # Filtres spécifiques
    notify_suspicious_objects = models.BooleanField(default=True)
    notify_anomalies = models.BooleanField(default=True)
    notify_high_frequency = models.BooleanField(default=True)
    notify_unusual_time = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def is_in_quiet_hours(self):
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
        else:
            return self.quiet_hours_start <= now <= self.quiet_hours_end
    
    def can_send_via_method(self, method, severity='medium'):
        """Check if notification can be sent via method based on preferences"""
        # Check if method is enabled
        if method not in self.enabled_methods:
            return False
        
        # Check severity threshold
        severity_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        current_level = severity_levels.get(severity, 1)
        
        min_severity_field = f'min_severity_{method}'
        if hasattr(self, min_severity_field):
            min_severity = getattr(self, min_severity_field)
            min_level = severity_levels.get(min_severity, 1)
            if current_level < min_level:
                return False
        
        # Check quiet hours for intrusive methods (SMS, Push)
        if method in ['sms', 'push'] and self.is_in_quiet_hours():
            # Only allow critical notifications during quiet hours
            if severity != 'critical':
                return False
        
        return True
    
    def generate_phone_verification_code(self):
        """Generate a 6-digit verification code for phone"""
        import random
        code = str(random.randint(100000, 999999))
        self.phone_verification_code = code
        self.phone_verification_expires = timezone.now() + timedelta(minutes=10)
        self.save()
        return code
    
    def verify_phone(self, code):
        """Verify phone number with code"""
        if not self.phone_verification_code or not self.phone_verification_expires:
            return False
        
        if timezone.now() > self.phone_verification_expires:
            return False
        
        if code == self.phone_verification_code:
            self.phone_verified = True
            self.phone_verification_code = None
            self.phone_verification_expires = None
            self.save()
            return True
        
        return False


class Notification(models.Model):
    """
    Individual notification record
    """
    NOTIFICATION_TYPES = [
        ('alert', 'Security Alert'),
        ('insight', 'Analytics Insight'),
        ('report', 'Report'),
        ('system', 'System Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('suppressed', 'Suppressed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium'
    )
    
    # Méthode d'envoi
    delivery_method = models.CharField(max_length=10, choices=NotificationPreference.NOTIFICATION_METHODS)
    
    # État
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Métadonnées
    metadata = models.JSONField(default=dict, help_text="Additional notification data")
    
    # Référence à l'alerte source
    related_alert_id = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Agrégation
    is_aggregated = models.BooleanField(default=False)
    aggregation_group_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'status', 'created_at']),
            models.Index(fields=['aggregation_group_id']),
        ]
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    @property
    def is_read(self):
        """Check if notification has been read"""
        return self.read_at is not None
    
    def get_age_minutes(self):
        """Get notification age in minutes"""
        return (timezone.now() - self.created_at).total_seconds() / 60


class SMSDeliveryLog(models.Model):
    """
    Logs SMS delivery attempts and status
    """
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('undelivered', 'Undelivered'),
    ]
    
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='sms_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sms_logs'
    )
    
    # SMS details
    phone_number = models.CharField(max_length=20)
    message_body = models.TextField()
    sms_provider = models.CharField(
        max_length=20,
        default='twilio',
        choices=[('twilio', 'Twilio'), ('other', 'Other')]
    )
    
    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    provider_message_id = models.CharField(max_length=100, blank=True, null=True)
    provider_status = models.CharField(max_length=50, blank=True, null=True)
    
    # Error tracking
    error_code = models.CharField(max_length=20, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Cost tracking
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    cost_currency = models.CharField(max_length=3, default='USD')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Retry tracking
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'SMS Delivery Log'
        verbose_name_plural = 'SMS Delivery Logs'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_message_id']),
        ]
    
    def __str__(self):
        return f"SMS to {self.phone_number} - {self.status}"
    
    def mark_as_sent(self, message_id=None):
        """Mark SMS as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if message_id:
            self.provider_message_id = message_id
        self.save()
    
    def mark_as_delivered(self):
        """Mark SMS as delivered"""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_code=None, error_message=None):
        """Mark SMS as failed"""
        self.status = 'failed'
        self.failed_at = timezone.now()
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save()
    
    def can_retry(self):
        """Check if SMS can be retried"""
        return self.retry_count < self.max_retries and self.status in ['failed', 'queued']
    
    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1
        self.status = 'queued'
        self.save()


class UserNotificationPreference(NotificationPreference):
    """Alias for backward compatibility"""
    class Meta:
        proxy = True


class NotificationRule(models.Model):
    """
    Custom notification rules for advanced filtering
    """
    CONDITION_CHOICES = [
        ('object_class', 'Object Class Detected'),
        ('detection_count', 'Detection Count Threshold'),
        ('time_range', 'Time Range'),
        ('confidence', 'Confidence Threshold'),
    ]
    
    ACTION_CHOICES = [
        ('notify', 'Send Notification'),
        ('suppress', 'Suppress Notification'),
        ('escalate', 'Escalate Severity'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_rules'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Condition
    condition_type = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    condition_value = models.JSONField(help_text="Condition parameters as JSON")
    
    # Action
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_parameters = models.JSONField(default=dict, help_text="Action parameters as JSON")
    
    # État
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority rules are evaluated first")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Notification Rule'
        verbose_name_plural = 'Notification Rules'
    
    def __str__(self):
        return f"{self.name} ({self.get_action_display()})"


class NotificationLog(models.Model):
    """
    Audit log for sent notifications
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    event = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
    
    def __str__(self):
        return f"{self.event} - {self.timestamp}"


class PredictiveAlert(models.Model):
    """
    Predictive alerts based on pattern analysis
    """
    PREDICTION_TYPES = [
        ('trend', 'Trend Prediction'),
        ('anomaly_forecast', 'Anomaly Forecast'),
        ('risk_assessment', 'Risk Assessment'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictive_alerts'
    )
    
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Prédiction
    predicted_event = models.CharField(max_length=100)
    confidence_score = models.FloatField(help_text="Prediction confidence (0-1)")
    
    # Fenêtre de prédiction
    predicted_timeframe_start = models.DateTimeField()
    predicted_timeframe_end = models.DateTimeField()
    
    # Données de support
    supporting_data = models.JSONField(default=dict)
    
    # Recommandations
    recommendations = models.TextField(blank=True)
    
    # État
    is_active = models.BooleanField(default=True)
    was_accurate = models.BooleanField(null=True, blank=True, help_text="Prediction accuracy (evaluated after timeframe)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
        verbose_name = 'Predictive Alert'
        verbose_name_plural = 'Predictive Alerts'
    
    def __str__(self):
        return f"{self.title} ({self.confidence_score:.2%})"
