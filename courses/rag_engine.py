# -*- coding: utf-8 -*-
"""
RAG Engine — BM25 Retrieval for EduShare PDF Chatbot.
Developed by Marino ATOHOUN.

Implements:
  - Paragraph-level chunking with overlapping context window
  - BM25 (Okapi BM25) scoring — zero external ML dependencies
  - Source citation metadata (page number + excerpt)
"""

import math
import re
from dataclasses import dataclass

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

CHUNK_SIZE_WORDS = 180      # target words per chunk
CHUNK_OVERLAP_WORDS = 40    # words of overlap between consecutive chunks
MAX_CHUNKS_RETURNED = 5     # chunks sent to the LLM
EXCERPT_MAX_CHARS = 220     # characters of preview shown as "source" in UI

# BM25 hyperparameters (standard values)
BM25_K1 = 1.5
BM25_B = 0.75

# Tokenisation
_WORD_RE = re.compile(r"[\wÀ-ÿ\-']{2,}", re.UNICODE)

# Stopwords (French + English) — filtered from query tokens only
_STOPWORDS = frozenset(
    """
    le la les un une des du de à au aux en dans sur pour par
    et ou mais donc or ni car est sont était avait avec sans
    il ils elle elles nous vous on se ce qui que qu dont où
    the a an of in to is was are be been being have has had
    do does did will would could should may might shall
    that this these those it its
    """.split()
)


# ──────────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Chunk:
    """One text chunk extracted from a PDF page."""
    chunk_id: int       # sequential index (0-based)
    page: int           # 1-based page number
    text: str           # full chunk text
    tokens: list[str]   # lower-cased tokens for BM25

    @property
    def excerpt(self) -> str:
        """Short preview for citation display in the UI."""
        stripped = self.text.strip()
        if len(stripped) <= EXCERPT_MAX_CHARS:
            return stripped
        # Try to cut at a sentence boundary
        cut = stripped[:EXCERPT_MAX_CHARS]
        for sep in (". ", "! ", "? ", "\n"):
            idx = cut.rfind(sep)
            if idx > EXCERPT_MAX_CHARS // 2:
                return cut[: idx + 1].strip() + "…"
        return cut.rstrip() + "…"


# ──────────────────────────────────────────────────────────────────────────────
# Tokenisation
# ──────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Return lower-cased word tokens from *text*."""
    return [t.lower() for t in _WORD_RE.findall(text or "")]


def _query_tokens(query: str) -> list[str]:
    """Return query tokens, filtering stop-words."""
    return [t for t in _tokenize(query) if t not in _STOPWORDS] or _tokenize(query)


# ──────────────────────────────────────────────────────────────────────────────
# Chunking
# ──────────────────────────────────────────────────────────────────────────────

def _split_into_paragraphs(page_text: str) -> list[str]:
    """Split a page into logical paragraphs (double-newline or long single-newline)."""
    # Normalise whitespace — collapse long spaces but keep paragraph breaks
    text = re.sub(r"[ \t]{2,}", " ", page_text)
    # Split on blank lines
    paragraphs = re.split(r"\n{2,}", text)
    # Filter very short noise lines
    return [p.strip() for p in paragraphs if len(p.strip()) >= 30]


