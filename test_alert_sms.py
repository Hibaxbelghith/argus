"""
Script pour créer une alerte de sécurité et tester l'envoi de SMS
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from authentication.models import CustomUser
from analytics.models import SecurityAlert
from detection.models import DetectionResult
from notifications.services import NotificationService

print("=" * 60)
print("TEST D'ALERTE DE SÉCURITÉ AVEC SMS")
print("=" * 60)

# 1. Récupérer l'utilisateur et la dernière détection
user = CustomUser.objects.get(username='oussama.ka')
detection = DetectionResult.objects.latest('uploaded_at')

print(f"\nUtilisateur: {user.username}")
print(f"Détection: #{detection.id}")
print(f"Objets détectés: {detection.objects_detected}")

# 2. Créer une alerte de sécurité CRITICAL
print("\n" + "=" * 60)
print("Création d'une alerte CRITICAL...")
print("=" * 60)

alert = SecurityAlert.objects.create(
    user=user,
    detection=detection,
    alert_type='suspicious_object',
    title='🚨 ALERTE SÉCURITÉ - Objet Suspect Détecté',
    message=f'''Un objet potentiellement dangereux a été détecté par votre système Argus. Heure: {detection.uploaded_at.strftime('%H:%M')} - Date: {detection.uploaded_at.strftime('%d/%m/%Y')} - Nombre d'objets: {detection.objects_detected}. Action recommandée: Vérifier immédiatement les images de détection.''',
    severity='critical'
)

print(f"✅ Alerte créée (ID: {alert.id})")
print(f"   Titre: {alert.title}")
print(f"   Sévérité: {alert.severity}")
print(f"   Type: {alert.alert_type}")

# 3. Créer les notifications (incluant SMS)
print("\n" + "=" * 60)
print("Création et envoi des notifications...")
print("=" * 60)

notifications = NotificationService.create_notification_from_alert(alert)

print(f"\n{len(notifications)} notification(s) créée(s):")
for notif in notifications:
    print(f"\n📱 Notification #{notif.id}")
    print(f"   Méthode: {notif.delivery_method}")
    print(f"   Statut: {notif.status}")
    print(f"   Titre: {notif.title}")
    
    if notif.delivery_method == 'sms':
        if notif.status == 'sent':
            print(f"   ✅ SMS ENVOYÉ à {user.phone_number}")
            print(f"   📱 Vérifiez votre téléphone !")
        else:
            print(f"   ❌ Échec: {notif.status}")
            
            # Afficher les logs d'erreur
            from notifications.models import NotificationLog
            logs = NotificationLog.objects.filter(notification=notif)
            for log in logs:
                print(f"      Log: {log.event} - {log.details}")

print("\n" + "=" * 60)
print("TEST TERMINÉ")
print("=" * 60)
print("\n💡 Si vous n'avez pas reçu de SMS, vérifiez:")
print("   1. Votre crédit Twilio")
print("   2. Que 'sms' est dans enabled_methods")
print("   3. Que min_severity_sms permet 'critical'")
