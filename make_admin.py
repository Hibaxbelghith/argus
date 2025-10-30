"""
Script pour changer un utilisateur en superuser/admin
"""
import os
import sys
import django

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from authentication.models import CustomUser

def make_superuser(username):
    """Convertit un utilisateur en superuser/admin"""
    try:
        # Récupérer l'utilisateur
        user = CustomUser.objects.get(username=username)
        
        # Changer les permissions
        user.is_staff = True
        user.is_superuser = True
        user.role = 'admin'
        user.save()
        
        print(f"✓ Succès: {user.username} est maintenant administrateur!")
        print(f"  - is_staff: {user.is_staff}")
        print(f"  - is_superuser: {user.is_superuser}")
        print(f"  - role: {user.role}")
        print(f"  - Email: {user.email}")
        
    except CustomUser.DoesNotExist:
        print(f"✗ Erreur: L'utilisateur '{username}' n'existe pas.")
        print("\nUtilisateurs disponibles:")
        for u in CustomUser.objects.all():
            print(f"  - {u.username} (Email: {u.email})")
    except Exception as e:
        print(f"✗ Erreur: {e}")

if __name__ == "__main__":
    # Remplacez par votre nom d'utilisateur
    username = "oussama.ka"
    
    print(f"Conversion de '{username}' en administrateur...\n")
    make_superuser(username)
