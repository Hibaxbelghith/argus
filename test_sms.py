"""
Script de test pour l'envoi de SMS via Twilio
Usage: python manage.py shell < test_sms.py
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from authentication.models import CustomUser
from notifications.models import Notification, NotificationPreference
from notifications.services import NotificationService

print("=" * 60)
print("TEST D'ENVOI DE SMS")
print("=" * 60)

# 1. Configurer le numéro de téléphone
print("\n1. Configuration du numéro de téléphone...")
try:
    # Récupérer le premier utilisateur (ou créez-en un)
    user = CustomUser.objects.first()
    if not user:
        print("❌ Aucun utilisateur trouvé. Créez un utilisateur d'abord.")
        exit(1)
    
    print(f"   Utilisateur: {user.username}")
    
    # Ajouter le numéro de téléphone
    user.phone_number = '+21627326154'  # Votre numéro tunisien
    user.save()
    print(f"   ✅ Numéro ajouté: {user.phone_number}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

# 2. Configurer les préférences de notification
print("\n2. Configuration des préférences de notification...")
try:
    prefs, created = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={
            'enabled_methods': ['web', 'sms'],
            'min_severity_web': 'low',
            'min_severity_email': 'high',
            'min_severity_sms': 'critical',
        }
    )
    
    # S'assurer que SMS est activé
    if 'sms' not in prefs.enabled_methods:
        prefs.enabled_methods.append('sms')
        prefs.save()
    
    print(f"   ✅ Préférences configurées")
    print(f"      - Méthodes activées: {', '.join(prefs.enabled_methods)}")
    print(f"      - Sévérité min SMS: {prefs.min_severity_sms}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Vérifier la configuration Twilio
print("\n3. Vérification de la configuration Twilio...")
from django.conf import settings

if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
    print(f"   ✅ Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
    print(f"   ✅ Auth Token: {'*' * 20}")
    print(f"   ✅ Numéro Twilio: {settings.TWILIO_PHONE_NUMBER}")
else:
    print("   ❌ Configuration Twilio manquante dans .env")
    print("\n   Créez un fichier .env avec:")
    print("   TWILIO_ACCOUNT_SID=votre_sid")
    print("   TWILIO_AUTH_TOKEN=votre_token")
    print("   TWILIO_PHONE_NUMBER=+33123456789")
    print("\n   ⚠️  Le test continuera mais l'envoi échouera sans credentials")

# 4. Créer une notification de test
print("\n4. Création d'une notification de test...")
try:
    notification = Notification.objects.create(
        user=user,
        notification_type='alert',
        title='🧪 Test SMS Argus',
        message='Ceci est un message de test depuis votre système de sécurité Argus. Si vous recevez ce SMS, la configuration est correcte !',
        severity='critical',
        delivery_method='sms',
        metadata={'test': True}
    )
    print(f"   ✅ Notification créée (ID: {notification.id})")
except Exception as e:
    print(f"   ❌ Erreur création notification: {e}")
    exit(1)

# 5. Envoyer le SMS
print("\n5. Envoi du SMS...")
try:
    NotificationService._send_notification(notification)
    
    # Vérifier le statut
    notification.refresh_from_db()
    
    if notification.status == 'sent':
        print(f"   ✅ SMS ENVOYÉ AVEC SUCCÈS !")
        print(f"      Destinataire: {user.phone_number}")
        print(f"      Vérifiez votre téléphone 📱")
    else:
        print(f"   ❌ Échec de l'envoi")
        print(f"      Statut: {notification.status}")
        
        # Afficher les logs
        from notifications.models import NotificationLog
        logs = NotificationLog.objects.filter(notification=notification)
        if logs.exists():
            print("\n      Logs d'erreur:")
            for log in logs:
                print(f"      - {log.event}: {log.details}")
    
except Exception as e:
    print(f"   ❌ Erreur lors de l'envoi: {e}")
    notification.status = 'failed'
    notification.save()

# 6. Résumé
print("\n" + "=" * 60)
print("RÉSUMÉ DU TEST")
print("=" * 60)
print(f"Utilisateur: {user.username}")
print(f"Téléphone: {user.phone_number}")
print(f"Notification ID: {notification.id}")
print(f"Statut final: {notification.status}")
print("=" * 60)

# Instructions supplémentaires
if notification.status != 'sent':
    print("\n⚠️  DÉPANNAGE:")
    print("1. Vérifiez votre fichier .env à la racine du projet")
    print("2. Vérifiez vos credentials Twilio sur https://console.twilio.com/")
    print("3. Vérifiez que votre numéro Twilio est activé")
    print("4. Vérifiez le format de votre numéro: +21627326154")
else:
    print("\n✅ Test réussi ! Vous devriez recevoir un SMS d'ici quelques secondes.")
