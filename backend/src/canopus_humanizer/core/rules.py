"""Rules loader for canopus-humanizer engine."""

import json
import os
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
    """Filter out metadata header blocks from JSON dictionaries or lists."""
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


# Rule Assets
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

