# 📡 Documentation API - Argus Detection System

API complète pour interagir avec le système de détection Argus.

---

## 🔑 Vue d'Ensemble

**Base URL** : `http://localhost:8000/`  
**Format** : JSON (sauf streaming vidéo)  
**Authentification** : Aucune (pour l'instant - à ajouter)

---

## 📋 Table des Matières

1. [Streaming Vidéo](#streaming-vidéo)
2. [Contrôle de la Détection](#contrôle-de-la-détection)
3. [Événements](#événements)
4. [Statistiques](#statistiques)
5. [Paramètres](#paramètres)
6. [Codes d'Erreur](#codes-derreur)
7. [Exemples d'Intégration](#exemples-dintégration)

---

## 🎥 Streaming Vidéo

### GET /video_feed/

Stream vidéo en temps réel avec détections visuelles.

**Headers** :

```
Content-Type: multipart/x-mixed-replace; boundary=frame
```

**Réponse** : Stream MJPEG continu

**Exemple JavaScript** :

```javascript
// Afficher le flux dans une balise <img>
const videoElement = document.getElementById("video");
videoElement.src = "http://localhost:8000/video_feed/";
```

**Exemple HTML** :

```html
<img id="video" src="/video_feed/" alt="Live Stream" />
```

**Notes** :

- Le stream s'arrête automatiquement quand la détection est arrêtée
- Rectangles rouges dessinés autour des visages détectés
- Informations affichées : timestamp, mouvement, nombre de visages, intensité

---

## 🎮 Contrôle de la Détection

### POST /api/start/

Démarre la détection.

**Request** :

```http
POST /api/start/
Content-Type: application/json
```

**Body** : Aucun

**Réponse Succès (200)** :

```json
{
  "status": "started",
  "message": "Détection démarrée avec succès"
}
```

**Réponse Erreur (500)** :

```json
{
  "status": "error",
  "message": "Impossible d'initialiser la caméra"
}
```

**Exemple cURL** :

```bash
curl -X POST http://localhost:8000/api/start/
```

**Exemple JavaScript** :

```javascript
fetch("/api/start/", {
  method: "POST",
  headers: {
    "X-CSRFToken": getCookie("csrftoken"),
  },
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Détection démarrée:", data);
  });
```

**Exemple Python** :

```python
import requests

response = requests.post('http://localhost:8000/api/start/')
print(response.json())
```

---

### POST /api/stop/

Arrête la détection.

**Request** :

```http
POST /api/stop/
Content-Type: application/json
```

**Réponse (200)** :

```json
{
  "status": "stopped",
  "message": "Détection arrêtée"
}
```

**Exemple cURL** :

```bash
curl -X POST http://localhost:8000/api/stop/
```

**Exemple JavaScript** :

```javascript
fetch("/api/stop/", {
  method: "POST",
  headers: {
    "X-CSRFToken": getCookie("csrftoken"),
  },
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Détection arrêtée:", data);
  });
```

---

### GET /api/status/

Obtient le statut actuel de la détection.

**Request** :

```http
GET /api/status/
```

**Réponse (200)** :

```json
{
  "is_running": true,
  "motion_detected": true,
  "faces_count": 2,
  "motion_intensity": 0.75,
  "timestamp": "2025-10-15T14:30:45.123456"
}
```

**Champs** :

- `is_running` (bool) : Détection active ou non
- `motion_detected` (bool) : Mouvement actuellement détecté
- `faces_count` (int) : Nombre de visages dans la frame actuelle
- `motion_intensity` (float) : Intensité du mouvement (0.0 à 1.0)
- `timestamp` (string) : Date/heure ISO 8601

**Exemple cURL** :

```bash
curl http://localhost:8000/api/status/
```

**Exemple JavaScript (polling)** :

```javascript
// Vérifier le statut toutes les 2 secondes
setInterval(() => {
  fetch("/api/status/")
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("status").innerText = data.is_running
        ? "Actif"
        : "Inactif";
      document.getElementById("faces").innerText = data.faces_count;
      document.getElementById("motion").innerText = data.motion_detected
        ? "Oui"
        : "Non";
    });
}, 2000);
```

---

## 📋 Événements

### GET /api/events/

Liste tous les événements de détection.

**Request** :

```http
GET /api/events/?page=1&type=face&limit=20
```

**Query Parameters** :

- `page` (int, optionnel) : Numéro de page (défaut: 1)
- `type` (string, optionnel) : Filtre par type (`motion`, `face`, `both`)
- `limit` (int, optionnel) : Événements par page (défaut: 20)

**Réponse (200)** :

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": 45,
      "detection_type": "face",
      "timestamp": "2025-10-15T14:30:00Z",
      "faces_count": 1,
      "motion_intensity": 0.2,
      "confidence": 0.95,
      "location": "Bureau Principal",
      "image_url": "/media/detections/2025/10/15/detection_45.jpg",
      "notes": ""
    },
    {
      "id": 44,
      "detection_type": "both",
      "timestamp": "2025-10-15T14:29:30Z",
      "faces_count": 2,
      "motion_intensity": 0.85,
      "confidence": 0.88,
      "location": "Bureau Principal",
      "image_url": "/media/detections/2025/10/15/detection_44.jpg",
      "notes": "Deux personnes"
    }
  ]
}
```

**Exemple cURL** :

```bash
# Tous les événements
curl http://localhost:8000/api/events/

# Seulement les visages
curl http://localhost:8000/api/events/?type=face

# Page 2
curl "http://localhost:8000/api/events/?page=2"
```

**Exemple JavaScript** :

```javascript
// Charger les événements
async function loadEvents(page = 1, type = null) {
  let url = `/api/events/?page=${page}`;
  if (type) url += `&type=${type}`;

  const response = await fetch(url);
  const data = await response.json();

  // Afficher les résultats
  data.results.forEach((event) => {
    console.log(
      `Event ${event.id}: ${event.detection_type} at ${event.timestamp}`
    );
  });

  return data;
}

// Usage
loadEvents(1, "face");
```

**Exemple Python** :

```python
import requests

# Récupérer tous les événements de visages
response = requests.get(
    'http://localhost:8000/api/events/',
    params={'type': 'face', 'limit': 50}
)

events = response.json()['results']
for event in events:
    print(f"Event {event['id']}: {event['faces_count']} visages")
```

---

### GET /api/events/{id}/

Détails d'un événement spécifique.

**Request** :

```http
GET /api/events/45/
```

**Réponse (200)** :

```json
{
  "id": 45,
  "detection_type": "face",
  "timestamp": "2025-10-15T14:30:00.123456Z",
  "faces_count": 1,
  "motion_intensity": 0.2,
  "confidence": 0.95,
  "location": "Bureau Principal",
  "image_url": "/media/detections/2025/10/15/detection_45.jpg",
  "notes": "Visiteur identifié",
  "user": null,
  "is_active": true
}
```

**Réponse Erreur (404)** :

```json
{
  "detail": "Event not found"
}
```

---

### DELETE /api/events/{id}/

Supprime un événement.

**Request** :

```http
DELETE /api/events/45/
```

**Réponse (204)** : No Content

**Réponse Erreur (404)** :

```json
{
  "detail": "Event not found"
}
```

---

## 📊 Statistiques

### GET /api/statistics/

Obtient les statistiques globales.

**Request** :

```http
GET /api/statistics/
```

**Réponse (200)** :

```json
{
  "total_events": 150,
  "motion_only": 85,
  "faces_only": 45,
  "both": 20,
  "last_24h": 35,
  "average_faces": 1.5,
  "by_type": {
    "motion": 56.7,
    "face": 30.0,
    "both": 13.3
  },
  "hourly_distribution": [
    { "hour": 0, "count": 2 },
    { "hour": 1, "count": 1 },
    { "hour": 8, "count": 15 },
    { "hour": 9, "count": 23 },
    { "hour": 14, "count": 18 }
  ],
  "top_locations": [
    { "location": "Bureau Principal", "count": 80 },
    { "location": "Entrée", "count": 45 },
    { "location": "Salle de réunion", "count": 25 }
  ]
}
```

**Exemple JavaScript** :

```javascript
fetch("/api/statistics/")
  .then((response) => response.json())
  .then((stats) => {
    document.getElementById("total").innerText = stats.total_events;

    // Créer un graphique avec Chart.js
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: ["Mouvement", "Visages", "Les deux"],
        datasets: [
          {
            data: [stats.motion_only, stats.faces_only, stats.both],
          },
        ],
      },
    });
  });
```

---

## ⚙️ Paramètres

### GET /api/settings/

Récupère les paramètres actuels de la caméra.

**Request** :

```http
GET /api/settings/
```

**Réponse (200)** :

```json
{
  "id": 1,
  "name": "Default Camera",
  "camera_index": 0,
  "enable_motion_detection": true,
  "enable_face_detection": true,
  "motion_threshold": 25,
  "min_contour_area": 500,
  "save_images": true,
  "detection_interval": 1,
  "is_active": true
}
```

---

### POST /api/settings/update/

Met à jour les paramètres de détection.

**Request** :

```http
POST /api/settings/update/
Content-Type: application/json

{
    "enable_motion_detection": true,
    "enable_face_detection": false,
    "motion_threshold": 30,
    "min_contour_area": 800,
    "save_images": false
}
```

**Réponse Succès (200)** :

```json
{
  "status": "success",
  "message": "Paramètres mis à jour",
  "settings": {
    "enable_motion_detection": true,
    "enable_face_detection": false,
    "motion_threshold": 30,
    "min_contour_area": 800,
    "save_images": false
  }
}
```

**Réponse Erreur (400)** :

```json
{
  "status": "error",
  "errors": {
    "motion_threshold": ["Doit être entre 1 et 100"]
  }
}
```

**Exemple JavaScript** :

```javascript
const settings = {
  enable_motion_detection: true,
  enable_face_detection: true,
  motion_threshold: 20,
  save_images: true,
};

fetch("/api/settings/update/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": getCookie("csrftoken"),
  },
  body: JSON.stringify(settings),
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Paramètres mis à jour:", data);
  });
