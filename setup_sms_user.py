#!/usr/bin/env python
"""
Script pour configurer votre profil utilisateur avec SMS
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.contrib.auth import get_user_model
from notifications.models import NotificationPreference

User = get_user_model()  # Récupère le bon modèle utilisateur

def setup_user_sms():
    """Configure les préférences SMS pour votre utilisateur"""
    
    print("\n" + "="*60)
    print("👤 CONFIGURATION UTILISATEUR SMS - ARGUS")
    print("="*60 + "\n")
    
    # Créer ou récupérer l'utilisateur
    username = input("Nom d'utilisateur (ou Enter pour 'admin'): ").strip() or "admin"
    
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': 'oussama@argus.com',
            'first_name': 'Oussama',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✅ Utilisateur '{username}' créé!")
    else:
        print(f"✅ Utilisateur '{username}' trouvé!")
    
    # Configurer les préférences de notification
    pref, created = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={
            'phone_number': '+21627326154',
            'phone_verified': True,
            'enabled_methods': ['web', 'email', 'sms'],
            'min_severity_sms': 'medium',
            'min_severity_email': 'low',
            'min_severity_web': 'low',
            'notify_suspicious_objects': True,
            'notify_anomalies': True,
            'notify_high_frequency': True,
        }
    )
    
    if not created:
        # Mettre à jour si existe déjà
        pref.phone_number = '+21627326154'
        pref.phone_verified = True
        if 'sms' not in pref.enabled_methods:
            pref.enabled_methods.append('sms')
        pref.min_severity_sms = 'medium'
        pref.save()
        print(f"✅ Préférences mises à jour!")
    else:
        print(f"✅ Préférences créées!")
    
    print()
    print("📊 Configuration actuelle:")
    print(f"   Utilisateur: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Téléphone: {pref.phone_number}")
    print(f"   Méthodes activées: {', '.join(pref.enabled_methods)}")
    print(f"   Sévérité min SMS: {pref.min_severity_sms}")
    print()
    
    # Envoyer un SMS de notification de test
    print("="*60)
    choice = input("Voulez-vous envoyer une notification SMS de test? (o/n): ").strip().lower()
    
    if choice == 'o':
        from notifications.models import Notification
        from notifications.multi_channel_delivery import get_delivery_service
        
        # Créer une notification
        notif = Notification.objects.create(
            user=user,
            title="🚨 Test Alerte Sécurité Argus",
            message="Détection de mouvement suspect dans la zone de surveillance. Système opérationnel.",
            notification_type='alert',
            severity='high',
            metadata={
                'source': 'test_script',
                'detection_type': 'motion',
                'confidence': 0.95
            }
        )
        
        print(f"\n✅ Notification créée (ID: {notif.id})")
        
        # Envoyer via SMS
        delivery = get_delivery_service()
        success = delivery.send_sms(
            user=user,
            notification=notif
        )
        
        if success:
            print("✅ SMS de notification envoyé avec succès!")
            print("📱 Vérifiez votre téléphone!")
            
            # Vérifier les logs
            from notifications.models import SMSDeliveryLog
            logs = SMSDeliveryLog.objects.filter(notification=notif)
            
            if logs.exists():
                log = logs.first()
                print(f"\n📋 Log d'envoi:")
                print(f"   Statut: {log.status}")
                print(f"   Message SID: {log.provider_message_id}")
                print(f"   Coût: {log.cost or 'N/A'}")
        else:
            print("❌ Échec de l'envoi SMS")
    
    print()
    print("="*60)
    print("✅ Configuration terminée!")
    print("="*60)

if __name__ == "__main__":
    setup_user_sms()
