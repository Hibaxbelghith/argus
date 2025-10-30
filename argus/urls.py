"""
URL configuration for argus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    path('', __import__('argus.views').views.home, name='home'),
    path('admin/', admin.site.urls),  # ✅ ajoute cette ligne si elle n'existe pas
    path('auth/', include('authentication.urls')),  # ton app d'authentification
    path('voicecontrol/', include('voicecontrol.urls')),
    path('emotion/', include('emotion.urls')),
    path('detection/', include('detection.urls')),
    path('analytics/', include('analytics.urls')),  # Module Analytics
    path('analytics/api/', include('analytics.advanced_urls')),  # 🆕 Advanced AI APIs
    path('notifications/', include('notifications.urls')),  # Module Notifications
    path('mouvment/', include('mouvment_detection.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
