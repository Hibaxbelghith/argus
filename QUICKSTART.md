# 🚀 Guide de Démarrage Rapide - Modules Analytics & Notifications

## ✅ Checklist d'Installation

### 1. Vérifier l'environnement Python

```powershell
python --version  # Doit être Python 3.11
```

### 2. Créer et exécuter les migrations

```powershell
# Créer les migrations pour les nouveaux modules
python manage.py makemigrations analytics
python manage.py makemigrations notifications

# Appliquer toutes les migrations
python manage.py migrate
```

### 3. Créer un superutilisateur (si pas déjà fait)

```powershell
python manage.py createsuperuser
# Entrez: username, email, password
```

### 4. Lancer le serveur de développement

```powershell
python manage.py runserver
```

---

## 🎯 Test des Modules

### Étape 1: Connexion
1. Aller sur `http://127.0.0.1:8000/auth/login/`
2. Se connecter avec votre compte

### Étape 2: Tester le Module de Détection
1. Aller sur `http://127.0.0.1:8000/detection/`
2. Uploader une image (exemple: photo avec des objets)
3. Le système va détecter les objets automatiquement

### Étape 3: Vérifier les Analytics
1. Aller sur `http://127.0.0.1:8000/analytics/`
2. Vous devriez voir:
   - Statistiques générales (nombre de détections, objets)
   - Graphiques de tendances
   - Top objets détectés
   - Insights générés automatiquement

### Étape 4: Consulter les Alertes
1. Aller sur `http://127.0.0.1:8000/analytics/alerts/`
2. Si votre image contenait des objets suspects, vous verrez des alertes

### Étape 5: Configurer les Notifications
1. Aller sur `http://127.0.0.1:8000/notifications/preferences/`
2. Configurer:
   - Canaux activés (web, email)
   - Sévérité minimale par canal
   - Heures silencieuses (optionnel)
   - Types d'alertes à recevoir

### Étape 6: Voir les Notifications
1. Aller sur `http://127.0.0.1:8000/notifications/`
2. Vous verrez les notifications créées depuis les alertes

### Étape 7: Alertes Prédictives
1. Après plusieurs détections, aller sur `http://127.0.0.1:8000/notifications/predictive/`
2. Vous verrez:
   - Évaluation du risque de sécurité
   - Prédictions de tendances
   - Forecast d'anomalies

---

## 📊 URLs Principales

| URL | Description |
|-----|-------------|
| `/analytics/` | Dashboard analytics principal |
| `/analytics/trends/` | Tendances d'objets détectés |
| `/analytics/alerts/` | Alertes de sécurité |
| `/analytics/insights/` | Insights IA |
| `/analytics/report/?period=weekly` | Rapport hebdomadaire |
| `/notifications/` | Dashboard notifications |
| `/notifications/preferences/` | Préférences de notifications |
| `/notifications/predictive/` | Alertes prédictives |
| `/admin/` | Interface d'administration Django |

---

## 🔧 Configuration Email (Optionnel)

Pour activer l'envoi d'emails, ajoutez dans `argus/settings.py`:

```python
# Configuration Gmail (exemple)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'  # Utiliser un mot de passe d'application
DEFAULT_FROM_EMAIL = 'Argus Security <noreply@argus.com>'

# Pour Gmail, créer un "App Password":
# https://myaccount.google.com/apppasswords
```

**Mode Console (pour tests sans SMTP):**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 🎨 Workflow Automatique

```
1. Upload Image → Détection d'objets (YOLOv5)
   ↓
2. Signal Django déclenché
   ↓
3. Analytics Module:
   - Génère statistiques quotidiennes
   - Met à jour tendances d'objets
   - Détecte anomalies
   - Crée SecurityAlert si nécessaire
   ↓
4. Notifications Module:
   - Reçoit SecurityAlert via signal
   - Applique préférences utilisateur
   - Filtre par sévérité/canal/horaire
   - Applique règles personnalisées
   - Crée Notification
   - Envoie (web/email/sms)
```

---

## 🧪 Exemples de Tests

