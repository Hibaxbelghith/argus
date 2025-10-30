# 🚀 Guide de Déploiement Argus

Ce guide vous montre comment déployer votre système Argus en production.

---

## ⚠️ IMPORTANT : Limitations du Système

Avant de déployer, comprenez les contraintes :

### 🎥 Accès à la Caméra

- **Développement local** : ✅ Fonctionne (accès direct à la webcam)
- **Serveur distant** : ❌ Ne peut pas accéder à VOTRE caméra locale
- **Serveur avec caméra** : ✅ Fonctionne (caméra connectée au serveur)

### 💡 Solutions

1. **Raspberry Pi** : Idéal pour surveillance locale avec caméra USB/Pi Camera
2. **Ordinateur dédié** : Utilisez un laptop/PC comme serveur de surveillance
3. **Architecture distribuée** : Agents locaux + serveur central (voir section avancée)

---

## 🏠 Option 1 : Déploiement Local (Recommandé)

### Scénario : Bureau, Maison, Petit Commerce

**Avantages** :

- ✅ Accès direct à la caméra
- ✅ Pas de latence réseau
- ✅ Données restent privées
- ✅ Gratuit (pas d'hébergement)

**Configuration** :

```powershell
# 1. Installer comme service Windows
# Créer un fichier: argus_service.bat

@echo off
cd /d "d:\hamza\5TWIN2K25\Django\argus"
call "..\env\Scripts\activate.bat"
python manage.py runserver 0.0.0.0:8000
```

```powershell
# 2. Accès depuis d'autres appareils du réseau local
# Trouver votre IP locale:
ipconfig

# Exemple: 192.168.1.100
# Accès depuis autre PC/téléphone: http://192.168.1.100:8000
```

**Utiliser NSSM pour créer un vrai service Windows** :

```powershell
# Télécharger NSSM: https://nssm.cc/download
# Installer le service:
nssm install ArgusDetection "d:\hamza\5TWIN2K25\Django\env\Scripts\python.exe"
nssm set ArgusDetection AppDirectory "d:\hamza\5TWIN2K25\Django\argus"
nssm set ArgusDetection AppParameters "manage.py runserver 0.0.0.0:8000"

# Démarrer le service
nssm start ArgusDetection

# Le service démarre automatiquement au boot !
```

---

## 🌐 Option 2 : Déploiement Web (Sans Caméra)

### Scénario : Gestion centralisée, API seulement

Si vous voulez juste l'interface web (sans streaming caméra actif).

### A. Hébergement sur PythonAnywhere (Gratuit)

```bash
# 1. Créer compte sur pythonanywhere.com
# 2. Ouvrir bash console

# 3. Cloner votre projet
git clone https://github.com/votre-username/argus.git

# 4. Créer environnement virtuel
mkvirtualenv argus --python=/usr/bin/python3.10

# 5. Installer dépendances (sans OpenCV si pas de caméra)
pip install django pillow

# 6. Configurer settings.py
nano argus/settings.py
# Modifier:
DEBUG = False
ALLOWED_HOSTS = ['votre-username.pythonanywhere.com']
SECRET_KEY = 'nouvelle-cle-secrete-unique'

# 7. Base de données
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# 8. Configurer Web App dans le dashboard PythonAnywhere
# - Source code: /home/votre-username/argus
# - Working directory: /home/votre-username/argus
# - WSGI file: modifier pour pointer vers argus.wsgi
```

**Note** : PythonAnywhere gratuit ne permet pas OpenCV/caméra. Seulement gestion des données.

### B. Hébergement sur Heroku

```bash
# 1. Installer Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Créer fichier Procfile
echo "web: gunicorn argus.wsgi" > Procfile

# 3. Créer runtime.txt
echo "python-3.11.0" > runtime.txt

# 4. Installer gunicorn
pip install gunicorn
pip freeze > requirements.txt

# 5. Créer app Heroku
heroku create argus-detection

# 6. Configurer variables d'environnement
heroku config:set DEBUG=False
heroku config:set SECRET_KEY='votre-cle-secrete'

# 7. Déployer
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 8. Migrer la base de données
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

**Note** : Heroku gratuit ne supporte pas les caméras non plus.

---

## 🍓 Option 3 : Raspberry Pi (Idéal pour Surveillance)

### Configuration Complète avec Caméra

**Matériel requis** :

- Raspberry Pi 4 (2GB minimum, 4GB recommandé)
- Carte SD 32GB+
- Caméra USB ou Pi Camera Module
- Alimentation 5V/3A

**Installation** :

```bash
# 1. Installer Raspberry Pi OS (64-bit)
# Utiliser Raspberry Pi Imager

# 2. Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# 3. Installer Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# 4. Installer dépendances système pour OpenCV
sudo apt install -y \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp7 \
    libtiff5 \
    libjasper-dev \
    libilmbase25 \
    libopenexr25 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libqtgui4 \
    libqt4-test

# 5. Cloner votre projet
cd /home/pi
git clone https://github.com/votre-username/argus.git
cd argus

# 6. Créer environnement virtuel
python3.11 -m venv env
source env/bin/activate

# 7. Installer dépendances
pip install django pillow numpy
pip install opencv-python  # Version allégée pour Pi

# 8. Configuration
nano argus/settings.py
# Modifier:
ALLOWED_HOSTS = ['*']  # ou votre IP locale
DEBUG = False

# 9. Migrer la base de données
python manage.py migrate
python manage.py createsuperuser

# 10. Tester la caméra
python -c "import cv2; print(cv2.VideoCapture(0).read())"

# 11. Créer service systemd
sudo nano /etc/systemd/system/argus.service
```

**Contenu de `/etc/systemd/system/argus.service`** :

```ini
[Unit]
Description=Argus Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/argus
Environment="PATH=/home/pi/argus/env/bin"
ExecStart=/home/pi/argus/env/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 12. Activer et démarrer le service
sudo systemctl enable argus
sudo systemctl start argus

# 13. Vérifier le statut
sudo systemctl status argus

# 14. Voir les logs
sudo journalctl -u argus -f
```

**Accès depuis le réseau local** :

```
http://[IP-DU-PI]:8000

# Exemple: http://192.168.1.150:8000
```

---

## 🔒 Sécurité en Production

### 1. Modifier `settings.py`

```python
# argus/settings.py

# SÉCURITÉ
DEBUG = False  # JAMAIS True en production !

SECRET_KEY = os.environ.get('SECRET_KEY', 'changez-moi-en-production')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',  # Votre IP locale
    'argus.votre-domaine.com',  # Si vous avez un domaine
]

