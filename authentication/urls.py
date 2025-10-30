from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('face-login/', views.face_login_api, name='face_login'),
    path('register/', views.register_view, name='register'),
    path('admin/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/block/<int:user_id>/', views.toggle_block_user, name='block_user'),
    path('admin/role/<int:user_id>/', views.change_role, name='change_role'),
    path('admin/search-users/', views.search_users, name='search_users'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('admin/search-attempts/', views.search_attempts, name='search_attempts')


    


]

