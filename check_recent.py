"""Check détections récentes"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from detection.models import DetectionResult
from analytics.models import SecurityAlert
from notifications.models import Notification

print("=" * 60)
print("VÉRIFICATION DÉTECTIONS #24 et #25")
print("=" * 60)

for det_id in [24, 25]:
    try:
        d = DetectionResult.objects.get(id=det_id)
        print(f"\n📦 Détection #{det_id}:")
        print(f"   Objets: {d.objects_detected}")
        objs = [obj.get('class') for obj in d.get_detection_data()]
        print(f"   Classes: {objs}")
        
        alerts = SecurityAlert.objects.filter(detection_id=det_id)
        print(f"   Alertes: {alerts.count()}")
        
        for alert in alerts:
            print(f"\n   ⚠️  Alerte #{alert.id}:")
            print(f"       Sévérité: {alert.severity}")
            print(f"       Titre: {alert.title}")
            
            notifs = Notification.objects.filter(related_alert_id=alert.id)
            print(f"       Notifications: {notifs.count()}")
            
            for n in notifs:
                print(f"       - {n.delivery_method}: {n.status}")
                if n.delivery_method == 'sms':
                    if n.status == 'sent':
                        print(f"         ✅ SMS ENVOYÉ!")
                    else:
                        print(f"         ❌ SMS ÉCHOUÉ: {n.status}")
    except:
        print(f"\n❌ Détection #{det_id} non trouvée")

print("\n" + "=" * 60)
