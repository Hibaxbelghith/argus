from django.contrib import admin
from .models import DetectionEvent, CameraSettings


@admin.register(DetectionEvent)
class DetectionEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'detection_type', 'timestamp', 'faces_count', 'motion_intensity', 'is_active']
    list_filter = ['detection_type', 'timestamp', 'is_active']
    search_fields = ['location', 'notes']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50


@admin.register(CameraSettings)
class CameraSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'camera_index', 'enable_motion_detection', 'enable_face_detection', 'is_active']
    list_filter = ['is_active', 'enable_motion_detection', 'enable_face_detection']
    search_fields = ['name']
