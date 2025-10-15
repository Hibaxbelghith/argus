import os
from django.conf import settings
from deepface import DeepFace
from pathlib import Path

def save_base64_image(data_url: str, filename: str) -> str:
    """
    Reçoit un data URL (data:image/png;base64,...) et le sauvegarde sous MEDIA_ROOT/temp/filename
    Retourne le chemin complet du fichier sauvegardé.
    """
    import base64, re
    header, encoded = data_url.split(',', 1)
    ext = 'png' if 'png' in header else 'jpg'
    data = base64.b64decode(encoded)
    temp_dir = Path(settings.MEDIA_ROOT) / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    path = temp_dir / f"{filename}.{ext}"
    with open(path, 'wb') as f:
        f.write(data)
    return str(path)

def verify_face(known_image_path: str, unknown_image_path: str) -> bool:
    """
    Utilise DeepFace.verify pour comparer deux images.
    Retourne True si correspondance.
    """
    try:
        result = DeepFace.verify(img1_path=known_image_path, img2_path=unknown_image_path, enforce_detection=False)
        return bool(result.get("verified", False))
    except Exception as e:
        # log exception en prod
        return False

def cleanup_temp_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass
