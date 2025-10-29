from django.db import models

class VoiceCommand(models.Model):
	text = models.CharField(max_length=100, unique=True, help_text="Main command text")
	synonyms = models.TextField(blank=True, help_text="Comma-separated synonyms")
	enabled = models.BooleanField(default=True, help_text="Is this command active?")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.text
# Create your models here.
