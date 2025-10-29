# 💡 Exemples d'Utilisation - Argus

Ce document présente des exemples concrets d'utilisation du système de détection.

---

## 1️⃣ Utilisation Basique

### Démarrer et Tester la Détection

```bash
# 1. Démarrer le serveur
cd d:\hamza\5TWIN2K25\Django\argus
..\env\Scripts\python.exe manage.py runserver

# 2. Ouvrir le navigateur
# http://127.0.0.1:8000/

# 3. Cliquer sur "Démarrer la Détection"
# 4. Bouger devant la caméra pour tester le mouvement
# 5. Montrer votre visage pour tester la détection de visages
```

---

## 2️⃣ Utilisation de l'API REST

### En Python (requests)

```python
import requests

# URL de base
BASE_URL = "http://127.0.0.1:8000"

# 1. Démarrer la détection
response = requests.post(f"{BASE_URL}/api/start/")
print(response.json())
# {'status': 'success', 'message': 'Détection démarrée', 'is_running': True}

# 2. Vérifier le statut
response = requests.get(f"{BASE_URL}/api/status/")
status = response.json()
print(f"Actif: {status['is_running']}")
print(f"Mouvement: {status['motion_detected']}")
print(f"Visages: {status['faces_detected']}")

# 3. Obtenir les derniers événements
response = requests.get(f"{BASE_URL}/api/events/?limit=5")
events = response.json()
for event in events['events']:
    print(f"{event['timestamp']}: {event['detection_type']}")

# 4. Modifier les paramètres
data = {
    'enable_motion': 'true',
    'enable_face': 'false'
}
response = requests.post(f"{BASE_URL}/api/settings/", data=data)
print(response.json())

# 5. Arrêter la détection
response = requests.post(f"{BASE_URL}/api/stop/")
print(response.json())
```

### En JavaScript (fetch)

```javascript
// 1. Démarrer la détection
fetch("http://127.0.0.1:8000/api/start/", {
  method: "POST",
})
  .then((response) => response.json())
  .then((data) => console.log(data));

// 2. Vérifier le statut toutes les secondes
setInterval(() => {
  fetch("http://127.0.0.1:8000/api/status/")
    .then((response) => response.json())
    .then((data) => {
      console.log("Mouvement:", data.motion_detected);
      console.log("Visages:", data.faces_detected);
    });
}, 1000);

// 3. Obtenir les événements
fetch("http://127.0.0.1:8000/api/events/?limit=10")
  .then((response) => response.json())
  .then((data) => {
    data.events.forEach((event) => {
      console.log(`${event.timestamp}: ${event.detection_type}`);
    });
  });
```

---

## 3️⃣ Utilisation du Shell Django

### Créer des Paramètres de Caméra

```bash
cd d:\hamza\5TWIN2K25\Django\argus
..\env\Scripts\python.exe manage.py shell
```

```python
from detection.models import CameraSettings

# Créer une configuration
settings = CameraSettings.objects.create(
    name='Bureau',
    camera_index=0,
    enable_motion_detection=True,
    enable_face_detection=True,
    motion_threshold=20,
    min_contour_area=800,
    save_images=True,
    detection_interval=2,
    is_active=True
)

print(f"Configuration '{settings.name}' créée !")
```

### Consulter les Événements

```python
from detection.models import DetectionEvent
from datetime import datetime, timedelta
from django.utils import timezone

# Tous les événements du jour
today = timezone.now().replace(hour=0, minute=0, second=0)
events_today = DetectionEvent.objects.filter(
    timestamp__gte=today
)
print(f"Événements aujourd'hui: {events_today.count()}")

# Événements avec visages
face_events = DetectionEvent.objects.filter(
    faces_count__gt=0
).order_by('-timestamp')[:10]

for event in face_events:
    print(f"{event.timestamp}: {event.faces_count} visage(s)")

# Événements de la dernière heure
last_hour = timezone.now() - timedelta(hours=1)
recent = DetectionEvent.objects.filter(
    timestamp__gte=last_hour
)
print(f"Dernière heure: {recent.count()} détections")
```

### Statistiques Avancées

