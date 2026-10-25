"""Pydantic schemas for turnitout API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HumanizeRequest(BaseModel):
    """Request schema for text humanization."""
    text: str = Field(..., min_length=1, max_length=50000, description="Input text to process")
    intensity: Optional[float] = Field(70.0, ge=10.0, le=100.0, description="Transformation intensity percentage")
    style: Optional[str] = Field("academic", description="Writing register (academic, conversational, technical)")
    protected_terms: Optional[List[str]] = Field(default_factory=list, description="Terms to preserve unchanged")
    seed: Optional[int] = Field(None, description="Optional integer seed for deterministic output")

    # Optional stage overrides
    enable_synonyms: Optional[bool] = Field(True)
    enable_phrase_rewrite: Optional[bool] = Field(True)
    enable_determiner_swap: Optional[bool] = Field(True)
    enable_discourse_rotate: Optional[bool] = Field(True)
    enable_sentence_fusion: Optional[bool] = Field(True)


class HumanizeResponse(BaseModel):
    """Response schema for text humanization."""
    success: bool
    humanized_text: str
    words_processed: int
    modifications_count: int
    latency_ms: float
    telemetry: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Response schema for service health status."""
    status: str
    engine: str
    version: str
    timestamp: float
