from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.document_chat import build_prompt
from courses.groq_llm import GroqError, groq_chat_completion
from courses.models import PDFDocument
from courses.utils import decrypt_id


class DocumentChatView(APIView):
    """
    Chat with a PDF document using Groq LLMs + model relay.

    POST:
      { "message": "...", "history": [{"role":"user|assistant","content":"..."}] }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, document_id: str):
        message = (request.data.get("message") or "").strip()
        history = request.data.get("history") or []
        if not message:
            return Response({"detail": "Message requis."}, status=status.HTTP_400_BAD_REQUEST)

        resolved = document_id
        if not str(resolved).isdigit():
            decoded = decrypt_id(resolved)
            if decoded:
                resolved = decoded
            else:
                return Response({"detail": "document_id invalide."}, status=status.HTTP_400_BAD_REQUEST)

        document = PDFDocument.objects.select_related(
            "course", "study_sublevel", "study_sublevel__level"
        ).prefetch_related("tags").filter(id=resolved, is_active=True).first()

        if not document:
            return Response({"detail": "Document non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        messages = build_prompt(document, message, history=history if isinstance(history, list) else None)

        try:
            result = groq_chat_completion(messages)
        except GroqError as e:
            msg = str(e) or ""
            if "missing groq_api_key" in msg.lower() or "missing groq" in msg.lower():
                return Response(
                    {"detail": "IA non configurée (GROQ_API_KEY manquante côté serveur)."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            if getattr(e, "status", None) in (401, 403):
                return Response(
                    {"detail": "IA non configurée (clé GROQ invalide ou non autorisée)."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            return Response(
                {"detail": "Erreur IA. Réessaie plus tard.", "error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "answer": result["content"],
                "model": result["model"],
            }
        )
