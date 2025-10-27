from django.urls import path
from . import views

urlpatterns = [
    path('voice-command/', views.voice_command, name='voice_command'),
    path('demo/', views.demo, name='voice_demo'),
]
