from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceSourceType(StrEnum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"


class Evidence(BaseModel):
    """Canonical evidence supporting an extracted or inferred result."""

    evidence_id: str
    source_type: EvidenceSourceType
    source_document_id: str
    section: str | None = None
    text: str
    start_offset: int | None = Field(default=None, ge=0)
    end_offset: int | None = Field(default=None, ge=0)
    evidence_type: str
    extractor: str | None = None
    relevance: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
