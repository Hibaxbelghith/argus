#!/usr/bin/env python
"""
Simulateur de détection de sécurité avec envoi SMS automatique
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.contrib.auth import get_user_model
from detection.models import DetectionResult

User = get_user_model()

def simulate_security_detection():
    """Simule une détection de sécurité et déclenche les notifications"""
    
    print("\n" + "="*70)
    print("🚨 SIMULATION DÉTECTION DE SÉCURITÉ - ARGUS")
    print("="*70 + "\n")
    
    # Récupérer l'utilisateur
    user = User.objects.get(username='oussama.ka')
    print(f"👤 Utilisateur: {user.username}")
    print(f"📧 Email: {user.email}")
    print(f"📱 Téléphone: {user.notification_preferences.phone_number}")
    print()
    
    # Créer une détection de sécurité suspecte
    print("🔍 Création d'une détection de sécurité...")
    
    # Préparer les données de détection
    detection_data = [{
        'class': 'person',
        'confidence': 0.94,
        'bbox': [100, 150, 400, 600],
        'is_suspicious': True,
        'metadata': {
            'detection_time': 'night',
            'zone': 'restricted_area',
            'movement': 'unauthorized',
            'camera_id': 'CAM-001',
            'location': 'Entrée principale'
        }
    }]
    
    detection = DetectionResult.objects.create(
        user=user,
        objects_detected=1,
        detection_data=json.dumps(detection_data)
    )
    
    print(f"✅ Détection créée (ID: {detection.id})")
    print(f"   Objets détectés: {detection.objects_detected}")
    print(f"   Date: {detection.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extraire les infos de la première détection
    det_info = detection.get_detection_data()[0]
    print(f"   Objet: {det_info['class']}")
    print(f"   Confiance: {det_info['confidence']:.1%}")
    print(f"   Suspect: {'OUI' if det_info.get('is_suspicious') else 'NON'}")
    print(f"   Lieu: {det_info['metadata'].get('location', 'Inconnu')}")
    print()
    
    # Le signal Django devrait automatiquement créer les analytics et notifications
    print("📊 Création de la notification...")
    
    # Utiliser directement le modèle Notification
    from notifications.models import Notification
    
    # Créer une notification de haute sévérité
    det_info = detection.get_detection_data()[0]
    location = det_info['metadata'].get('location', 'zone inconnue')
    
    notif = Notification.objects.create(
        user=user,
        title=f"🚨 ALERTE: Détection suspecte",
        message=f"Personne détectée dans {location} à {detection.uploaded_at.strftime('%H:%M')}. "
                f"Confiance: {det_info['confidence']:.1%}. Zone: {det_info['metadata'].get('zone', 'inconnue')}.",
        notification_type='alert',
        severity='high',
        metadata={
            'detection_id': detection.id,
            'object': det_info['class'],
            'confidence': float(det_info['confidence']),
            'is_suspicious': det_info.get('is_suspicious', False),
            'location': location
        }
    )
    
    print(f"✅ Notification créée (ID: {notif.id})")
    print(f"   Titre: {notif.title}")
    print(f"   Sévérité: {notif.severity}")
    print()
    
    # Envoyer par SMS directement
    print("📤 Envoi de l'alerte SMS...")
    
    from notifications.multi_channel_delivery import get_delivery_service
    
    delivery = get_delivery_service()
    
    # Envoyer le SMS (notification, user)
    sms_success = delivery.send_sms(notif, user)
    
    print()
    print("📊 Résultats d'envoi:")
    print(f"   SMS: {'✅ Envoyé' if sms_success else '❌ Échec'}")
    
    # Afficher le log SMS
    if sms_success:
        from notifications.models import SMSDeliveryLog
        sms_log = SMSDeliveryLog.objects.filter(notification=notif).first()
        
        if sms_log:
            print()
            print("📱 Détails SMS:")
            print(f"   Destinataire: {sms_log.phone_number}")
            print(f"   Statut: {sms_log.status}")
            print(f"   Message SID: {sms_log.provider_message_id}")
            print(f"   Envoyé à: {sms_log.sent_at.strftime('%H:%M:%S')}")
    
    print()
    print("="*70)
    print("✅ SIMULATION TERMINÉE - VÉRIFIEZ VOTRE TÉLÉPHONE!")
    print("="*70)
    print()
    
    print("💡 Pour voir l'historique dans le dashboard:")
    print("   py manage.py runserver")
    print("   → http://127.0.0.1:8000/notifications/")
    print()

if __name__ == "__main__":
    simulate_security_detection()
