#!/usr/bin/env python
"""
Script de test rapide pour vérifier la configuration Twilio
Avant d'exécuter ce script, assurez-vous d'avoir un numéro de téléphone Twilio configuré!
"""

import os
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.conf import settings

def test_twilio_configuration():
    """Vérifie que Twilio est correctement configuré"""
    
    print("\n" + "="*60)
    print("🔍 VÉRIFICATION CONFIGURATION TWILIO")
    print("="*60 + "\n")
    
    # Vérifier les credentials
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    phone_number = settings.TWILIO_PHONE_NUMBER
    
    if not account_sid:
        print("❌ TWILIO_ACCOUNT_SID manquant!")
        return False
    
    if not auth_token:
        print("❌ TWILIO_AUTH_TOKEN manquant!")
        return False
    
    if not phone_number:
        print("⚠️  TWILIO_PHONE_NUMBER non configuré (vous devrez l'ajouter)")
        print("   Allez sur https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
        print("   pour obtenir votre numéro Twilio")
    
    print("✅ Account SID:", account_sid[:10] + "..." + account_sid[-4:])
    print("✅ Auth Token:", auth_token[:4] + "..." + auth_token[-4:])
    
    if phone_number:
        print("✅ Phone Number:", phone_number)
    
    # Tester la connexion Twilio
    try:
        from twilio.rest import Client
        
        print("\n📞 Test de connexion à Twilio...")
        client = Client(account_sid, auth_token)
        
        # Récupérer les informations du compte
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Connexion réussie!")
        print(f"   Nom du compte: {account.friendly_name}")
        print(f"   Statut: {account.status}")
        
        # Récupérer les numéros de téléphone
        print("\n📱 Numéros Twilio disponibles:")
        incoming_numbers = client.incoming_phone_numbers.list(limit=10)
        
        if not incoming_numbers:
            print("   ⚠️  Aucun numéro trouvé! Vous devez:")
            print("   1. Aller sur https://console.twilio.com/us1/develop/phone-numbers/manage/incoming")
            print("   2. Cliquer 'Buy a number' (avec votre crédit gratuit)")
            print("   3. Ajouter le numéro dans votre fichier .env")
        else:
            for number in incoming_numbers:
                print(f"   • {number.phone_number} ({number.friendly_name})")
                if not phone_number:
                    print(f"     → Ajoutez ce numéro dans .env: TWILIO_PHONE_NUMBER={number.phone_number}")
        
        # Vérifier le solde
        print("\n💰 Solde du compte:")
        balance = client.balance.fetch()
        print(f"   Devise: {balance.currency}")
        print(f"   Montant: {balance.balance}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur de connexion Twilio:")
        print(f"   {str(e)}")
        return False

def send_test_sms():
    """Envoie un SMS de test"""
    
    phone_number = settings.TWILIO_PHONE_NUMBER
    
    if not phone_number:
        print("\n⚠️  Configurez d'abord TWILIO_PHONE_NUMBER dans .env")
        return
    
    print("\n" + "="*60)
    print("📤 ENVOI D'UN SMS DE TEST")
    print("="*60 + "\n")
    
    # Demander le numéro destinataire
    to_number = input("Entrez le numéro destinataire (format E.164, ex: +33612345678): ").strip()
    
    if not to_number:
        print("❌ Numéro invalide")
        return
    
    try:
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body="🚨 Test SMS depuis Argus Security System! Votre système de surveillance est opérationnel.",
            from_=phone_number,
            to=to_number
        )
        
        print(f"✅ SMS envoyé avec succès!")
        print(f"   Message SID: {message.sid}")
        print(f"   Statut: {message.status}")
        print(f"   De: {message.from_}")
        print(f"   Vers: {message.to}")
        print(f"   Prix: {message.price} {message.price_unit}")
        
    except Exception as e:
        print(f"\n❌ Erreur d'envoi SMS:")
        print(f"   {str(e)}")

if __name__ == "__main__":
    print("\n🔐 ARGUS SECURITY - TEST TWILIO SMS\n")
    
    # Test de configuration
    if test_twilio_configuration():
        print("\n" + "="*60)
        
        choice = input("\nVoulez-vous envoyer un SMS de test? (o/n): ").lower().strip()
        
        if choice == 'o':
            send_test_sms()
        else:
            print("\n✅ Configuration vérifiée avec succès!")
    else:
        print("\n❌ Veuillez corriger la configuration avant de continuer.")
    
    print("\n" + "="*60)
    print("✅ Test terminé!")
    print("="*60 + "\n")
