"""FastAPI router implementation for turnitout API."""

import time
from typing import Optional
from fastapi import APIRouter

from turnitout.api.schemas import HealthResponse, HumanizeRequest, HumanizeResponse
from turnitout.config import GLOBAL_CONFIG, ConfigNamespace
from turnitout.core.modifier import DocumentModifier

router = APIRouter(prefix="/v1", tags=["turnitout API"])


@router.post("/humanize", response_model=HumanizeResponse)
async def humanize_endpoint(payload: HumanizeRequest) -> HumanizeResponse:
    """Transforms input text using linguistic variation stages."""
    start_time = time.perf_counter()

    req_config = ConfigNamespace()
    req_config.INTENSITY = payload.intensity if payload.intensity is not None else 70.0
    req_config.STYLE = payload.style or "academic"
    if payload.enable_synonyms is not None:
        req_config.ENABLE_SYNONYMS = payload.enable_synonyms
    if payload.enable_phrase_rewrite is not None:
        req_config.ENABLE_PHRASE_REWRITE = payload.enable_phrase_rewrite
    if payload.enable_determiner_swap is not None:
        req_config.ENABLE_DETERMINER_SWAP = payload.enable_determiner_swap
    if payload.enable_discourse_rotate is not None:
        req_config.ENABLE_DISCOURSE_ROTATE = payload.enable_discourse_rotate
    if payload.enable_sentence_fusion is not None:
        req_config.ENABLE_SENTENCE_FUSION = payload.enable_sentence_fusion

    modifier = DocumentModifier(config=req_config, seed=payload.seed)
    protected_set = set(payload.protected_terms or [])

    humanized = modifier.modify_document(
        payload.text,
        protected_terms=protected_set,
        enable_citations=False,
    )

    latency = round((time.perf_counter() - start_time) * 1000.0, 2)
    words = len(payload.text.split())

    return HumanizeResponse(
        success=True,
        humanized_text=humanized,
        words_processed=words,
        modifications_count=modifier.total_transforms,
        latency_ms=latency,
        telemetry={
            "total_modifications": modifier.total_transforms,
            "word_count": words,
            "stages_applied": [
                k for k, v in {
                    "phrase_rewrite": modifier.phrase_rewrite_count,
                    "synonyms": modifier.synonym_count,
                    "determiner_swap": modifier.determiner_swap_count,
                    "discourse_rotation": modifier.discourse_rotate_count,
                    "sentence_fusion": modifier.sentence_fusion_count,
                }.items() if v > 0
            ],
        },
    )


@router.get("/health", response_model=HealthResponse)
async def health_endpoint() -> HealthResponse:
    """Service health and liveness probe."""
    return HealthResponse(
        status="healthy",
        engine="turnitout",
        version=GLOBAL_CONFIG.VERSION,
        timestamp=time.time(),
    )
