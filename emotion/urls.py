from django.urls import path
from .views import detect_emotion, live_emotion_page

urlpatterns = [
    path('detect/', detect_emotion, name='detect_emotion'),
    path('live/', live_emotion_page, name='live_emotion_page'),
]
