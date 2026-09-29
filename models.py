"""Bounded request and response contracts; no user text is written to disk."""

import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Language = Literal["English", "French", "Spanish", "German"]
NOTICE = "Draft for review only. Have a qualified legal professional review it before use."
Text = Annotated[str, StringConstraints(strip_whitespace=True)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class DocumentRequest(StrictModel):
    document_type: Text = Field(min_length=3, max_length=80)
    parties: Text = Field(min_length=5, max_length=4000)
    terms: Text = Field(min_length=10, max_length=12000)
    dates: Text = Field(min_length=3, max_length=200)
    jurisdiction: Text = Field(default="Not specified", min_length=1, max_length=200)
    language: Language = "English"

    @field_validator("terms")
    @classmethod
    def validate_terms(cls, value: str) -> str:
        parts = [p.strip() for p in re.split(r"[;\n]+", value) if p.strip()]
        if not parts or len(parts) > 60:
            raise ValueError("Provide between 1 and 60 terms, separated by semicolons or new lines.")
        if any(len(p) > 2000 for p in parts):
            raise ValueError("Each term must be at most 2,000 characters.")
        return value


class DocumentResponse(BaseModel):
    document: str
    provider: str
    model: str
    notice: str = NOTICE


class AnalysisRequest(StrictModel):
    document: Text = Field(min_length=30, max_length=60000)
    language: Language = "English"


class Analysis(BaseModel):
    summary: str = Field(min_length=1, max_length=6000)
    key_clauses: list[str] = Field(min_length=1, max_length=20)
    review_points: list[str] = Field(min_length=1, max_length=20)


class AnalysisResponse(Analysis):
    provider: str
    notice: str = NOTICE


class Branding(StrictModel):
    company_name: str = Field(default="LegalEase", max_length=80)
    font: Literal["serif", "sans"] = "serif"
    logo_base64: str | None = Field(default=None, max_length=2_800_000)


class ExportRequest(StrictModel):
    document: Text = Field(min_length=20, max_length=60000)
    document_type: Text = Field(default="Legal document", min_length=1, max_length=80)
    format: Literal["txt", "docx", "pdf"]
    branding: Branding = Field(default_factory=Branding)


class ImportRequest(StrictModel):
    filename: Text = Field(min_length=1, max_length=200)
    content_base64: Text = Field(min_length=1, max_length=7_000_000)
