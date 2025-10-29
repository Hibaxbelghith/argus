#!/usr/bin/env python
"""
Script pour envoyer un SMS de test vers votre numéro personnel
"""

import os
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client

def send_test_sms():
    """Envoie un SMS de test"""
    
    print("\n" + "="*60)
    print("📤 ENVOI SMS DE TEST - ARGUS SECURITY")
    print("="*60 + "\n")
    
    # Configuration
    from_number = settings.TWILIO_PHONE_NUMBER  # +16054534662
    to_number = "+21627326154"  # Votre numéro en Tunisie (format E.164)
    
    print(f"De (Twilio): {from_number}")
    print(f"Vers (Vous): {to_number}")
    print()
    
    try:
        # Créer le client Twilio
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Envoyer le SMS
        message = client.messages.create(
            body="🚨 ARGUS SECURITY - Test SMS réussi! Votre système de surveillance est maintenant configuré et opérationnel. Vous recevrez des alertes de sécurité sur ce numéro.",
            from_=from_number,
            to=to_number
        )
        
        print("✅ SMS ENVOYÉ AVEC SUCCÈS!\n")
        print(f"Message SID: {message.sid}")
        print(f"Statut: {message.status}")
        print(f"Direction: {message.direction}")
        
        if message.price:
            print(f"Prix: {message.price} {message.price_unit}")
        
        print("\n📱 Vérifiez votre téléphone, vous devriez recevoir le SMS d'ici quelques secondes!")
        
        # Vérifier le statut après quelques secondes
        import time
        print("\n⏳ Vérification du statut de livraison...")
        time.sleep(3)
        
        # Récupérer le statut mis à jour
        message = client.messages(message.sid).fetch()
        print(f"Statut mis à jour: {message.status}")
        
        status_info = {
            'queued': '📋 En file d\'attente',
            'sending': '📤 En cours d\'envoi',
            'sent': '✅ Envoyé',
            'delivered': '✅ Livré',
            'failed': '❌ Échec',
            'undelivered': '❌ Non livré'
        }
        
        print(f"→ {status_info.get(message.status, message.status)}")
        
        if message.error_code:
            print(f"⚠️ Code erreur: {message.error_code}")
            print(f"   Message: {message.error_message}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'envoi du SMS:")
        print(f"   {str(e)}")
        
        # Conseils de dépannage
        print("\n💡 CONSEILS:")
        print("   1. Vérifiez que votre numéro Twilio est vérifié")
        print("   2. Pour Twilio Trial, vérifiez votre numéro +216273261546 sur:")
        print("      https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("   3. Les comptes Trial ne peuvent envoyer qu'aux numéros vérifiés")
        
        return False

if __name__ == "__main__":
    print("\n🔐 ARGUS SECURITY - TEST D'ENVOI SMS\n")
    send_test_sms()
    print("\n" + "="*60)
    print("✅ Test terminé!")
    print("="*60 + "\n")
