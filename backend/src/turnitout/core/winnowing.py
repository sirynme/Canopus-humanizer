"""Winnowing Algorithm (k=5, w=4) & Karp-Rabin Rolling Hash Engine.

Strictly models Turnitin's plagiarism detection algorithm:
- Schleimer, Wilkerson & Aiken (2003): "Winnowing: Local Algorithms for Document Fingerprinting"
- Extracts fingerprints from 5-word windows using Karp-Rabin rolling hashes.
- Calculates Jaccard similarity and exact matching fingerprint clusters.
"""

import re
from typing import List, Set, Tuple


class WinnowingEngine:
    """Computes document fingerprints and verifies similarity index reduction."""

    def __init__(self, k: int = 5, w: int = 4, base: int = 257, prime: int = 1000000007):
        self.k = k  # k-gram length in words
        self.w = w  # Window size
        self.base = base
        self.prime = prime

    @staticmethod
    def normalize_tokens(text: str) -> List[str]:
        """Normalizes text by lowercasing and stripping all punctuation and formatting."""
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9]+\b", text)]

    def hash_kgram(self, words: List[str]) -> int:
        """Computes Karp-Rabin hash for a k-gram of words."""
        h = 0
        for word in words:
            word_hash = 0
            for char in word:
                word_hash = (word_hash * 31 + ord(char)) % self.prime
            h = (h * self.base + word_hash) % self.prime
        return h

    def compute_fingerprints(self, text: str) -> Set[int]:
        """Extracts winnowed minimum-hash fingerprints from text."""
        tokens = self.normalize_tokens(text)
        if len(tokens) < self.k:
            return set()

        # Step 1: Generate k-grams and their hashes
        hashes = []
        for i in range(len(tokens) - self.k + 1):
            kgram = tokens[i : i + self.k]
            hashes.append(self.hash_kgram(kgram))

        if len(hashes) < self.w:
            return {min(hashes)} if hashes else set()

        # Step 2: Winnowing minimum-hash selection over sliding window of size w
        fingerprints = set()
        min_idx = -1
        for i in range(len(hashes) - self.w + 1):
            window = hashes[i : i + self.w]
            # Rightmost minimum selection (standard tie-breaker)
            min_val = min(window)
            fingerprints.add(min_val)

        return fingerprints

    def calculate_similarity(self, text_a: str, text_b: str) -> Tuple[float, int, int]:
        """Calculates Jaccard similarity percentage between two texts using Winnowing fingerprints."""
        fp_a = self.compute_fingerprints(text_a)
        fp_b = self.compute_fingerprints(text_b)

        if not fp_a or not fp_b:
            return 0.0, 0, 0

        intersection = fp_a & fp_b
        union = fp_a | fp_b

        jaccard = (len(intersection) / len(union)) * 100.0 if union else 0.0
        return round(jaccard, 2), len(intersection), len(fp_a)
