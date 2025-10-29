from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('face-login/', views.face_login_api, name='face_login'),
    path('register/', views.register_view, name='register'), 

]

