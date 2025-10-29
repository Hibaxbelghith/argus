import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'argus.settings')
django.setup()

from notifications.models import Notification

sms_notifications = Notification.objects.filter(
    delivery_method='sms',
    id__in=[28, 30]
).order_by('id')

print(f"📱 SMS Envoyés:\n")
for sms in sms_notifications:
    print(f"SMS #{sms.id}:")
    print(f"   📞 Destinataire: {sms.user.phone_number}")
    print(f"   📋 Titre: {sms.title}")
    print(f"   💬 Message: {sms.message[:100]}...")
    print(f"   ⚠️  Sévérité: {sms.severity}")
    print(f"   ✅ Status: {sms.status}")
    print(f"   🆔 Twilio SID: {sms.sms_id if sms.sms_id else '❌ Pas de SID'}")
    print(f"   🕐 Envoyé: {sms.sent_at if sms.sent_at else '❌ Non envoyé'}")
    print()
