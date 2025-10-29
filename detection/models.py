from django.db import models
from django.conf import settings
import json


class DetectionResult(models.Model):
    """Model to store object detection results"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='detections'
    )
    original_image = models.ImageField(upload_to='detections/original/')
    annotated_image = models.ImageField(upload_to='detections/annotated/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    objects_detected = models.IntegerField(default=0)
    detection_data = models.TextField(blank=True, help_text="JSON string with detection details")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Detection Result'
        verbose_name_plural = 'Detection Results'
    
    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_detection_data(self):
        """Parse JSON detection data"""
        if self.detection_data:
            try:
                return json.loads(self.detection_data)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_detection_data(self, data):
        """Store detection data as JSON"""
        self.detection_data = json.dumps(data)
