"""Contextual Academic Citation Inserter & BibTeX / JSON / LaTeX Generator.

Adheres strictly to ARCHITECTURE_RULES.md:
- 100% decoupled from Streamlit / UI dependencies.
- Automatic discipline detection using ACADEMIC_TAXONOMY.
- Multi-format reference generation (BibTeX, IEEE, APA, LaTeX \\cite).
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from turnitout.core.rules import ACADEMIC_TAXONOMY


class CitationEngine:
    """Matches text against academic taxonomy and generates formatted citations and bibliographies."""

    def __init__(self):
        self.taxonomy = ACADEMIC_TAXONOMY

    def detect_discipline(self, text: str) -> Tuple[str, str, Dict[str, Any]]:
        """Scans text for academic keywords and returns (discipline, subfield, metadata)."""
        lower = text.lower()
        best_match = ("computer_science", "machine_learning_deep_learning", {})
        max_hits = 0

        for discipline, subfields in self.taxonomy.items():
            for subfield_id, subfield_data in subfields.items():
                if isinstance(subfield_data, list):
                    for item in subfield_data:
                        keywords = item.get("keywords", [])
                        hits = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", lower))
                        if hits > max_hits:
                            max_hits = hits
                            best_match = (discipline, item.get("subfield_id", subfield_id), item)

        return best_match

    def generate_bibtex_entry(self, author: str, title: str, journal: str, year: int = 2024, key: Optional[str] = None) -> str:
        """Generates a valid BibTeX @article block."""
        surname = author.split(",")[0].strip().replace(" ", "") if "," in author else author.split()[-1].strip()
        slug = re.sub(r"[^a-zA-Z0-9]", "", title.title())[:20]
        cite_key = key or f"{surname}{year}{slug}"

        return (
            f"@article{{{cite_key},\n"
            f"  author  = {{{author}}},\n"
            f"  title   = {{{title}}},\n"
            f"  journal = {{{journal}}},\n"
            f"  year    = {{{year}}},\n"
            f"  volume  = {{42}},\n"
            f"  number  = {{1}},\n"
            f"  pages   = {{100--115}},\n"
            f"  doi     = {{10.1016/j.turnitout.{year}.001}}\n"
            f"}}"
        )

    def insert_citations(
        self,
        text: str,
        citation_count: int = 2,
        citation_format: str = "IEEE [1]",
        discipline: Optional[str] = None
    ) -> Dict[str, Any]:
        """Contextually inserts citations and produces matching BibTeX and JSON packages."""
        if not text or not text.strip():
            return {
                "cited_text": text,
                "bib_text": "",
                "citations": [],
                "citation_count": 0
            }

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        num_citations = min(citation_count if citation_count > 0 else 1, len(sentences))
        
        # Detect or filter discipline
        detected_disc, subfield_id, metadata = self.detect_discipline(text)
        target_disc = discipline if discipline and discipline in self.taxonomy else detected_disc

        # Resolve pool of authors & journals
        author_pool = metadata.get("author_pool", ["Smith, R. M.", "Johnson, A. K.", "Williams, E. T."])
        journal_pool = metadata.get("journals", ["Journal of Advanced Research", "IEEE Transactions on Science", "Nature Computing"])

        bib_entries = []
        citation_records = []
        cited_sentences = []
        citations_placed = 0

        # Step interval to scatter citations across the text
        step = max(1, len(sentences) // num_citations)

        for idx, sent in enumerate(sentences):
            if citations_placed < num_citations and (idx % step == 0 or idx == len(sentences) - 1):
                citations_placed += 1
                author = author_pool[(citations_placed - 1) % len(author_pool)]
                journal = journal_pool[(citations_placed - 1) % len(journal_pool)]
                surname = author.split(",")[0].strip()

                title_terms = [w for w in re.findall(r"\b[A-Za-z]{4,}\b", sent) if w.lower() not in ("this", "that", "these", "their", "which", "there")]
                title_topic = " ".join(title_terms[:3]) if title_terms else "Empirical Methodology"
                title = f"A study on {title_topic.lower()}"

                cite_key = f"{surname}2024{re.sub(r'[^a-zA-Z0-9]', '', title_topic.title())}"
                bib_entry = self.generate_bibtex_entry(author=author, title=title, journal=journal, year=2024, key=cite_key)
                bib_entries.append(bib_entry)

                if "LaTeX" in citation_format or r"\cite" in citation_format:
                    marker = f" \\cite{{{cite_key}}}"
                elif "APA" in citation_format:
                    marker = f" ({surname} et al., 2024)"
                else:
                    marker = f" [{citations_placed}]"

                citation_records.append({
                    "id": citations_placed,
                    "key": cite_key,
                    "marker": marker.strip(),
                    "author": author,
                    "title": title,
                    "journal": journal,
                    "year": 2024
                })

                # Insert citation before punctuation
                if sent.endswith((".", "!", "?")):
                    cited_sent = sent[:-1] + marker + sent[-1]
                else:
                    cited_sent = sent + marker
                cited_sentences.append(cited_sent)
            else:
                cited_sentences.append(sent)

        # Assemble BibTeX bundle with standard AI Auto-fill instruction header
        bib_header = (
            "% ==============================================================================\n"
            "% 🤖 AI AUTO-FILL INSTRUCTIONS (CHATGPT / CLAUDE / GEMINI / DEEPSEEK)\n"
            "% ------------------------------------------------------------------------------\n"
            "% To replace these contextual placeholders with genuine published academic papers,\n"
            "% simply paste this entire file directly into your AI assistant without any extra prompt!\n"
            "% ==============================================================================\n\n"
        )
        full_bib = bib_header + "\n\n".join(bib_entries) + "\n"

        return {
            "cited_text": " ".join(cited_sentences),
            "bib_text": full_bib,
            "citations": citation_records,
            "citation_count": citations_placed,
            "discipline": target_disc
        }
