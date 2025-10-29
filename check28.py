import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from analytics.models import SecurityAlert
from notifications.models import Notification

for det_id in [29, 30]:
    alerts = SecurityAlert.objects.filter(detection_id=det_id)
    print(f'\n📦 Détection #{det_id}:')
    print(f'   Alertes: {alerts.count()}')

    for a in alerts:
        print(f'   ⚠️  {a.severity}: {a.title}')
        notifs = Notification.objects.filter(related_alert_id=a.id)
        print(f'      Notifications: {notifs.count()}')
        for n in notifs:
            status_icon = '✅' if n.status == 'sent' else '❌'
            print(f'      {status_icon} {n.delivery_method}: {n.status}')
            if n.delivery_method == 'sms' and n.status == 'sent':
                print(f'         📱 SMS ENVOYÉ !')

print('\n' + '='*60)
