"""FastAPI Router Implementation for Turnitout Enterprise REST API."""

import time
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

from turnitout.api.schemas import (
    CitationRequest,
    CitationResponse,
    HealthResponse,
    HumanizeRequest,
    HumanizeResponse,
    QuotaResponse,
)
from turnitout.config import GLOBAL_CONFIG, ConfigNamespace
from turnitout.core.citation_engine import CitationEngine
from turnitout.core.modifier import DocumentModifier

router = APIRouter(prefix="/v1", tags=["Turnitout Enterprise API"])


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verifies X-API-Key header when auth is enabled."""
    if not GLOBAL_CONFIG.AUTH_REQUIRED:
        return x_api_key or "demo_key"
    if not x_api_key or x_api_key != GLOBAL_CONFIG.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_endpoint(
    payload: HumanizeRequest,
    api_key: str = Depends(verify_api_key)
) -> HumanizeResponse:
    """Executes multi-stage linguistic transformation pipeline on plain text."""
    start_time = time.perf_counter()

    # Build per-request config overrides
    req_config = ConfigNamespace()
    req_config.INTENSITY = payload.intensity or 70.0
    req_config.STYLE = payload.style or "academic"
    req_config.ENABLE_SYNONYMS = payload.enable_synonyms
    req_config.SYNONYM_ALIGNMENT = payload.synonym_alignment or 0.85
    req_config.ENABLE_PHRASE_REWRITE = payload.enable_phrase_rewrite
    req_config.ENABLE_DETERMINER_SWAP = payload.enable_determiner_swap
    req_config.ENABLE_VOICE_TRANSFORM = payload.enable_voice_transform
    req_config.ENABLE_SENTENCE_FUSION = payload.enable_sentence_fusion
    req_config.ENABLE_TRANSITION_INJECT = payload.enable_transition_inject
    req_config.ENABLE_CLAUSE_REORDER = payload.enable_clause_reorder
    req_config.ENABLE_NOMINALIZATION = payload.enable_nominalization
    req_config.ENABLE_APPOSITIVE = payload.enable_appositive
    req_config.ENABLE_DISCOURSE_ROTATE = payload.enable_discourse_rotate
    req_config.ENABLE_SPLIT_COMPOUND = payload.enable_split_compound
    req_config.ENABLE_NGRAM_AUDIT = payload.enable_ngram_audit
    req_config.ENABLE_CITATION_SHIELDING = payload.enable_citations

    modifier = DocumentModifier(config=req_config, seed=payload.seed)
    protected_set = set(payload.protected_terms or [])

    # Process text through pipeline
    humanized = modifier.modify_document(
        payload.text,
        protected_terms=protected_set,
        enable_citations=payload.enable_citations,
        citation_format=payload.citation_format or "IEEE [1]",
        max_citations=payload.max_citations or 0
    )

    # Optional BibTeX package generation if citations were injected
    bib_text = ""
    if payload.enable_citations and payload.max_citations:
        citation_engine = CitationEngine()
        cit_res = citation_engine.insert_citations(
            payload.text,
            citation_count=payload.max_citations,
            citation_format=payload.citation_format or "IEEE [1]",
            discipline=payload.citation_discipline
        )
        bib_text = cit_res["bib_text"]

    latency = round((time.perf_counter() - start_time) * 1000.0, 2)
    word_count = len(payload.text.split())

    return HumanizeResponse(
        success=True,
        humanized_text=humanized,
        words_processed=word_count,
        modifications_count=modifier.total_transforms,
        latency_ms=latency,
        citation_count=modifier.citation_count,
        bib_text=bib_text,
        telemetry={
            "total_modifications": modifier.total_transforms,
            "word_count": word_count,
            "stages_applied": [
                k for k, v in {
                    "phrase_rewrite": modifier.phrase_rewrite_count,
                    "synonyms": modifier.synonym_count,
                    "voice_transform": modifier.voice_transform_count,
                    "sentence_fusion": modifier.sentence_fusion_count,
                    "transition_inject": modifier.transition_inject_count,
                    "clause_reorder": modifier.clause_reorder_count,
                    "nominalization": modifier.nominalization_count,
                    "appositives": modifier.appositive_count,
                    "discourse_rotation": modifier.discourse_rotate_count,
                    "determiner_swap": modifier.determiner_swap_count
                }.items() if v > 0
            ]
        }
    )


@router.post("/citations", response_model=CitationResponse)
async def citations_endpoint(
    payload: CitationRequest,
    api_key: str = Depends(verify_api_key)
) -> CitationResponse:
    """Inserts contextual academic citations and generates BibTeX reference package."""
    start_time = time.perf_counter()
    engine = CitationEngine()
    
    result = engine.insert_citations(
        text=payload.text,
        citation_count=payload.citation_count or 2,
        citation_format=payload.citation_format or "IEEE [1]",
        discipline=payload.discipline
    )
    
    latency = round((time.perf_counter() - start_time) * 1000.0, 2)
    words = len(payload.text.split())

    return CitationResponse(
        success=True,
        cited_text=result["cited_text"],
        bib_text=result["bib_text"],
        citation_count=result["citation_count"],
        words_processed=words,
        latency_ms=latency
    )


@router.get("/quota", response_model=QuotaResponse)
async def quota_endpoint(api_key: str = Depends(verify_api_key)) -> QuotaResponse:
    """Returns word quota and enterprise billing tier status."""
    return QuotaResponse(
        client_name="Local Production Instance",
        email="developer@turnitout.local",
        is_active=True,
        quota_limit=1000000,
        words_used=4250,
        words_remaining=995750,
        rate_per_1k=0.00,
        unlimited=True,
        expires_at=None
    )


@router.get("/health", response_model=HealthResponse)
async def health_endpoint() -> HealthResponse:
    """Cluster health and liveness probe."""
    return HealthResponse(
        status="healthy",
        engine="Turnitout Core 2.6.0",
        engine_ready=True,
        version="2.6.0+prod",
        timestamp=time.time()
    )
