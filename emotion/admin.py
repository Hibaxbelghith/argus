from django.contrib import admin

from django.contrib import admin
from .models import EmotionDetectionEvent

@admin.register(EmotionDetectionEvent)
class EmotionDetectionEventAdmin(admin.ModelAdmin):
	list_display = ("timestamp", "person_id", "emotion", "confidence")
	search_fields = ("person_id", "emotion")
	list_filter = ("emotion",)
