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
    
    # Editable metadata fields for CRUD
    title = models.CharField(max_length=200, blank=True, help_text="Custom title for this detection")
    description = models.TextField(blank=True, help_text="Description or notes about this detection")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags (e.g., 'security, entrance, daytime')")
    location = models.CharField(max_length=200, blank=True, help_text="Location where image was captured")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Detection Result'
        verbose_name_plural = 'Detection Results'
    
    def __str__(self):
        if self.title:
            return f"{self.title} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
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
