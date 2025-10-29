# 📡 DOCUMENTATION API REST - ARGUS

**Version:** 1.0  
**Date:** 29 octobre 2025  
**Base URL:** `http://localhost:8000/`

---

## 🔐 Authentification

Toutes les APIs nécessitent une authentification. L'utilisateur doit être connecté via session Django.

**Headers requis:**
```http
Cookie: sessionid=<session_token>
Content-Type: application/json
```

---

## 📊 MODULE ANALYTICS

Base URL: `/analytics/api/`

### 1. Résumé des Statistiques

**GET** `/analytics/api/stats/summary/`

Retourne un aperçu global des statistiques.

**Réponse:**
```json
{
    "status": "success",
    "data": {
        "total_detections": 150,
        "total_objects": 420,
        "weekly_detections": 35,
        "alerts": {
            "total": 12,
            "unread": 3,
            "critical": 2,
            "high": 5
        },
        "top_objects": [
            {
                "object_class": "person",
                "detection_count": 89,
                "is_anomaly": false
            }
        ]
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 2. Liste des Tendances

**GET** `/analytics/api/trends/`

**Paramètres:**
- `anomalies_only` (bool): Afficher uniquement les anomalies (default: false)
- `limit` (int): Nombre de résultats (default: 50)

**Exemple:**
```http
GET /analytics/api/trends/?anomalies_only=true&limit=10
```

**Réponse:**
```json
{
    "status": "success",
    "count": 10,
    "data": [
        {
            "id": 5,
            "object_class": "knife",
            "detection_count": 15,
            "first_detected": "2025-10-15T10:30:00Z",
            "last_detected": "2025-10-29T16:45:00Z",
            "trend_direction": "increasing",
            "is_anomaly": true,
            "anomaly_score": 0.85
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 3. Liste des Alertes

**GET** `/analytics/api/alerts/`

**Paramètres:**
- `severity` (string): low|medium|high|critical
- `unread_only` (bool): Afficher uniquement non lues (default: false)
- `limit` (int): Nombre de résultats (default: 50)

**Exemple:**
```http
GET /analytics/api/alerts/?severity=critical&unread_only=true
```

**Réponse:**
```json
{
    "status": "success",
    "count": 2,
    "data": [
        {
            "id": 23,
            "alert_type": "suspicious_object",
            "severity": "critical",
            "title": "Détection d'arme",
            "message": "Un couteau a été détecté dans la zone surveillée",
            "is_read": false,
            "is_acknowledged": false,
            "created_at": "2025-10-29T16:45:00Z",
            "context_data": {
                "object_class": "knife",
                "confidence": 0.95,
                "location": "Entrée principale"
            }
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 4. Acquitter une Alerte

**POST** `/analytics/api/alerts/<alert_id>/acknowledge/`

**Exemple:**
```http
POST /analytics/api/alerts/23/acknowledge/
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Alerte acquittée avec succès",
    "alert_id": 23,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 5. Liste des Insights

**GET** `/analytics/api/insights/`

**Paramètres:**
- `type` (string): pattern|prediction|recommendation|summary
- `active_only` (bool): Afficher uniquement actifs (default: true)

**Réponse:**
```json
{
    "status": "success",
    "count": 5,
    "data": [
        {
            "id": 12,
            "insight_type": "pattern",
            "title": "Pic d'activité le soir",
            "description": "Les détections augmentent de 45% entre 18h et 20h",
            "confidence_score": 0.87,
            "is_active": true,
            "created_at": "2025-10-29T08:00:00Z",
            "data": {
                "peak_hours": [18, 19, 20],
                "increase_percentage": 45
            }
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 6. Analytics Périodiques

**GET** `/analytics/api/analytics/period/`

**Paramètres:**
- `period` (string): daily|weekly|monthly (default: daily)
- `days` (int): Nombre de périodes à récupérer (default: 7)

**Exemple:**
```http
GET /analytics/api/analytics/period/?period=daily&days=7
```

**Réponse:**
```json
{
    "status": "success",
    "period": "daily",
    "count": 7,
    "data": [
        {
            "id": 45,
            "period_type": "daily",
            "period_start": "2025-10-29T00:00:00Z",
            "period_end": "2025-10-29T23:59:59Z",
            "total_detections": 25,
            "total_objects_detected": 68,
            "avg_objects_per_detection": 2.72,
            "suspicious_objects_count": 3,
            "high_risk_detections": 1,
            "objects_by_class": {
                "person": 45,
                "car": 12,
                "bicycle": 8,
                "knife": 3
            },
            "detections_by_hour": {
                "8": 2,
                "9": 5,
                "10": 3,
                "18": 8,
                "19": 7
            }
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 7. Données pour Graphiques

**GET** `/analytics/api/charts/detections/`

**Paramètres:**
- `days` (int): Nombre de jours (default: 7)
- `period` (string): daily|weekly (default: daily)

**Réponse:**
```json
{
    "status": "success",
    "chart_data": {
        "labels": ["23/10", "24/10", "25/10", "26/10", "27/10", "28/10", "29/10"],
        "datasets": {
            "detections": [18, 22, 15, 28, 31, 19, 25],
            "objects": [45, 58, 39, 72, 85, 51, 68],
            "suspicious": [2, 1, 0, 3, 4, 1, 3]
        }
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

**Utilisation avec Chart.js:**
```javascript
fetch('/analytics/api/charts/detections/')
    .then(response => response.json())
    .then(result => {
        const chartData = result.chart_data;
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Détections',
                    data: chartData.datasets.detections
                }]
            }
        });
    });
```

---

### 8. Générer Analytics

**POST** `/analytics/api/analytics/generate/`

Force la génération des analytics pour une période.

**Body:**
```json
{
    "period": "daily"
}
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Analytics daily générées avec succès",
    "analytics": {
        "total_detections": 25,
        "total_objects": 68,
        "period_start": "2025-10-29T00:00:00Z",
        "period_end": "2025-10-29T23:59:59Z"
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 9. Détecter Anomalies

**GET** `/analytics/api/anomalies/detect/`

Met à jour et retourne les anomalies détectées.

**Réponse:**
```json
{
    "status": "success",
    "anomalies_count": 3,
    "data": [
        {
            "object_class": "knife",
            "detection_count": 15,
            "anomaly_score": 0.9,
            "trend_direction": "increasing",
            "last_detected": "2025-10-29T16:45:00Z"
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 10. Health Check

**GET** `/analytics/api/health/`

Vérifie l'état du module analytics.

**Réponse:**
```json
{
    "status": "healthy",
    "module": "analytics",
    "stats": {
        "analytics_count": 156,
        "trends_count": 42,
        "alerts_count": 28,
        "insights_count": 15,
        "unread_alerts": 5
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

## 🔔 MODULE NOTIFICATIONS

Base URL: `/notifications/api/`

### 1. Liste des Notifications

**GET** `/notifications/api/list/`

**Paramètres:**
- `unread_only` (bool): Non lues uniquement (default: false)
- `limit` (int): Nombre de résultats (default: 50)
- `type` (string): alert|insight|report|system
- `severity` (string): low|medium|high|critical

**Exemple:**
```http
GET /notifications/api/list/?unread_only=true&severity=high&limit=10
```

**Réponse:**
```json
{
    "status": "success",
    "count": 3,
    "data": [
        {
            "id": 45,
            "type": "alert",
            "title": "Alerte de sécurité",
            "message": "Détection d'activité suspecte",
            "severity": "high",
            "delivery_method": "web",
            "status": "sent",
            "is_read": false,
            "is_aggregated": false,
            "created_at": "2025-10-29T16:45:00Z",
            "read_at": null,
            "metadata": {
                "alert_id": 23,
                "location": "Zone A"
            }
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 2. Marquer comme Lue

**POST** `/notifications/api/<notification_id>/mark-read/`

**Exemple:**
```http
POST /notifications/api/45/mark-read/
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Notification marquée comme lue",
    "notification_id": 45,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 3. Tout Marquer comme Lu

**POST** `/notifications/api/mark-all-read/`

**Réponse:**
```json
{
    "status": "success",
    "message": "8 notification(s) marquée(s) comme lue(s)",
    "count": 8,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 4. Statistiques Notifications

**GET** `/notifications/api/stats/`

**Réponse:**
```json
{
    "status": "success",
    "stats": {
        "global": {
            "total": 145,
            "unread": 8,
            "by_severity_critical": 5,
            "by_severity_high": 18,
            "by_severity_medium": 67,
            "by_severity_low": 55,
            "sent": 140,
            "pending": 3,
            "failed": 2
        },
        "by_type": {
            "alert": 89,
            "insight": 23,
            "report": 15,
            "system": 18
        },
        "weekly_count": 42
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 5. Obtenir Préférences

**GET** `/notifications/api/preferences/`

**Réponse:**
```json
{
    "status": "success",
    "preferences": {
        "enabled_methods": ["web", "email"],
        "min_severity_web": "low",
        "min_severity_email": "high",
        "min_severity_sms": "critical",
        "quiet_hours_enabled": true,
        "quiet_hours_start": "22:00:00",
        "quiet_hours_end": "08:00:00",
        "enable_aggregation": true,
        "aggregation_window_minutes": 30,
        "max_notifications_per_hour": 10,
        "notify_suspicious_objects": true,
        "notify_anomalies": true,
        "notify_high_frequency": true,
        "notify_unusual_time": false
    },
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 6. Mettre à Jour Préférences

**POST** `/notifications/api/preferences/update/`

**Body:**
```json
{
    "enabled_methods": ["web", "email", "sms"],
    "min_severity_email": "medium",
    "quiet_hours_enabled": true,
    "max_notifications_per_hour": 15
}
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Préférences mises à jour avec succès",
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 7. Liste des Règles

**GET** `/notifications/api/rules/`

**Paramètres:**
- `active_only` (bool): Règles actives uniquement (default: false)

**Réponse:**
```json
{
    "status": "success",
    "count": 4,
    "data": [
        {
            "id": 7,
            "name": "Alerte Armes",
            "description": "Notifier immédiatement pour armes détectées",
            "condition_type": "object_class",
            "condition_value": {
                "classes": ["knife", "gun", "rifle"]
            },
            "action": "notify",
            "action_parameters": {
                "priority": "critical",
                "methods": ["web", "email", "sms"]
            },
            "is_active": true,
            "priority": 10,
            "created_at": "2025-10-20T10:00:00Z"
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 8. Créer une Règle

**POST** `/notifications/api/rules/create/`

**Body:**
```json
{
    "name": "Alerte Incendie",
    "description": "Notifier pour détection de feu ou fumée",
    "condition_type": "object_class",
    "condition_value": {
        "classes": ["fire", "smoke"]
    },
    "action": "notify",
    "action_parameters": {
        "methods": ["web", "email", "sms"]
    },
    "priority": 10,
    "is_active": true
}
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Règle créée avec succès",
    "rule_id": 8,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 9. Basculer Règle (Activer/Désactiver)

**POST** `/notifications/api/rules/<rule_id>/toggle/`

**Exemple:**
```http
POST /notifications/api/rules/7/toggle/
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Règle désactivée",
    "rule_id": 7,
    "is_active": false,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 10. Supprimer une Règle

**DELETE** `/notifications/api/rules/<rule_id>/delete/`

**Exemple:**
```http
DELETE /notifications/api/rules/7/delete/
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Règle supprimée avec succès",
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 11. Alertes Prédictives

**GET** `/notifications/api/predictive/`

Génère et retourne les alertes prédictives.

**Réponse:**
```json
{
    "status": "success",
    "count": 2,
    "predictions": [
        {
            "id": 5,
            "prediction_type": "trend",
            "title": "Augmentation prévue des détections",
            "description": "Basé sur les tendances, une augmentation de 30% est prévue",
            "predicted_event": "trend_increase_knife",
            "confidence_score": 0.78,
            "timeframe_start": "2025-10-30T00:00:00Z",
            "timeframe_end": "2025-11-06T23:59:59Z",
            "recommendations": "Renforcer la surveillance dans les zones à risque",
            "supporting_data": {
                "current_trend": "increasing",
                "detection_count": 15,
                "increase_rate": 0.3
            },
            "is_active": true
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 12. Test de Notification

**POST** `/notifications/api/test/`

Envoie une notification de test.

**Body:**
```json
{
    "method": "email",
    "message": "Ceci est un test d'email"
}
```

**Réponse:**
```json
{
    "status": "success",
    "message": "Notification de test envoyée via email",
    "notification_id": 146,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 13. Historique d'une Notification

**GET** `/notifications/api/<notification_id>/logs/`

**Exemple:**
```http
GET /notifications/api/45/logs/
```

**Réponse:**
```json
{
    "status": "success",
    "notification_id": 45,
    "logs": [
        {
            "event": "created",
            "details": "Notification créée à partir de SecurityAlert #23",
            "timestamp": "2025-10-29T16:45:00Z"
        },
        {
            "event": "sent",
            "details": "Envoyée via web",
            "timestamp": "2025-10-29T16:45:02Z"
        },
        {
            "event": "marked_read",
            "details": "Notification marquée comme lue via API",
            "timestamp": "2025-10-29T17:30:00Z"
        }
    ],
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

### 14. Health Check

**GET** `/notifications/api/health/`

**Réponse:**
```json
{
    "status": "healthy",
    "module": "notifications",
    "stats": {
        "notifications_count": 145,
        "unread_count": 8,
        "rules_count": 4,
        "active_rules_count": 3,
        "predictive_alerts_count": 2
    },
    "has_preferences": true,
    "timestamp": "2025-10-29T17:30:00Z"
}
```

---

## 🔍 Exemples d'Utilisation

### JavaScript (Fetch API)

```javascript
// Récupérer les alertes critiques
async function getCriticalAlerts() {
    const response = await fetch('/analytics/api/alerts/?severity=critical&unread_only=true');
    const data = await response.json();
    
    if (data.status === 'success') {
        data.data.forEach(alert => {
            console.log(`Alerte: ${alert.title}`);
        });
    }
}

// Marquer toutes les notifications comme lues
async function markAllRead() {
    const response = await fetch('/notifications/api/mark-all-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    
    const data = await response.json();
    console.log(data.message);
}

// Créer une règle de notification
async function createRule() {
    const ruleData = {
        name: "Alerte Personnes",
        condition_type: "detection_count",
        condition_value: { threshold: 10 },
        action: "notify",
        priority: 5
    };
    
    const response = await fetch('/notifications/api/rules/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(ruleData)
    });
    
    const result = await response.json();
    console.log(`Règle créée: ID ${result.rule_id}`);
}
```

### Python (Requests)

```python
import requests

# Base URL
BASE_URL = 'http://localhost:8000'

# Session avec authentification
session = requests.Session()
session.post(f'{BASE_URL}/auth/login/', data={
    'username': 'user',
    'password': 'password'
})

# Récupérer les statistiques
response = session.get(f'{BASE_URL}/analytics/api/stats/summary/')
stats = response.json()
print(f"Total détections: {stats['data']['total_detections']}")

# Créer une notification de test
response = session.post(
    f'{BASE_URL}/notifications/api/test/',
    json={'method': 'email', 'message': 'Test'}
)
result = response.json()
print(result['message'])
```

### cURL

```bash
# Récupérer les tendances d'anomalies
curl -X GET "http://localhost:8000/analytics/api/trends/?anomalies_only=true" \
  -H "Cookie: sessionid=<your_session_id>"

# Acquitter une alerte
curl -X POST "http://localhost:8000/analytics/api/alerts/23/acknowledge/" \
  -H "Cookie: sessionid=<your_session_id>" \
  -H "Content-Type: application/json"

# Mettre à jour les préférences
curl -X POST "http://localhost:8000/notifications/api/preferences/update/" \
  -H "Cookie: sessionid=<your_session_id>" \
  -H "Content-Type: application/json" \
  -d '{"min_severity_email": "high", "max_notifications_per_hour": 20}'
```

---

## ⚠️ Gestion des Erreurs

Toutes les APIs retournent un format cohérent pour les erreurs :

**Erreur 404 (Not Found):**
```json
{
    "status": "error",
    "message": "Alerte non trouvée"
}
```

**Erreur 400 (Bad Request):**
```json
{
    "status": "error",
    "message": "Données invalides: le champ 'name' est requis"
}
```

**Erreur 401 (Unauthorized):**
```json
{
    "status": "error",
    "message": "Authentification requise"
}
```

---

## 📈 Limites et Rate Limiting

- **Limite par défaut:** 50 résultats par requête
- **Maximum:** 200 résultats par requête
- **Rate limiting:** Pas encore implémenté (à venir)

---

**🎯 API complète et prête à l'emploi !**
