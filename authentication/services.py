import os
import base64
import uuid
from deepface import DeepFace
from django.conf import settings

# ---------------------------------------------------------------------
# 1. Sauvegarde d'une image Base64 envoyée depuis le front (webcam)
# ---------------------------------------------------------------------
def save_base64_image(data_url, username):
    try:
        header, encoded = data_url.split(',', 1)
        if not header.startswith("data:image/"):
            print("[save_base64_image] Format image invalide.")
            return None

        data = base64.b64decode(encoded)
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_faces')
        os.makedirs(temp_dir, exist_ok=True)

        filename = f"{username}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "wb") as f:
            f.write(data)

        return file_path
    except Exception as e:
        print(f"[save_base64_image] Erreur: {e}")
        return None


# ---------------------------------------------------------------------
# 2. Suppression sécurisée d’un fichier temporaire
# ---------------------------------------------------------------------
def cleanup_temp_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"[cleanup_temp_file] Erreur: {e}")


# ---------------------------------------------------------------------
# 3. Vérification faciale avec DeepFace
# ---------------------------------------------------------------------
def verify_face(known_path, test_path, model_name="Facenet512", threshold=0.6):
    """
    Compare deux visages et retourne True si correspondance.
    DeepFace gère l’alignement, le pré-traitement et le modèle.
    """
    try:
        result = DeepFace.verify(
            img1_path=known_path,
            img2_path=test_path,
            model_name=model_name,
            enforce_detection=False
        )
        print(f"[verify_face] Résultat DeepFace : {result}")
        return result.get("verified", False)
    except Exception as e:
        print(f"[verify_face] Erreur DeepFace: {e}")
        return False
