from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    # Image detection endpoints
    path('', views.detection_home, name='home'),
    path('process/<int:pk>/', views.process_detection, name='process'),
    path('result/<int:pk>/', views.detection_result, name='result'),
    path('history/', views.detection_history, name='history'),
    path('edit/<int:pk>/', views.edit_detection, name='edit'),
    path('delete/<int:pk>/', views.delete_detection, name='delete'),
    
    # Real-time security monitoring endpoints
    path('security/', views.security_monitor, name='security_monitor'),
    path('security/start/', views.start_security_camera, name='start_camera'),
    path('security/stop/', views.stop_security_camera, name='stop_camera'),
    path('security/feed/', views.video_feed, name='video_feed'),
    path('security/detections/', views.get_detections_data, name='get_detections'),
    path('security/logs/', views.security_logs, name='security_logs'),
]
