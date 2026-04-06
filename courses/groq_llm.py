import json
import os
import threading
import time
import urllib.error
import urllib.request
import logging

from django.conf import settings


class GroqError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


_lock = threading.Lock()
_rr_index = 0
_log = logging.getLogger("courses.groq")


def _choose_start_model(models: list[str]) -> int:
    global _rr_index
    with _lock:
        idx = _rr_index % max(len(models), 1)
        _rr_index += 1
    return idx


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 45) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = ""
        raise GroqError(body or str(e), status=getattr(e, "code", None)) from e
    except urllib.error.URLError as e:
        raise GroqError(str(e), status=None) from e


def _extract_output_text(data: dict) -> str:
    """
    Best-effort extraction for both:
    - OpenAI Chat Completions format
    - OpenAI Responses format
    """
    # Chat Completions
    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", None)
    )
    if isinstance(content, str):
        return content

    # Responses API (best effort)
    if isinstance(data.get("output_text"), str):
        return data["output_text"]

    output = data.get("output")
    if isinstance(output, list):
        # Prefer "message" items (avoid leaking "reasoning" blocks).
        preferred: list[str] = []
        fallback: list[str] = []
        parts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            for c in (item.get("content") or []):
                if not isinstance(c, dict) or not isinstance(c.get("text"), str):
                    continue
                ctype = c.get("type")
                text = c["text"]
                if item_type == "message":
                    preferred.append(text)
                else:
                    # Keep as fallback but skip explicit reasoning text types
                    if ctype not in ("reasoning_text",):
                        fallback.append(text)
        if preferred:
            return "\n".join(preferred)
        if fallback:
            return "\n".join(fallback)

    return ""


def _messages_to_responses_input(messages: list[dict]) -> str:
    """
    Groq supports OpenAI-compatible endpoints. For the Responses API, we keep it simple:
    we convert the chat messages into a single prompt string.
    """
    chunks: list[str] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = (m.get("role") or "").upper()
        content = m.get("content")
        if role and isinstance(content, str) and content.strip():
            chunks.append(f"{role}:\n{content.strip()}")
    return "\n\n".join(chunks).strip()


def groq_chat_completion(messages: list[dict], temperature: float = 0.2) -> dict:
    """
    Calls Groq Chat Completions with model relay + basic load balancing.
    Returns: {content, model, usage?}
    """
    api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise GroqError("Missing GROQ_API_KEY")

    models = list(getattr(settings, "GROQ_MODELS", [])) or [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile",
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # Cloudflare may block default python-urllib user-agent on some endpoints.
        "User-Agent": "EduShare/1.0",
    }

    start_idx = _choose_start_model(models)
    ordered = models[start_idx:] + models[:start_idx]

    last_err: GroqError | None = None
    for model in ordered:
        try:
            # Prefer the Responses API (matches Groq examples) and fall back to Chat Completions.
            try:
                url = "https://api.groq.com/openai/v1/responses"
                payload = {
                    "model": model,
                    "input": _messages_to_responses_input(messages),
                    "temperature": temperature,
                }
                data = _post_json(url, payload, headers=headers, timeout=60)
                content = _extract_output_text(data)
                if content:
                    return {"content": content, "model": model, "raw": data}
            except GroqError as e:
                # If the endpoint isn't available or payload isn't accepted, try chat completions.
                if e.status not in (400, 404, 405):
                    raise
                _log.info("Responses API fallback to chat.completions (model=%s status=%s)", model, e.status)

            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": model, "messages": messages, "temperature": temperature}
            data = _post_json(url, payload, headers=headers, timeout=60)
            content = _extract_output_text(data)
            return {"content": content or "", "model": model, "raw": data}
        except GroqError as e:
            last_err = e
            # Retry next model on rate limit / server errors.
            if e.status in (429, 500, 502, 503, 504):
                continue
            # Some free tiers may not have access to a given model.
            if e.status == 400:
                msg = (str(e) or "").lower()
                if "model" in msg or "not_found" in msg or "not found" in msg:
                    continue
            break

    raise last_err or GroqError("Groq call failed")