```python
from detection.models import DetectionEvent
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta

# Statistiques générales
stats = DetectionEvent.objects.aggregate(
    total=Count('id'),
    avg_faces=Avg('faces_count'),
    avg_intensity=Avg('motion_intensity'),
    max_faces=Max('faces_count')
)
print(stats)

# Événements par type
by_type = DetectionEvent.objects.values('detection_type').annotate(
    count=Count('id')
).order_by('-count')
for item in by_type:
    print(f"{item['detection_type']}: {item['count']}")

# Événements par heure (dernières 24h)
last_24h = timezone.now() - timedelta(hours=24)
by_hour = DetectionEvent.objects.filter(
    timestamp__gte=last_24h
).extra(
    select={'hour': 'strftime("%%H", timestamp)'}
).values('hour').annotate(
    count=Count('id')
).order_by('hour')

for item in by_hour:
    print(f"Heure {item['hour']}: {item['count']} détections")
```

---

## 4️⃣ Scénarios d'Usage Réels

### Scénario 1 : Surveillance de Bureau

```python
# Configuration optimale pour un bureau
from detection.models import CameraSettings

settings = CameraSettings.objects.create(
    name='Bureau - Journée',
    camera_index=0,
    enable_motion_detection=True,
    enable_face_detection=True,
    motion_threshold=25,          # Sensibilité moyenne
    min_contour_area=1000,        # Ignorer petits mouvements
    save_images=True,             # Sauvegarder les preuves
    detection_interval=5,         # Toutes les 5 secondes
    is_active=True
)
```

### Scénario 2 : Surveillance Nocturne

```python
# Configuration pour surveillance de nuit (plus sensible)
settings = CameraSettings.objects.create(
    name='Nuit - Haute Sensibilité',
    camera_index=0,
    enable_motion_detection=True,
    enable_face_detection=False,  # Moins efficace dans le noir
    motion_threshold=15,          # Très sensible
    min_contour_area=500,         # Détecte petits mouvements
    save_images=True,
    detection_interval=1,         # Chaque seconde
    is_active=True
)
```

### Scénario 3 : Comptage de Visiteurs

```python
# Configuration pour compter les visages
settings = CameraSettings.objects.create(
    name='Compteur de Visiteurs',
    camera_index=0,
    enable_motion_detection=False,
    enable_face_detection=True,   # Seulement visages
    save_images=True,
    detection_interval=2,
    is_active=True
)

# Script pour obtenir le compte
from detection.models import DetectionEvent
from datetime import date

today = date.today()
events = DetectionEvent.objects.filter(
    timestamp__date=today,
    faces_count__gt=0
)

total_faces = sum(e.faces_count for e in events)
print(f"Visiteurs aujourd'hui: {total_faces}")
```

---

## 5️⃣ Intégration avec d'Autres Systèmes

### Envoyer une Notification par Email

```python
from django.core.mail import send_mail
from detection.models import DetectionEvent

def notify_on_detection(event):
    """Envoie un email lors d'une détection"""
    subject = f"🚨 Détection: {event.get_detection_type_display()}"
    message = f"""
    Une détection a été enregistrée:

    Type: {event.get_detection_type_display()}
    Date: {event.timestamp}
    Visages: {event.faces_count}
    Intensité: {event.motion_intensity:.2f}
    """

    send_mail(
        subject,
        message,
        'noreply@argus.local',
        ['admin@example.com'],
        fail_silently=True,
    )

# À intégrer dans detector.py, méthode save_detection_event
```

### Webhook vers un Service Externe

```python
import requests
from detection.models import DetectionEvent

def send_webhook(event):
    """Envoie les données à un webhook externe"""
    webhook_url = "https://your-service.com/webhook"

    data = {
        'type': event.detection_type,
        'timestamp': event.timestamp.isoformat(),
        'faces_count': event.faces_count,
        'motion_intensity': event.motion_intensity,
        'image_url': event.image.url if event.image else None
    }

    try:
        response = requests.post(webhook_url, json=data, timeout=5)
        response.raise_for_status()
        print(f"Webhook envoyé: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur webhook: {e}")
```

---

## 6️⃣ Personnalisation Avancée

### Modifier le Classificateur de Visages

Dans `detection/detector.py` :

```python
# Utiliser un classificateur plus précis
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
self.face_cascade = cv2.CascadeClassifier(cascade_path)

# Ou pour détecter les profils aussi
cascade_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
self.profile_cascade = cv2.CascadeClassifier(cascade_path)
```

### Ajouter la Détection de Sourires

