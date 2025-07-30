# -*- coding: utf-8 -*-
"""
Models for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import os


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
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.domain})"


class PDFDocument(models.Model):
    """Model for PDF documents"""
    title = models.CharField(max_length=300, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
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


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, verbose_name="Biographie")
    institution = models.CharField(max_length=200, blank=True, verbose_name="Institution")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username}"

