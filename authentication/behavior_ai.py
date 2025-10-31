import datetime
from django.conf import settings
from .models import LoginAttempt



# Facultatif : base GeoLite2 gratuite (mettre le fichier .mmdb dans /geo/)
GEOIP_DB = None

def compute_anomaly_score(user, ip, timestamp):
    """
    Calcule un score de risque entre 0 et 1 basé sur l'heure, l'IP et l'historique.
    """
    score = 0.0
    details = []

    # 1. IP nouvelle
    last_ips = LoginAttempt.objects.filter(user=user, success=True).values_list("ip_address", flat=True).distinct()
    if ip and ip not in last_ips:
        score += 0.4
        details.append("nouvelle IP")

    # 2. Heure inhabituelle (connexion de nuit)
    local_hour = timestamp.hour
    if local_hour < 6 or local_hour > 22:
        score += 0.3
        details.append("heure nocturne")

    # 3. Fréquence élevée
    recent = LoginAttempt.objects.filter(user=user, timestamp__gte=timestamp - datetime.timedelta(minutes=5)).count()
    if recent > 3:
        score += 0.3
        details.append("trop de tentatives")

    # Clamp
    score = min(score, 1.0)
    return score, ", ".join(details)


def analyze_login(user, ip):
    """
    Détecte les anomalies et met à jour la dernière tentative.
    """
    attempt = LoginAttempt.objects.filter(user=user).latest("timestamp")
    score, reason = compute_anomaly_score(user, ip, attempt.timestamp)
    attempt.anomaly_score = score
    attempt.note = f"Analyse comportementale: {reason}"
    attempt.save()

    if score >= 0.7:
        print(f"[ALERTE] Connexion suspecte détectée pour {user.username}: {reason}")
        return True
    return False
