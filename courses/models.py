# -*- coding: utf-8 -*-
"""
Models for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os
import hashlib
import secrets
from django.utils import timezone


def pdf_upload_path(instance, filename):
    """Generate upload path for PDF files"""
    return f'pdfs/{instance.course.domain}/{filename}'


class Course(models.Model):
    """Model for course categories/domains"""
    name = models.CharField(max_length=200, verbose_name="Nom du cours")
    domain = models.CharField(max_length=100, unique=True, verbose_name="Domaine")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Domaine"
        verbose_name_plural = "Domaines"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.domain})"


class StudyLevel(models.Model):
    """Reference model for study levels (e.g. Primaire, Université)."""
    key = models.SlugField(max_length=64, unique=True, verbose_name="Clé")
    name = models.CharField(max_length=100, verbose_name="Nom")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Niveau d'étude"
        verbose_name_plural = "Niveaux d'étude"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class StudySubLevel(models.Model):
    """Reference model for study sub-levels (e.g. CE1, Terminale)."""
    level = models.ForeignKey(StudyLevel, on_delete=models.CASCADE, related_name="sublevels")
    key = models.SlugField(max_length=64, verbose_name="Clé")
    name = models.CharField(max_length=100, verbose_name="Nom")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Sous-niveau"
        verbose_name_plural = "Sous-niveaux"
        ordering = ["level__order", "order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["level", "key"], name="uniq_sublevel_level_key"),
        ]

    def __str__(self):
        return f"{self.level.name} - {self.name}"


class Tag(models.Model):
    """Simple tag model for documents search and discovery."""
    key = models.SlugField(max_length=64, unique=True, verbose_name="Clé")
    name = models.CharField(max_length=100, verbose_name="Nom")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class APIPlan(models.Model):
    """API subscription plan (freemium/paid tiers)."""

    BILLING_MONTHLY = "monthly"
    BILLING_YEARLY = "yearly"
    BILLING_CHOICES = [
        (BILLING_MONTHLY, "Mensuel"),
        (BILLING_YEARLY, "Annuel"),
    ]

    code = models.SlugField(max_length=32, unique=True, verbose_name="Code")
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    billing_period = models.CharField(max_length=16, choices=BILLING_CHOICES, default=BILLING_MONTHLY)
    price_cents = models.PositiveIntegerField(default=0, verbose_name="Prix (centimes)")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    # Quotas
    daily_requests_limit = models.PositiveIntegerField(default=500, verbose_name="Limite requêtes/jour")
    daily_download_limit = models.PositiveIntegerField(default=50, verbose_name="Limite téléchargements/jour")
    max_page_size = models.PositiveIntegerField(default=100, verbose_name="Taille max page")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offre API"
        verbose_name_plural = "Offres API"
        ordering = ["price_cents", "name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserSubscription(models.Model):
    """User subscription to an API plan. Payment integration can be added later."""

    STATUS_ACTIVE = "active"
    STATUS_CANCELED = "canceled"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Actif"),
        (STATUS_CANCELED, "Annulé"),
        (STATUS_EXPIRED, "Expiré"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_subscriptions")
    plan = models.ForeignKey(APIPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    started_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonnement API"
        verbose_name_plural = "Abonnements API"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.code} ({self.status})"

    @property
    def is_current(self):
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.ends_at and self.ends_at <= timezone.now():
            return False
        return True


class APIKey(models.Model):
    """API Key for programmatic access. Only stores a hash (never plaintext)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100, blank=True, default="", verbose_name="Nom")

    prefix = models.CharField(max_length=32, db_index=True, verbose_name="Préfixe")
    key_hash = models.CharField(max_length=64, db_index=True, verbose_name="Hash (sha256)")

    is_active = models.BooleanField(default=True, verbose_name="Actif")
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Clé API"
        verbose_name_plural = "Clés API"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["prefix", "key_hash"], name="uniq_api_key_prefix_hash"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.prefix}"

    @staticmethod
    def hash_key(plaintext: str) -> str:
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()

    @classmethod
    def generate(cls) -> tuple[str, str, str]:
        """Returns (plaintext_key, prefix, hash)."""
        prefix = "edush_" + secrets.token_hex(3)  # 6 hex chars
        secret_part = secrets.token_urlsafe(32)
        plaintext = f"{prefix}.{secret_part}"
        return plaintext, prefix, cls.hash_key(plaintext)

    def revoke(self):
        if not self.revoked_at:
            self.revoked_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_active", "revoked_at"])