# HTTPS (si vous utilisez un certificat SSL)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Base de données (PostgreSQL recommandé en prod)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Fichiers statiques
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### 2. Variables d'Environnement

```bash
# Créer fichier .env
nano .env
```

```env
SECRET_KEY=votre-cle-super-secrete-unique-a-generer
DEBUG=False
DB_NAME=argus_db
DB_USER=argus_user
DB_PASSWORD=mot-de-passe-fort
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100
```

```python
# Charger les variables (installer python-decouple)
# pip install python-decouple

from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 3. Authentification (Ajout Recommandé)

```python
# argus/settings.py

MIDDLEWARE = [
    # ... autres middlewares
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
```

```python
# detection/views.py
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # ...
```

---

## 🌍 Option 4 : Architecture Distribuée (Avancé)

### Scénario : Plusieurs Caméras + Serveur Central

**Architecture** :

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Agent 1    │     │  Agent 2    │     │  Agent 3    │
│  (Caméra 1) │     │  (Caméra 2) │     │  (Caméra 3) │
│  Raspberry  │     │  PC Bureau  │     │  Laptop     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ API POST
                    ┌──────▼──────┐
                    │  Serveur    │
                    │  Central    │
                    │  (Django)   │
                    └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Base de    │
                    │  Données    │
                    └─────────────┘
```

**Agent Local (agent.py)** :

```python
# agent.py - À exécuter sur chaque machine avec caméra
import cv2
import requests
import time
from datetime import datetime

SERVER_URL = "http://192.168.1.100:8000/api/detection"
API_KEY = "votre-cle-api-secrete"
CAMERA_NAME = "Bureau Principal"

def detect_and_send():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Détection locale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Motion
        motion_detected = False
        if prev_frame is not None:
            frame_diff = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
            motion_detected = cv2.countNonZero(thresh) > 500

        # Faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        # Envoyer au serveur si détection
        if motion_detected or len(faces) > 0:
            _, buffer = cv2.imencode('.jpg', frame)

            data = {
                'camera_name': CAMERA_NAME,
                'timestamp': datetime.now().isoformat(),
                'motion_detected': motion_detected,
                'faces_count': len(faces),
            }

            files = {'image': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}

            try:
                response = requests.post(
                    SERVER_URL,
                    data=data,
                    files=files,
                    headers={'Authorization': f'Bearer {API_KEY}'}
                )
                print(f"✓ Envoyé: {response.status_code}")
            except Exception as e:
                print(f"✗ Erreur: {e}")

        prev_frame = gray
        time.sleep(1)  # 1 détection par seconde

    cap.release()

if __name__ == "__main__":
    detect_and_send()
```

**Serveur Central - Nouvelle API** :

```python
# detection/views.py
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def receive_detection(request):
    """Receive detection from remote agents"""
    camera_name = request.POST.get('camera_name')
    motion_detected = request.POST.get('motion_detected') == 'True'
    faces_count = int(request.POST.get('faces_count', 0))
    image = request.FILES.get('image')

    # Déterminer le type
    if motion_detected and faces_count > 0:
        detection_type = 'both'
    elif faces_count > 0:
        detection_type = 'face'
    else:
        detection_type = 'motion'

    # Sauvegarder
    event = DetectionEvent.objects.create(
        detection_type=detection_type,
        faces_count=faces_count,
        image=image,
        location=camera_name,
    )

    return Response({
        'status': 'success',
        'event_id': event.id
    })
```

---

## 🔧 Nginx + Gunicorn (Production Linux)

### Configuration Complète

```bash
# 1. Installer dépendances
sudo apt install nginx postgresql

# 2. Installer Gunicorn
pip install gunicorn

# 3. Tester Gunicorn
gunicorn argus.wsgi:application --bind 0.0.0.0:8000

# 4. Créer socket systemd
sudo nano /etc/systemd/system/gunicorn.socket
```

**gunicorn.socket** :

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

**gunicorn.service** :

```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/argus
Environment="PATH=/var/www/argus/env/bin"
ExecStart=/var/www/argus/env/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          argus.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Activer
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

**Nginx Configuration** :

```bash
sudo nano /etc/nginx/sites-available/argus
```

```nginx
server {
    listen 80;
    server_name argus.example.com;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/argus/staticfiles/;
    }

    location /media/ {
        alias /var/www/argus/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;

        # Pour le streaming vidéo
        proxy_buffering off;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/argus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Monitoring

### Logs

```bash
# Systemd service logs
sudo journalctl -u argus -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logs (configurer dans settings.py)
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/argus/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## ✅ Checklist de Déploiement

### Avant de Déployer

- [ ] `DEBUG = False` dans settings.py
- [ ] SECRET_KEY unique et sécurisée
- [ ] ALLOWED_HOSTS configurés
- [ ] Base de données configurée (pas SQLite en prod)
- [ ] Variables d'environnement configurées
- [ ] requirements.txt à jour
- [ ] Tests passent tous : `python manage.py test`
- [ ] Collectstatic exécuté : `python manage.py collectstatic`
- [ ] Migrations appliquées : `python manage.py migrate`
- [ ] Superuser créé

### Après Déploiement

- [ ] Accès à l'admin fonctionne
- [ ] Caméra détectée (si applicable)
- [ ] Détection de mouvement fonctionne
- [ ] Détection de visages fonctionne
- [ ] Images sauvegardées correctement
- [ ] API endpoints répondent
- [ ] Pas d'erreurs dans les logs
- [ ] Backup de la base de données configuré

---

Votre système Argus est maintenant prêt pour la production ! 🚀
