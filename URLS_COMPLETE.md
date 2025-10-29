# 🌐 LISTE COMPLÈTE DES URLs - ARGUS

**Date:** 29 octobre 2025  
**Base URL:** `http://localhost:8000`

---

## 📋 URLs Principales

### 🏠 Page d'Accueil
```
GET  /                              - Page d'accueil
```

### 🔐 Authentication
```
GET   /auth/login/                  - Page de connexion
POST  /auth/login/                  - Soumettre connexion
GET   /auth/register/               - Page d'inscription
POST  /auth/register/               - Soumettre inscription
GET   /auth/logout/                 - Déconnexion
GET   /auth/dashboard/              - Dashboard utilisateur
```

### 🎥 Detection
```
GET   /detection/                   - Page de détection
POST  /detection/                   - Upload image pour détection
GET   /detection/history/           - Historique des détections
GET   /detection/result/<id>/       - Voir résultat de détection
POST  /detection/delete/<id>/       - Supprimer une détection
```

### 🎙️ VoiceControl
```
GET   /voicecontrol/demo/           - Démo contrôle vocal
POST  /voicecontrol/process/        - Traiter commande vocale
```

---

## 📊 Module Analytics

### Pages Web
```
GET   /analytics/                   - Dashboard analytics
GET   /analytics/trends/            - Page des tendances
GET   /analytics/alerts/            - Liste des alertes
GET   /analytics/alerts/<id>/       - Détail d'une alerte
POST  /analytics/alerts/<id>/acknowledge/  - Acquitter alerte
GET   /analytics/insights/          - Page des insights
GET   /analytics/report/            - Générer rapport
```

### APIs REST
```
GET   /analytics/api/stats/summary/           - Résumé statistiques
GET   /analytics/api/trends/                  - Liste tendances
      ?anomalies_only=true&limit=10
      
GET   /analytics/api/alerts/                  - Liste alertes
      ?severity=critical&unread_only=true&limit=20
      
POST  /analytics/api/alerts/<id>/acknowledge/ - Acquitter alerte

GET   /analytics/api/insights/                - Liste insights
      ?type=pattern&active_only=true
      
GET   /analytics/api/analytics/period/        - Analytics périodiques
      ?period=daily&days=7
      
GET   /analytics/api/charts/detections/       - Données graphiques
      ?days=7&period=daily
      
POST  /analytics/api/analytics/generate/      - Forcer génération
      Body: {"period": "daily"}
      
GET   /analytics/api/anomalies/detect/        - Détecter anomalies

GET   /analytics/api/health/                  - Health check
```

---

## 🔔 Module Notifications

### Pages Web
```
GET   /notifications/                         - Dashboard notifications
GET   /notifications/<id>/                    - Détail notification
POST  /notifications/mark-all-read/           - Tout marquer comme lu
GET   /notifications/preferences/             - Page préférences
POST  /notifications/preferences/             - Sauvegarder préférences
GET   /notifications/rules/                   - Liste des règles
POST  /notifications/rules/create/            - Créer règle
POST  /notifications/rules/<id>/toggle/       - Activer/désactiver règle
POST  /notifications/rules/<id>/delete/       - Supprimer règle
GET   /notifications/predictive/              - Alertes prédictives
```

### APIs REST
```
GET   /notifications/api/list/                - Liste notifications
      ?unread_only=true&limit=10&type=alert&severity=high
      
POST  /notifications/api/<id>/mark-read/      - Marquer comme lue

POST  /notifications/api/mark-all-read/       - Tout marquer comme lu

GET   /notifications/api/stats/               - Statistiques

GET   /notifications/api/<id>/logs/           - Historique notification

GET   /notifications/api/preferences/         - Récupérer préférences

POST  /notifications/api/preferences/update/  - Mettre à jour préférences
      Body: {
        "enabled_methods": ["web", "email"],
        "min_severity_email": "high",
        "quiet_hours_enabled": true
      }

GET   /notifications/api/rules/               - Liste règles
      ?active_only=true
      
POST  /notifications/api/rules/create/        - Créer règle
      Body: {
        "name": "Alerte Armes",
        "condition_type": "object_class",
        "condition_value": {"classes": ["knife", "gun"]},
        "action": "notify",
        "priority": 10
      }

POST  /notifications/api/rules/<id>/toggle/   - Activer/désactiver

DELETE /notifications/api/rules/<id>/delete/  - Supprimer règle

GET   /notifications/api/predictive/          - Alertes prédictives

POST  /notifications/api/test/                - Test notification
      Body: {"method": "email", "message": "Test"}

GET   /notifications/api/health/              - Health check
```

