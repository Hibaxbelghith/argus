# 📱 Configuration des Notifications SMS avec Twilio

## ✅ Modifications Effectuées

### 1. Modèle User
- **Fichier**: `authentication/models.py`
- **Changement**: Ajout du champ `phone_number` au modèle `CustomUser`
```python
phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Format: +33612345678")
```

### 2. Service de Notifications
- **Fichier**: `notifications/services.py`
- **Changement**: Implémentation de la méthode `_send_sms()` avec Twilio
- **Fonctionnalités**:
  - Vérification des credentials Twilio
  - Vérification du numéro de téléphone utilisateur
  - Envoi de SMS avec gestion d'erreurs
  - Logging des événements

### 3. Admin Interface
- **Fichier**: `authentication/admin.py`
- **Changement**: Ajout de `phone_number` dans l'interface d'administration
- Permet aux admins d'ajouter/modifier les numéros de téléphone

## 🔧 Configuration Requise

### 1. Variables d'environnement
Créez un fichier `.env` à la racine du projet avec :

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=votre_account_sid
TWILIO_AUTH_TOKEN=votre_auth_token
TWILIO_PHONE_NUMBER=+33123456789
```

### 2. Obtenir les Credentials Twilio

1. **Créer un compte Twilio** : https://www.twilio.com/try-twilio
2. **Récupérer les credentials** :
   - Account SID : Tableau de bord Twilio
   - Auth Token : Tableau de bord Twilio
   - Phone Number : Acheter un numéro Twilio

### 3. Format du Numéro de Téléphone
- **Format international** : `+33612345678` (France)
- **Sans espaces** : Important pour Twilio
- **Avec indicatif pays** : `+` suivi du code pays

## 📝 Configuration Utilisateur

### Option 1 : Via l'Admin Django
1. Accédez à : http://127.0.0.1:8000/admin/
2. Allez dans **Authentication → Users**
3. Sélectionnez un utilisateur
4. Remplissez le champ **Phone number** : `+33612345678`
5. Sauvegardez

### Option 2 : Via le Shell Django
```python
python manage.py shell

from authentication.models import CustomUser
user = CustomUser.objects.get(username='votre_username')
user.phone_number = '+33612345678'
user.save()
```

### Option 3 : Via SQL Direct
```sql
UPDATE authentication_customuser 
SET phone_number = '+33612345678' 
WHERE username = 'votre_username';
```

## 🔔 Configuration des Préférences de Notifications

### Via l'Admin
1. Accédez à : http://127.0.0.1:8000/admin/notifications/notificationpreference/
2. Créez ou modifiez les préférences pour un utilisateur :
   - **Enabled methods** : Cochez `sms`
   - **Min severity SMS** : Choisissez `critical` (recommandé)
   - Sauvegardez

### Via le Shell
```python
from notifications.models import NotificationPreference
from authentication.models import CustomUser

user = CustomUser.objects.get(username='votre_username')
prefs, created = NotificationPreference.objects.get_or_create(user=user)

# Activer les SMS
prefs.enabled_methods = ['web', 'email', 'sms']
prefs.min_severity_sms = 'critical'  # Seulement pour les alertes critiques
prefs.save()
```

## 🧪 Tester l'Envoi de SMS

### Test Simple
```python
python manage.py shell

from notifications.services import NotificationService
from notifications.models import Notification
from authentication.models import CustomUser

# Récupérer un utilisateur
user = CustomUser.objects.get(username='votre_username')

# Créer une notification de test
notification = Notification.objects.create(
    user=user,
    notification_type='alert',
    title='Test SMS',
    message='Ceci est un test de notification SMS depuis Argus',
    severity='critical',
    delivery_method='sms'
)

# Envoyer
NotificationService._send_notification(notification)

# Vérifier le statut
print(f"Status: {notification.status}")
```

### Test Complet avec Alerte
```python
from analytics.models import SecurityAlert
from notifications.services import NotificationService

# Créer une alerte de sécurité
alert = SecurityAlert.objects.create(
    user=user,
    alert_type='suspicious_object',
    title='🚨 Objet Suspect Détecté',
    message='Un objet suspect (knife) a été détecté à 21:45',
    severity='critical'
)

# Créer les notifications (incluant SMS)
notifications = NotificationService.create_notification_from_alert(alert)

# Vérifier
for notif in notifications:
    print(f"{notif.delivery_method}: {notif.status}")
