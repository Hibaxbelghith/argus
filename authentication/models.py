from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # photo de référence pour la reconnaissance faciale
    photo = models.ImageField(upload_to='faces/', blank=True, null=True)
    # Numéro de téléphone pour les notifications SMS
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Format: +33612345678")
    

    def __str__(self):
        return self.username

class LoginAttempt(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    method = models.CharField(max_length=20, choices=(('password', 'password'), ('face', 'face')), default='password')
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {'OK' if self.success else 'FAIL'} at {self.timestamp}"