---

## 🛠️ Admin Django
```
GET   /admin/                                 - Interface admin
GET   /admin/analytics/detectionanalytics/    - Gestion analytics
GET   /admin/analytics/objecttrend/           - Gestion tendances
GET   /admin/analytics/securityalert/         - Gestion alertes
GET   /admin/analytics/analyticsinsight/      - Gestion insights
GET   /admin/notifications/notification/      - Gestion notifications
GET   /admin/notifications/notificationpreference/  - Gestion préférences
GET   /admin/notifications/notificationrule/  - Gestion règles
GET   /admin/notifications/predictivealert/   - Gestion alertes prédictives
```

---

## 📦 Médias
```
GET   /media/detections/original/<filename>   - Images originales
GET   /media/detections/annotated/<filename>  - Images annotées
GET   /media/faces/<filename>                 - Photos de profil
```

---

## 🎯 Exemples d'Utilisation

### 1. Workflow Complet de Détection
```bash
# 1. Se connecter
curl -c cookies.txt -X POST http://localhost:8000/auth/login/ \
  -d "username=admin&password=admin"

# 2. Uploader une image pour détection
curl -b cookies.txt -X POST http://localhost:8000/detection/ \
  -F "image=@test.jpg"

# 3. Vérifier les nouvelles alertes
curl -b cookies.txt http://localhost:8000/analytics/api/alerts/?unread_only=true

# 4. Voir les statistiques
curl -b cookies.txt http://localhost:8000/analytics/api/stats/summary/

# 5. Vérifier les notifications
curl -b cookies.txt http://localhost:8000/notifications/api/list/?unread_only=true
```

### 2. Configuration des Notifications
```javascript
// Récupérer les préférences actuelles
fetch('/notifications/api/preferences/')
    .then(res => res.json())
    .then(data => console.log(data.preferences));

// Mettre à jour les préférences
fetch('/notifications/api/preferences/update/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        enabled_methods: ['web', 'email'],
        min_severity_email: 'high',
        quiet_hours_enabled: true,
        quiet_hours_start: '22:00:00',
        quiet_hours_end: '08:00:00'
    })
});
```

### 3. Créer une Règle de Notification
```javascript
fetch('/notifications/api/rules/create/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        name: "Alerte Armes Détectées",
        description: "Notifier immédiatement si arme détectée",
        condition_type: "object_class",
        condition_value: {
            classes: ["knife", "gun", "rifle"]
        },
        action: "notify",
        action_parameters: {
            methods: ["web", "email", "sms"],
            priority: "critical"
        },
        priority: 10,
        is_active: true
    })
})
.then(res => res.json())
.then(data => console.log(`Règle créée: ID ${data.rule_id}`));
```

### 4. Dashboard Temps Réel
```javascript
// Mettre à jour le dashboard toutes les 30 secondes
setInterval(() => {
    // Stats globales
    fetch('/analytics/api/stats/summary/')
        .then(res => res.json())
        .then(data => {
            document.getElementById('total-detections').textContent = data.data.total_detections;
            document.getElementById('unread-alerts').textContent = data.data.alerts.unread;
        });
    
    // Nouvelles notifications
    fetch('/notifications/api/list/?unread_only=true&limit=5')
        .then(res => res.json())
        .then(data => {
            if (data.count > 0) {
                showNotificationBadge(data.count);
                data.data.forEach(notif => addToNotificationList(notif));
            }
        });
}, 30000);
```

