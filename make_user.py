"""
Script pour changer le rôle d'un utilisateur en 'user'
"""
import os
import sys
import django

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from authentication.models import CustomUser

def change_to_user(username):
    """Change le rôle d'un utilisateur en 'user'"""
    try:
        # Récupérer l'utilisateur
        user = CustomUser.objects.get(username=username)
        
        # Changer le rôle
        user.role = 'user'
        user.save()
        
        print(f"✓ Succès: Le rôle de {user.username} a été changé!")
        print(f"  - role: {user.role}")
        print(f"  - is_staff: {user.is_staff}")
        print(f"  - is_superuser: {user.is_superuser}")
        
    except CustomUser.DoesNotExist:
        print(f"✗ Erreur: L'utilisateur '{username}' n'existe pas.")
    except Exception as e:
        print(f"✗ Erreur: {e}")

if __name__ == "__main__":
    username = "oussama.ka"
    
    print(f"Changement du rôle de '{username}' en 'user'...\n")
    change_to_user(username)
