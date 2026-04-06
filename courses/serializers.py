# -*- coding: utf-8 -*-
"""
Serializers for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from rest_framework import serializers
from django.contrib.auth.models import User
import logging
from .models import (
    Course,
    PDFDocument,
    StudyLevel,
    StudySubLevel,
    Tag,
    UserProfile,
    Newsletter,
    Advertisement,
    AdInteraction,
)
from .utils import encrypt_id

logger = logging.getLogger("courses.serializers")

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
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        # Générer un username unique à partir de l'email
        email = validated_data.get('email')
        base_username = email.split('@')[0]
        username = base_username
        i = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{i}"
            i += 1
        validated_data['username'] = username
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        # Record initial activity
        request = self.context.get('request')
        if request:
            try:
                record_user_activity(user, request)
            except Exception:
                logger.exception("Error recording initial activity")
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


class StudySubLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySubLevel
        fields = ["id", "key", "name", "order"]


class StudyLevelSerializer(serializers.ModelSerializer):
    sublevels = StudySubLevelSerializer(many=True, read_only=True)

    class Meta:
        model = StudyLevel
        fields = ["id", "key", "name", "order", "sublevels"]


class PDFDocumentSerializer(serializers.ModelSerializer):
    """Serializer for PDFDocument model"""
    uploaded_by = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    file_size_mb = serializers.ReadOnlyField()

    encrypted_id = serializers.SerializerMethodField()
    study_level = serializers.SerializerMethodField()
    study_sublevel = serializers.SerializerMethodField()
    study_sublevel_id = serializers.PrimaryKeyRelatedField(
        source="study_sublevel",
        queryset=StudySubLevel.objects.select_related("level").all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    tags = serializers.SerializerMethodField()
    tags_input = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = PDFDocument
        fields = [
            'id', 'encrypted_id', 'title', 'description', 'course', 'course_id', 'uploaded_by',
            'study_level', 'study_sublevel', 'study_sublevel_id',
            'tags', 'tags_input',
            'pdf_file', 'file_size', 'file_size_mb', 'download_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'encrypted_id', 'uploaded_by', 'file_size', 'download_count', 'created_at', 'updated_at', 'is_active']

    def get_encrypted_id(self, obj):
        return encrypt_id(obj.id)

    def get_study_level(self, obj):
        if not obj.study_sublevel_id:
            return ""
        return obj.study_sublevel.level.name

    def get_study_sublevel(self, obj):
        if not obj.study_sublevel_id:
            return ""
        return obj.study_sublevel.name

    def get_tags(self, obj):
        return [t.name for t in obj.tags.all().order_by("name")]

    def _normalize_tag_key(self, value: str) -> str:
        return (
            value.strip()
            .lower()
            .replace(" ", "_")
            .replace("è", "e")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("à", "a")
            .replace("ç", "c")
            .replace("’", "")
            .replace("'", "")
            .replace("/", "_")
        )

    def _parse_tags(self):
        # Accept tags_input="a,b,c" (multipart friendly) or tags=["a","b"]
        raw = self.initial_data.get("tags_input", None)
        if raw is None:
            raw = self.initial_data.get("tags", None)

        if raw in (None, ""):
            return []

        if isinstance(raw, (list, tuple)):
            candidates = [str(x) for x in raw]
        else:
            candidates = str(raw).split(",")

        tags = []
        for item in candidates:
            name = (item or "").strip()
            if not name:
                continue
            if len(name) > 50:
                name = name[:50]
            tags.append(name)

        # Dedupe case-insensitively
        unique = []
        seen = set()
        for t in tags:
            k = t.lower()
            if k in seen:
                continue
            seen.add(k)
            unique.append(t)

        return unique[:20]

    def _save_tags(self, instance):
        names = self._parse_tags()
        if not names:
            instance.tags.clear()
            return

        tag_ids = []
        for name in names:
            key = self._normalize_tag_key(name)
            tag, _ = Tag.objects.get_or_create(key=key, defaults={"name": name})
            # Keep display name in sync with latest user-provided version
            if tag.name != name:
                Tag.objects.filter(pk=tag.pk).update(name=name)
                tag.refresh_from_db()
            tag_ids.append(tag.id)

        instance.tags.set(tag_ids)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Backward compatibility: accept (study_level, study_sublevel) strings on create
        if self.instance is None and not attrs.get("study_sublevel"):
            level_name = (self.initial_data.get("study_level") or "").strip()
            sub_name = (self.initial_data.get("study_sublevel") or "").strip()
            if level_name and sub_name:
                resolved = StudySubLevel.objects.filter(level__name=level_name, name=sub_name).first()
                if resolved:
                    attrs["study_sublevel"] = resolved

        if self.instance is None and not attrs.get("study_sublevel"):
            raise serializers.ValidationError(
                {"study_sublevel_id": "Le sous-niveau est requis (après sélection du niveau)."}
            )

        return attrs

    def create(self, validated_data):
        # Remove non-model writable fields
        validated_data.pop("tags_input", None)
        validated_data['uploaded_by'] = self.context['request'].user
        instance = super().create(validated_data)
        self._save_tags(instance)
        return instance

    def update(self, instance, validated_data):
        # Remove non-model writable fields
        validated_data.pop("tags_input", None)
        instance = super().update(instance, validated_data)
        self._save_tags(instance)
        return instance


class PDFDocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing PDF documents"""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_domain = serializers.CharField(source='course.domain', read_only=True)
    file_size_mb = serializers.ReadOnlyField()

    encrypted_id = serializers.SerializerMethodField()
    study_level = serializers.SerializerMethodField()
    study_sublevel = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = PDFDocument
        fields = [
            'id', 'encrypted_id', 'title', 'description', 'course_name', 'course_domain',
            'study_level', 'study_sublevel',
            'tags',
            'uploaded_by_username', 'file_size_mb', 'download_count', 'created_at'
        ]

    def get_encrypted_id(self, obj):
        return encrypt_id(obj.id)

    def get_study_level(self, obj):
        if not obj.study_sublevel_id:
            return ""
        return obj.study_sublevel.level.name

    def get_study_sublevel(self, obj):
        if not obj.study_sublevel_id:
            return ""
        return obj.study_sublevel.name

    def get_tags(self, obj):
        return [t.name for t in obj.tags.all().order_by("name")]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model"""
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer for Advertisement model"""
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'description', 'content', 'image', 
            'link_url', 'contact_info', 'ad_type', 'trigger_action', 'duration'
        ]

class AdInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdInteraction
        fields = ['ad', 'interaction_type', 'time_to_close']
