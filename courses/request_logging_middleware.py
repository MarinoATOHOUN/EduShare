import logging
import time


logger = logging.getLogger("courses.requests")


class RequestLoggingMiddleware:
    """
    Lightweight request logging.
    Logs method, path, status, duration and user id when available.
    Avoids logging request bodies or Authorization headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        user_id = None
        try:
            if hasattr(request, "user") and request.user and request.user.is_authenticated:
                user_id = request.user.id
        except Exception:
            user_id = None

        logger.info(
            "%s %s %s %dms user=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            user_id if user_id is not None else "-",
        )

        return response

