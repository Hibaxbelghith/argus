from django.db import models
from django.utils import timezone

class EmotionDetectionEvent(models.Model):
	timestamp = models.DateTimeField(default=timezone.now)
	person_id = models.CharField(max_length=128, blank=True, null=True)
	emotion = models.CharField(max_length=32)
	confidence = models.FloatField()
	extra_data = models.JSONField(blank=True, null=True)

	def __str__(self):
		return f"{self.timestamp}: {self.emotion} ({self.confidence:.2f})"
