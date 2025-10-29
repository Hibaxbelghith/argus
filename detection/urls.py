from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.detection_home, name='home'),
    path('process/<int:pk>/', views.process_detection, name='process'),
    path('result/<int:pk>/', views.detection_result, name='result'),
    path('history/', views.detection_history, name='history'),
    path('delete/<int:pk>/', views.delete_detection, name='delete'),
]
