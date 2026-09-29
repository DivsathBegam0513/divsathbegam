"""Thin API routes. Blocking SDK and export work runs in FastAPI's thread pool."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ai_core.gemini_generator import GeminiDocumentGenerator, GenerationError
from config import get_settings
from models import AnalysisRequest, AnalysisResponse, DocumentRequest, DocumentResponse, ExportRequest, ImportRequest
from security import protect
from services.exporter import export_document, safe_filename
from services.importer import extract_document

router = APIRouter(dependencies=[Depends(protect)])


def get_generator():
    return GeminiDocumentGenerator(get_settings())


@router.post("/generate", response_model=DocumentResponse)
def generate(request: DocumentRequest, generator=Depends(get_generator)):
    try:
        text = generator.generate_document(request)
    except GenerationError as exc:
        raise HTTPException(exc.status_code, str(exc)) from None
    settings = get_settings()
    return DocumentResponse(
        document=text,
        provider=settings.ai_provider,
        model=settings.gemini_model if settings.ai_provider == "gemini" else "offline-template",
    )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest, generator=Depends(get_generator)):
    try:
        result = generator.analyze(request)
    except GenerationError as exc:
        raise HTTPException(exc.status_code, str(exc)) from None
    return AnalysisResponse(**result.model_dump(), provider=get_settings().ai_provider)


@router.post("/export")
def export(request: ExportRequest):
    try:
        data, mime = export_document(request)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return Response(
        content=data,
        media_type=mime,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename(request.document_type)}.{request.format}"'
        },
    )


@router.post("/extract")
def extract(request: ImportRequest):
    try:
        text = extract_document(request)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    return {
        "document": text,
        "notice": "Text extraction does not preserve the source document layout. Review the result.",
    }
