# -*- coding: utf-8 -*-
"""
Admin configuration for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.contrib import admin
from .models import (
    Course,
    PDFDocument,
    APIKey,
    APIPlan,
    APIUsageDaily,
    StudyLevel,
    StudySubLevel,
    Tag,
    UserSubscription,
    UserProfile,
    UserActivity,
    Newsletter,
    Advertisement,
    AdInteraction,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'created_at', 'documents_count']
    list_filter = ['created_at']
    search_fields = ['name', 'domain', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fields = ['name', 'domain', 'description', 'created_at', 'updated_at']
    prepopulated_fields = {'domain': ('name',)}

    def documents_count(self, obj):
        return obj.documents.filter(is_active=True).count()
    documents_count.short_description = 'Nombre de documents'


@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'study_level_name', 'study_sublevel', 'uploaded_by', 'file_size_mb', 'download_count', 'is_active', 'created_at']
    list_filter = ['course', 'study_sublevel__level', 'study_sublevel', 'is_active', 'created_at', 'uploaded_by']
    search_fields = ['title', 'description', 'course__name', 'uploaded_by__username', 'study_sublevel__level__name', 'study_sublevel__name']
    readonly_fields = ['file_size', 'download_count', 'created_at', 'updated_at']
    list_editable = ['is_active']
    filter_horizontal = ['tags']

    def study_level_name(self, obj):
        if not obj.study_sublevel_id:
            return ""
        return obj.study_sublevel.level.name
    study_level_name.short_description = "Niveau d'étude"

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


@admin.register(StudyLevel)
class StudyLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "order"]
    list_editable = ["order"]
    search_fields = ["name", "key"]
    ordering = ["order", "name"]


@admin.register(StudySubLevel)
class StudySubLevelAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "level", "order"]
    list_filter = ["level"]
    list_editable = ["order"]
    search_fields = ["name", "key", "level__name", "level__key"]
    ordering = ["level__order", "order", "name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "key", "created_at"]
    search_fields = ["name", "key"]
    readonly_fields = ["created_at"]


@admin.register(APIPlan)
class APIPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "billing_period", "price_cents", "daily_requests_limit", "daily_download_limit", "max_page_size", "is_active"]
    list_filter = ["billing_period", "is_active"]
    search_fields = ["name", "code", "description"]
    list_editable = ["is_active"]


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "started_at", "ends_at"]
    list_filter = ["status", "plan"]
    search_fields = ["user__username", "user__email", "plan__code"]
    autocomplete_fields = ["user", "plan"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "prefix", "is_active", "created_at", "last_used_at", "revoked_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__username", "user__email", "name", "prefix"]
    autocomplete_fields = ["user"]
    readonly_fields = ["prefix", "key_hash", "created_at", "last_used_at", "revoked_at"]


@admin.register(APIUsageDaily)
class APIUsageDailyAdmin(admin.ModelAdmin):
    list_display = ["api_key", "date", "requests_count", "downloads_count", "updated_at"]
    list_filter = ["date"]
    search_fields = ["api_key__prefix", "api_key__user__username"]
    readonly_fields = ["api_key", "date", "requests_count", "downloads_count", "updated_at"]


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
