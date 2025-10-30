"""
Multi-Channel Notification Delivery System
Supports SMS (Twilio), Email (SendGrid), Push (Firebase)
"""
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import logging
import os

logger = logging.getLogger(__name__)

# Conditional imports for delivery services
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. SMS notifications disabled.")

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not installed. Advanced email features disabled.")

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase not installed. Push notifications disabled.")


class MultiChannelDeliveryService:
    """
    Service principal pour l'envoi de notifications multi-canal
    """
    
    def __init__(self):
        self.twilio_client = self._init_twilio()
        self.sendgrid_client = self._init_sendgrid()
        self.firebase_app = self._init_firebase()
    
    def _init_twilio(self):
        """Initialise le client Twilio"""
        if TWILIO_AVAILABLE and TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            try:
                return TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            except Exception as e:
                logger.error(f"Twilio initialization failed: {e}")
        return None
    
    def _init_sendgrid(self):
        """Initialise le client SendGrid"""
        if SENDGRID_AVAILABLE and SENDGRID_API_KEY:
            try:
                return SendGridAPIClient(SENDGRID_API_KEY)
            except Exception as e:
                logger.error(f"SendGrid initialization failed: {e}")
        return None
    
    def _init_firebase(self):
        """Initialise Firebase Admin SDK"""
        if FIREBASE_AVAILABLE and FIREBASE_CREDENTIALS and os.path.exists(FIREBASE_CREDENTIALS):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
                    return firebase_admin.initialize_app(cred)
                return firebase_admin.get_app()
            except Exception as e:
                logger.error(f"Firebase initialization failed: {e}")
        return None
    
    def deliver_notification(self, notification, user):
        """
        Envoie une notification via le canal approprié
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec statut de delivery
        """
        method = notification.delivery_method
        
        handlers = {
            'email': self.send_email,
            'sms': self.send_sms,
            'push': self.send_push,
            'web': self.send_web
        }
        
        handler = handlers.get(method)
        
        if handler:
            try:
                result = handler(notification, user)
                return result
            except Exception as e:
                logger.error(f"Delivery failed for {method}: {e}")
                return {
                    'success': False,
                    'method': method,
                    'error': str(e)
                }
        
        return {
            'success': False,
            'method': method,
            'error': 'Unsupported delivery method'
        }
    
    def send_email(self, notification, user):
        """
        Envoie une notification par email
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec résultat
        """
        if not user.email:
            return {
                'success': False,
                'method': 'email',
                'error': 'User has no email address'
            }
        
        # Utiliser SendGrid si disponible, sinon Django email
        if self.sendgrid_client:
            return self._send_email_sendgrid(notification, user)
        else:
            return self._send_email_django(notification, user)
    
    def _send_email_sendgrid(self, notification, user):
        """Envoie via SendGrid"""
        try:
            # Créer le contenu HTML
            html_content = self._render_email_template(notification)
            
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=user.email,
                subject=f"[{notification.severity.upper()}] {notification.title}",
                html_content=html_content
            )
            
            response = self.sendgrid_client.send(message)
            
            return {
                'success': True,
                'method': 'email',
                'provider': 'sendgrid',
                'status_code': response.status_code
            }
        
        except Exception as e:
            logger.error(f"SendGrid email failed: {e}")
            return {
                'success': False,
                'method': 'email',
                'provider': 'sendgrid',
                'error': str(e)
            }
    
    def _send_email_django(self, notification, user):
        """Envoie via Django email backend"""
        try:
            send_mail(
                subject=f"[{notification.severity.upper()}] {notification.title}",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            return {
                'success': True,
                'method': 'email',
                'provider': 'django'
            }
        
        except Exception as e:
            logger.error(f"Django email failed: {e}")
            return {
                'success': False,
                'method': 'email',
                'provider': 'django',
                'error': str(e)
            }
    
    def _render_email_template(self, notification):
        """Rend le template HTML pour email"""
        # Template simple pour l'instant
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {'#f44336' if notification.severity == 'critical' else '#ff9800' if notification.severity == 'high' else '#2196F3'}; 
                           color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ padding: 20px; background-color: #f5f5f5; }}
                .footer {{ padding: 10px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{notification.title}</h2>
                    <p>Severity: {notification.severity.upper()}</p>
                </div>
                <div class="content">
                    <p>{notification.message}</p>
                    <p><em>Type: {notification.get_notification_type_display()}</em></p>
                    <p><small>Created: {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
                </div>
                <div class="footer">
                    <p>Argus Security Monitoring System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_sms(self, notification, user):
        """
        Envoie une notification par SMS via Twilio avec logging complet
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec résultat détaillé
        """
        from .models import SMSDeliveryLog, NotificationPreference
        
        if not self.twilio_client:
            logger.warning("Twilio client not initialized")
            return {
                'success': False,
                'method': 'sms',
                'error': 'Twilio not configured. Install twilio and set credentials.'
            }
        
        # Récupérer les préférences de notification
        try:
            prefs = NotificationPreference.objects.get(user=user)
            phone_number = prefs.phone_number
            
            # Vérifier que le numéro est vérifié
            if not prefs.phone_verified:
                logger.warning(f"Phone number not verified for user {user.username}")
                return {
                    'success': False,
                    'method': 'sms',
                    'error': 'Phone number not verified'
                }
        except NotificationPreference.DoesNotExist:
            logger.warning(f"No notification preferences for user {user.username}")
            return {
                'success': False,
                'method': 'sms',
                'error': 'No notification preferences configured'
            }
        
        if not phone_number:
            return {
                'success': False,
                'method': 'sms',
                'error': 'User has no phone number configured'
            }
        
        # Créer le log SMS
        sms_log = SMSDeliveryLog.objects.create(
            notification=notification,
            user=user,
            phone_number=phone_number,
            message_body='',  # Will be updated below
            sms_provider='twilio',
            status='queued'
        )
        
        try:
            # Créer un message SMS court et optimisé
            sms_body = self._format_sms_message(notification)
            sms_log.message_body = sms_body
            sms_log.status = 'sending'
            sms_log.save()
            
            # Envoyer via Twilio
            message = self.twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number,
                status_callback=getattr(settings, 'TWILIO_STATUS_CALLBACK_URL', None)
            )
            
            # Mettre à jour le log
            sms_log.mark_as_sent(message_id=message.sid)
            sms_log.provider_status = message.status
            if hasattr(message, 'price') and message.price:
                sms_log.cost = abs(float(message.price))
                sms_log.cost_currency = message.price_unit or 'USD'
            sms_log.save()
            
            logger.info(f"SMS sent successfully to {phone_number}: {message.sid}")
            
            return {
                'success': True,
                'method': 'sms',
                'provider': 'twilio',
                'message_sid': message.sid,
                'status': message.status,
                'phone_number': phone_number,
                'log_id': sms_log.id
            }
        
        except Exception as e:
            # Logger l'erreur
            error_msg = str(e)
            logger.error(f"Twilio SMS failed for {phone_number}: {error_msg}")
            
            # Mettre à jour le log avec l'erreur
            sms_log.mark_as_failed(
                error_code=getattr(e, 'code', 'unknown'),
                error_message=error_msg
            )
            
            return {
                'success': False,
                'method': 'sms',
                'provider': 'twilio',
                'error': error_msg,
                'phone_number': phone_number,
                'log_id': sms_log.id
            }
    
    def _format_sms_message(self, notification):
        """
        Formate un message SMS optimisé (max 160 caractères recommandé)
        
        Args:
            notification: Notification instance
            
        Returns:
            str: Message SMS formaté
        """
        # Emojis par sévérité
        severity_icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': 'ℹ️',
            'low': '📢'
        }
        
        icon = severity_icons.get(notification.severity, '📢')
        
        # Format court et direct
        # Exemple: "🚨 ALERTE: Objet suspect détecté - Weapon à 95% confiance"
        if len(notification.message) <= 100:
            sms_body = f"{icon} {notification.title}\n{notification.message}"
        else:
            # Tronquer le message si trop long
            short_message = notification.message[:97] + "..."
            sms_body = f"{icon} {notification.title}\n{short_message}"
        
        # Ajouter un lien vers le dashboard si configuré
        dashboard_url = getattr(settings, 'DASHBOARD_URL', None)
        if dashboard_url and len(sms_body) < 130:
            sms_body += f"\n{dashboard_url}"
        
        return sms_body
    
    def send_push(self, notification, user):
        """
        Envoie une notification push via Firebase
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec résultat
        """
        if not self.firebase_app:
            return {
                'success': False,
                'method': 'push',
                'error': 'Firebase not configured'
            }
        
        # Récupérer le token FCM de l'utilisateur
        # (Supposant qu'il y a une relation avec un modèle DeviceToken)
        fcm_token = self._get_user_fcm_token(user)
        
        if not fcm_token:
            return {
                'success': False,
                'method': 'push',
                'error': 'User has no FCM token registered'
            }
        
        try:
            # Créer le message push
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.message[:100],
                ),
                data={
                    'notification_id': str(notification.id),
                    'severity': notification.severity,
                    'type': notification.notification_type,
                },
                token=fcm_token,
            )
            
            response = messaging.send(message)
            
            return {
                'success': True,
                'method': 'push',
                'provider': 'firebase',
                'message_id': response
            }
        
        except Exception as e:
            logger.error(f"Firebase push failed: {e}")
            return {
                'success': False,
                'method': 'push',
                'provider': 'firebase',
                'error': str(e)
            }
    
    def _get_user_fcm_token(self, user):
        """Récupère le token FCM de l'utilisateur"""
        # À implémenter selon votre modèle de device tokens
        # Par exemple:
        # return user.device_tokens.filter(is_active=True).first().fcm_token
        return None
    
    def send_web(self, notification, user):
        """
        Notification web (stockée en DB, visible dans le dashboard)
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec résultat
        """
        # Les notifications web sont déjà stockées en DB
        # Ici on pourrait envoyer via WebSocket pour temps réel
        
        return {
            'success': True,
            'method': 'web',
            'message': 'Notification stored in database'
        }
    
    def send_call(self, notification, user):
        """
        Envoie une notification vocale via Twilio (pour alertes critiques)
        
        Args:
            notification: Notification instance
            user: User instance
            
        Returns:
            Dict avec résultat
        """
        if not self.twilio_client:
            return {
                'success': False,
                'method': 'call',
                'error': 'Twilio not configured'
            }
        
        phone_number = getattr(user, 'phone_number', None)
        
        if not phone_number:
            return {
                'success': False,
                'method': 'call',
                'error': 'User has no phone number'
            }
        
        try:
            # Créer un message vocal avec TwiML
            twiml = f"""
            <Response>
                <Say voice="alice">
                    Critical security alert from Argus monitoring system.
                    {notification.title}.
                    {notification.message[:100]}.
                    Please check your dashboard immediately.
                </Say>
            </Response>
            """
            
            call = self.twilio_client.calls.create(
                twiml=twiml,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            return {
                'success': True,
                'method': 'call',
                'provider': 'twilio',
                'call_sid': call.sid
            }
        
        except Exception as e:
            logger.error(f"Twilio call failed: {e}")
            return {
                'success': False,
                'method': 'call',
                'provider': 'twilio',
                'error': str(e)
            }
    
    def send_verification_sms(self, user, verification_code):
        """
        Envoie un SMS de vérification de numéro de téléphone
        
        Args:
            user: User instance
            verification_code: Code de vérification à 6 chiffres
            
        Returns:
            Dict avec résultat
        """
        from .models import NotificationPreference
        
        if not self.twilio_client:
            return {
                'success': False,
                'method': 'sms',
                'error': 'Twilio not configured'
            }
        
        try:
            prefs = NotificationPreference.objects.get(user=user)
            phone_number = prefs.phone_number
        except NotificationPreference.DoesNotExist:
            return {
                'success': False,
                'method': 'sms',
                'error': 'No phone number configured'
            }
        
        if not phone_number:
            return {
                'success': False,
                'method': 'sms',
                'error': 'No phone number configured'
            }
        
        try:
            # Message de vérification
            sms_body = f"🔐 Argus Security - Code de vérification: {verification_code}\nCe code expire dans 10 minutes."
            
            message = self.twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"Verification SMS sent to {phone_number}: {message.sid}")
            
            return {
                'success': True,
                'method': 'sms',
                'provider': 'twilio',
                'message_sid': message.sid,
                'phone_number': phone_number
            }
        
        except Exception as e:
            logger.error(f"Verification SMS failed: {e}")
            return {
                'success': False,
                'method': 'sms',
                'provider': 'twilio',
                'error': str(e)
            }
    
    def send_test_sms(self, user, message="Test notification from Argus Security System"):
        """
        Envoie un SMS de test
        
        Args:
            user: User instance
            message: Message de test personnalisé
            
        Returns:
            Dict avec résultat
        """
        from .models import NotificationPreference
        
        if not self.twilio_client:
            return {
                'success': False,
                'method': 'sms',
                'error': 'Twilio not configured'
            }
        
        try:
            prefs = NotificationPreference.objects.get(user=user)
            phone_number = prefs.phone_number
            
            if not prefs.phone_verified:
                return {
                    'success': False,
                    'method': 'sms',
                    'error': 'Phone number not verified. Verify first.'
                }
        except NotificationPreference.DoesNotExist:
            return {
                'success': False,
                'method': 'sms',
                'error': 'No phone number configured'
            }
        
        if not phone_number:
            return {
                'success': False,
                'method': 'sms',
                'error': 'No phone number configured'
            }
        
        try:
            sms_body = f"📱 {message}"
            
            message_obj = self.twilio_client.messages.create(
                body=sms_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"Test SMS sent to {phone_number}: {message_obj.sid}")
            
            return {
                'success': True,
                'method': 'sms',
                'provider': 'twilio',
                'message_sid': message_obj.sid,
                'phone_number': phone_number
            }
        
        except Exception as e:
            logger.error(f"Test SMS failed: {e}")
            return {
                'success': False,
                'method': 'sms',
                'provider': 'twilio',
                'error': str(e)
            }
    
    def get_sms_delivery_status(self, message_sid):
        """
        Récupère le statut de livraison d'un SMS
        
        Args:
            message_sid: Twilio message SID
            
        Returns:
            Dict avec statut
        """
        if not self.twilio_client:
            return {
                'success': False,
                'error': 'Twilio not configured'
            }
        
        try:
            message = self.twilio_client.messages(message_sid).fetch()
            
            return {
                'success': True,
                'message_sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'date_sent': message.date_sent,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'price': message.price,
                'price_unit': message.price_unit
            }
        
        except Exception as e:
            logger.error(f"Failed to fetch SMS status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_send_sms(self, notifications_users_list):
        """
        Envoie plusieurs SMS en batch
        
        Args:
            notifications_users_list: List of tuples [(notification, user), ...]
            
        Returns:
            Dict avec résultats
        """
        results = {
            'total': len(notifications_users_list),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        for notification, user in notifications_users_list:
            result = self.send_sms(notification, user)
            
            if result['success']:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'user': user.username,
                'notification_id': notification.id,
                'result': result
            })
        
        return results


# Fonction utilitaire pour initialiser le service
_delivery_service_instance = None

def get_delivery_service():
    """
    Retourne une instance singleton du service de delivery
    """
    global _delivery_service_instance
    if _delivery_service_instance is None:
        _delivery_service_instance = MultiChannelDeliveryService()
    return _delivery_service_instance
