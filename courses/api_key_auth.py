import logging
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, Throttled

from courses.models import APIKey, APIPlan, APIUsageDaily, UserSubscription


logger = logging.getLogger("courses.api_key")


def _get_raw_api_key(request) -> str | None:
    # Prefer X-API-Key: <key>
    raw = request.headers.get("X-API-Key")
    if raw:
        raw = raw.strip()
        if raw.lower().startswith("apikey="):
            raw = raw.split("=", 1)[1].strip()
        return raw

    # Also accept: Authorization: ApiKey <key>
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("apikey "):
        raw = auth.split(" ", 1)[1].strip()
        if raw.lower().startswith("apikey="):
            raw = raw.split("=", 1)[1].strip()
        return raw

    return None


@dataclass(frozen=True)
class APIKeyContext:
    api_key: APIKey
    plan: APIPlan


class APIKeyAuthentication(BaseAuthentication):
    """
    Auth via API Key for developer access.

    Header:
      - X-API-Key: <plaintext>
      - Authorization: ApiKey <plaintext>
    """

    def authenticate(self, request):
        raw = _get_raw_api_key(request)
        if not raw:
            return None

        # Quick parse: we expect "prefix.secret"
        if "." not in raw:
            raise AuthenticationFailed("API key invalide.")

        prefix = raw.split(".", 1)[0]
        key_hash = APIKey.hash_key(raw)

        api_key = (
            APIKey.objects.select_related("user")
            .filter(prefix=prefix, key_hash=key_hash, is_active=True)
            .first()
        )
        if not api_key:
            raise AuthenticationFailed("API key invalide ou révoquée.")

        if not api_key.user.is_active:
            raise AuthenticationFailed("Utilisateur inactif.")

        plan = self._get_current_plan(api_key.user)
        if not plan or not plan.is_active:
            raise AuthenticationFailed("Aucun abonnement API actif.")

        # Quota check (daily). We do it here so it applies to all API-key endpoints by default.
        self._enforce_quota(api_key, plan, request)

        # Touch last_used_at without blocking request
        APIKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        request.api_context = APIKeyContext(api_key=api_key, plan=plan)
        return (api_key.user, api_key)

    def _get_current_plan(self, user):
        # Prefer current active subscription; fallback to free plan if present.
        sub = (
            UserSubscription.objects.select_related("plan")
            .filter(user=user, status=UserSubscription.STATUS_ACTIVE)
            .order_by("-started_at")
            .first()
        )
        if sub and sub.is_current:
            return sub.plan

        return APIPlan.objects.filter(code="free", is_active=True).first()

    @transaction.atomic
    def _enforce_quota(self, api_key: APIKey, plan: APIPlan, request):
        today = timezone.localdate()
        usage, _ = APIUsageDaily.objects.select_for_update().get_or_create(api_key=api_key, date=today)

        # Count every request
        if usage.requests_count + 1 > plan.daily_requests_limit:
            raise Throttled(detail="Quota de requêtes API dépassé.", wait=None)

        # Count downloads only for file download endpoint (by path convention)
        is_download = request.path.endswith("/download/") and "/api/data/" in request.path
        if is_download and (usage.downloads_count + 1 > plan.daily_download_limit):
            raise Throttled(detail="Quota de téléchargements API dépassé.", wait=None)

        usage.requests_count += 1
        if is_download:
            usage.downloads_count += 1
        usage.save(update_fields=["requests_count", "downloads_count", "updated_at"])
