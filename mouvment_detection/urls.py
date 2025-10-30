from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    # Page principale
    path('', views.index, name='index'),
    
    # Streaming vidéo
    path('video_feed/', views.video_feed, name='video_feed'),
    
    # Contrôles de détection
    path('api/start/', views.start_detection, name='start_detection'),
    path('api/stop/', views.stop_detection, name='stop_detection'),
    path('api/status/', views.detection_status, name='detection_status'),
    path('api/settings/', views.update_settings, name='update_settings'),
    
    # Événements
    path('events/', views.events_list, name='events_list'),
    path('api/events/', views.events_api, name='events_api'),
    
    # Statistiques et paramètres
    path('statistics/', views.statistics, name='statistics'),
    path('settings/', views.settings_view, name='settings'),
]
