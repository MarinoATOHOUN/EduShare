import os
import re

from django.utils import timezone

from courses.models import PDFDocument, PDFDocumentText
from courses.pdf_text import extract_pdf_pages


_WORD_RE = re.compile(r"[\\wÀ-ÿ]{3,}", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text or "")]


def ensure_document_text_cache(document: PDFDocument) -> PDFDocumentText:
    pdf_path = document.pdf_file.path
    file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
    file_mtime = os.path.getmtime(pdf_path) if os.path.exists(pdf_path) else 0

    cache = getattr(document, "text_cache", None)
    if cache and cache.file_size == file_size and cache.file_mtime == file_mtime and cache.pages:
        return cache

    pages = extract_pdf_pages(pdf_path)
    cache, _ = PDFDocumentText.objects.get_or_create(document=document)
    cache.pages = pages
    cache.file_size = file_size
    cache.file_mtime = file_mtime
    cache.save(update_fields=["pages", "file_size", "file_mtime", "updated_at"])
    return cache


def pick_relevant_pages(pages: list[str], query: str, max_pages: int = 4) -> list[tuple[int, str]]:
    """
    Returns list of (page_number_1based, page_text) best matching the query.
    """
    tokens = _tokenize(query)
    if not tokens:
        return [(1, pages[0])] if pages else []

    token_set = set(tokens[:25])
    scored: list[tuple[int, int]] = []
    for idx, page in enumerate(pages):
        pl = (page or "").lower()
        score = 0
        for t in token_set:
            if t in pl:
                score += 1
        if score:
            scored.append((idx, score))

    if not scored:
        # Fallback: first pages
        return [(i + 1, pages[i]) for i in range(min(max_pages, len(pages)))]

    scored.sort(key=lambda x: x[1], reverse=True)
    chosen = [idx for idx, _ in scored[:max_pages]]
    chosen.sort()
    return [(i + 1, pages[i]) for i in chosen]


def build_prompt(document: PDFDocument, question: str, history: list[dict] | None = None) -> list[dict]:
    cache = ensure_document_text_cache(document)
    relevant = pick_relevant_pages(cache.pages or [], question, max_pages=4)
    context = "\n\n".join([f"[Page {p}]\n{text}" for p, text in relevant])

    system = (
        "Tu es un assistant pédagogique. Réponds en français.\n"
        "Tu dois répondre uniquement à partir du CONTEXTE fourni (pages du PDF).\n"
        "Si l'information n'est pas dans le contexte, dis-le clairement et propose des questions de clarification.\n"
        "Donne des réponses précises et cite les pages comme (p. X).\n"
        "Format: Markdown simple + LaTeX pour les maths ($...$ ou $$...$$).\n"
    )

    messages: list[dict] = [{"role": "system", "content": system}]
    if history:
        # Keep a short window
        for m in history[-8:]:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({"role": role, "content": content})

    user_content = f"CONTEXTE:\n{context}\n\nQUESTION:\n{question}"
    messages.append({"role": "user", "content": user_content})
    return messages

