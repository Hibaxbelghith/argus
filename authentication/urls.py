from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/face-login/', views.face_login_api, name='face_login_api'),
    path('logout/', views.logout_view, name='logout'),
    # register, dashboard, logout etc.
]
