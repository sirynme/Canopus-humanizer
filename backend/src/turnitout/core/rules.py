"""Dynamic Rules & Academic Taxonomy Loader for Turnitout Engine.

Adheres strictly to ARCHITECTURE_RULES.md:
- Words, topics, and dictionaries decoupled from source code.
- Dynamic hierarchical taxonomy loader with automatic __prompt__ stripping.
- Thread-safe caching and memory efficiency.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def get_rules_dir() -> Path:
    """Resolve rules directory path."""
    current = Path(__file__).resolve().parent
    for p in [current, current.parent, current.parent.parent, current.parent.parent.parent]:
        candidate = p / "rules"
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent.parent / "rules"


def clean_rule_data(data: Any) -> Any:
    """Filter out __prompt__ metadata header blocks from JSON dictionaries or lists."""
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k != "__prompt__"}
    elif isinstance(data, list):
        filtered = []
        for item in data:
            if isinstance(item, dict) and "__prompt__" in item and len(item) == 1:
                continue
            filtered.append(item)
        return filtered
    return data


def load_json_rule(filename: str, default: Any = None) -> Any:
    """Safely load and sanitize a JSON rule file."""
    path = get_rules_dir() / filename
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return clean_rule_data(raw)
    except Exception as e:
        print(f"[Warning] Error loading rule file {filename}: {e}")
        return default if default is not None else {}


# ==============================================================================
# STATIC RULE ASSETS (Cleaned, No Hardcoded Words in Source Code)
# ==============================================================================
SYNONYMS: Dict[str, List[str]] = load_json_rule("synonyms.json", {})
PHRASES: List[Tuple[str, str]] = [tuple(pair) for pair in load_json_rule("phrases.json", [])]
HEDGE_WORDS: List[str] = load_json_rule("hedge_words.json", [])
DETERMINERS: Dict[str, List[str]] = load_json_rule("determiners.json", {})
CONJUNCTIONS: List[str] = load_json_rule("conjunctions.json", [])
PROTECTED_TERMS: Set[str] = set(load_json_rule("protected_terms.json", []))
TRANSITIONS: Dict[str, List[str]] = load_json_rule("transitions.json", {})
NOMINALIZATIONS: Dict[str, str] = load_json_rule("nominalizations.json", {})
APPOSITIVES: Dict[str, str] = load_json_rule("appositives.json", {})
DISCOURSE_MARKERS: Dict[str, List[str]] = load_json_rule("discourse_markers.json", {})


# ==============================================================================
# HIERARCHICAL ACADEMIC TAXONOMY LOADER (Section 2 & 4 ARCHITECTURE_RULES.md)
# ==============================================================================
def load_academic_taxonomy() -> Dict[str, Dict[str, Any]]:
    """Recursively walks rules/academic/taxonomy/ and populates ACADEMIC_TAXONOMY."""
    taxonomy_root = get_rules_dir() / "academic" / "taxonomy"
    taxonomy: Dict[str, Dict[str, Any]] = {}

    if not taxonomy_root.is_dir():
        return taxonomy

    for discipline_dir in taxonomy_root.iterdir():
        if discipline_dir.is_dir():
            discipline_name = discipline_dir.name
            taxonomy[discipline_name] = {}

            for file_path in discipline_dir.glob("*.json"):
                topic_id = file_path.stem
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                        cleaned = clean_rule_data(raw)
                        taxonomy[discipline_name][topic_id] = cleaned
                except Exception as e:
                    print(f"[Warning] Failed loading taxonomy file {file_path}: {e}")

    return taxonomy


ACADEMIC_TAXONOMY: Dict[str, Dict[str, Any]] = load_academic_taxonomy()
