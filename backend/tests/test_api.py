"""Unit & Integration Tests for Enterprise REST API Endpoints."""

import asyncio
import pytest
from turnitout.api.routes import citations_endpoint, health_endpoint, humanize_endpoint, quota_endpoint
from turnitout.api.schemas import CitationRequest, HumanizeRequest


def test_health_endpoint():
    """Verify GET /v1/health probe response."""
    res = asyncio.run(health_endpoint())
    assert res.status == "healthy"
    assert res.engine_ready is True
    assert "Turnitout Core" in res.engine


def test_quota_endpoint():
    """Verify GET /v1/quota response."""
    res = asyncio.run(quota_endpoint())
    assert res.is_active is True
    assert res.words_remaining > 0


def test_humanize_endpoint():
    """Verify POST /v1/humanize linguistic transformation and response schema."""
    req = HumanizeRequest(
        text="Furthermore, our experimental findings demonstrate that deep learning models introduce formulaic syntax across large datasets.",
        intensity=75.0,
        style="academic",
        protected_terms=["ResNet-50", "PyTorch"],
        enable_citations=True,
        max_citations=1,
        citation_format="IEEE [1]"
    )
    res = asyncio.run(humanize_endpoint(payload=req, api_key="demo_key"))
    
    assert res.success is True
    assert len(res.humanized_text) > 0
    assert res.words_processed > 10
    assert res.modifications_count > 0
    assert res.latency_ms > 0
    assert "stages_applied" in res.telemetry


def test_citations_endpoint():
    """Verify POST /v1/citations citation insertion and BibTeX generation."""
    req = CitationRequest(
        text="Machine learning models provide notable improvements in analyzing genomic sequences. Stochastic optimization enables stable convergence across parameters.",
        citation_count=2,
        citation_format="IEEE [1]"
    )
    res = asyncio.run(citations_endpoint(payload=req, api_key="demo_key"))

    assert res.success is True
    assert res.citation_count == 2
    assert "[1]" in res.cited_text
    assert "[2]" in res.cited_text
    assert "@article{" in res.bib_text
