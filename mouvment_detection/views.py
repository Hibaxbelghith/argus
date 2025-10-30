from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .detector import detector
from .models import DetectionEvent, CameraSettings


def index(request):
    """Page d'accueil avec le flux vidéo en temps réel"""
    context = {
        'title': 'Système de Détection - Argus',
        'enable_motion': detector.enable_motion_detection,
        'enable_face': detector.enable_face_detection,
    }
    return render(request, 'mouvment_detection/index.html', context)


def video_feed(request):
    """
    Vue pour le streaming vidéo en temps réel
    Utilise multipart/x-mixed-replace pour envoyer les frames en continu
    """
    # Démarrer le détecteur si ce n'est pas déjà fait
    if not detector.is_running:
        detector.start()
    
    return StreamingHttpResponse(
        detector.generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@csrf_exempt
@require_http_methods(["POST"])
def start_detection(request):
    """Démarre la détection"""
    try:
        if detector.start():
            return JsonResponse({
                'status': 'success',
                'message': 'Détection démarrée avec succès',
                'is_running': True
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Impossible de démarrer la détection',
                'is_running': False
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'is_running': False
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def stop_detection(request):
    """Arrête la détection"""
    try:
        detector.stop()
        return JsonResponse({
            'status': 'success',
            'message': 'Détection arrêtée',
            'is_running': False
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def detection_status(request):
    """Retourne le statut actuel de la détection"""
    try:
        return JsonResponse({
            'is_running': detector.is_running,
            'motion_detected': detector.motion_detected,
            'faces_detected': detector.faces_detected,
            'motion_intensity': detector.last_motion_intensity,
            'enable_motion_detection': detector.enable_motion_detection,
            'enable_face_detection': detector.enable_face_detection,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_settings(request):
    """Met à jour les paramètres de détection en temps réel"""
    try:
        enable_motion = request.POST.get('enable_motion', 'true').lower() == 'true'
        enable_face = request.POST.get('enable_face', 'true').lower() == 'true'
        
        detector.enable_motion_detection = enable_motion
        detector.enable_face_detection = enable_face
        
        return JsonResponse({
            'status': 'success',
            'message': 'Paramètres mis à jour',
            'enable_motion_detection': detector.enable_motion_detection,
            'enable_face_detection': detector.enable_face_detection,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def events_list(request):
    """Liste des événements de détection"""
    events = DetectionEvent.objects.filter(is_active=True).order_by('-timestamp')
    
    # Filtres
    detection_type = request.GET.get('type')
    if detection_type:
        events = events.filter(detection_type=detection_type)
    
    # Pagination
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Historique des Détections',
        'page_obj': page_obj,
        'events': page_obj.object_list,
    }
    return render(request, 'mouvment_detection/events_list.html', context)


def events_api(request):
    """API JSON pour récupérer les événements récents"""
    limit = int(request.GET.get('limit', 10))
    events = DetectionEvent.objects.filter(is_active=True).order_by('-timestamp')[:limit]
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'detection_type': event.get_detection_type_display(),
            'timestamp': event.timestamp.isoformat(),
            'faces_count': event.faces_count,
            'motion_intensity': event.motion_intensity,
            'image_url': event.image.url if event.image else None,
        })
    
    return JsonResponse({
        'status': 'success',
        'count': len(events_data),
        'events': events_data
    })


def statistics(request):
    """Page de statistiques"""
    from django.db.models import Count, Avg
    from datetime import timedelta
    from django.utils import timezone
    
    # Statistiques générales
    total_events = DetectionEvent.objects.filter(is_active=True).count()
    motion_events = DetectionEvent.objects.filter(detection_type='motion', is_active=True).count()
    face_events = DetectionEvent.objects.filter(detection_type='face', is_active=True).count()
    both_events = DetectionEvent.objects.filter(detection_type='both', is_active=True).count()
    
    # Événements des dernières 24h
    last_24h = timezone.now() - timedelta(hours=24)
    recent_events = DetectionEvent.objects.filter(
        is_active=True,
        timestamp__gte=last_24h
    ).count()
    
    # Moyenne des visages détectés
    avg_faces = DetectionEvent.objects.filter(
        is_active=True,
        faces_count__gt=0
    ).aggregate(Avg('faces_count'))['faces_count__avg'] or 0
    
    context = {
        'title': 'Statistiques',
        'total_events': total_events,
        'motion_events': motion_events,
        'face_events': face_events,
        'both_events': both_events,
        'recent_events': recent_events,
        'avg_faces': round(avg_faces, 2),
    }
    return render(request, 'mouvment_detection/statistics.html', context)


def settings_view(request):
    """Page de configuration"""
    if request.method == 'POST':
        # Sauvegarder ou mettre à jour les paramètres
        name = request.POST.get('name', 'Default')
        
        settings, created = CameraSettings.objects.get_or_create(
            name=name,
            defaults={
                'camera_index': int(request.POST.get('camera_index', 0)),
                'enable_motion_detection': request.POST.get('enable_motion', 'on') == 'on',
                'enable_face_detection': request.POST.get('enable_face', 'on') == 'on',
                'motion_threshold': int(request.POST.get('motion_threshold', 25)),
                'min_contour_area': int(request.POST.get('min_contour_area', 500)),
                'save_images': request.POST.get('save_images', 'on') == 'on',
                'detection_interval': int(request.POST.get('detection_interval', 1)),
                'is_active': True,
            }
        )
        
        if not created:
            settings.camera_index = int(request.POST.get('camera_index', 0))
            settings.enable_motion_detection = request.POST.get('enable_motion', 'on') == 'on'
            settings.enable_face_detection = request.POST.get('enable_face', 'on') == 'on'
            settings.motion_threshold = int(request.POST.get('motion_threshold', 25))
            settings.min_contour_area = int(request.POST.get('min_contour_area', 500))
            settings.save_images = request.POST.get('save_images', 'on') == 'on'
            settings.detection_interval = int(request.POST.get('detection_interval', 1))
            settings.save()
        
        # Recharger les paramètres dans le détecteur
        detector.load_settings()
    
    # Récupérer les paramètres actuels
    current_settings = CameraSettings.objects.filter(is_active=True).first()
    
    context = {
        'title': 'Paramètres',
        'settings': current_settings,
    }
    return render(request, 'mouvment_detection/settings.html', context)