```

---

## ❌ Codes d'Erreur

| Code | Signification         | Description                              |
| ---- | --------------------- | ---------------------------------------- |
| 200  | OK                    | Requête réussie                          |
| 201  | Created               | Ressource créée                          |
| 204  | No Content            | Suppression réussie                      |
| 400  | Bad Request           | Données invalides                        |
| 404  | Not Found             | Ressource introuvable                    |
| 405  | Method Not Allowed    | Méthode HTTP incorrecte                  |
| 500  | Internal Server Error | Erreur serveur (ex: caméra inaccessible) |

**Format d'erreur standard** :

```json
{
  "status": "error",
  "message": "Description de l'erreur",
  "code": "ERROR_CODE",
  "details": {}
}
```

---

## 🔧 Exemples d'Intégration

### 1. Dashboard Temps Réel (React)

```jsx
import React, { useState, useEffect } from "react";

function DetectionDashboard() {
  const [status, setStatus] = useState({});
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Polling du statut toutes les 2s
    const interval = setInterval(() => {
      fetch("/api/status/")
        .then((r) => r.json())
        .then(setStatus);
    }, 2000);

    // Charger les événements
    fetch("/api/events/")
      .then((r) => r.json())
      .then((data) => setEvents(data.results));

    return () => clearInterval(interval);
  }, []);

  const startDetection = () => {
    fetch("/api/start/", { method: "POST" })
      .then((r) => r.json())
      .then((data) => alert(data.message));
  };

  return (
    <div>
      <h1>Argus Dashboard</h1>

      <div>
        <p>Status: {status.is_running ? "Actif" : "Inactif"}</p>
        <p>Visages: {status.faces_count}</p>
        <p>Mouvement: {status.motion_detected ? "Oui" : "Non"}</p>
        <button onClick={startDetection}>Démarrer</button>
      </div>

      <img src="/video_feed/" alt="Live Stream" />

      <ul>
        {events.map((event) => (
          <li key={event.id}>
            {event.detection_type} - {event.timestamp}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

### 2. Application Mobile (React Native)

```javascript
import React, { useState, useEffect } from "react";
import { View, Text, Image, Button, FlatList } from "react-native";

const API_BASE = "http://192.168.1.100:8000";

export default function App() {
  const [status, setStatus] = useState({});
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Rafraîchir le statut
    const interval = setInterval(async () => {
      const response = await fetch(`${API_BASE}/api/status/`);
      const data = await response.json();
      setStatus(data);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const loadEvents = async () => {
    const response = await fetch(`${API_BASE}/api/events/`);
    const data = await response.json();
    setEvents(data.results);
  };

  const toggleDetection = async () => {
    const endpoint = status.is_running ? "/api/stop/" : "/api/start/";
    await fetch(`${API_BASE}${endpoint}`, { method: "POST" });
    // Rafraîchir le statut
  };

  return (
    <View>
      <Text>Argus Mobile</Text>
      <Text>Status: {status.is_running ? "Actif" : "Inactif"}</Text>
      <Text>Visages: {status.faces_count}</Text>

      <Button
        title={status.is_running ? "Arrêter" : "Démarrer"}
        onPress={toggleDetection}
      />

      {/* Note: Le streaming MJPEG ne fonctionne pas bien en React Native */}
      {/* Utiliser plutôt un système de snapshots */}

      <Button title="Charger Événements" onPress={loadEvents} />

      <FlatList
        data={events}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View>
            <Text>{item.detection_type}</Text>
            <Text>{item.timestamp}</Text>
            <Image
              source={{ uri: `${API_BASE}${item.image_url}` }}
              style={{ width: 200, height: 150 }}
            />
          </View>
        )}
      />
    </View>
  );
}
```

---

### 3. Script Python pour Notifications

```python
import requests
import time
from datetime import datetime

API_BASE = 'http://localhost:8000'
TELEGRAM_BOT_TOKEN = 'votre-token'
TELEGRAM_CHAT_ID = 'votre-chat-id'

def send_telegram_notification(event):
    """Envoie une notification Telegram"""
    message = f"""
🚨 Détection Argus

Type: {event['detection_type']}
Heure: {event['timestamp']}
Visages: {event['faces_count']}
Intensité: {event['motion_intensity']:.2f}
    """

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    requests.post(url, data={
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    })

    # Envoyer l'image si disponible
    if event['image_url']:
        image_url = f"{API_BASE}{event['image_url']}"
        requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
            data={'chat_id': TELEGRAM_CHAT_ID},
            files={'photo': requests.get(image_url).content}
        )

def monitor_events():
    """Monitore les nouveaux événements"""
    last_event_id = 0

    while True:
        try:
            response = requests.get(f'{API_BASE}/api/events/?limit=10')
            events = response.json()['results']

            for event in events:
                if event['id'] > last_event_id:
                    print(f"Nouvel événement: {event['id']}")
                    send_telegram_notification(event)
                    last_event_id = event['id']

            time.sleep(5)  # Vérifier toutes les 5 secondes

        except Exception as e:
            print(f"Erreur: {e}")
            time.sleep(10)

if __name__ == '__main__':
    monitor_events()
```

---

### 4. Webhook Discord

```python
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK_URL = 'https://discord.com/api/webhooks/...'

def send_discord_alert(event):
    webhook = DiscordWebhook(url=WEBHOOK_URL)

    embed = DiscordEmbed(
        title='🎥 Détection Argus',
        description=f"Type: {event['detection_type']}",
        color='03b2f8'
    )

    embed.add_embed_field(name='Heure', value=event['timestamp'])
    embed.add_embed_field(name='Visages', value=str(event['faces_count']))
    embed.add_embed_field(name='Intensité', value=f"{event['motion_intensity']:.2%}")

    if event['image_url']:
        embed.set_image(url=f"http://localhost:8000{event['image_url']}")

    webhook.add_embed(embed)
    webhook.execute()

# Usage
response = requests.get('http://localhost:8000/api/events/?limit=1')
latest_event = response.json()['results'][0]
send_discord_alert(latest_event)
```

---

### 5. Export CSV

```python
import requests
import csv
from datetime import datetime

def export_events_to_csv(filename='events.csv'):
    """Exporte tous les événements en CSV"""
    all_events = []
    page = 1

    while True:
        response = requests.get(
            f'http://localhost:8000/api/events/?page={page}&limit=100'
        )
        data = response.json()
        all_events.extend(data['results'])

        if not data['next']:
            break
        page += 1

    # Écrire le CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'id', 'detection_type', 'timestamp', 'faces_count',
            'motion_intensity', 'confidence', 'location'
        ])
        writer.writeheader()
        writer.writerows(all_events)

    print(f"✓ {len(all_events)} événements exportés vers {filename}")

# Usage
export_events_to_csv()
```

---

### 6. Widget Web Autonome

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Argus Widget</title>
    <style>
      #argus-widget {
        width: 400px;
        padding: 20px;
        border: 2px solid #667eea;
        border-radius: 10px;
        font-family: Arial, sans-serif;
      }
      #argus-status {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
      }
      .status-active {
        color: #48bb78;
      }
      .status-inactive {
        color: #e53e3e;
      }
    </style>
  </head>
  <body>
    <div id="argus-widget">
      <h3>🎥 Argus Status</h3>
      <div id="argus-status">
        <span>Status: <strong id="status">...</strong></span>
        <span>Visages: <strong id="faces">0</strong></span>
      </div>
      <button onclick="toggleDetection()">Toggle</button>
    </div>

    <script>
      const API_BASE = "http://localhost:8000";
      let isRunning = false;

      async function updateStatus() {
        const response = await fetch(`${API_BASE}/api/status/`);
        const data = await response.json();

        isRunning = data.is_running;
        document.getElementById("status").innerText = isRunning
          ? "Actif"
          : "Inactif";
        document.getElementById("status").className = isRunning
          ? "status-active"
          : "status-inactive";
        document.getElementById("faces").innerText = data.faces_count;
      }

      async function toggleDetection() {
        const endpoint = isRunning ? "/api/stop/" : "/api/start/";
        await fetch(`${API_BASE}${endpoint}`, { method: "POST" });
        updateStatus();
      }

      // Update every 3 seconds
      setInterval(updateStatus, 3000);
      updateStatus();
    </script>
  </body>
</html>
```

---

## 🔐 Sécurisation de l'API (À Implémenter)

### Authentification par Token

```python
# À ajouter dans settings.py
INSTALLED_APPS += ['rest_framework', 'rest_framework.authtoken']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

```python
# Dans views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_detection(request):
    # ...
```

**Usage avec Token** :

```javascript
fetch("/api/start/", {
  method: "POST",
  headers: {
    Authorization: "Token votre-token-ici",
    "Content-Type": "application/json",
  },
});
```

---

Votre API est maintenant complètement documentée ! 📡✨