class APIUsageDaily(models.Model):
    """Daily counters for API usage per key (quotas)."""

    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name="daily_usage")
    date = models.DateField(db_index=True)
    requests_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Usage API (jour)"
        verbose_name_plural = "Usages API (jour)"
        constraints = [
            models.UniqueConstraint(fields=["api_key", "date"], name="uniq_api_key_date"),
        ]


class PDFDocument(models.Model):
    """Model for PDF documents"""
    title = models.CharField(max_length=300, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    study_sublevel = models.ForeignKey(
        StudySubLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name="Sous-niveau",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="documents", verbose_name="Tags")

    pdf_file = models.FileField(
        upload_to=pdf_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name="Fichier PDF"
    )
    file_size = models.PositiveIntegerField(default=0, verbose_name="Taille du fichier (bytes)")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de téléchargements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Document PDF"
        verbose_name_plural = "Documents PDF"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pdf_file:
            self.file_size = self.pdf_file.size
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)

    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class PDFDocumentText(models.Model):
    """Cached extracted text (per page) for a PDF document."""

    document = models.OneToOneField(PDFDocument, on_delete=models.CASCADE, related_name="text_cache")
    pages = models.JSONField(default=list, blank=True)  # list[str]

    file_size = models.PositiveIntegerField(default=0)
    file_mtime = models.FloatField(default=0)  # os.path.getmtime
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Texte PDF (cache)"
        verbose_name_plural = "Textes PDF (cache)"


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name="Biographie")
    institution = models.CharField(max_length=200, blank=True, verbose_name="Institution")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

class UserActivity(models.Model):
    """Model to track user activity, IP, device and location"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    user_agent = models.TextField(verbose_name="Agent utilisateur")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Type d'appareil")
    os = models.CharField(max_length=50, blank=True, verbose_name="Système d'exploitation")
    browser = models.CharField(max_length=50, blank=True, verbose_name="Navigateur")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    country = models.CharField(max_length=100, blank=True, verbose_name="Pays")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateurs"
        ordering = ['-created_at']

class Newsletter(models.Model):
    """Model for newsletter subscriptions"""
    email = models.EmailField(unique=True, verbose_name="Adresse Email")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Advertisement(models.Model):
    """Model for custom targeted advertisements"""
    AD_TYPES = [
        ('popup', 'Pop-up'),
        ('notification', 'Notification'),
        ('banner', 'Bannière'),
    ]

    TRIGGERS = [
        ('on_load', 'Au chargement de la page'),
        ('on_download', 'Au téléchargement'),
        ('on_upload', 'À l\'envoi d\'un document'),
        ('on_scroll', 'Au défilement'),
        ('on_timer', 'Basé sur le temps (périodique)'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre de la pub")
    description = models.TextField(verbose_name="Description du produit/service")
    content = models.TextField(blank=True, help_text="Contenu HTML additionnel", verbose_name="Contenu personnalisé")
    image = models.ImageField(upload_to='ads/', blank=True, null=True, verbose_name="Image publicitaire")
    link_url = models.URLField(blank=True, verbose_name="Lien vers le produit")
    contact_info = models.CharField(max_length=200, blank=True, verbose_name="Contact (Tel/Email)")
    
    ad_type = models.CharField(max_length=20, choices=AD_TYPES, default='notification', verbose_name="Type de pub")
    trigger_action = models.CharField(max_length=20, choices=TRIGGERS, default='on_load', verbose_name="Déclencheur")
    duration = models.IntegerField(default=5, help_text="Durée d'affichage en secondes (pour les popups/notifs auto-fermantes)", verbose_name="Durée (secondes)")
    
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class AdInteraction(models.Model):
    """Model to track user engagement with advertisements"""
    INTERACTION_TYPES = [
        ('view', 'Vue'),
        ('click', 'Clic'),
        ('close', 'Fermeture'),
    ]
    
    ad = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)
    
    # For 'close' interactions, track how long the ad was visible
    time_to_close = models.FloatField(null=True, blank=True, help_text="Temps en secondes avant fermeture")
    
    # Contextual info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Interaction Publicitaire"
        verbose_name_plural = "Interactions Publicitaires"

    def __str__(self):
        return f"{self.ad.title} - {self.interaction_type} ({self.created_at})"
