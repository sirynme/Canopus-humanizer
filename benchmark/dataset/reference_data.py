"""Verified Reference Material and Curated Linguistic Corpora for Benchmark Generation.

Ensures real-world ground truth for factual accuracy testing and explicit distinction
between verified reference facts and synthetic generator text.
"""

from typing import Any, Dict, List

# ------------------------------------------------------------------------------
# VERIFIED REFERENCE FACTS (Real-world verifiable historical & scientific ground truth)
# ------------------------------------------------------------------------------
VERIFIED_REFERENCE_FACTS: List[Dict[str, Any]] = [
    {
        "id": "REF-FACT-01",
        "domain": "Biomedicine",
        "claim": "The human genome consists of approximately 3.2 billion base pairs organized into 23 chromosome pairs.",
        "entities": ["human genome"],
        "numbers": ["3.2 billion", "23"],
        "verified_source": "International Human Genome Sequencing Consortium (2004)"
    },
    {
        "id": "REF-FACT-02",
        "domain": "Computer Science",
        "claim": "In 1971, Ray Tomlinson sent the first network email across ARPANET using the @ symbol to separate user and host.",
        "entities": ["Ray Tomlinson", "ARPANET"],
        "numbers": ["1971"],
        "verified_source": "RFC 561 / Computer History Museum"
    },
    {
        "id": "REF-FACT-03",
        "domain": "Physics",
        "claim": "The speed of light in a vacuum is exactly 299,792,458 meters per second by international agreement adopted in 1983.",
        "entities": ["speed of light"],
        "numbers": ["299,792,458", "1983"],
        "verified_source": "17th Conférence Générale des Poids et Mesures (CGPM)"
    },
    {
        "id": "REF-FACT-04",
        "domain": "Economics",
        "claim": "During the 2008 financial crisis, the United States Federal Reserve lowered the federal funds rate target to a range of 0.0% to 0.25% in December 2008.",
        "entities": ["United States Federal Reserve"],
        "numbers": ["2008", "0.0%", "0.25%"],
        "verified_source": "Federal Reserve Monetary Policy Release (Dec 16, 2008)"
    },
    {
        "id": "REF-FACT-05",
        "domain": "Environmental Science",
        "claim": "According to NOAA observatory measurements at Mauna Loa, atmospheric carbon dioxide concentration exceeded 420 parts per million in May 2022.",
        "entities": ["NOAA", "Mauna Loa"],
        "numbers": ["420", "2022"],
        "verified_source": "NOAA Global Monitoring Laboratory"
    }
]

# ------------------------------------------------------------------------------
# VERIFIED REAL SCHOLARLY CITATIONS (Legitimate Peer-Reviewed Literature)
# ------------------------------------------------------------------------------
VERIFIED_SCHOLARLY_CITATIONS: List[Dict[str, Any]] = [
    {
        "key": "vaswani2017attention",
        "authors": "Vaswani et al.",
        "year": "2017",
        "title": "Attention Is All You Need",
        "venue": "NeurIPS",
        "doi": "10.48550/arXiv.1706.03762",
        "ieee": "[1]",
        "apa": "(Vaswani et al., 2017)",
        "latex": "\\cite{vaswani2017attention}"
    },
    {
        "key": "schleimer2003winnowing",
        "authors": "Schleimer, Wilkerson & Aiken",
        "year": "2003",
        "title": "Winnowing: Local Algorithms for Document Fingerprinting",
        "venue": "ACM SIGMOD",
        "doi": "10.1145/872757.872770",
        "ieee": "[2]",
        "apa": "(Schleimer et al., 2003)",
        "latex": "\\cite{schleimer2003winnowing}"
    },
    {
        "key": "durbin1998biological",
        "authors": "Durbin et al.",
        "year": "1998",
        "title": "Biological Sequence Analysis: Probabilistic Models of Proteins and Nucleic Acids",
        "venue": "Cambridge University Press",
        "doi": "10.1017/CBO9780511790492",
        "ieee": "[3]",
        "apa": "(Durbin et al., 1998)",
        "latex": "\\cite{durbin1998biological}"
    }
]

# ------------------------------------------------------------------------------
# DOMAIN CORPUS VOCABULARY & ARCHETYPES
# ------------------------------------------------------------------------------
DOMAIN_METADATA = {
    "Computer Science": {
        "technical_terms": ["backpropagation", "convolutional kernel", "gradient descent", "throughput", "latency", "distributed consensus", "sharding", "vector space"],
        "named_entities": ["Turing", "von Neumann", "Linus Torvalds", "MIT", "Stanford University", "Google DeepMind", "ACM"],
        "typical_metrics": ["4.8 ms", "128 GB", "99.99% uptime", "10,000 queries per second", "32-bit floating point"]
    },
    "Biomedicine": {
        "technical_terms": ["monoclonal antibody", "ribosomal transcription", "angiogenesis", "pharmacokinetics", "in vitro assay", "clinical cohort", "pathogenicity"],
        "named_entities": ["Pasteur Institute", "Johns Hopkins", "WHO", "Dr. Rosalind Franklin", "NIH", "Lancet"],
        "typical_metrics": ["50 mg/kg", "p < 0.001", "95% confidence interval", "14-day incubation period", "300 patients"]
    },
    "Economics/Finance": {
        "technical_terms": ["liquidity trap", "arbitrage spread", "marginal propensity to consume", "stochastic volatility", "macroeconomic equilibrium", "capital adequacy ratio"],
        "named_entities": ["Keynes", "Milton Friedman", "International Monetary Fund", "World Bank", "London Stock Exchange"],
        "typical_metrics": ["$4.5 billion", "3.2% inflation", "25 basis points", "0.85 Gini coefficient", "Q3 2024"]
    },
    "Environmental Science": {
        "technical_terms": ["carbon sequestration", "trophic cascade", "albedo effect", "eutrophication", "paleoclimatological data", "biome transition"],
        "named_entities": ["IPCC", "Amazon Basin", "Greenland Ice Sheet", "Kyoto Protocol", "Great Barrier Reef"],
        "typical_metrics": ["1.5°C threshold", "415 ppm", "12,000 square kilometers", "2050 net-zero target"]
    },
    "Everyday": {
        "technical_terms": ["schedule", "meeting notes", "groceries", "weekend plans", "neighborhood event", "customer feedback"],
        "named_entities": ["Alice", "Bob", "Central Park", "Metro Station", "Oak Street Community Center"],
        "typical_metrics": ["3:00 PM", "5 miles", "$25.00", "45 minutes", "2 weeks"]
    }
}
