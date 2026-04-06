import os
import subprocess


class PDFTextExtractionError(RuntimeError):
    pass


def extract_pdf_pages(pdf_path: str) -> list[str]:
    """
    Extract text from a PDF as a list of pages using `pdftotext`.

    - Keeps page boundaries (split on form-feed \\f).
    - Uses `-layout` to preserve basic formatting.
    """
    if not os.path.exists(pdf_path):
        raise PDFTextExtractionError("PDF file not found")

    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", pdf_path, "-"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:
        raise PDFTextExtractionError(str(exc)) from exc

    if result.returncode != 0:
        raise PDFTextExtractionError(result.stderr.strip() or "pdftotext failed")

    # pdftotext separates pages with form-feed.
    raw_pages = result.stdout.split("\f")
    pages = [p.strip() for p in raw_pages if p and p.strip()]
    return pages

