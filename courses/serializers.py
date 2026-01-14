# -*- coding: utf-8 -*-
"""
Serializers for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, PDFDocument, UserProfile
from .utils import encrypt_id


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


from .utils_tracking import record_user_activity

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        
        # Record initial activity
        request = self.context.get('request')
        if request:
            try:
                # We pass the user explicitly because they might not be in request.user yet
                record_user_activity(user, request)
            except Exception as e:
                print(f"Error recording initial activity: {e}")
                
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'bio', 'institution', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    documents_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'domain', 'description', 'documents_count', 'created_at']

    def get_documents_count(self, obj):
        return obj.documents.filter(is_active=True).count()


class PDFDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PDFDocument model"""
    uploaded_by = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    file_size_mb = serializers.ReadOnlyField()

    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = PDFDocument
        fields = [
            'id', 'encrypted_id', 'title', 'description', 'course', 'course_id', 'uploaded_by',
            'pdf_file', 'file_size', 'file_size_mb', 'download_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'encrypted_id', 'uploaded_by', 'file_size', 'download_count', 'created_at', 'updated_at', 'is_active']

    def get_encrypted_id(self, obj):
        return encrypt_id(obj.id)

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class PDFDocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing PDF documents"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_domain = serializers.CharField(source='course.domain', read_only=True)
    file_size_mb = serializers.ReadOnlyField()

    encrypted_id = serializers.SerializerMethodField()

    class Meta:
        model = PDFDocument
        fields = [
            'id', 'encrypted_id', 'title', 'description', 'course_name', 'course_domain',
            'uploaded_by_username', 'file_size_mb', 'download_count', 'created_at'
        ]

    def get_encrypted_id(self, obj):
        return encrypt_id(obj.id)

