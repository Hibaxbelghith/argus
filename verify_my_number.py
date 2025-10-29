#!/usr/bin/env python
"""
Script pour vérifier votre numéro de téléphone avec Twilio
Nécessaire pour les comptes Trial
"""

import os
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from django.conf import settings
from twilio.rest import Client

def verify_phone_number():
    """Guide pour vérifier votre numéro de téléphone"""
    
    print("\n" + "="*70)
    print("📱 VÉRIFICATION DE VOTRE NUMÉRO - TWILIO TRIAL")
    print("="*70 + "\n")
    
    your_number = "+216273261546"
    
    print("Votre numéro à vérifier:", your_number)
    print()
    
    print("⚠️  COMPTE TWILIO TRIAL DÉTECTÉ")
    print()
    print("Les comptes Trial ont des restrictions de sécurité:")
    print("  • Vous ne pouvez envoyer des SMS qu'aux numéros VÉRIFIÉS")
    print("  • Vous devez vérifier votre numéro avant de recevoir des SMS")
    print()
    
    print("="*70)
    print("🔐 ÉTAPES POUR VÉRIFIER VOTRE NUMÉRO:")
    print("="*70)
    print()
    
    print("1️⃣  ALLER SUR LA CONSOLE TWILIO:")
    print("   https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print()
    
    print("2️⃣  CLIQUER SUR LE BOUTON ROUGE 'Verify a phone number'")
    print()
    
    print("3️⃣  SAISIR VOTRE NUMÉRO:")
    print(f"   → {your_number}")
    print()
    
    print("4️⃣  TWILIO VOUS APPELLERA OU ENVERRA UN CODE PAR SMS")
    print("   • Choisissez 'Call' (Appel) ou 'SMS'")
    print("   • Vous recevrez un code à 6 chiffres")
    print()
    
    print("5️⃣  ENTRER LE CODE REÇU DANS LA CONSOLE TWILIO")
    print()
    
    print("6️⃣  UNE FOIS VÉRIFIÉ, RE-EXÉCUTEZ:")
    print("   py send_test_sms.py")
    print()
    
    print("="*70)
    print()
    
    # Vérifier si on peut utiliser l'API pour la vérification
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Lister les numéros déjà vérifiés
        print("📋 Numéros actuellement vérifiés:")
        print()
        
        verified_numbers = client.validation_requests.list(limit=20)
        
        if verified_numbers:
            for num in verified_numbers:
                print(f"  ✅ {num.phone_number}")
        else:
            print("  ⚠️  Aucun numéro vérifié pour le moment")
        
        print()
        
    except Exception as e:
        print(f"⚠️  Impossible de récupérer la liste: {str(e)}")
        print()
    
    print("="*70)
    print()
    
    choice = input("Voulez-vous ouvrir la page de vérification dans votre navigateur? (o/n): ").lower().strip()
    
    if choice == 'o':
        import webbrowser
        webbrowser.open("https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
        print("\n✅ Page ouverte dans votre navigateur!")
    
    print()
    print("💡 ASTUCE:")
    print("   Une fois votre numéro vérifié, vous pourrez:")
    print("   • Recevoir des SMS de test d'Argus")
    print("   • Tester tout le système de notifications")
    print("   • Recevoir des alertes de sécurité en temps réel")
    print()
    
    print("📞 Si vous voulez supprimer les restrictions Trial:")
    print("   • Upgradez votre compte Twilio (ajoutez une carte bancaire)")
    print("   • Vous pourrez alors envoyer à n'importe quel numéro")
    print("   • Le crédit gratuit de $15.50 restera utilisable")
    print()

if __name__ == "__main__":
    print("\n🔐 ARGUS SECURITY - CONFIGURATION NUMÉRO PERSONNEL\n")
    verify_phone_number()
    print("="*70)
    print("✅ Configuration terminée!")
    print("="*70 + "\n")
