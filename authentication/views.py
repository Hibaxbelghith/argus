from django.shortcuts import render

# Create your views here.
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
import ipaddress

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
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})

@csrf_exempt
def face_login_api(request):
    """
    Endpoint POST : reçoit JSON { 'image': 'data:image/png;base64,...', 'username': '...' }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    import json
    data = json.loads(request.body)
    data_url = data.get('image')
    username = data.get('username')
    user = None
    try:
        user = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        LoginAttempt.objects.create(user=None, success=False, ip_address=get_client_ip(request), method='face', note='user not found')
        return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé'})

    # Save uploaded image temp
    temp_path = save_base64_image(data_url, f"{username}_attempt_{timezone.now().timestamp()}")
    known_path = user.photo.path if user.photo else None
    verified = False
    if known_path:
        verified = verify_face(known_path, temp_path)
    # Clean temp
    cleanup_temp_file(temp_path)

    LoginAttempt.objects.create(user=user, success=verified, ip_address=get_client_ip(request), method='face', note='face verification')
    if verified:
        # authenticate + login user with Django session
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return JsonResponse({'success': True, 'message': 'Authentification réussie'})
    else:
        return JsonResponse({'success': False, 'message': 'Visage non reconnu'})
