"""Unit Tests for In-Place Document Stream Processor."""

import pytest
from turnitout.core.doc_processor import DocumentProcessor


def test_markdown_processing():
    """Verify markdown headers and code blocks are protected."""
    processor = DocumentProcessor()
    md_sample = (
        "# Main Academic Title\n\n"
        "```python\n"
        "def compute_loss():\n"
        "    return 0.42\n"
        "```\n\n"
        "Furthermore, our experimental findings demonstrate significant convergence."
    )
    res = processor.process_markdown(md_sample)
    assert "# Main Academic Title" in res
    assert "def compute_loss():" in res
    assert "return 0.42" in res


def test_latex_processing():
    """Verify LaTeX structure and commands are protected."""
    processor = DocumentProcessor()
    tex_sample = (
        r"\documentclass{article}" "\n"
        r"\begin{document}" "\n"
        r"\section{Introduction}" "\n"
        r"Furthermore, this study plays a pivotal role in finite difference modeling." "\n"
        r"\end{document}"
    )
    res = processor.process_latex(tex_sample)
    assert r"\documentclass{article}" in res
    assert r"\section{Introduction}" in res
    assert r"\end{document}" in res


def test_in_memory_zip_creation():
    """Verify that in-memory ZIP package is generated without disk leaks."""
    processor = DocumentProcessor()
    files = [("test1.txt", b"Content 1"), ("test2.txt", b"Content 2")]
    zip_name, zip_bytes = processor.create_in_memory_zip(files, archive_prefix="Test_Bundle")
    
    assert zip_name.startswith("Test_Bundle_")
    assert zip_name.endswith(".zip")
    assert len(zip_bytes) > 50
