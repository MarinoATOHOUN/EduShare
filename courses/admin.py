# -*- coding: utf-8 -*-
"""
Admin configuration for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.contrib import admin
from .models import Course, PDFDocument, UserProfile, UserActivity, Newsletter, Advertisement, AdInteraction


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'created_at', 'documents_count']
    list_filter = ['created_at']
    search_fields = ['name', 'domain', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def documents_count(self, obj):
        return obj.documents.filter(is_active=True).count()
    documents_count.short_description = 'Nombre de documents'


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_by', 'file_size_mb', 'download_count', 'is_active', 'created_at']
    list_filter = ['course', 'is_active', 'created_at', 'uploaded_by']
    search_fields = ['title', 'description', 'course__name', 'uploaded_by__username']
    readonly_fields = ['file_size', 'download_count', 'created_at', 'updated_at']
    list_editable = ['is_active']

    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = 'Taille (MB)'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'created_at']
    list_filter = ['created_at', 'institution']
    search_fields = ['user__username', 'user__email', 'institution', 'bio']
    readonly_fields = ['created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_type', 'os', 'browser', 'city', 'country', 'created_at']
    list_filter = ['device_type', 'os', 'browser', 'country', 'created_at']
    search_fields = ['user__username', 'ip_address', 'city', 'country', 'user_agent']
    readonly_fields = ['created_at']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ['title', 'ad_type', 'trigger_action', 'duration', 'is_active', 'start_date', 'end_date']
    list_filter = ['ad_type', 'trigger_action', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'contact_info']
    fieldsets = (
        ('Informations Générales', {
            'fields': ('title', 'description', 'content', 'image')
        }),
        ('Ciblage et Type', {
            'fields': ('ad_type', 'trigger_action', 'duration')
        }),
        ('Lien et Contact', {
            'fields': ('link_url', 'contact_info')
        }),
        ('Statut et Dates', {
            'fields': ('is_active', 'start_date', 'end_date')
        }),
    )

@admin.register(AdInteraction)
class AdInteractionAdmin(admin.ModelAdmin):
    list_display = ['ad', 'interaction_type', 'user', 'time_to_close', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['ad__title', 'user__username', 'ip_address']
    readonly_fields = ['ad', 'interaction_type', 'user', 'time_to_close', 'ip_address', 'user_agent', 'created_at']
