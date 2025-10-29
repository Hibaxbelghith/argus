import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from analytics.models import SecurityAlert
from notifications.models import Notification

alert = SecurityAlert.objects.get(id=9)
notifications = Notification.objects.filter(alert=alert)

print(f"🚨 Alert #9:")
print(f"   Titre: {alert.title}")
print(f"   Sévérité: {alert.severity}")
print(f"   Type: {alert.alert_type}")
print(f"   Détection: #{alert.detection.id}")

print(f"\n📧 Notifications créées: {notifications.count()}")
for notif in notifications:
    print(f"   - {notif.method}: {notif.title}")
    print(f"     Status: {notif.status}")
    if notif.method == 'sms':
        print(f"     📱 SMS ID: {notif.sms_id}")
        print(f"     Téléphone: {notif.user.phone_number}")
