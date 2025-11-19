"""Document text extraction helpers."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Optional

import docx2txt
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader


class ExtractionError(RuntimeError):
    """Raised when the system cannot extract text from a file."""


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(parts).strip()


def _extract_docx(path: Path) -> str:
    return docx2txt.process(str(path)) or ""


def _extract_image(path: Path) -> str:
    image = Image.open(str(path))
    return pytesseract.image_to_string(image)


def _extract_plain(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


EXTRACTORS = {
    "application/pdf": _extract_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": _extract_docx,
    "image/jpeg": _extract_image,
    "image/png": _extract_image,
    "text/plain": _extract_plain,
}


def extract_text(path: Path, *, content_type: Optional[str] = None) -> str:
    """Detect the appropriate extractor for the file and return text."""
    ctype = content_type or mimetypes.guess_type(path.name)[0]
    extractor = EXTRACTORS.get(ctype)

    if extractor is None:
        # Fallback to PDF if extension matches, otherwise attempt plain text
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            extractor = _extract_pdf
        elif suffix in {".docx"}:
            extractor = _extract_docx
        elif suffix in {".png", ".jpg", ".jpeg"}:
            extractor = _extract_image
        else:
            extractor = _extract_plain

    try:
        text = extractor(path)  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover - library specific errors
        raise ExtractionError(f"Failed to extract text: {exc}") from exc

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        raise ExtractionError("No text detected in the uploaded document")
    return cleaned


__all__ = ["extract_text", "ExtractionError"]
