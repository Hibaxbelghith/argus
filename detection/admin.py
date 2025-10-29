from django.contrib import admin
from .models import DetectionResult

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at', 'objects_detected')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username',)
    readonly_fields = ('uploaded_at',)
