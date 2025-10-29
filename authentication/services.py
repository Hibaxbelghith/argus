# services.py - VERSION URGENCE
from deepface import DeepFace
import os
import base64
from django.conf import settings
import uuid
import cv2
import numpy as np

def save_base64_image(data_url, filename_prefix):
    """Sauvegarde une image base64 dans un fichier temporaire"""
    try:
        print(f"📸 Sauvegarde image pour {filename_prefix}")
        
        # Extraire les données base64
        if ',' in data_url:
            format, imgstr = data_url.split(',', 1)
        else:
            imgstr = data_url
        
        # Décoder l'image
        image_data = base64.b64decode(imgstr)
        
        # Convertir en numpy array pour OpenCV
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("❌ Erreur: Impossible de décoder l'image")
            return None
        
        # Redimensionner l'image si trop grande (optimisation)
        height, width = img.shape[:2]
        if height > 800 or width > 800:
            scale = 800 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            print(f"📏 Image redimensionnée: {width}x{height} -> {new_width}x{new_height}")
        
        # Créer un nom de fichier unique
        filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', filename)
        
        # Créer le dossier temp si nécessaire
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        # Sauvegarder en JPG avec qualité optimisée
        success = cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        if not success:
            print("❌ Erreur: Impossible de sauvegarder l'image")
            return None
            
        print(f"✅ Image temporaire sauvegardée: {temp_path}")
        return temp_path
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde image: {e}")
        return None

def verify_face(known_image_path, unknown_image_path, confidence_threshold=0.4):  # Seuil réduit à 0.4
    """Vérifie si les deux images contiennent le même visage - VERSION URGENCE"""
    try:
        print(f"🔍 Début vérification faciale URGENCE...")
        print(f"   Image référence: {known_image_path}")
        print(f"   Image capture: {unknown_image_path}")
        
        # Vérifier que les fichiers existent
        if not os.path.exists(known_image_path):
            print("❌ Image référence n'existe pas")
            return False
        if not os.path.exists(unknown_image_path):
            print("❌ Image capture n'existe pas")
            return False
        
        # DEBUG: Vérifier la taille des fichiers
        ref_size = os.path.getsize(known_image_path)
        cap_size = os.path.getsize(unknown_image_path)
        print(f"   Taille référence: {ref_size} bytes")
        print(f"   Taille capture: {cap_size} bytes")
        
        # OPTION 1: Essayer d'abord avec detection désactivée
        print("🔄 Essai 1: enforce_detection=False")
        result = DeepFace.verify(
            img1_path=known_image_path,
            img2_path=unknown_image_path,
            model_name="VGG-Face",
            detector_backend="opencv",
            enforce_detection=False,  # IMPORTANT: Désactive la détection de visage
            align=True,
            normalization="base",
            distance_metric="cosine"
        )
        
        print(f"✅ Résultat Essai 1: {result}")
        
        # Vérifier le seuil de confiance
        distance = result.get('distance', 1.0)
        confidence = 1 - distance
        
        print(f"📊 Distance: {distance}, Confiance: {confidence:.2%}")
        
        is_verified = result.get('verified', False) and confidence >= confidence_threshold
        
        if is_verified:
            print(f"🎯 Reconnaissance RÉUSSIE avec confiance: {confidence:.2%}")
            return True
        else:
            print(f"⚠️  Essai 1 échoué, confiance: {confidence:.2%}")
            
            # OPTION 2: Essayer avec un backend différent
            print("🔄 Essai 2: backend mtcnn")
            try:
                result2 = DeepFace.verify(
                    img1_path=known_image_path,
                    img2_path=unknown_image_path,
                    model_name="VGG-Face", 
                    detector_backend="mtcnn",  # Alternative à opencv
                    enforce_detection=False,
                    align=True
                )
                distance2 = result2.get('distance', 1.0)
                confidence2 = 1 - distance2
                is_verified2 = result2.get('verified', False) and confidence2 >= confidence_threshold
                print(f"📊 Essai 2 - Confiance: {confidence2:.2%}, Réussi: {is_verified2}")
                
                if is_verified2:
                    return True
            except Exception as e2:
                print(f"⚠️  Essai 2 échoué: {e2}")
            
            # OPTION 3: Essayer avec un modèle différent
            print("🔄 Essai 3: modèle Facenet")
            try:
                result3 = DeepFace.verify(
                    img1_path=known_image_path,
                    img2_path=unknown_image_path,
                    model_name="Facenet",  # Modèle alternatif
                    detector_backend="opencv",
                    enforce_detection=False,
                    align=True
                )
                distance3 = result3.get('distance', 1.0)
                confidence3 = 1 - distance3
                is_verified3 = result3.get('verified', False) and confidence3 >= confidence_threshold
                print(f"📊 Essai 3 - Confiance: {confidence3:.2%}, Réussi: {is_verified3}")
                
                return is_verified3
            except Exception as e3:
                print(f"⚠️  Essai 3 échoué: {e3}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur vérification faciale: {e}")
        return False

def cleanup_temp_file(file_path):
    """Nettoie le fichier temporaire"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Fichier temporaire nettoyé: {file_path}")
    except Exception as e:
        print(f"⚠️ Erreur nettoyage fichier temporaire: {e}")