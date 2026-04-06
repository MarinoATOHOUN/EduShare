from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.api_key_auth import APIKeyAuthentication
from courses.api_serializers import (
    APIKeyCreateResponseSerializer,
    APIKeyCreateSerializer,
    APIKeyListSerializer,
    APIPlanPublicSerializer,
    DataPDFDocumentSerializer,
    UserSubscriptionSerializer,
)
from courses.models import APIKey, APIPlan, APIUsageDaily, PDFDocument, UserSubscription
from courses.utils import decrypt_id


class PlanPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 50


class DataPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"

    def get_page_size(self, request):
        size = super().get_page_size(request) or self.page_size
        try:
            max_size = request.api_context.plan.max_page_size
        except Exception:
            max_size = 100
        return min(size, max_size)


class APIPlanListView(generics.ListAPIView):
    serializer_class = APIPlanPublicSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PlanPagination

    def get_queryset(self):
        return APIPlan.objects.filter(is_active=True).order_by("price_cents", "name")


class CurrentSubscriptionView(generics.RetrieveAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        sub = (
            UserSubscription.objects.select_related("plan")
            .filter(user=self.request.user, status=UserSubscription.STATUS_ACTIVE)
            .order_by("-started_at")
            .first()
        )
        if sub and sub.is_current:
            return sub

        # Fallback to a virtual free subscription response
        free = APIPlan.objects.filter(code="free", is_active=True).first()
        if not free:
            raise Http404("Aucune offre disponible.")

        # Non-persisted object-like dict via serializer fields
        return UserSubscription(user=self.request.user, plan=free, status=UserSubscription.STATUS_ACTIVE, started_at=timezone.now())


class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return APIKeyCreateSerializer
        return APIKeyListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ensure user has at least a free plan fallback
        if not UserSubscription.objects.filter(user=request.user, status=UserSubscription.STATUS_ACTIVE, ends_at__isnull=True).exists():
            free = APIPlan.objects.filter(code="free", is_active=True).first()
            if free:
                # Don't create duplicates
                if not UserSubscription.objects.filter(user=request.user, plan=free, status=UserSubscription.STATUS_ACTIVE).exists():
                    UserSubscription.objects.create(user=request.user, plan=free, status=UserSubscription.STATUS_ACTIVE, ends_at=None)

        api_key, plaintext = serializer.save()
        payload = {
            "id": api_key.id,
            "name": api_key.name,
            "prefix": api_key.prefix,
            "api_key": plaintext,
            "created_at": api_key.created_at,
        }
        return Response(APIKeyCreateResponseSerializer(payload).data, status=status.HTTP_201_CREATED)


class APIKeyRevokeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, key_id: int):
        api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
        api_key.revoke()
        return Response({"status": "revoked"})


class DataDocumentListView(generics.ListAPIView):
    """
    Data API: list documents metadata for bulk download workflows.
    Protected by API key + quotas.
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DataPDFDocumentSerializer
    pagination_class = DataPagination

    def get_queryset(self):
        qs = (
            PDFDocument.objects.filter(is_active=True)
            .select_related("course", "uploaded_by", "study_sublevel", "study_sublevel__level")
            .prefetch_related("tags")
        )

        # Filters
        course_domain = self.request.query_params.get("domain")
        if course_domain:
            qs = qs.filter(course__domain__icontains=course_domain)

        study_level = self.request.query_params.get("study_level")
        if study_level:
            if str(study_level).isdigit():
                qs = qs.filter(study_sublevel__level_id=int(study_level))
            else:
                qs = qs.filter(Q(study_sublevel__level__key=study_level) | Q(study_sublevel__level__name=study_level))

        study_sublevel = self.request.query_params.get("study_sublevel")
        if study_sublevel:
            if str(study_sublevel).isdigit():
                qs = qs.filter(study_sublevel_id=int(study_sublevel))
            else:
                qs = qs.filter(Q(study_sublevel__key=study_sublevel) | Q(study_sublevel__name=study_sublevel))

        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(Q(tags__key=tag) | Q(tags__name__iexact=tag))

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__name__icontains=search)
                | Q(course__name__icontains=search)
            )

        return qs.distinct().order_by("-created_at")


class DataDocumentDownloadView(APIView):
    """
    Data API: download the PDF file via API key.
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id: str):
        # Decrypt ID if needed
        resolved = document_id
        if not str(resolved).isdigit():
            decoded = decrypt_id(resolved)
            if decoded:
                resolved = decoded
            else:
                return Response({"detail": "document_id invalide."}, status=status.HTTP_400_BAD_REQUEST)

        document = get_object_or_404(PDFDocument, id=resolved, is_active=True)

        # Increment platform download count (optional but useful)
        document.increment_download_count()

        try:
            response = FileResponse(open(document.pdf_file.path, "rb"), content_type="application/pdf")
            safe_title = (document.title or "document").replace('"', "'")
            response["Content-Disposition"] = f'attachment; filename="{safe_title}.pdf"'
            return response
        except FileNotFoundError:
            raise Http404("Fichier non trouvé")


class DataWhoAmIView(APIView):
    """
    Small debugging endpoint to confirm API key validity + quotas.
    """

    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ctx = request.api_context
        today = timezone.localdate()
        usage = APIUsageDaily.objects.filter(api_key=ctx.api_key, date=today).first()
        requests_count = usage.requests_count if usage else 0
        downloads_count = usage.downloads_count if usage else 0

        return Response(
            {
                "user_id": request.user.id,
                "plan": {
                    "code": ctx.plan.code,
                    "name": ctx.plan.name,
                    "billing_period": ctx.plan.billing_period,
                    "daily_requests_limit": ctx.plan.daily_requests_limit,
                    "daily_download_limit": ctx.plan.daily_download_limit,
                    "max_page_size": ctx.plan.max_page_size,
                },
                "today": {
                    "date": str(today),
                    "requests_count": requests_count,
                    "downloads_count": downloads_count,
                    "requests_remaining": max(ctx.plan.daily_requests_limit - requests_count, 0),
                    "downloads_remaining": max(ctx.plan.daily_download_limit - downloads_count, 0),
                },
                "api_key": {"prefix": ctx.api_key.prefix, "is_active": ctx.api_key.is_active},
            }
        )