### 5. Générer un Graphique
```javascript
// Récupérer données pour graphique
fetch('/analytics/api/charts/detections/?days=7')
    .then(res => res.json())
    .then(result => {
        const chartData = result.chart_data;
        
        // Créer graphique Chart.js
        new Chart(document.getElementById('myChart'), {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Détections',
                    data: chartData.datasets.detections,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }, {
                    label: 'Objets Détectés',
                    data: chartData.datasets.objects,
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }, {
                    label: 'Objets Suspects',
                    data: chartData.datasets.suspicious,
                    borderColor: 'rgb(255, 159, 64)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });
```

---

## 🔍 Paramètres de Requête Disponibles

### Analytics APIs

#### `/analytics/api/trends/`
- `anomalies_only` (bool): true/false
- `limit` (int): 1-200

#### `/analytics/api/alerts/`
- `severity` (string): low|medium|high|critical
- `unread_only` (bool): true/false
- `limit` (int): 1-200

#### `/analytics/api/insights/`
- `type` (string): pattern|prediction|recommendation|summary
- `active_only` (bool): true/false

#### `/analytics/api/analytics/period/`
- `period` (string): daily|weekly|monthly
- `days` (int): nombre de périodes

#### `/analytics/api/charts/detections/`
- `days` (int): 1-90
- `period` (string): daily|weekly

### Notifications APIs

#### `/notifications/api/list/`
- `unread_only` (bool): true/false
- `limit` (int): 1-200
- `type` (string): alert|insight|report|system
- `severity` (string): low|medium|high|critical

#### `/notifications/api/rules/`
- `active_only` (bool): true/false

---

## 📊 Codes de Statut HTTP

### Succès
- `200 OK` - Requête réussie
- `201 Created` - Ressource créée

### Erreurs Client
- `400 Bad Request` - Données invalides
- `401 Unauthorized` - Non authentifié
- `403 Forbidden` - Accès refusé
- `404 Not Found` - Ressource introuvable

### Erreurs Serveur
- `500 Internal Server Error` - Erreur serveur

---

## 🧪 Testing des URLs

### Avec cURL
```bash
# Test simple
curl http://localhost:8000/

# Test avec authentification
curl -c cookies.txt -X POST http://localhost:8000/auth/login/ \
  -d "username=admin&password=admin"

curl -b cookies.txt http://localhost:8000/analytics/api/stats/summary/

# Test POST avec JSON
curl -b cookies.txt -X POST \
  http://localhost:8000/notifications/api/test/ \
  -H "Content-Type: application/json" \
  -d '{"method": "web", "message": "Test"}'
```

### Avec Python
```python
import requests

session = requests.Session()
session.post('http://localhost:8000/auth/login/', data={
    'username': 'admin',
    'password': 'admin'
})

# Tester une URL
response = session.get('http://localhost:8000/analytics/api/stats/summary/')
print(response.json())
```

### Avec JavaScript
```javascript
// Fetch simple
fetch('/analytics/api/stats/summary/')
    .then(res => res.json())
    .then(data => console.log(data));

// POST avec données
fetch('/notifications/api/preferences/update/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        min_severity_email: 'high'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 📝 Notes Importantes

1. **Authentification requise** pour toutes les URLs sauf `/`, `/auth/login/`, `/auth/register/`
2. **Token CSRF requis** pour toutes les requêtes POST, PUT, DELETE
3. **Format JSON** pour toutes les APIs REST
4. **Pagination** automatique sur les listes (limit par défaut: 50)
5. **Timestamps** au format ISO 8601 (UTC)

---

**Total URLs:** 50+ endpoints disponibles  
**APIs REST:** 30+ endpoints  
**Pages Web:** 20+ pages  

✅ **Système complet et prêt à l'emploi !**
