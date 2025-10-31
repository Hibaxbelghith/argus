# 🎯 Scénarios d'Utilisation Avancés - Argus

Cas d'usage concrets et implémentations avancées.

---

## 📋 Table des Matières

1. [Surveillance de Bureau](#surveillance-de-bureau)
2. [Sécurité Magasin](#sécurité-magasin)
3. [Comptage de Visiteurs](#comptage-de-visiteurs)
4. [Surveillance Nocturne](#surveillance-nocturne)
5. [Détection de Présence](#détection-de-présence)
6. [Analyse de Flux](#analyse-de-flux)
7. [Systèmes Multi-Caméras](#systèmes-multi-caméras)
8. [Intégration Domotique](#intégration-domotique)

---

## 🏢 1. Surveillance de Bureau

### Objectif

Monitorer l'accès à votre bureau personnel et recevoir des notifications.

### Configuration

```python
# Paramètres optimaux
CameraSettings.objects.update_or_create(
    name='Bureau Personnel',
    defaults={
        'enable_motion_detection': True,
        'enable_face_detection': True,
        'motion_threshold': 20,  # Plus sensible
        'min_contour_area': 300,  # Détecte les petits mouvements
        'save_images': True,
        'detection_interval': 2  # Une image toutes les 2 secondes
    }
)
```

### Script de Notification Email

```python
# bureau_monitor.py
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta

# Configuration
API_BASE = 'http://localhost:8000'
EMAIL_FROM = 'argus@votre-domaine.com'
EMAIL_TO = 'vous@exemple.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'votre-email@gmail.com'
SMTP_PASSWORD = 'votre-mot-de-passe-app'

# Heures de surveillance (9h-18h, lundi-vendredi)
WORK_HOURS = range(9, 18)

def is_work_time():
    now = datetime.now()
    return (now.weekday() < 5 and  # Lundi à vendredi
            now.hour in WORK_HOURS)

def send_email_alert(event):
    msg = MIMEMultipart()
    msg['Subject'] = f'🚨 Détection dans votre bureau - {event["detection_type"]}'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    # Corps de l'email
    body = f"""
    <html>
    <body>
        <h2>Détection Argus</h2>
        <p><strong>Type:</strong> {event['detection_type']}</p>
        <p><strong>Heure:</strong> {event['timestamp']}</p>
        <p><strong>Nombre de visages:</strong> {event['faces_count']}</p>
        <p><strong>Intensité:</strong> {event['motion_intensity']:.2%}</p>
        <p><strong>Localisation:</strong> {event['location']}</p>
        <hr>
        <p><a href="{API_BASE}/events/">Voir tous les événements</a></p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    # Attacher l'image si disponible
    if event['image_url']:
        try:
            image_response = requests.get(f"{API_BASE}{event['image_url']}")
            if image_response.status_code == 200:
                image = MIMEImage(image_response.content)
                image.add_header('Content-ID', '<detection_image>')
                msg.attach(image)
        except:
            pass

    # Envoyer
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"✓ Email envoyé pour l'événement {event['id']}")
    except Exception as e:
        print(f"✗ Erreur d'envoi: {e}")

def monitor_office():
    last_event_id = 0
    print("🎥 Surveillance du bureau démarrée...")

    while True:
        try:
            if is_work_time():
                # Vérifier les nouveaux événements
                response = requests.get(f'{API_BASE}/api/events/?limit=5')
                events = response.json()['results']

                for event in events:
                    if event['id'] > last_event_id:
                        print(f"⚠️ Nouvel événement détecté: {event['detection_type']}")
                        send_email_alert(event)
                        last_event_id = event['id']

            time.sleep(10)  # Vérifier toutes les 10 secondes

        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(30)

if __name__ == '__main__':
    monitor_office()
```

### Lancer au démarrage (Windows)

```batch
REM bureau_monitor.bat
@echo off
cd /d "d:\hamza\5TWIN2K25\Django\argus"
call "..\env\Scripts\activate.bat"
python bureau_monitor.py
```

Ajouter au démarrage Windows:

1. Win+R → `shell:startup`
2. Copier `bureau_monitor.bat` dans ce dossier

---

## 🏪 2. Sécurité Magasin

### Objectif

Surveiller l'entrée d'un magasin, compter les visiteurs, détecter les activités suspectes.

### Modèle Personnalisé

```python
# detection/models.py - Ajouter ce modèle

class VisitorLog(models.Model):
    """Log des visiteurs du magasin"""
    date = models.DateField(auto_now_add=True)
    hour = models.IntegerField()  # 0-23
    visitor_count = models.IntegerField(default=0)
    peak_time = models.TimeField(null=True)

    class Meta:
        unique_together = ('date', 'hour')

    def __str__(self):
        return f"{self.date} {self.hour}h - {self.visitor_count} visiteurs"
```

### Script d'Analyse

```python
# store_analytics.py
import requests
from datetime import datetime, timedelta
from collections import defaultdict

API_BASE = 'http://localhost:8000'

def analyze_store_traffic():
    """Analyse le traffic du magasin"""

    # Récupérer les événements des dernières 24h
    yesterday = datetime.now() - timedelta(days=1)
    response = requests.get(f'{API_BASE}/api/events/')
    all_events = response.json()['results']

    # Filtrer les événements avec visages (= visiteurs)
    face_events = [e for e in all_events if e['faces_count'] > 0]

    # Compter par heure
    hourly_counts = defaultdict(int)
    for event in face_events:
        hour = datetime.fromisoformat(event['timestamp'].replace('Z', '')).hour
        hourly_counts[hour] += event['faces_count']

    # Trouver l'heure de pointe
    peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)

    # Rapport
    print("=" * 50)
    print("📊 RAPPORT QUOTIDIEN - TRAFFIC MAGASIN")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Total visiteurs détectés: {sum(hourly_counts.values())}")
    print(f"Heure de pointe: {peak_hour[0]}h ({peak_hour[1]} visiteurs)")
    print("\nRépartition par heure:")

    for hour in sorted(hourly_counts.keys()):
        bar = '█' * (hourly_counts[hour] // 2)
        print(f"{hour:02d}h: {bar} ({hourly_counts[hour]})")

    # Détecter les anomalies (activité nocturne)
    night_events = [h for h in hourly_counts.keys() if h < 6 or h > 22]
    if night_events:
        print("\n⚠️ ALERTE: Activité détectée en dehors des heures d'ouverture!")
        for hour in night_events:
            print(f"  - {hour}h: {hourly_counts[hour]} détections")

def send_daily_report():
    """Envoie le rapport quotidien par email"""
    # Utiliser la fonction send_email_alert du scénario 1
    pass

# Exécuter tous les soirs à 23h
if __name__ == '__main__':
    analyze_store_traffic()
```

### Automatisation (Task Scheduler Windows)

```powershell
# Créer une tâche planifiée
$action = New-ScheduledTaskAction -Execute "d:\hamza\5TWIN2K25\Django\env\Scripts\python.exe" -Argument "d:\hamza\5TWIN2K25\Django\argus\store_analytics.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 11PM
Register-ScheduledTask -TaskName "ArgusStoreReport" -Action $action -Trigger $trigger
```

---

## 👥 3. Comptage de Visiteurs

### Objectif

Compter précisément le nombre de personnes entrant dans un lieu.

### Logique de Comptage Avancée

```python
# visitor_counter.py
import cv2
import numpy as np
from collections import deque
from detection.models import DetectionEvent

class VisitorCounter:
    """Compteur intelligent de visiteurs avec tracking"""

    def __init__(self):
        self.tracked_faces = {}
        self.next_id = 0
        self.visitor_count = 0
        self.entrance_line_y = 240  # Ligne virtuelle au milieu (640x480)

    def get_face_center(self, face_rect):
        x, y, w, h = face_rect
        return (x + w//2, y + h//2)

    def track_faces(self, faces, frame_height):
        """Track faces across frames and count crossings"""
        current_centers = [self.get_face_center(f) for f in faces]

        # Associer les visages aux tracks existants
        new_tracked = {}
        for center in current_centers:
            # Trouver le track le plus proche
            min_dist = float('inf')
            closest_id = None

            for track_id, track_data in self.tracked_faces.items():
                prev_center = track_data['center']
                dist = np.sqrt((center[0] - prev_center[0])**2 +
                             (center[1] - prev_center[1])**2)
                if dist < min_dist and dist < 100:  # Seuil de distance
                    min_dist = dist
                    closest_id = track_id

            # Nouveau visage ou track existant
            if closest_id is None:
                track_id = self.next_id
                self.next_id += 1
                prev_y = center[1]
            else:
                track_id = closest_id
                prev_y = self.tracked_faces[closest_id]['prev_y']

            # Détecter traversée de la ligne
            if prev_y < self.entrance_line_y <= center[1]:
                self.visitor_count += 1
                print(f"✓ Visiteur #{self.visitor_count} détecté!")

            new_tracked[track_id] = {
                'center': center,
                'prev_y': prev_y
            }

        self.tracked_faces = new_tracked
        return self.visitor_count

    def get_count(self):
        return self.visitor_count

    def reset(self):
        self.visitor_count = 0
        self.tracked_faces = {}

# Intégration dans detector.py
# Modifier la classe MotionDetector pour inclure le comptage

def process_frame_with_counting(self, frame):
    # ... code existant de détection ...

    if len(faces) > 0:
        count = self.visitor_counter.track_faces(faces, frame.shape[0])

        # Dessiner la ligne d'entrée
        cv2.line(frame, (0, self.visitor_counter.entrance_line_y),
                (frame.shape[1], self.visitor_counter.entrance_line_y),
                (0, 255, 0), 2)

        # Afficher le compteur
        cv2.putText(frame, f"Visiteurs: {count}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
```

### Widget de Comptage

```html
<!-- counter_widget.html -->
<!DOCTYPE html>
<html>
  <head>
    <title>Compteur de Visiteurs</title>
    <style>
      body {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: Arial, sans-serif;
      }
      .counter {
        text-align: center;
        background: white;
        padding: 50px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
      }
      .count {
        font-size: 120px;
        font-weight: bold;
        color: #667eea;
        margin: 20px 0;
      }
      .label {
        font-size: 24px;
        color: #666;
      }
      .reset-btn {
        margin-top: 30px;
        padding: 15px 30px;
        font-size: 18px;
        background: #f56565;
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
    <div class="counter">
      <div class="label">Visiteurs Aujourd'hui</div>
      <div class="count" id="count">0</div>
      <button class="reset-btn" onclick="resetCounter()">Réinitialiser</button>
    </div>

    <script>
      let count = 0;

      async function updateCount() {
        const response = await fetch("/api/events/?limit=100");
        const data = await response.json();

        // Compter les visages détectés aujourd'hui
        const today = new Date().toISOString().split("T")[0];
        count = data.results
          .filter((e) => e.timestamp.startsWith(today) && e.faces_count > 0)
          .reduce((sum, e) => sum + e.faces_count, 0);

        document.getElementById("count").innerText = count;
      }

      function resetCounter() {
        count = 0;
        document.getElementById("count").innerText = 0;
      }

      setInterval(updateCount, 3000);
      updateCount();
    </script>
  </body>
</html>
```

---

## 🌙 4. Surveillance Nocturne

### Objectif

Détecter toute activité pendant la nuit avec alertes immédiates.

### Configuration

```python
# night_watch.py
import requests
import time
from datetime import datetime
import winsound  # Alarme sonore Windows

API_BASE = 'http://localhost:8000'
NIGHT_HOURS = range(22, 6)  # 22h-6h

def is_night():
    return datetime.now().hour in NIGHT_HOURS or datetime.now().hour < 6

def sound_alarm():
    """Déclenche une alarme sonore"""
    for _ in range(3):
        winsound.Beep(1000, 500)  # 1000Hz pendant 500ms
        time.sleep(0.2)

def send_sms_alert(event):
    """Envoie un SMS via une API (ex: Twilio)"""
    # Implémenter avec votre service SMS préféré
    pass

def night_surveillance():
    last_event_id = 0
    print("🌙 Mode surveillance nocturne activé")

    while True:
        try:
            if is_night():
                # Vérifier les nouveaux événements
                response = requests.get(f'{API_BASE}/api/events/?limit=5')
                events = response.json()['results']

                for event in events:
                    if event['id'] > last_event_id:
                        print(f"🚨 ALERTE NOCTURNE: {event['detection_type']}")
                        sound_alarm()
                        send_sms_alert(event)
                        last_event_id = event['id']

            time.sleep(5)  # Vérifier toutes les 5 secondes la nuit

        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(30)

if __name__ == '__main__':
    night_surveillance()
```

### Intégration avec Philips Hue (Lumières d'Alerte)

```python
# hue_integration.py
from phue import Bridge

HUE_BRIDGE_IP = '192.168.1.2'  # IP de votre Hue Bridge
bridge = Bridge(HUE_BRIDGE_IP)

def trigger_light_alarm():
    """Fait clignoter les lumières en rouge"""
    lights = bridge.get_light_objects()

    for light in lights:
        original_state = light.on

        # Clignoter 5 fois
        for _ in range(5):
            light.on = True
            light.hue = 0  # Rouge
            light.brightness = 254
            time.sleep(0.3)
            light.on = False
            time.sleep(0.3)

        # Restaurer l'état original
        light.on = original_state

# Utiliser dans night_watch.py
def night_surveillance():
    # ...
    if event['id'] > last_event_id:
        trigger_light_alarm()
        # ...
```

---

## 🏠 5. Détection de Présence (Domotique)

### Objectif

Détecter si quelqu'un est présent à la maison.

### Script Intelligent

```python
# presence_detection.py
import requests
from datetime import datetime, timedelta

API_BASE = 'http://localhost:8000'

class PresenceDetector:
    def __init__(self, timeout_minutes=10):
        self.timeout_minutes = timeout_minutes
        self.is_present = False

    def check_presence(self):
        """Vérifie si quelqu'un est présent"""
        response = requests.get(f'{API_BASE}/api/events/?limit=10')
        events = response.json()['results']

        # Chercher un événement récent avec visage
        cutoff_time = datetime.now() - timedelta(minutes=self.timeout_minutes)

        for event in events:
            event_time = datetime.fromisoformat(event['timestamp'].replace('Z', ''))
            if event_time > cutoff_time and event['faces_count'] > 0:
                self.is_present = True
                return True

        self.is_present = False
        return False

    def get_last_seen(self):
        """Retourne l'heure de dernière présence"""
        response = requests.get(f'{API_BASE}/api/events/?type=face&limit=1')
        events = response.json()['results']

        if events:
            return events[0]['timestamp']
        return None

# Intégration Home Assistant
def update_home_assistant():
    """Met à jour le statut dans Home Assistant"""
    detector = PresenceDetector()
    is_home = detector.check_presence()

    # Poster à Home Assistant
    import requests
    response = requests.post(
        'http://homeassistant.local:8123/api/states/binary_sensor.argus_presence',
        headers={
            'Authorization': 'Bearer YOUR_HOME_ASSISTANT_TOKEN',
            'Content-Type': 'application/json'
        },
        json={
            'state': 'on' if is_home else 'off',
            'attributes': {
                'friendly_name': 'Argus Presence Detection',
                'last_seen': detector.get_last_seen()
            }
        }
    )

# Boucle de mise à jour
while True:
    update_home_assistant()
    time.sleep(60)  # Toutes les minutes
```

---

## 📊 6. Analyse de Flux (Heatmap)

### Objectif

Créer une carte de chaleur des zones d'activité.

### Génération de Heatmap

```python
# heatmap_generator.py
import cv2
import numpy as np
import requests
from PIL import Image
from datetime import datetime, timedelta

API_BASE = 'http://localhost:8000'

def generate_heatmap(days=7):
    """Génère une heatmap des détections"""

    # Récupérer tous les événements avec images
    response = requests.get(f'{API_BASE}/api/events/?limit=1000')
    events = [e for e in response.json()['results'] if e['image_url']]

    # Créer une matrice d'accumulation
    heatmap = np.zeros((480, 640), dtype=np.float32)

    for event in events:
        try:
            # Télécharger l'image
            img_response = requests.get(f"{API_BASE}{event['image_url']}")
            img_array = np.asarray(bytearray(img_response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Convertir en niveaux de gris et ajouter à la heatmap
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

            # Trouver les contours (zones de mouvement)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                          cv2.CHAIN_APPROX_SIMPLE)

            # Incrémenter la heatmap aux zones de contours
            for contour in contours:
                cv2.drawContours(heatmap, [contour], -1, 1, -1)

        except:
            continue

    # Normaliser et appliquer une colormap
    heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap = heatmap.astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # Sauvegarder
    cv2.imwrite('heatmap.jpg', heatmap_colored)
    print("✓ Heatmap générée: heatmap.jpg")

    return heatmap_colored

if __name__ == '__main__':
    generate_heatmap()
```

---

## 🎥 7. Système Multi-Caméras

### Objectif

Gérer plusieurs caméras simultanément.

### Architecture

```python
# multi_camera_manager.py
from detection.detector import MotionDetector
import threading

class MultiCameraManager:
    def __init__(self):
        self.cameras = {}
        self.threads = {}

    def add_camera(self, camera_id, camera_index, location):
        """Ajoute une caméra au système"""
        detector = MotionDetector()
        detector.camera_index = camera_index
        detector.location = location

        self.cameras[camera_id] = detector
        print(f"✓ Caméra '{location}' ajoutée (index {camera_index})")

    def start_camera(self, camera_id):
        """Démarre une caméra spécifique"""
        if camera_id not in self.cameras:
            return False

        detector = self.cameras[camera_id]
        thread = threading.Thread(
            target=detector.start_detection,
            daemon=True
        )
        thread.start()
        self.threads[camera_id] = thread

        print(f"✓ Caméra {camera_id} démarrée")
        return True

    def start_all(self):
        """Démarre toutes les caméras"""
        for camera_id in self.cameras:
            self.start_camera(camera_id)

    def stop_camera(self, camera_id):
        """Arrête une caméra"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop_detection()

    def stop_all(self):
        """Arrête toutes les caméras"""
        for camera_id in self.cameras:
            self.stop_camera(camera_id)

    def get_status(self):
        """Retourne le statut de toutes les caméras"""
        status = {}
        for camera_id, detector in self.cameras.items():
            status[camera_id] = {
                'location': detector.location,
                'is_running': detector.is_running,
                'motion_detected': detector.motion_detected,
                'faces_count': detector.faces_count
            }
        return status

# Usage
manager = MultiCameraManager()
manager.add_camera('cam1', 0, 'Entrée Principale')
manager.add_camera('cam2', 1, 'Bureau')
manager.add_camera('cam3', 2, 'Entrepôt')
manager.start_all()

# Dashboard multi-caméras
while True:
    status = manager.get_status()
    for cam_id, data in status.items():
        print(f"{data['location']}: {data['faces_count']} visages")
    time.sleep(5)
```

---

## 🏡 8. Intégration Domotique Complète

### Objectif

Intégrer Argus avec votre système domotique.

### Node-RED Flow

```json
[
  {
    "id": "argus_status",
    "type": "http request",
    "name": "Get Argus Status",
    "method": "GET",
    "url": "http://localhost:8000/api/status/",
    "repeat": "5"
  },
  {
    "id": "check_faces",
    "type": "switch",
    "name": "Check Faces",
    "property": "payload.faces_count",
    "rules": [{ "t": "gt", "v": "0" }]
  },
  {
    "id": "send_notification",
    "type": "pushbullet",
    "name": "Send Alert",
    "title": "Argus Detection"
  }
]
```

### MQTT Integration

```python
# mqtt_bridge.py
import paho.mqtt.client as mqtt
import requests
import json
import time

MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'home/argus'

API_BASE = 'http://localhost:8000'

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

def publish_status():
    """Publie le statut Argus sur MQTT"""
    response = requests.get(f'{API_BASE}/api/status/')
    status = response.json()

    client.publish(f'{MQTT_TOPIC}/status', json.dumps(status))
    client.publish(f'{MQTT_TOPIC}/faces_count', status['faces_count'])
    client.publish(f'{MQTT_TOPIC}/motion', 'ON' if status['motion_detected'] else 'OFF')

# Boucle de publication
while True:
    publish_status()
    time.sleep(5)
```

### Home Assistant Configuration

```yaml
# configuration.yaml
mqtt:
  sensor:
    - name: "Argus Faces Count"
      state_topic: "home/argus/faces_count"
      unit_of_measurement: "personnes"

  binary_sensor:
    - name: "Argus Motion"
      state_topic: "home/argus/motion"
      device_class: motion

automation:
  - alias: "Argus Motion Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.argus_motion
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "Mouvement détecté par Argus!"
      - service: light.turn_on
        entity_id: light.all_lights
```

---

Vos scénarios avancés sont maintenant documentés ! 🎯✨
