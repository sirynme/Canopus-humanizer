"""Automated Multi-Level Benchmark Dataset Generator.

Generates reproducible test cases across five distinct difficulty levels
with controlled variation in domain, length, syntactic complexity, formality,
citation density, argument structure, and factual/numerical content.
"""

from dataclasses import asdict, dataclass, field
import random
import re
from typing import Any, Dict, List, Optional, Set

from benchmark.dataset.reference_data import (
    DOMAIN_METADATA,
    VERIFIED_REFERENCE_FACTS,
    VERIFIED_SCHOLARLY_CITATIONS,
)


@dataclass
class BenchmarkCase:
    """Represents a single benchmark test document with ground-truth metadata."""
    id: str
    level: int
    level_name: str
    domain: str
    topic: str
    formality: str
    target_length: str
    original_text: str
    expected_facts: List[Dict[str, Any]] = field(default_factory=list)
    expected_entities: List[str] = field(default_factory=list)
    expected_numbers: List[str] = field(default_factory=list)
    expected_negations: List[str] = field(default_factory=list)
    expected_citations: List[str] = field(default_factory=list)
    is_challenging_case: bool = False
    challenge_type: Optional[str] = None
    is_verified_fact: bool = False
    academic_elements: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BenchmarkDatasetGenerator:
    """Configurable dataset generator with deterministic random seeding."""

    LEVEL_NAMES = {
        1: "Basic Everyday Writing",
        2: "Informational & Professional",
        3: "Analytical & Technical",
        4: "Academic Writing & Literature Review",
        5: "Research Proposal & Formal Academic Structure"
    }

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def _extract_numbers(self, text: str) -> List[str]:
        """Extracts numerical patterns including decimals, percentages, currency, and years."""
        pattern = r"\$?\b\d+(?:,\d{3})*(?:\.\d+)?%?(?:\s*(?:billion|million|kg|meters|ppm|bits|ms|°C))?\b"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        # Filter out empty or whitespace matches
        return [m.strip() for m in matches if m.strip() and not m.isspace()]

    def _extract_negations(self, text: str) -> List[str]:
        """Extracts critical negation keywords that alter sentence truth value."""
        negation_words = ["not", "never", "neither", "nor", "none", "cannot", "hardly", "scarcely", "barely", "fails to", "without"]
        found = []
        for word in negation_words:
            if re.search(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE):
                found.append(word.lower())
        return list(set(found))

    # --------------------------------------------------------------------------
    # LEVEL 1 GENERATOR: Basic Everyday Writing
    # --------------------------------------------------------------------------
    def _generate_level_1(self, index: int, domain: str = "Everyday") -> BenchmarkCase:
        is_challenge = (index % 3 == 0)
        
        if is_challenge:
            # Challenging Level 1: Negation and exact time/number dependency
            text = (
                "Alice did not attend the team briefing at 9:30 AM because her train was delayed by 45 minutes. "
                "She never received the updated meeting agenda on Oak Street, so she cannot confirm the project delivery date."
            )
            challenge_type = "negation_and_time_constraint"
        else:
            text = (
                "We had a productive team lunch yesterday near Central Park. The weather was pleasant, and we discussed "
                "the upcoming community project. Everyone agreed to meet again next Tuesday at 3:00 PM."
            )
            challenge_type = None

        return BenchmarkCase(
            id=f"BENCH-L1-{index:03d}",
            level=1,
            level_name=self.LEVEL_NAMES[1],
            domain=domain,
            topic="Daily Coordination",
            formality="casual",
            target_length="short",
            original_text=text,
            expected_entities=["Alice", "Oak Street", "Central Park"] if is_challenge else ["Central Park"],
            expected_numbers=self._extract_numbers(text),
            expected_negations=self._extract_negations(text),
            is_challenging_case=is_challenge,
            challenge_type=challenge_type,
            metadata={"seed": self.seed, "generator_version": "2.0"}
        )

    # --------------------------------------------------------------------------
    # LEVEL 2 GENERATOR: Informational & Professional Content
    # --------------------------------------------------------------------------
    def _generate_level_2(self, index: int, domain: str = "Economics/Finance") -> BenchmarkCase:
        is_challenge = (index % 3 == 0)

        if is_challenge:
            # Challenging Level 2: High density of financial percentages and conditional qualifiers
            text = (
                "Dear Stakeholders, in our Q3 2024 performance review, the investment portfolio gained 14.8%, "
                "surpassing our conservative target of 11.2%. However, the Asian equity market did not recover as anticipated. "
                "Unless inflation drops below 3.0% by November, we must not authorize the $4.5 million expansion for the London office."
            )
            challenge_type = "financial_density_and_conditional_negation"
        else:
            text = (
                "Dear Team, this email summarizes our departmental progress for the past month. We successfully onboarded "
                "15 new enterprise clients, resulting in an estimated 18% increase in operational throughput. "
                "Furthermore, our customer support satisfaction rating reached 94.5% across all regions."
            )
            challenge_type = None

        return BenchmarkCase(
            id=f"BENCH-L2-{index:03d}",
            level=2,
            level_name=self.LEVEL_NAMES[2],
            domain=domain,
            topic="Executive Summary & Performance Review",
            formality="professional",
            target_length="medium",
            original_text=text,
            expected_entities=["London office", "Asian equity market"] if is_challenge else ["enterprise clients"],
            expected_numbers=self._extract_numbers(text),
            expected_negations=self._extract_negations(text),
            is_challenging_case=is_challenge,
            challenge_type=challenge_type,
            metadata={"seed": self.seed, "audience": "stakeholders"}
        )

    # --------------------------------------------------------------------------
    # LEVEL 3 GENERATOR: Analytical Essays & Technical Explanations
    # --------------------------------------------------------------------------
    def _generate_level_3(self, index: int, domain: str = "Computer Science") -> BenchmarkCase:
        is_challenge = (index % 2 == 0)

        if is_challenge:
            # Challenging Level 3: Technical compound nouns ("learning rate", "gradient descent") & formulaic AI clichés
            text = (
                "Furthermore, it is important to delve into the comprehensive tapestry of modern distributed systems. "
                "The convolutional kernel optimization does not guarantee convergence when the learning rate exceeds 0.05. "
                "Under high-concurrency workloads reaching 12,000 queries per second, the database cluster experienced a 3.8 ms latency spike, "
                "which stands as a testament to the fundamental constraints of the CAP theorem."
            )
            challenge_type = "technical_compounds_and_ai_cliches"
        else:
            text = (
                "This technical analysis examines database sharding strategies across high-throughput clusters. "
                "By partitioning customer records across 16 independent database nodes, memory contention was reduced by 34.2%. "
                "Consequently, the system maintained 99.99% uptime throughout the peak transaction period in December."
            )
            challenge_type = None

        return BenchmarkCase(
            id=f"BENCH-L3-{index:03d}",
            level=3,
            level_name=self.LEVEL_NAMES[3],
            domain=domain,
            topic="Distributed Systems Architecture",
            formality="technical",
            target_length="medium",
            original_text=text,
            expected_entities=["CAP theorem"] if is_challenge else ["database nodes"],
            expected_numbers=self._extract_numbers(text),
            expected_negations=self._extract_negations(text),
            is_challenging_case=is_challenge,
            challenge_type=challenge_type,
            metadata={"contains_ai_cliches": is_challenge}
        )

    # --------------------------------------------------------------------------
    # LEVEL 4 GENERATOR: Academic Writing & Literature Review
    # --------------------------------------------------------------------------
    def _generate_level_4(self, index: int, domain: str = "Biomedicine") -> BenchmarkCase:
        ref_fact = VERIFIED_REFERENCE_FACTS[index % len(VERIFIED_REFERENCE_FACTS)]
        citation = VERIFIED_SCHOLARLY_CITATIONS[index % len(VERIFIED_SCHOLARLY_CITATIONS)]

        text = (
            f"Recent literature has emphasized the critical dynamics of clinical genomics. Specifically, {ref_fact['claim']} "
            f"As established by {citation['authors']} {citation['apa']}, structural variations directly modulate transcription efficiency. "
            "However, previous empirical inquiries failed to account for environmental epigenetic factors. "
            "Therefore, modern molecular biology requires rigorous longitudinal cohorts to validate therapeutic efficacy without introducing systemic observational bias."
        )

        return BenchmarkCase(
            id=f"BENCH-L4-{index:03d}",
            level=4,
            level_name=self.LEVEL_NAMES[4],
            domain=ref_fact["domain"],
            topic="Literature Review & Scholarly Synthesis",
            formality="scholarly",
            target_length="long",
            original_text=text,
            expected_facts=[ref_fact],
            expected_entities=ref_fact["entities"] + [citation["authors"]],
            expected_numbers=self._extract_numbers(text),
            expected_negations=self._extract_negations(text),
            expected_citations=[c for c in [citation["apa"], citation["key"]] if c in text],
            is_challenging_case=True,
            challenge_type="citation_and_verified_reference_integrity",
            is_verified_fact=True,
            metadata={"citation_doi": citation["doi"], "verified_source": ref_fact["verified_source"]}
        )

    # --------------------------------------------------------------------------
    # LEVEL 5 GENERATOR: Complete Research Proposal Structure
    # --------------------------------------------------------------------------
    def _generate_level_5(self, index: int, domain: str = "Computer Science") -> BenchmarkCase:
        citation1 = VERIFIED_SCHOLARLY_CITATIONS[0]
        citation2 = VERIFIED_SCHOLARLY_CITATIONS[1]

        academic_elements = {
            "problem_statement": "Deep neural network representations suffer from catastrophic forgetting during sequential task learning in distributed environments.",
            "research_questions": [
                "RQ1: How does selective synaptic consolidation mitigate representation drift in transformer models under continuous data streams?",
                "RQ2: What is the computational latency overhead of Winnowing fingerprint-based weight regularization?"
            ],
            "hypotheses": [
                "H1: Dynamic parameter isolation reduces catastrophic forgetting by at least 25.0% compared to standard rehearsal baselines.",
                "H0: Parameter isolation yields no statistically significant retention difference (p >= 0.05)."
            ],
            "objectives": [
                "1. Develop an empirical benchmark evaluating representation stability across 50 sequential tasks.",
                "2. Quantify inference throughput degradation when applying fingerprint constraint masks."
            ],
            "methodology": "A randomized controlled trial utilizing ResNet-50 and Vision Transformer architectures on the ImageNet-1K benchmark, evaluated via 5-fold cross-validation.",
            "limitations": "The investigation is constrained by GPU memory limits to batch sizes under 128 and does not evaluate multi-modal audio architectures."
        }

        text = (
            "1. Problem Statement: Deep neural network representations suffer from catastrophic forgetting during sequential task learning in distributed environments. "
            f"Prior foundational studies, notably {citation1['authors']} {citation1['apa']}, demonstrated that self-attention mechanisms exhibit high representation plasticity. "
            "However, continual weight updates frequently overwrite previously acquired representations.\n\n"
            "2. Research Questions & Hypotheses:\n"
            f"- {academic_elements['research_questions'][0]}\n"
            f"- {academic_elements['research_questions'][1]}\n"
            f"We hypothesize (H1) that dynamic parameter isolation reduces catastrophic forgetting by at least 25.0% compared to standard rehearsal baselines (H0: p >= 0.05).\n\n"
            "3. Objectives & Methodology:\n"
            f"The primary objective is to {academic_elements['objectives'][0]} "
            f"In accordance with fingerprint indexing methods established by {citation2['authors']} {citation2['apa']}, we implement a randomized controlled trial utilizing ResNet-50 and Vision Transformer architectures across 5-fold cross-validation.\n\n"
            f"4. Limitations: {academic_elements['limitations']}"
        )

        return BenchmarkCase(
            id=f"BENCH-L5-{index:03d}",
            level=5,
            level_name=self.LEVEL_NAMES[5],
            domain="Computer Science & Machine Learning",
            topic="Continual Learning in Transformer Architectures",
            formality="formal_academic_proposal",
            target_length="multi_section_proposal",
            original_text=text,
            expected_entities=["ResNet-50", "Vision Transformer", "ImageNet-1K", citation1["authors"], citation2["authors"]],
            expected_numbers=self._extract_numbers(text),
            expected_negations=self._extract_negations(text),
            expected_citations=[citation1["apa"], citation2["apa"]],
            is_challenging_case=True,
            challenge_type="academic_structural_alignment_and_citations",
            is_verified_fact=False,  # This is a synthetic proposal structure incorporating real citations
            academic_elements=academic_elements,
            metadata={"num_sections": 4, "contains_formal_hypotheses": True}
        )

    # --------------------------------------------------------------------------
    # PUBLIC SUITE GENERATION API
    # --------------------------------------------------------------------------
    def generate_suite(self, count_per_level: int = 5) -> List[BenchmarkCase]:
        """Generates a comprehensive benchmark suite across all 5 difficulty levels."""
        suite: List[BenchmarkCase] = []

        domains = ["Everyday", "Economics/Finance", "Computer Science", "Biomedicine", "Environmental Science"]

        for level in range(1, 6):
            for i in range(1, count_per_level + 1):
                domain = domains[(level + i) % len(domains)]
                if level == 1:
                    case = self._generate_level_1(index=i, domain="Everyday")
                elif level == 2:
                    case = self._generate_level_2(index=i, domain="Economics/Finance")
                elif level == 3:
                    case = self._generate_level_3(index=i, domain="Computer Science")
                elif level == 4:
                    case = self._generate_level_4(index=i, domain="Biomedicine")
                elif level == 5:
                    case = self._generate_level_5(index=i, domain="Computer Science")
                suite.append(case)

        return suite
