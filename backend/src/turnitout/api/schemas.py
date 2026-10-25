"""Pydantic Request and Response Schemas matching ENTERPRISE_API.md."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HumanizeRequest(BaseModel):
    """Schema for POST /v1/humanize endpoint."""
    text: str = Field(..., min_length=5, max_length=50000, description="Plain text to humanize")
    intensity: Optional[float] = Field(70.0, ge=10.0, le=100.0, description="Paraphrasing aggressiveness")
    style: Optional[str] = Field("academic", description="Writing register (academic, conversational, technical)")
    convert_docstrings: Optional[bool] = Field(False, description="Convert Python docstrings to comments")
    protected_terms: Optional[List[str]] = Field(default_factory=list, description="Terms never to substitute")
    
    # Granular stage toggles
    enable_synonyms: Optional[bool] = Field(True, description="Enable synonym substitution")
    synonym_alignment: Optional[float] = Field(0.85, ge=0.50, le=1.00)
    random_alignment: Optional[bool] = Field(False)
    enable_phrase_rewrite: Optional[bool] = Field(True)
    enable_determiner_swap: Optional[bool] = Field(True)
    enable_voice_transform: Optional[bool] = Field(True)
    enable_sentence_fusion: Optional[bool] = Field(True)
    enable_transition_inject: Optional[bool] = Field(True)
    enable_clause_reorder: Optional[bool] = Field(True)
    enable_nominalization: Optional[bool] = Field(True)
    enable_appositive: Optional[bool] = Field(True)
    enable_discourse_rotate: Optional[bool] = Field(True)
    enable_contraction: Optional[bool] = Field(True)
    enable_ngram_audit: Optional[bool] = Field(True)
    enable_split_compound: Optional[bool] = Field(True)
    enable_ai_tell_scrubber: Optional[bool] = Field(True)
    
    # Citations
    enable_citations: Optional[bool] = Field(False)
    max_citations: Optional[int] = Field(0, ge=0, le=50)
    citation_format: Optional[str] = Field("IEEE [1]")
    citation_discipline: Optional[str] = Field(None)
    
    seed: Optional[int] = Field(None, description="Integer seed for deterministic reproduction")


class HumanizeResponse(BaseModel):
    """Schema for POST /v1/humanize response."""
    success: bool
    humanized_text: str
    words_processed: int
    modifications_count: int
    latency_ms: float
    citation_count: int
    bib_text: str
    telemetry: Dict[str, Any]


class CitationRequest(BaseModel):
    """Schema for POST /v1/citations endpoint."""
    text: str = Field(..., min_length=5, description="Input text for citation injection")
    citation_count: Optional[int] = Field(2, ge=1, le=50)
    citation_format: Optional[str] = Field("IEEE [1]")
    discipline: Optional[str] = Field(None)


class CitationResponse(BaseModel):
    """Schema for POST /v1/citations response."""
    success: bool
    cited_text: str
    bib_text: str
    citation_count: int
    words_processed: int
    latency_ms: float


class QuotaResponse(BaseModel):
    """Schema for GET /v1/quota response."""
    client_name: str
    email: str
    is_active: bool
    quota_limit: int
    words_used: int
    words_remaining: int
    rate_per_1k: float
    unlimited: bool
    expires_at: Optional[str]


class HealthResponse(BaseModel):
    """Schema for GET /v1/health response."""
    status: str
    engine: str
    engine_ready: bool
    version: str
    timestamp: float
