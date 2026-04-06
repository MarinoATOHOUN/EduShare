from rest_framework import serializers

from courses.models import APIKey, APIPlan, UserSubscription
from courses.serializers import PDFDocumentListSerializer
from courses.utils import encrypt_id


class APIPlanPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIPlan
        fields = [
            "code",
            "name",
            "description",
            "billing_period",
            "price_cents",
            "daily_requests_limit",
            "daily_download_limit",
            "max_page_size",
        ]


class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = APIPlanPublicSerializer(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ["id", "status", "started_at", "ends_at", "plan"]


class APIKeyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["id", "name", "prefix", "is_active", "created_at", "last_used_at", "revoked_at"]


class APIKeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True, max_length=100)

    def create(self, validated_data):
        user = self.context["request"].user
        plaintext, prefix, key_hash = APIKey.generate()
        api_key = APIKey.objects.create(
            user=user,
            name=validated_data.get("name", ""),
            prefix=prefix,
            key_hash=key_hash,
            is_active=True,
        )
        return api_key, plaintext


class APIKeyCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    prefix = serializers.CharField()
    api_key = serializers.CharField()
    created_at = serializers.DateTimeField()


class DataPDFDocumentSerializer(PDFDocumentListSerializer):
    """
    Reuse list serializer fields but add download URL for API clients.
    """

    download_url = serializers.SerializerMethodField()

    class Meta(PDFDocumentListSerializer.Meta):
        fields = PDFDocumentListSerializer.Meta.fields + ["download_url"]

    def get_download_url(self, obj):
        request = self.context.get("request")
        if request is None or getattr(obj, "id", None) is None:
            return ""
        encrypted_id = encrypt_id(obj.id) or str(obj.id)
        path = f"/api/data/documents/{encrypted_id}/download/"
        return request.build_absolute_uri(path)
