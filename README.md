# 🎥 Argus - Système de Détection de Mouvement et de Visages

## Description

Argus est un système complet de détection de mouvement et de visages pour Django 4.2, 100% local et gratuit. Il utilise OpenCV pour la détection en temps réel via la caméra du laptop.

## Fonctionnalités

### ✅ Détection en Temps Réel

- **Détection de mouvement** : Analyse les différences entre les frames pour détecter les mouvements
- **Détection de visages** : Utilise Haar Cascade (inclus avec OpenCV) pour détecter les visages
- **Streaming vidéo** : Affichage en temps réel du flux de la caméra avec annotations

### 📊 Gestion des Événements

- Enregistrement automatique des détections dans la base de données
- Sauvegarde optionnelle des images capturées
- Historique complet avec filtres et pagination
- Statistiques détaillées des détections

### ⚙️ Configuration

- Interface web pour configurer les paramètres de détection
- Ajustement de la sensibilité du mouvement
- Activation/désactivation indépendante des détections
- Configuration de l'intervalle d'enregistrement

## Technologies Utilisées

- **Django 4.2** : Framework web Python
- **OpenCV 4.12** : Bibliothèque de vision par ordinateur
- **NumPy 2.2** : Calculs numériques
- **Pillow 11.3** : Traitement d'images
- **SQLite** : Base de données (par défaut)

## Installation et Configuration

### 1. Prérequis

- Python 3.11+
- Caméra fonctionnelle (webcam intégrée ou externe)

### 2. Installation des dépendances

Les dépendances sont déjà installées dans votre environnement virtuel. Sinon :

```bash
pip install -r requirements.txt
```

### 3. Migrations de la base de données

```bash
cd d:\hamza\5TWIN2K25\Django\argus
python manage.py makemigrations
python manage.py migrate
```

### 4. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 5. Lancer le serveur

```bash
python manage.py runserver
```

## Utilisation

### Accès à l'application

- **Page principale** : http://127.0.0.1:8000/
- **Admin Django** : http://127.0.0.1:8000/admin/
- **Historique** : http://127.0.0.1:8000/events/
- **Statistiques** : http://127.0.0.1:8000/statistics/
- **Paramètres** : http://127.0.0.1:8000/settings/

### Démarrage de la Détection

1. Accédez à la page principale
2. Cliquez sur "▶️ Démarrer la Détection"
3. Autorisez l'accès à la caméra si demandé
4. Le flux vidéo apparaît avec les détections en temps réel

### Configuration des Paramètres

1. Allez dans **Paramètres**
2. Ajustez les paramètres selon vos besoins :
   - **Index de la caméra** : 0 pour la caméra par défaut
   - **Seuil de mouvement** : Plus bas = plus sensible
   - **Surface minimale** : Ignorer les petits mouvements
   - **Intervalle de détection** : Temps entre deux enregistrements

## Structure du Projet

```
argus/
├── argus/                          # Configuration Django
│   ├── settings.py                 # Paramètres du projet
│   ├── urls.py                     # URLs principales
│   └── wsgi.py
├── detection/                      # Application de détection
│   ├── models.py                   # Modèles de données
│   ├── views.py                    # Vues Django
│   ├── urls.py                     # URLs de l'application
│   ├── admin.py                    # Interface admin
│   ├── detector.py                 # Logique de détection OpenCV
│   └── templates/detection/        # Templates HTML
│       ├── base.html
│       ├── index.html              # Page principale
│       ├── events_list.html        # Historique
│       ├── statistics.html         # Statistiques
│       └── settings.html           # Configuration
├── media/                          # Images capturées
│   └── detections/
├── manage.py
└── requirements.txt
```

## API Endpoints

### Contrôle de la Détection

- `POST /api/start/` - Démarrer la détection
- `POST /api/stop/` - Arrêter la détection
- `GET /api/status/` - Obtenir le statut actuel
- `POST /api/settings/` - Mettre à jour les paramètres

### Données

- `GET /api/events/` - Liste des événements (JSON)
- `GET /video_feed/` - Streaming vidéo en temps réel

## Modèles de Données

### DetectionEvent

Enregistre chaque événement de détection :

- Type de détection (mouvement, visage, ou les deux)
- Timestamp
- Nombre de visages détectés
- Intensité du mouvement
- Image capturée (optionnel)

### CameraSettings

Stocke les paramètres de configuration :

- Index de la caméra
- Activation des détections
- Seuils et sensibilité
- Options d'enregistrement

## Personnalisation

### Ajuster la Détection de Mouvement

Dans `detection/detector.py`, modifiez :

- `motion_threshold` : Sensibilité de détection (5-50)
- `min_contour_area` : Taille minimale des objets (100-5000)

### Améliorer la Détection de Visages

Vous pouvez utiliser d'autres cascades Haar :

```python
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
```

## Sécurité

⚠️ **Important pour la production** :

- Changez `SECRET_KEY` dans `settings.py`
- Mettez `DEBUG = False`
- Configurez `ALLOWED_HOSTS`
- Utilisez une base de données comme PostgreSQL
- Ajoutez l'authentification pour les vues sensibles

## Dépannage

### La caméra ne fonctionne pas

- Vérifiez que la caméra n'est pas utilisée par une autre application
- Essayez de changer `camera_index` (0, 1, 2...)
- Vérifiez les permissions de la caméra dans Windows

### Erreur "Module not found"

```bash
pip install -r requirements.txt
```

### Problèmes de performance

- Réduisez la résolution de la caméra dans `detector.py`
- Augmentez `detection_interval`
- Désactivez la sauvegarde d'images si non nécessaire

## Évolutions Futures

- [ ] Authentification et autorisation
- [ ] Frontend React
- [ ] Notifications en temps réel (WebSocket)
- [ ] Reconnaissance faciale avancée
- [ ] Support multi-caméras
- [ ] Export des données en CSV/JSON
- [ ] Détection d'objets spécifiques
- [ ] Zones d'intérêt configurables

## Licence

Ce projet est 100% gratuit et utilise uniquement des technologies open-source.

## Support

Pour toute question ou problème, consultez la documentation OpenCV : https://docs.opencv.org/

---

Développé avec ❤️ pour Django 4.2 et Python 3.11+
