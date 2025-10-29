"""
Script pour diagnostiquer pourquoi pas de SMS reçu
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from detection.models import DetectionResult
from analytics.models import SecurityAlert
from notifications.models import Notification

print("=" * 60)
print("DIAGNOSTIC SMS - Détection #22")
print("=" * 60)

# Vérifier la détection
try:
    detection = DetectionResult.objects.get(id=22)
    print(f"\n✅ Détection #17 trouvée")
    print(f"   User: {detection.user.username}")
    print(f"   Date: {detection.uploaded_at}")
    print(f"   Objets détectés: {detection.objects_detected}")
    
    # Afficher les objets détectés
    detection_data = detection.get_detection_data()
    print(f"\n📦 Objets dans la détection:")
    for obj in detection_data:
        print(f"   - {obj.get('class')}: {obj.get('confidence', 0):.2f}")
    
except DetectionResult.DoesNotExist:
    print("\n❌ Détection #22 non trouvée")
    print("\nDernières détections:")
    for d in DetectionResult.objects.order_by('-id')[:5]:
        print(f"   #{d.id}: {d.objects_detected} objets - {d.uploaded_at}")

# Vérifier les alertes créées
print("\n" + "=" * 60)
print("ALERTES DE SÉCURITÉ")
print("=" * 60)

alerts = SecurityAlert.objects.filter(detection_id=22)
if alerts.exists():
    print(f"\n✅ {alerts.count()} alerte(s) trouvée(s):")
    for alert in alerts:
        print(f"\n   Alerte #{alert.id}:")
        print(f"   - Type: {alert.alert_type}")
        print(f"   - Sévérité: {alert.severity}")
        print(f"   - Titre: {alert.title}")
else:
    print("\n❌ Aucune alerte créée pour la détection #22")
    print("\nDernières alertes:")
    for alert in SecurityAlert.objects.order_by('-id')[:5]:
        print(f"   #{alert.id}: {alert.severity} - {alert.title}")

# Vérifier les notifications
print("\n" + "=" * 60)
print("NOTIFICATIONS")
print("=" * 60)

# Notifications liées aux alertes de la détection #22
if alerts.exists():
    for alert in alerts:
        notifs = Notification.objects.filter(related_alert_id=alert.id)
        if notifs.exists():
            print(f"\n✅ {notifs.count()} notification(s) pour l'alerte #{alert.id}:")
            for notif in notifs:
                print(f"\n   Notification #{notif.id}:")
                print(f"   - Méthode: {notif.delivery_method}")
                print(f"   - Statut: {notif.status}")
                print(f"   - Sévérité: {notif.severity}")
                
                if notif.delivery_method == 'sms':
                    if notif.status == 'sent':
                        print(f"   ✅ SMS ENVOYÉ")
                    else:
                        print(f"   ❌ SMS NON ENVOYÉ")
                        
                        # Vérifier les logs
                        from notifications.models import NotificationLog
                        logs = NotificationLog.objects.filter(notification=notif)
                        if logs.exists():
                            print(f"\n   Logs:")
                            for log in logs:
                                print(f"      - {log.event}: {log.details}")
        else:
            print(f"\n❌ Aucune notification créée pour l'alerte #{alert.id}")
else:
    print("\n❌ Pas d'alerte, donc pas de notification")

# Vérifier la configuration utilisateur
print("\n" + "=" * 60)
print("CONFIGURATION UTILISATEUR")
print("=" * 60)

from authentication.models import CustomUser
from notifications.models import NotificationPreference

try:
    detection = DetectionResult.objects.get(id=22)
    user = detection.user
    
    print(f"\nUtilisateur: {user.username}")
    print(f"Téléphone: {user.phone_number}")
    
    prefs = NotificationPreference.objects.get(user=user)
    print(f"\nPréférences:")
    print(f"   - Méthodes activées: {prefs.enabled_methods}")
    print(f"   - Min severity SMS: {prefs.min_severity_sms}")
    print(f"   - Max notif/heure: {prefs.max_notifications_per_hour}")
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TERMINÉ")
print("=" * 60)
