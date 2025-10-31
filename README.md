# 🧠 ARGUS – Plateforme de Sécurité Intelligente avec IA

## 🎯 Objectif du projet

**ARGUS** est une plateforme web intelligente développée en **Django + Python**, permettant d'assurer la **sécurité des espaces** via des technologies d’**intelligence artificielle (IA)** appliquées à la **vision par ordinateur**.

Elle intègre plusieurs modules :

- 🔐 Authentification sécurisée (avec reconnaissance faciale)
- 🎥 Affichage du flux vidéo en direct
- 🤖 Détection automatique (personne, objet, mouvement)
- ⚠️ Système d’alertes
- 📊 Historique des alertes et analyses automatiques
- 😊 Détection d'émotions en temps réel
- 🗣️ Contrôle vocal pour actions de sécurité

## Project Overview

Argus is an intelligent surveillance platform that integrates facial recognition, object/person detection, movement detection, emotion detection, and voice command detection for security actions.

## Live Emotion Detection

Detect emotions in real time using your webcam, with results shown as overlays on the video feed.
Start it with: `python emotion_launcher.py`

**How it works:**
- Go to `/emotion/live/` in the web UI.
- Click "Launch Live Emotion Detection". This sends a request to the local launcher.
- The launcher opens a desktop window with your webcam feed and emotion labels (using DeepFace).
- It may take a few seconds for the window to appear.

**Requirements:**
- Run `emotion_launcher.py` locally before using the feature

**Note:** This feature runs locally for privacy and performance. The web UI only triggers the desktop app; it does not stream video to the server.

## ⚙️ Technologies utilisées

- **Backend** : Django (Python 3.13)
- **Frontend** : HTML5, CSS3, Bootstrap 5
- **Base de données** : SQLite
- **IA / Vision** : DeepFace, OpenCV, YOLOv5, MediaPipe
- **Analyse NLP** : OpenAI API / HuggingFace Summarization
- **Versioning** : Git + GitHub

## Quick Setup
1. Clone repo
2. Create & activate virtual env (Python 3.11):
   `python -m venv venv && .\venv\Scripts\Activate`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py runserver`
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Troubleshooting
- Use Python 3.11

---

## ⚙️ Technologies utilisées

- **Backend** : Django (Python 3.13)
- **Frontend** : HTML5, CSS3, Bootstrap 5
- **Base de données** : SQLite
- **IA / Vision** : DeepFace, OpenCV, YOLOv5, MediaPipe
- **Analyse NLP** : OpenAI API / HuggingFace Summarization
- **Versioning** : Git + GitHub

## Quick Setup

1. Clone repo
2. Create & activate virtual env (Python 3.11):
   `python -m venv venv && .\venv\Scripts\Activate`
3. `pip install -r requirements.txt`
4. `python -m spacy download en_core_web_md`
4. `python manage.py migrate`
5. `python manage.py runserver`
   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Troubleshooting

- Use Python 3.11

---

Projet académique – non commercial.  
© 2025 ARGUS Project – Tous droits réservés.