def build_chunks(pages: list[str]) -> list[Chunk]:
    """
    Convert a list of page texts into overlapping word-level chunks.

    Strategy:
      1. For each page, split into paragraphs.
      2. Accumulate paragraphs into a sliding window of ~CHUNK_SIZE_WORDS words.
      3. When the window is full, emit a chunk and keep the last CHUNK_OVERLAP_WORDS
         words as the beginning of the next chunk (continuity context).
    """
    chunks: list[Chunk] = []
    chunk_id = 0

    for page_idx, page_text in enumerate(pages):
        page_no = page_idx + 1  # 1-based
        paragraphs = _split_into_paragraphs(page_text)

        if not paragraphs:
            # Page has no usable text — still emit a small chunk so page isn't lost
            if page_text.strip():
                text = page_text.strip()
                chunks.append(Chunk(chunk_id, page_no, text, _tokenize(text)))
                chunk_id += 1
            continue

        buffer_words: list[str] = []
        buffer_text_parts: list[str] = []

        def _flush(force_page: int) -> None:
            nonlocal chunk_id
            if not buffer_words:
                return
            text = " ".join(buffer_text_parts).strip()
            chunks.append(Chunk(chunk_id, force_page, text, _tokenize(text)))
            chunk_id += 1

        for para in paragraphs:
            words = para.split()
            buffer_words.extend(words)
            buffer_text_parts.append(para)

            if len(buffer_words) >= CHUNK_SIZE_WORDS:
                _flush(page_no)
                # Keep last CHUNK_OVERLAP_WORDS as overlap for the next chunk
                overlap_words = buffer_words[-CHUNK_OVERLAP_WORDS:]
                overlap_text = " ".join(overlap_words)
                buffer_words = list(overlap_words)
                buffer_text_parts = [overlap_text]

        # Flush remaining buffer for this page
        if buffer_words:
            _flush(page_no)
            buffer_words = []
            buffer_text_parts = []

    return chunks


# ──────────────────────────────────────────────────────────────────────────────
# BM25 Scoring
# ──────────────────────────────────────────────────────────────────────────────

class BM25Index:
    """
    In-memory BM25 index over a list of Chunk objects.
    Built once per document query (fast — no persistence needed for <1000 chunks).
    """

    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.n = len(chunks)
        if self.n == 0:
            self._avgdl = 0.0
            self._df: dict[str, int] = {}
            return

        # Document lengths
        self._dl = [len(c.tokens) for c in chunks]
        self._avgdl = sum(self._dl) / self.n

        # Document frequency per term
        self._df: dict[str, int] = {}
        for chunk in chunks:
            for term in set(chunk.tokens):
                self._df[term] = self._df.get(term, 0) + 1

    def score(self, chunk: Chunk, query_tokens: list[str], dl: int) -> float:
        """Compute BM25 score for one chunk given query tokens."""
        score = 0.0
        for term in query_tokens:
            tf = chunk.tokens.count(term)
            if tf == 0:
                continue
            df = self._df.get(term, 0)
            if df == 0:
                continue
            idf = math.log((self.n - df + 0.5) / (df + 0.5) + 1.0)
            tf_norm = (tf * (BM25_K1 + 1)) / (
                tf + BM25_K1 * (1 - BM25_B + BM25_B * dl / max(self._avgdl, 1))
            )
            score += idf * tf_norm
        return score

    def retrieve(self, query: str, top_k: int = MAX_CHUNKS_RETURNED) -> list[tuple[Chunk, float]]:
        """
        Return the top-k chunks most relevant to *query*, sorted by score desc.
        Falls back to first chunks if no term matches anything.
        """
        if not self.chunks:
            return []

        q_tokens = _query_tokens(query)
        if not q_tokens:
            q_tokens = _tokenize(query)

        scored = [
            (chunk, self.score(chunk, q_tokens, self._dl[i]))
            for i, chunk in enumerate(self.chunks)
        ]
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Filter zero-score results (no term matched at all)
        nonzero = [(c, s) for c, s in scored if s > 0]

        if nonzero:
            # Return top_k, but keep page order for coherence
            top = nonzero[:top_k]
            top.sort(key=lambda x: (x[0].page, x[0].chunk_id))
            return top

        # Fallback: return first top_k chunks (beginning of the document)
        return [(c, 0.0) for c in self.chunks[:top_k]]


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def retrieve_relevant_chunks(
    pages: list[str],
    query: str,
    top_k: int = MAX_CHUNKS_RETURNED,
) -> list[Chunk]:
    """
    High-level function: given raw page texts and a user query,
    return the *top_k* most relevant Chunk objects using BM25.
    """
    chunks = build_chunks(pages)
    index = BM25Index(chunks)
    results = index.retrieve(query, top_k=top_k)
    return [chunk for chunk, _score in results]
