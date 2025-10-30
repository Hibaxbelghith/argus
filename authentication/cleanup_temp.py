import os, time
from django.conf import settings

def clean_temp_faces(max_age_seconds=600):
    """
    Supprime les images temporaires plus anciennes que `max_age_seconds`.
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_faces')
    if not os.path.exists(temp_dir):
        return

    now = time.time()
    removed = 0
    for f in os.listdir(temp_dir):
        path = os.path.join(temp_dir, f)
        if os.path.isfile(path):
            age = now - os.path.getmtime(path)
            if age > max_age_seconds:
                os.remove(path)
                removed += 1
    print(f"[cleanup_temp_faces] {removed} fichier(s) supprimé(s).")
