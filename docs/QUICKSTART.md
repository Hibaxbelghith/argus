# 🚀 Guide de Démarrage Rapide - Argus

## Démarrer le Serveur

### Option 1 : Double-clic sur le fichier

1. Double-cliquez sur `start_server.bat`
2. Le serveur démarrera automatiquement

### Option 2 : Ligne de commande

```bash
cd d:\hamza\5TWIN2K25\Django\argus
..\env\Scripts\python.exe manage.py runserver
```

## Accéder à l'Application

Une fois le serveur démarré, ouvrez votre navigateur et accédez à :

### 🏠 Page Principale (Détection en Direct)

**http://127.0.0.1:8000/**

### 📱 Autres Pages

- Historique des détections : http://127.0.0.1:8000/events/
- Statistiques : http://127.0.0.1:8000/statistics/
- Paramètres : http://127.0.0.1:8000/settings/
- Admin Django : http://127.0.0.1:8000/admin/

## Première Utilisation

### 1. Configuration Initiale (Optionnel)

Créez un superutilisateur pour accéder à l'admin :

```bash
cd d:\hamza\5TWIN2K25\Django\argus
..\env\Scripts\python.exe manage.py createsuperuser
```

Suivez les instructions pour définir :

- Nom d'utilisateur
- Email
- Mot de passe

### 2. Démarrer la Détection

1. Allez sur http://127.0.0.1:8000/
2. Cliquez sur **"▶️ Démarrer la Détection"**
3. Autorisez l'accès à la caméra si demandé
4. Le flux vidéo s'affichera avec les détections en temps réel

### 3. Configurer les Paramètres

1. Cliquez sur **"Paramètres"** dans le menu
2. Ajustez selon vos besoins :
   - ✅ Activer/désactiver détection de mouvement
   - ✅ Activer/désactiver détection de visages
   - 🎚️ Régler la sensibilité (seuil de mouvement)
   - ⏱️ Définir l'intervalle d'enregistrement

## Fonctionnalités Clés

### 🎥 Détection en Temps Réel

- **Mouvement** : Détecte automatiquement les mouvements dans le champ de vision
- **Visages** : Identifie et encadre les visages détectés
- **Double mode** : Les deux détections peuvent fonctionner simultanément

### 💾 Enregistrement Automatique

- Sauvegarde des événements dans la base de données SQLite
- Capture d'images lors des détections (optionnel)
- Stockage dans `media/detections/YYYY/MM/DD/`

### 📊 Analyse et Statistiques

- **Compteurs** : Total des détections par type
- **Graphiques** : Répartition visuelle des détections
- **Historique** : Liste complète avec filtres et recherche

## Contrôles en Direct

Sur la page principale, vous pouvez :

- ▶️ **Démarrer** la détection
- ⏹️ **Arrêter** la détection
- 🔄 **Activer/désactiver** chaque type de détection
- 📊 Voir les **statistiques en temps réel**

## Arrêter le Serveur

Dans le terminal où le serveur tourne :

- Appuyez sur `Ctrl + C`
- Confirmez avec `Y` si demandé

## Résolution des Problèmes Courants

### ❌ La caméra ne démarre pas

**Solution** :

1. Vérifiez qu'aucune autre application n'utilise la caméra
2. Essayez de changer l'index de caméra dans Paramètres (0 → 1)
3. Redémarrez le serveur après changement

### ❌ Erreur "Module not found"

**Solution** :

```bash
cd d:\hamza\5TWIN2K25\Django
.\env\Scripts\pip.exe install -r argus\requirements.txt
```

### ❌ Page blanche ou erreur 500

**Solution** :

1. Vérifiez que les migrations sont appliquées :

```bash
..\env\Scripts\python.exe manage.py migrate
```

2. Vérifiez les logs dans le terminal

### ⚠️ Performances lentes

**Solution** :

1. Allez dans Paramètres
2. Augmentez "Intervalle de détection" (ex: 2-3 secondes)
3. Augmentez "Surface minimale du contour" (ex: 1000)
4. Désactivez la sauvegarde d'images si non nécessaire

## Structure des Fichiers

```
argus/
├── start_server.bat        ← Double-cliquez pour démarrer
├── manage.py
├── requirements.txt
├── README.md              ← Documentation complète
├── QUICKSTART.md          ← Ce fichier
├── db.sqlite3             ← Base de données
├── media/                 ← Images capturées
│   └── detections/
├── detection/             ← Code de l'application
└── argus/                 ← Configuration Django
```

## Prochaines Étapes

### Pour Développer

1. Consultez `README.md` pour la documentation complète
2. Explorez `detection/detector.py` pour la logique de détection
3. Modifiez `detection/templates/` pour personnaliser l'interface

### Pour Déployer

1. Changez `SECRET_KEY` dans `argus/settings.py`
2. Mettez `DEBUG = False`
3. Configurez `ALLOWED_HOSTS`
4. Utilisez un serveur de production (Gunicorn, uWSGI)
5. Configurez une base de données PostgreSQL

## Conseils d'Utilisation

### 💡 Pour de Meilleurs Résultats

- Assurez un bon éclairage
- Positionnez la caméra de manière stable
- Évitez les arrière-plans trop chargés
- Ajustez la sensibilité selon l'environnement

### 🔒 Sécurité

- Ne partagez pas votre `SECRET_KEY`
- Changez les identifiants admin par défaut
- Activez l'authentification avant un déploiement public

## Support

Pour des questions détaillées, consultez :

- `README.md` : Documentation complète
- OpenCV Docs : https://docs.opencv.org/
- Django Docs : https://docs.djangoproject.com/

---

✅ **Vous êtes prêt !** Lancez `start_server.bat` et commencez à détecter !
