"""Evaluation Module A: Language Quality.

Assesses grammar heuristics, readability indices (Flesch Reading Ease, Flesch-Kincaid,
Gunning Fog), sentence variety, lexical diversity (TTR), verbosity, and unnatural phrasing.
"""

import math
import re
from typing import Any, Dict, List, Tuple


class LanguageQualityEvaluator:
    """Evaluates syntactic fluency, readability, variety, and lexical quality."""

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimates syllable count using heuristic vowel group counting."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        word = re.sub(r"(?:[^laeiouy]|ed|es|e)$", "", word)
        word = re.sub(r"^y", "", word)
        syllables = len(re.findall(r"[aeiouy]{1,2}", word))
        return max(1, syllables)

    @classmethod
    def calculate_readability(cls, text: str) -> Dict[str, float]:
        """Calculates Flesch Reading Ease and Flesch-Kincaid Grade Level."""
        if not text.strip():
            return {"flesch_reading_ease": 0.0, "flesch_kincaid_grade": 0.0, "gunning_fog": 0.0}

        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        words = [w.strip() for w in re.findall(r"\b[a-zA-Z0-9']+\b", text) if w.strip()]

        num_sentences = max(1, len(sentences))
        num_words = max(1, len(words))
        num_syllables = sum(cls._count_syllables(w) for w in words)
        complex_words = sum(1 for w in words if cls._count_syllables(w) >= 3)

        asl = num_words / num_sentences  # Average Sentence Length
        asw = num_syllables / num_words  # Average Syllables per Word
        pct_complex = (complex_words / num_words) * 100.0

        # Flesch Reading Ease: 206.835 - 1.015 * ASL - 84.6 * ASW
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = round(max(0.0, min(100.0, fre)), 2)

        # Flesch-Kincaid Grade Level: 0.39 * ASL + 11.8 * ASW - 15.59
        fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
        fkgl = round(max(0.0, fkgl), 2)

        # Gunning Fog Index: 0.4 * (ASL + Pct Complex)
        fog = 0.4 * (asl + pct_complex)
        fog = round(max(0.0, fog), 2)

        return {
            "flesch_reading_ease": fre,
            "flesch_kincaid_grade": fkgl,
            "gunning_fog": fog,
            "avg_sentence_length": round(asl, 2),
            "avg_syllables_per_word": round(asw, 2)
        }

    @staticmethod
    def calculate_sentence_variety(text: str) -> Dict[str, float]:
        """Measures sentence length dispersion and burstiness."""
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if len(sentences) <= 1:
            return {"std_dev_sentence_length": 0.0, "burstiness": 0.0}

        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        burstiness = (std_dev / mean_len) if mean_len > 0 else 0.0

        return {
            "std_dev_sentence_length": round(std_dev, 2),
            "burstiness": round(burstiness, 3)
        }

    @staticmethod
    def calculate_lexical_diversity(text: str) -> Dict[str, float]:
        """Calculates Type-Token Ratio (TTR) and word repetition frequency."""
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9']+\b", text)]
        if not words:
            return {"ttr": 0.0, "total_words": 0, "unique_words": 0}

        unique_words = set(words)
        ttr = len(unique_words) / len(words)
        return {
            "ttr": round(ttr, 3),
            "total_words": len(words),
            "unique_words": len(unique_words)
        }

    @staticmethod
    def audit_grammar_and_syntax(text: str) -> List[Dict[str, Any]]:
        """Heuristic audit of common synthetic grammar and punctuation defects."""
        issues = []

        # 1. Repeated consecutive words ("the the", "in in")
        dup_matches = re.finditer(r"\b([a-zA-Z]+)\s+\1\b", text, flags=re.IGNORECASE)
        for m in dup_matches:
            issues.append({"type": "duplicate_consecutive_words", "snippet": m.group(0), "pos": m.start()})

        # 2. Broken double punctuation ("..", ",,", ", ."), excluding standard abbreviations like "al.,"
        for m in re.finditer(r"([,.!?;:]\s*[,.!?;:])", text):
            start = m.start()
            prefix = text[max(0, start - 5):start].lower()
            if m.group(0).strip() == ".," and any(prefix.endswith(abbr) for abbr in ["al", "etc", "e.g", "i.e"]):
                continue
            issues.append({"type": "broken_punctuation", "snippet": m.group(0), "pos": m.start()})

        # 3. Awkward adverb-in-compound injections (e.g. "broadly learning rate")
        awkward_compounds = re.finditer(r"\b(broadly|reliably|evidently|consequentially)\s+(learning rate|gradient descent|neural network|operating system)\b", text, flags=re.IGNORECASE)
        for m in awkward_compounds:
            issues.append({"type": "awkward_compound_injection", "snippet": m.group(0), "pos": m.start()})

        return issues

    @classmethod
    def evaluate(cls, original_text: str, humanized_text: str) -> Dict[str, Any]:
        """Runs comprehensive language quality evaluation and computes a 0-100 score."""
        orig_read = cls.calculate_readability(original_text)
        human_read = cls.calculate_readability(humanized_text)

        variety = cls.calculate_sentence_variety(humanized_text)
        diversity = cls.calculate_lexical_diversity(humanized_text)
        syntax_issues = cls.audit_grammar_and_syntax(humanized_text)

        # Base score starting at 85
        score = 85.0

        # Variety bonus (healthy burstiness between 0.3 and 0.8)
        if 0.3 <= variety["burstiness"] <= 0.8:
            score += 8.0
        elif variety["burstiness"] < 0.15:
            score -= 5.0

        # Lexical diversity bonus/penalty
        if diversity["ttr"] > 0.65:
            score += 7.0
        elif diversity["ttr"] < 0.40:
            score -= 10.0

        # Penalty for syntax/grammar issues
        score -= min(len(syntax_issues) * 12.0, 40.0)

        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "score": final_score,
            "readability": human_read,
            "readability_delta": round(human_read["flesch_reading_ease"] - orig_read["flesch_reading_ease"], 2),
            "sentence_variety": variety,
            "lexical_diversity": diversity,
            "syntax_issues": syntax_issues,
            "issues_count": len(syntax_issues),
            "grade_level": human_read["flesch_kincaid_grade"]
        }