### Test 1: Objet Normal
- Uploader une image avec des objets communs (personne, chaise, téléphone)
- Résultat attendu: Analytics OK, pas d'alerte critique

### Test 2: Objet Suspect
- Uploader une image contenant un couteau (ou taper "knife" dans la recherche d'images)
- Résultat attendu: Alerte "suspicious_object" créée, notification envoyée

### Test 3: Haute Fréquence
- Uploader 10+ images en peu de temps
- Résultat attendu: Alerte "high_frequency" créée

### Test 4: Heure Inhabituelle
- Modifier l'heure système à 3h du matin, uploader une image
- Résultat attendu: Alerte "unusual_time" créée

---

## 📱 Interface Admin Django

Accédez à `/admin/` pour gérer:

### Analytics
- `DetectionAnalytics`: Voir toutes les analytics générées
- `ObjectTrend`: Voir tendances par objet
- `SecurityAlert`: Gérer alertes de sécurité
- `AnalyticsInsight`: Voir insights IA

### Notifications
- `Notification`: Toutes les notifications envoyées
- `NotificationPreference`: Préférences utilisateurs
- `NotificationRule`: Règles personnalisées
- `PredictiveAlert`: Prédictions générées

---

## 🐛 Dépannage

### Problème: Migrations ne fonctionnent pas
```powershell
python manage.py makemigrations analytics --empty
python manage.py makemigrations notifications --empty
python manage.py migrate --run-syncdb
```

### Problème: Signaux ne se déclenchent pas
Vérifiez dans `analytics/apps.py` et `notifications/apps.py`:
```python
def ready(self):
    import analytics.signals  # ou notifications.signals
```

### Problème: Templates non trouvés
Vérifiez `settings.py`:
```python
TEMPLATES = [
    {
        ...
        'APP_DIRS': True,  # Doit être True
        ...
    },
]
```

### Problème: Pas d'analytics générées
Exécutez manuellement:
```python
python manage.py shell

from django.contrib.auth import get_user_model
from analytics.services import AnalyticsEngine

User = get_user_model()
user = User.objects.first()

# Générer analytics
analytics = AnalyticsEngine.generate_period_analytics(user, 'daily')
print(analytics)
```

---

## 📈 Utilisation Avancée

### Créer une Règle Personnalisée

1. Aller sur `/notifications/rules/`
2. Créer une nouvelle règle
3. Exemple: "Supprimer notifications pour 'person' entre 8h-18h"

### Générer un Rapport

1. `/analytics/report/?period=daily` - Rapport journalier
2. `/analytics/report/?period=weekly` - Rapport hebdomadaire
3. `/analytics/report/?period=monthly` - Rapport mensuel

### API JSON pour Graphiques

```javascript
fetch('/analytics/api/data/?period=daily')
    .then(response => response.json())
    .then(data => {
        console.log(data.labels);      // Dates
        console.log(data.detections);  // Nombre détections
        console.log(data.objects);     // Nombre objets
        console.log(data.suspicious);  // Objets suspects
    });
```

---

## ✨ Fonctionnalités Clés

### Analytics
- ✅ Statistiques en temps réel
- ✅ Détection d'anomalies automatique
- ✅ Insights IA générés
- ✅ Graphiques interactifs
- ✅ Rapports imprimables

### Notifications
- ✅ Multi-canal (web/email/sms/push)
- ✅ Filtrage intelligent
- ✅ Agrégation automatique
- ✅ Heures silencieuses
- ✅ Règles personnalisables
- ✅ Alertes prédictives

---

## 📚 Documentation Complète

Voir `MODULES_README.md` pour la documentation technique complète.

---

## 💡 Conseils

1. **Premier Usage**: Faites plusieurs détections pour générer des données
2. **Analytics**: Les tendances deviennent pertinentes après 5-10 détections
3. **Prédictions**: Nécessitent au moins 3-5 jours de données
4. **Email**: Testez d'abord avec `console.EmailBackend`
5. **Production**: Changez `SECRET_KEY` et `DEBUG=False`

---

**Bon développement avec Argus ! 🛡️**
