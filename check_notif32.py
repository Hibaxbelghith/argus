import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from notifications.models import Notification

# Vérifier les dernières notifications
recent = Notification.objects.filter(delivery_method='sms').order_by('-id')[:5]

print(f"📱 Dernières notifications SMS:\n")
for n in recent:
    print(f"#{n.id}: {n.status} - {n.title}")

print(f"\n🔍 Détail notification #32:")
n = Notification.objects.get(id=32)
print(f"   Status: {n.status}")
print(f"   User: {n.user.username}")
print(f"   Phone: {n.user.phone_number}")
print(f"   Created: {n.created_at}")
print(f"   Sent: {n.sent_at}")

# Vérifier les logs
from notifications.models import NotificationLog
logs = NotificationLog.objects.filter(notification_id=32).order_by('timestamp')
print(f"\n📋 Logs pour notification #32:")
for log in logs:
    print(f"   [{log.timestamp}] {log.event}: {log.details}")
