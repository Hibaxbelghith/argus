from django.contrib import admin
from .models import (
    Notification,
    NotificationPreference,
    NotificationRule,
    NotificationLog,
    PredictiveAlert
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'severity', 'delivery_method', 'status', 
                    'is_aggregated', 'created_at', 'read_at']
    list_filter = ['notification_type', 'severity', 'delivery_method', 'status', 
                   'is_aggregated', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'sent_at', 'read_at']
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_sent', 'mark_as_read']
    
    def mark_as_sent(self, request, queryset):
        for notification in queryset:
            notification.mark_as_sent()
    mark_as_sent.short_description = "Marquer comme envoyé"
    
    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
    mark_as_read.short_description = "Marquer comme lu"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'min_severity_web', 'min_severity_email', 
                    'quiet_hours_enabled', 'enable_aggregation', 'max_notifications_per_hour']
    list_filter = ['quiet_hours_enabled', 'enable_aggregation']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'condition_type', 'action', 'is_active', 'priority']
    list_filter = ['condition_type', 'action', 'is_active']
    search_fields = ['user__username', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_rules', 'deactivate_rules']
    
    def activate_rules(self, request, queryset):
        queryset.update(is_active=True)
    activate_rules.short_description = "Activer les règles"
    
    def deactivate_rules(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_rules.short_description = "Désactiver les règles"


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['notification', 'event', 'timestamp']
    list_filter = ['event', 'timestamp']
    search_fields = ['notification__title', 'event', 'details']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(PredictiveAlert)
class PredictiveAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'prediction_type', 'title', 'confidence_score', 
                    'is_active', 'was_accurate', 'created_at']
    list_filter = ['prediction_type', 'is_active', 'was_accurate', 'created_at']
    search_fields = ['user__username', 'title', 'description', 'predicted_event']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