```python
# Dans la classe MotionDetector, __init__
smile_cascade = cv2.data.haarcascades + 'haarcascade_smile.xml'
self.smile_cascade = cv2.CascadeClassifier(smile_cascade)

# Dans detect_faces
smiles = self.smile_cascade.detectMultiScale(gray, 1.8, 20)
for (x, y, w, h) in smiles:
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
```

### Détecter d'Autres Objets

```python
# Yeux
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

# Corps complet
body_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_fullbody.xml'
)
```

---

## 7️⃣ Export et Analyse des Données

### Exporter en CSV

```python
import csv
from detection.models import DetectionEvent

def export_to_csv(filename='detections.csv'):
    events = DetectionEvent.objects.all().order_by('-timestamp')

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Type', 'Timestamp', 'Visages',
            'Intensité', 'Emplacement'
        ])

        for event in events:
            writer.writerow([
                event.id,
                event.get_detection_type_display(),
                event.timestamp,
                event.faces_count,
                event.motion_intensity,
                event.location
            ])

    print(f"Export terminé: {filename}")

# Utilisation
export_to_csv('mes_detections.csv')
```

### Générer un Rapport JSON

```python
import json
from detection.models import DetectionEvent
from django.core.serializers.json import DjangoJSONEncoder

def generate_json_report():
    events = DetectionEvent.objects.all().values(
        'id', 'detection_type', 'timestamp',
        'faces_count', 'motion_intensity'
    )

    data = {
        'total': len(events),
        'events': list(events)
    }

    with open('report.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=DjangoJSONEncoder, indent=2)

    print("Rapport JSON généré")

generate_json_report()
```

---

## 8️⃣ Maintenance et Nettoyage

### Supprimer les Anciennes Détections

```python
from detection.models import DetectionEvent
from datetime import timedelta
from django.utils import timezone

# Supprimer détections de plus de 30 jours
thirty_days_ago = timezone.now() - timedelta(days=30)
old_events = DetectionEvent.objects.filter(timestamp__lt=thirty_days_ago)
count = old_events.count()
old_events.delete()
print(f"{count} anciennes détections supprimées")
```

### Nettoyer les Images Orphelines

```python
import os
from detection.models import DetectionEvent
from django.conf import settings

def clean_orphan_images():
    # Images dans la base de données
    db_images = set(
        DetectionEvent.objects.values_list('image', flat=True)
    )

    # Images sur le disque
    media_root = settings.MEDIA_ROOT / 'detections'
    disk_images = []
    for root, dirs, files in os.walk(media_root):
        for file in files:
            path = os.path.join(root, file)
            relative = os.path.relpath(path, settings.MEDIA_ROOT)
            disk_images.append(relative)

    # Supprimer les orphelines
    for img in disk_images:
        if img not in db_images:
            full_path = settings.MEDIA_ROOT / img
            os.remove(full_path)
            print(f"Supprimé: {img}")

clean_orphan_images()
```

---

## 9️⃣ Tests et Debugging

### Tester sans Caméra (Mode Mock)

```python
# Créer un fichier detection/mock_detector.py
class MockDetector:
    def __init__(self):
        self.is_running = False
        self.motion_detected = True
        self.faces_detected = 2
        self.last_motion_intensity = 0.75

    def start(self):
        self.is_running = True
        return True

    def stop(self):
        self.is_running = False

    def generate_frames(self):
        import time
        while self.is_running:
            # Générer une image de test
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\nTEST\r\n'
            time.sleep(0.1)

# Dans views.py, remplacer
# from .detector import detector
# par
# from .mock_detector import MockDetector
# detector = MockDetector()
```

---

## 🎯 Conseils de Performance

### 1. Optimiser pour la Vitesse

```python
# Réduire la résolution
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Augmenter l'intervalle
self.detection_interval = 3  # Toutes les 3 secondes

# Désactiver la sauvegarde
self.save_images = False
```

### 2. Optimiser pour la Qualité

```python
# Augmenter la résolution
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Réduire l'intervalle
self.detection_interval = 0.5  # Deux fois par seconde

# Ajuster la détection
self.motion_threshold = 20  # Plus précis
self.min_contour_area = 800  # Moins de faux positifs
```

---

Vous avez maintenant tous les outils pour utiliser Argus efficacement ! 🎉
