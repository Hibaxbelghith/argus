import datetime
from django.utils import timezone
from django.http import JsonResponse
from authentication.models import LoginAttempt


class LimitFaceLoginMiddleware:
    RATE_LIMIT = 5          # tentatives max
    WINDOW_SECONDS = 60     # période en secondes

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/auth/face-login/' and request.method == 'POST':
            ip = request.META.get('REMOTE_ADDR')
            cutoff = timezone.now() - datetime.timedelta(seconds=self.WINDOW_SECONDS)

            recent_attempts = LoginAttempt.objects.filter(
                ip_address=ip,
                timestamp__gte=cutoff
            ).count()

            if recent_attempts >= self.RATE_LIMIT:
                return JsonResponse({
                    'success': False,
                    'message': 'Trop de tentatives faciales. Réessayez plus tard.'
                }, status=429)

        return self.get_response(request)