```

## 📊 Quand les SMS sont-ils Envoyés ?

### Automatiquement lors :
1. **Détections d'Objets Suspects** :
   - Armes (knife, gun)
   - Objets dangereux
   - Sévérité : HIGH ou CRITICAL

2. **Anomalies ML** :
   - Patterns inhabituels détectés
   - Sévérité : MEDIUM, HIGH ou CRITICAL

3. **Haute Fréquence** :
   - Trop de détections en peu de temps
   - Sévérité : HIGH ou CRITICAL

4. **Détections Hors Heures** :
   - Activité inhabituelle
   - Sévérité : MEDIUM ou plus

### Contrôle du Volume
Les paramètres `NotificationPreference` permettent de :
- **Limiter la fréquence** : `max_notifications_per_hour`
- **Filtrer par sévérité** : `min_severity_sms`
- **Heures silencieuses** : `quiet_hours_start/end`
- **Agrégation** : `enable_aggregation`

## ⚙️ Paramètres Recommandés

### Pour un Usage Normal
```python
prefs.enabled_methods = ['web', 'email', 'sms']
prefs.min_severity_web = 'low'
prefs.min_severity_email = 'high'
prefs.min_severity_sms = 'critical'  # Seulement urgent
prefs.max_notifications_per_hour = 5
prefs.enable_aggregation = True
```

### Pour Surveillance Intensive
```python
prefs.enabled_methods = ['web', 'sms']
prefs.min_severity_sms = 'medium'  # Plus de SMS
prefs.max_notifications_per_hour = 10
prefs.quiet_hours_start = None  # Pas d'heures silencieuses
prefs.enable_aggregation = False  # Toutes les alertes
```

### Pour Tests/Développement
```python
prefs.enabled_methods = ['web']  # Pas de SMS en dev
prefs.min_severity_sms = 'critical'
prefs.max_notifications_per_hour = 3
```

## 🐛 Dépannage

### Problème : "SMS delivery not configured"
**Solution** : Vérifier que `_send_sms()` est bien implémenté dans `services.py`

### Problème : "No phone number configured"
**Solution** : Ajouter le numéro via l'admin ou le shell

### Problème : "Twilio credentials not configured"
**Solution** : Vérifier le fichier `.env` et les variables d'environnement

### Problème : SMS non reçus
**Causes possibles** :
1. **Numéro invalide** : Vérifier le format international
2. **Crédits Twilio épuisés** : Vérifier le solde
3. **Sévérité trop basse** : Vérifier `min_severity_sms`
4. **Méthode désactivée** : Vérifier `enabled_methods`
5. **Heures silencieuses** : Vérifier `quiet_hours`

### Vérifier les Logs
```python
from notifications.models import NotificationLog

# Logs récents
logs = NotificationLog.objects.order_by('-timestamp')[:10]
for log in logs:
    print(f"{log.timestamp}: {log.event} - {log.details}")
```

## 💰 Coûts Twilio

- **SMS sortants** : ~0.05€ par SMS (varie selon pays)
- **Numéro de téléphone** : ~1€/mois
- **Crédit d'essai** : 15€ offerts à l'inscription
- **Recommandation** : Utiliser `min_severity_sms='critical'` pour limiter les coûts

## 📚 Ressources

- **Documentation Twilio** : https://www.twilio.com/docs/sms
- **Twilio Python** : https://www.twilio.com/docs/libraries/python
- **Tarifs** : https://www.twilio.com/sms/pricing
- **Dashboard Twilio** : https://console.twilio.com/

## ✨ Exemple Complet de Configuration

```bash
# 1. Configurer l'environnement
echo "TWILIO_ACCOUNT_SID=AC..." >> .env
echo "TWILIO_AUTH_TOKEN=..." >> .env
echo "TWILIO_PHONE_NUMBER=+33..." >> .env

# 2. Appliquer les migrations
python manage.py migrate

# 3. Ajouter le numéro utilisateur
python manage.py shell
>>> from authentication.models import CustomUser
>>> user = CustomUser.objects.get(username='admin')
>>> user.phone_number = '+33612345678'
>>> user.save()

# 4. Configurer les préférences
>>> from notifications.models import NotificationPreference
>>> prefs, _ = NotificationPreference.objects.get_or_create(user=user)
>>> prefs.enabled_methods = ['web', 'sms']
>>> prefs.min_severity_sms = 'critical'
>>> prefs.save()

# 5. Tester
>>> from notifications.services import NotificationService
>>> from notifications.models import Notification
>>> notif = Notification.objects.create(
...     user=user,
...     notification_type='alert',
...     title='Test',
...     message='Test SMS',
...     severity='critical',
...     delivery_method='sms'
... )
>>> NotificationService._send_notification(notif)
>>> print(notif.status)
```

---

**Status** : ✅ Configuration complète et fonctionnelle
**Date** : 29 Octobre 2025
