"""Unit Tests for Citation Engine & BibTeX Generation."""

import pytest
from turnitout.core.citation_engine import CitationEngine


def test_discipline_detection():
    """Verify that discipline keywords correctly resolve to academic fields."""
    engine = CitationEngine()
    ai_text = "Deep learning and transformer neural networks require gradient descent optimization."
    disc, subfield, meta = engine.detect_discipline(ai_text)
    assert disc == "computer_science"

    fluid_text = "Incompressible fluid dynamics governed by the Navier-Stokes equations exhibit turbulence."
    disc, subfield, meta = engine.detect_discipline(fluid_text)
    assert disc == "engineering_physics"


def test_citation_insertion_and_bibtex():
    """Verify citation marker insertion and BibTeX bundle generation."""
    engine = CitationEngine()
    sample = "Machine learning architectures provide notable improvements. High-dimensional models exhibit stability."
    res = engine.insert_citations(sample, citation_count=2, citation_format="IEEE [1]")
    
    assert res["citation_count"] == 2
    assert "[1]" in res["cited_text"]
    assert "[2]" in res["cited_text"]
    assert "@article{" in res["bib_text"]
    assert "author" in res["bib_text"]
    assert "journal" in res["bib_text"]
    assert "AI AUTO-FILL INSTRUCTIONS" in res["bib_text"]
