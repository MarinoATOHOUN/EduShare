# -*- coding: utf-8 -*-
"""
Admin configuration for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.contrib import admin
from .models import Course, PDFDocument, UserProfile


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

