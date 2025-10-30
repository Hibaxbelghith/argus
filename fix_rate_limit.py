import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.utils import timezone
from authentication.models import CustomUser
from notifications.models import NotificationPreference, Notification

user = CustomUser.objects.get(username='oussama.ka')
prefs = NotificationPreference.objects.get(user=user)

# Vérifier l'état actuel
one_hour_ago = timezone.now() - timedelta(hours=1)
recent_notifs = Notification.objects.filter(
    user=user,
    created_at__gte=one_hour_ago
)

print(f"📊 État actuel:")
print(f"   Max notifications/heure: {prefs.max_notifications_per_hour}")
print(f"   Notifications dernière heure: {recent_notifs.count()}")
print(f"   Types: {list(recent_notifs.values_list('notification_type', flat=True))}")

# Augmenter la limite
print(f"\n🔧 Augmentation de la limite à 50/heure...")
prefs.max_notifications_per_hour = 50
prefs.save()

print(f"✅ Limite mise à jour: {prefs.max_notifications_per_hour} notifications/heure")
