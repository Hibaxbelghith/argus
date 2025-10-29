# views.py - VERSION AMÉLIORÉE
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm
from .models import CustomUser, LoginAttempt
from .services import save_base64_image, verify_face, cleanup_temp_file
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib import messages
import json
import os

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def dashboard_view(request):
    return render(request, 'authentication/dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})

@csrf_exempt
def face_login_api(request):
    """
    Endpoint POST : reçoit JSON { 'image': 'data:image/png;base64,...', 'username': '...' }
    """
    print(f"🔍 Début face_login_api...")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    
    try:
        data = json.loads(request.body)
        data_url = data.get('image')
        username = data.get('username')
        
        print(f"👤 Username reçu: {username}")
        print(f"📷 Taille image data: {len(data_url) if data_url else 0} chars")
        
        if not data_url or not username:
            LoginAttempt.objects.create(
                user=None, 
                success=False, 
                ip_address=get_client_ip(request), 
                method='face', 
                note='Données manquantes'
            )
            return JsonResponse({'success': False, 'message': 'Données manquantes'})

        user = None
        try:
            user = CustomUser.objects.get(username=username)
            print(f"✅ Utilisateur trouvé: {user.username}")
        except CustomUser.DoesNotExist:
            print(f"❌ Utilisateur non trouvé: {username}")
            LoginAttempt.objects.create(
                user=None, 
                success=False, 
                ip_address=get_client_ip(request), 
                method='face', 
                note='user not found'
            )
            return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'})

        # Vérifier si l'utilisateur a une photo
        if not user.photo:
            print(f"❌ Utilisateur {username} n'a pas de photo")
            LoginAttempt.objects.create(
                user=user, 
                success=False, 
                ip_address=get_client_ip(request), 
                method='face', 
                note='user has no photo'
            )
            return JsonResponse({'success': False, 'message': 'Aucune photo de référence configurée'})

        # Save uploaded image temp
        temp_path = save_base64_image(data_url, f"{username}_attempt")
        if not temp_path:
            print("❌ Échec sauvegarde image temporaire")
            LoginAttempt.objects.create(
                user=user, 
                success=False, 
                ip_address=get_client_ip(request), 
                method='face', 
                note='failed to save temp image'
            )
            return JsonResponse({'success': False, 'message': 'Erreur de traitement de l\'image'})

        known_path = user.photo.path
        print(f"📁 Chemin photo référence: {known_path}")
        print(f"📁 Chemin photo temporaire: {temp_path}")

        # Vérifier que les fichiers existent
        if not os.path.exists(known_path):
            print(f"❌ Photo référence n'existe pas: {known_path}")
            cleanup_temp_file(temp_path)
            return JsonResponse({'success': False, 'message': 'Photo de référence introuvable'})

        verified = verify_face(known_path, temp_path)
        
        # Clean temp
        cleanup_temp_file(temp_path)

        LoginAttempt.objects.create(
            user=user, 
            success=verified, 
            ip_address=get_client_ip(request), 
            method='face', 
            note='face verification completed'
        )
        
        if verified:
            print(f"✅ Reconnaissance faciale réussie pour {username}")
            # authenticate + login user with Django session
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return JsonResponse({
                'success': True, 
                'message': 'Authentification réussie par reconnaissance faciale!'
            })
        else:
            print(f"❌ Reconnaissance faciale échouée pour {username}")
            return JsonResponse({
                'success': False, 
                'message': 'Visage non reconnu. Essayez avec votre mot de passe.'
            })
            
    except Exception as e:
        print(f"❌ Erreur générale dans face_login_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'message': f'Erreur serveur: {str(e)}'
        })

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Enregistrer la création de compte
            LoginAttempt.objects.create(
                user=user,
                success=True,
                ip_address=get_client_ip(request),
                method='registration',
                note='Création de compte utilisateur'
            )
            
            # Connecter automatiquement l'utilisateur
            login(request, user)
            messages.success(request, 'Compte créé avec succès! Bienvenue.')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'authentication/register.html', {'form': form})