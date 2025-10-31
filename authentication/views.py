import os
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import RegisterForm, LoginForm
from .models import CustomUser, LoginAttempt
from .services import save_base64_image, cleanup_temp_file, verify_face
from django.utils.timezone import localtime
from .behavior_ai import analyze_login
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm, CustomPasswordChangeForm



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def logout_view(request):
    logout(request)
    return redirect('login')


@csrf_protect
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            LoginAttempt.objects.create(
                user=user,
                success=True,
                ip_address=get_client_ip(request),
                method='password'
            )
            analyze_login(user, get_client_ip(request))

            # 🔹 Rediriger selon le rôle
            if user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = LoginForm()
    return render(request, 'authentication/login.html', {'form': form})



@csrf_exempt
def face_login_api(request):
    """POST: { "image": "data:image/png;base64,...", "username": "..." }"""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST only'}, status=405)

        # Lire le JSON
        data = json.loads(request.body)
        data_url = data.get('image')
        username = data.get('username')

        if not data_url or not username:
            return JsonResponse({'success': False, 'message': 'Données manquantes'})

        if not data_url.startswith("data:image/"):
            return JsonResponse({'success': False, 'message': 'Format image non valide'})

        # Chercher utilisateur
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            LoginAttempt.objects.create(
                user=None, success=False, ip_address=get_client_ip(request),
                method='face', note='Utilisateur non trouvé'
            )
            return JsonResponse({'success': False, 'message': 'Utilisateur inconnu'})

        if not user.photo:
            return JsonResponse({'success': False, 'message': 'Aucune photo de référence configurée'})

        # Sauver image temporaire
        temp_path = save_base64_image(data_url, f"{username}_attempt")
        if not temp_path:
            return JsonResponse({'success': False, 'message': 'Erreur de traitement image'})

        known_path = user.photo.path
        if not os.path.exists(known_path):
            cleanup_temp_file(temp_path)
            return JsonResponse({'success': False, 'message': 'Photo de référence introuvable'})

        # Vérification faciale
        verified = verify_face(known_path, temp_path)
        cleanup_temp_file(temp_path)

        LoginAttempt.objects.create(
            user=user, success=verified,
            ip_address=get_client_ip(request),
            method='face', note='face verification done'
        )

        if verified:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            analyze_login(user, get_client_ip(request))
            return JsonResponse({'success': True, 'message': 'Authentification faciale réussie'})
        else:
            return JsonResponse({'success': False, 'message': 'Visage non reconnu'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur serveur: {str(e)}'})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            LoginAttempt.objects.create(
                user=user,
                success=True,
                ip_address=get_client_ip(request),
                method='registration',
                note='Création de compte utilisateur'
            )
            messages.success(request, 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user

    if user.role == 'admin':
        users = CustomUser.objects.all()
        attempts = LoginAttempt.objects.order_by('-timestamp')[:50]
        recommendation = None
        if attempts and attempts[0].anomaly_score > 0.7:
            recommendation = "⚠️ Activité suspecte détectée : changez votre mot de passe ou vérifiez votre identité."

        return render(request, 'authentication/admin_dashboard.html', {
            'users': users,
            'attempts': attempts,
            'recommendation': recommendation
        })
    else:
        attempts = LoginAttempt.objects.filter(user=user).order_by('-timestamp')[:10]
        return render(request, 'authentication/dashboard.html', {'attempts': attempts})


@login_required
def dashboard(request):
    attempts = LoginAttempt.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'authentication/dashboard.html', {'attempts': attempts})


@login_required
def admin_dashboard(request):
    users = CustomUser.objects.all()
    attempts = list(LoginAttempt.objects.order_by('-timestamp')[:50])
    attempts.reverse()  # chronologique pour le graphique

    chart_labels = [localtime(a.timestamp).strftime("%H:%M") for a in attempts]
    chart_scores = [round(a.anomaly_score or 0.0, 3) for a in attempts]

    recommendation = None
    if attempts and (attempts[-1].anomaly_score or 0) > 0.7:
        recommendation = "⚠️ Activité suspecte détectée : changez votre mot de passe ou vérifiez votre identité."

    return render(
        request,
        "authentication/admin_dashboard.html",
        {
            "users": users,
            "attempts": attempts[::-1],  # tableau HTML en ordre récent→ancien
            "recommendation": recommendation,
            "chart_labels": chart_labels,
            "chart_scores": chart_scores,
        },
    )



def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
@require_POST
def delete_user(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if user and user.role != 'admin':  # sécurité
        user.delete()
        messages.success(request, f"Utilisateur {user.username} supprimé.")
    else:
        messages.error(request, "Impossible de supprimer cet utilisateur.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
@require_POST
def toggle_block_user(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('admin_dashboard')

    user.is_active = not user.is_active
    user.save()
    action = "bloqué" if not user.is_active else "débloqué"
    messages.info(request, f"Utilisateur {user.username} {action}.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
@require_POST
def change_role(request, user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('admin_dashboard')

    user.role = 'admin' if user.role == 'user' else 'user'
    user.save()
    messages.success(request, f"Rôle de {user.username} changé en {user.role}.")
    return redirect('admin_dashboard')



@user_passes_test(is_admin)
def search_users(request):
    q = request.GET.get("q", "").strip()
    page_number = request.GET.get("page", 1)

    users = CustomUser.objects.all().order_by("username")
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q))

    paginator = Paginator(users, 5)
    page_obj = paginator.get_page(page_number)

    data = []
    for u in page_obj:
        data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email or "",
            "role": u.role,
            "last_login": u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "",
            "is_active": u.is_active,
        })

    return JsonResponse({
        "users": data,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
    })

@user_passes_test(is_admin)
def search_attempts(request):
    page_number = request.GET.get("page", 1)
    attempts = LoginAttempt.objects.select_related("user").order_by("-timestamp")
    paginator = Paginator(attempts, 6)  # 6 lignes par page
    page_obj = paginator.get_page(page_number)

    data = []
    for a in page_obj:
        data.append({
            "user": a.user.username if a.user else "Unknown",
            "ip_address": a.ip_address or "N/A",
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M"),
            "method": a.method,
            "success": a.success,
            "anomaly_score": round(a.anomaly_score, 2),
            "note": a.note or "",
        })

    return JsonResponse({
        "attempts": data,
        "num_pages": paginator.num_pages,
        "current_page": page_obj.number,
    })



@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'authentication/profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent logout
            messages.success(request, "🔒 Password changed successfully.")
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'authentication/change_password.html', {'form': form})
