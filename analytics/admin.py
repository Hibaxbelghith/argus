from django.contrib import admin
from .models import (
    DetectionAnalytics,
    ObjectTrend,
    SecurityAlert,
    AnalyticsInsight
)


@admin.register(DetectionAnalytics)
class DetectionAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_type', 'period_start', 'total_detections', 
                    'total_objects_detected', 'suspicious_objects_count', 'created_at']
    list_filter = ['period_type', 'period_start', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'period_start'


@admin.register(ObjectTrend)
class ObjectTrendAdmin(admin.ModelAdmin):
    list_display = ['user', 'object_class', 'detection_count', 'trend_direction', 
                    'is_anomaly', 'anomaly_score', 'last_detected']
    list_filter = ['trend_direction', 'is_anomaly', 'user']
    search_fields = ['user__username', 'object_class']
    readonly_fields = ['updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-detection_count')


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'severity', 'title', 'is_read', 
                    'is_acknowledged', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_read', 'is_acknowledged', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'acknowledged_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_acknowledged']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_acknowledged(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_acknowledged=True, acknowledged_at=timezone.now())
    mark_as_acknowledged.short_description = "Marquer comme reconnu"


@admin.register(AnalyticsInsight)
class AnalyticsInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'title', 'confidence_score', 
                    'is_active', 'created_at']
    list_filter = ['insight_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
