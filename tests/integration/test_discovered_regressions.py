"""Regression test suite covering actual defects discovered and resolved during implementation."""

import re
import pytest
from pathlib import Path

from canopus_humanizer.engine.protected_spans import ProtectedSpanDetector
from canopus_humanizer.engine.errors import OUTPUT_VALIDATION_FAILED
from canopus_humanizer.adapters.plain_text import PlainTextAdapter
from canopus_humanizer.adapters.latex import LatexAdapter


def test_regression_pyproject_author_email_format():
    """
    Regression Test: In the previous configuration, project.authors[0].email had value
    'canopus-humanizer@local', which caused setuptools/validate-pyproject to crash during
    'pip install -e .' with:
        'configuration error: `project.authors[0].email` must be idn-email'.
    This test verifies pyproject.toml has a compliant idn-email format.
    """
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'email\s*=\s*"([^"]+)"', content)
    assert match is not None
    email = match.group(1)
    # Must have a standard top-level domain compliant with idn-email
    assert "@" in email and "." in email.split("@")[-1]
    assert not email.endswith(".local")


def test_regression_latex_error_import_symbol():
    """
    Regression Test: latex.py previously attempted to import VALIDATION_FAILED
    instead of OUTPUT_VALIDATION_FAILED from canopus_humanizer.engine.errors, crashing on load.
    This test verifies that LatexAdapter imports cleanly and exports correct symbol.
    """
    adapter = LatexAdapter()
    assert adapter.format_name == "latex"
    assert OUTPUT_VALIDATION_FAILED == "OUTPUT_VALIDATION_FAILED"


def test_regression_plain_text_optional_typing_import():
    """
    Regression Test: plain_text.py previously omitted Optional from typing imports,
    which triggered NameError when type hints evaluated.
    """
    adapter = PlainTextAdapter()
    assert adapter.format_name == "plain_text"


def test_regression_dollar_math_vs_currency_distinction():
    """
    Regression Test: Naive regex for inline math '$...$' captured dollar amounts such as
    '$25.00' or '$4.5 million', mangling currency formatting.
    This test verifies that currency expressions are never misclassified as inline math.
    """
    detector = ProtectedSpanDetector()
    text = "The price was $25.00 and the funding was $4.5 million, whereas $x + y = z$ is math."
    spans = detector.detect(text)

    span_dict = {s.original: s.kind for s in spans}
    assert span_dict["$25.00"] == "currency"
    assert span_dict["$4.5 million"] == "currency"
    assert span_dict["$x + y = z$"] == "math_inline"
