"""FastAPI application for extracting text and generating ClientProfile data."""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import models, templates, text_extractor
from .openai_client import OpenAIProfileGenerator

app = FastAPI(title="Trust KYC Autofill - Individual")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

profile_generator = OpenAIProfileGenerator()


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple readiness probe."""
    return {"status": "ok"}


@app.post("/api/extract", response_model=models.DocumentText)
async def extract_document(file: UploadFile = File(...)) -> models.DocumentText:
    """Extract raw text from an uploaded document."""
    with NamedTemporaryFile(delete=False) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)

    try:
        text = text_extractor.extract_text(tmp_path, content_type=file.content_type)
    except text_extractor.ExtractionError as exc:  # pragma: no cover - pass-through
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    return models.DocumentText(source_name=file.filename or "uploaded", text=text)


@app.post("/api/generate", response_model=models.GenerationResponse)
async def generate_from_text(payload: models.GenerationRequest) -> models.GenerationResponse:
    """Generate a ClientProfile and question/answer list from extracted text."""
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text is required for generation")

    profile = profile_generator.generate_profile(payload.text, payload.hints or {})
    questions = templates.build_form_answers(profile)
    return models.GenerationResponse(profile=profile, forms=questions)


@app.post("/api/process", response_model=models.GenerationResponse)
async def process_document(file: UploadFile = File(...)) -> models.GenerationResponse:
    """Convenience endpoint: extract text and immediately generate answers."""
    document_text = await extract_document(file)
    payload = models.GenerationRequest(text=document_text.text)
    return await generate_from_text(payload)


__all__ = ["app"]
