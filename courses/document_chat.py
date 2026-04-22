# -*- coding: utf-8 -*-
"""
Document Chat — prompt building with BM25 RAG retrieval.
Developed by Marino ATOHOUN.
"""

import os

from courses.models import PDFDocument, PDFDocumentText
from courses.pdf_text import extract_pdf_pages
from courses.rag_engine import Chunk, retrieve_relevant_chunks


# ──────────────────────────────────────────────────────────────────────────────
# PDF text cache
# ──────────────────────────────────────────────────────────────────────────────

def ensure_document_text_cache(document: PDFDocument) -> PDFDocumentText:
    """
    Return the cached PDFDocumentText for *document*, refreshing it if the
    underlying file has changed (size or modification time).
    """
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


# ──────────────────────────────────────────────────────────────────────────────
# Prompt builder
# ──────────────────────────────────────────────────────────────────────────────

def build_prompt(
    document: PDFDocument,
    question: str,
    history: list[dict] | None = None,
) -> tuple[list[dict], list[dict]]:
    """
    Build the LLM messages list and return the source metadata.

    Returns:
        (messages, sources)

        messages : list of OpenAI-style chat dicts to pass to groq_chat_completion
        sources  : list of source dicts — [{"page": int, "excerpt": str, "chunk_id": int}, …]
                   to be forwarded to the frontend for citation display.
    """
    cache = ensure_document_text_cache(document)
    pages: list[str] = cache.pages or []

    # ── BM25 retrieval ────────────────────────────────────────────────────────
    top_chunks: list[Chunk] = retrieve_relevant_chunks(pages, question)

    # Build the context block injected into the user message
    context_parts: list[str] = []
    for chunk in top_chunks:
        context_parts.append(f"[Page {chunk.page}]\n{chunk.text}")
    context = "\n\n---\n\n".join(context_parts)

    # Build the sources list for the UI
    sources: list[dict] = [
        {
            "page": chunk.page,
            "excerpt": chunk.excerpt,
            "chunk_id": chunk.chunk_id,
        }
        for chunk in top_chunks
    ]

    # ── System prompt ─────────────────────────────────────────────────────────
    system = (
        "Tu es un assistant pédagogique expert. Réponds UNIQUEMENT en français.\n\n"
        "RÈGLES STRICTES :\n"
        "1. Appuie-toi EXCLUSIVEMENT sur le CONTEXTE fourni (extraits de pages du PDF).\n"
        "2. Si l'information est absente du contexte, dis-le clairement et propose une "
        "reformulation de la question.\n"
        "3. Cite systématiquement les pages sources sous la forme **(p. X)** après chaque "
        "affirmation clé.\n"
        "4. Si plusieurs pages traitent du sujet, cite toutes les pages concernées.\n"
        "5. Formatte ta réponse en Markdown clair (titres ##, listes, gras **…**).\n"
        "6. Pour les mathématiques, utilise LaTeX inline $…$ ou display $$…$$.\n"
        "7. Termine par une section **Sources** listant les pages utilisées.\n"
    )

    messages: list[dict] = [{"role": "system", "content": system}]

    # ── Conversation history (keep last 8 turns) ──────────────────────────────
    if history:
        for m in history[-8:]:
            role = m.get("role")
            content = m.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                messages.append({"role": role, "content": content})

    # ── User message with injected context ────────────────────────────────────
    user_content = (
        f"CONTEXTE (extraits du PDF \"{document.title}\") :\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"QUESTION :\n{question}"
    )
    messages.append({"role": "user", "content": user_content})

    return messages, sources
