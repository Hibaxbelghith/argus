from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class DetectionEvent(models.Model):
    """
    Modèle pour enregistrer les événements de détection de mouvement et de visages
    """
    DETECTION_TYPES = (
        ('motion', 'Détection de Mouvement'),
        ('face', 'Détection de Visage'),
        ('both', 'Mouvement et Visage'),
    )
    
    detection_type = models.CharField(
        max_length=10,
        choices=DETECTION_TYPES,
        default='motion',
        verbose_name='Type de détection'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Horodatage'
    )
    image = models.ImageField(
        upload_to='detections/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Image capturée'
    )
    confidence = models.FloatField(
        default=0.0,
        verbose_name='Niveau de confiance'
    )
    faces_count = models.IntegerField(
        default=0,
        verbose_name='Nombre de visages détectés'
    )
    motion_intensity = models.FloatField(
        default=0.0,
        verbose_name='Intensité du mouvement'
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Localisation (optionnel)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Utilisateur'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Événement de détection'
        verbose_name_plural = 'Événements de détection'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['detection_type']),
        ]

    def __str__(self):
        return f"{self.get_detection_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class CameraSettings(models.Model):
    """
    Modèle pour stocker les paramètres de la caméra et de détection
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la configuration'
    )
    camera_index = models.IntegerField(
        default=0,
        verbose_name='Index de la caméra'
    )
    enable_motion_detection = models.BooleanField(
        default=True,
        verbose_name='Activer détection de mouvement'
    )
    enable_face_detection = models.BooleanField(
        default=True,
        verbose_name='Activer détection de visages'
    )
    motion_threshold = models.IntegerField(
        default=25,
        verbose_name='Seuil de mouvement'
    )
    min_contour_area = models.IntegerField(
        default=500,
        verbose_name='Surface minimale du contour'
    )
    save_images = models.BooleanField(
        default=True,
        verbose_name='Sauvegarder les images'
    )
    detection_interval = models.IntegerField(
        default=1,
        verbose_name='Intervalle de détection (secondes)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Configuration active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification'
    )

    class Meta:
        verbose_name = 'Paramètre de caméra'
        verbose_name_plural = 'Paramètres de caméra'

    def __str__(self):
        return self.name
