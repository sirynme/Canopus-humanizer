"""Turnitout Production Command-Line Interface.

Adheres strictly to GodGuide.md Section 6:
- Supports --max-aggressiveness, --disable-stages, --dry-run, --verbose.
- Detailed transformation counters breakdown and summary reporting.
"""

import argparse
import os
import sys
from pathlib import Path

# Auto-resolve src directory
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from turnitout.config import ConfigNamespace, GLOBAL_CONFIG
from turnitout.core.citation_engine import CitationEngine
from turnitout.core.doc_processor import DocumentProcessor
from turnitout.core.modifier import DocumentModifier


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="turnitout",
        description="Turnitout — Plagiarism & AI Detection Evasion Engine (Deterministic 17-Stage Pipeline)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", type=str, help="Plain text string to transform")
    group.add_argument("-f", "--file", type=str, help="Path to input file (.txt, .md, .tex, .docx)")

    parser.add_argument("-o", "--output", type=str, help="Path to output file")
    parser.add_argument("--intensity", type=float, default=70.0, help="Paraphrasing intensity (10.0 - 100.0, default: 70.0)")
    parser.add_argument("--style", type=str, default="academic", help="Target register (academic, conversational, technical)")
    parser.add_argument("--citations", type=int, default=0, help="Number of contextual citations to insert")
    parser.add_argument("--citation-format", type=str, default="IEEE [1]", help="Format: 'IEEE [1]', 'APA', or 'LaTeX \\cite{}'")
    parser.add_argument("--discipline", type=str, default=None, help="Academic discipline taxonomy override")
    
    # Flags required by GodGuide.md Section 6
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing output files")
    parser.add_argument("--verbose", action="store_true", help="Print detailed per-line modification logs during processing")
    parser.add_argument("--disable-stages", type=str, default="", help="Comma-separated stages to disable: voice,fusion,transition,reorder,nominal,appositive,discourse")
    parser.add_argument("--max-aggressiveness", action="store_true", help="Override all fire rates to maximum for maximum similarity reduction")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    config = ConfigNamespace()
    config.INTENSITY = args.intensity
    config.STYLE = args.style

    # Handle --disable-stages
    if args.disable_stages:
        stage_map = {
            "voice": "ENABLE_VOICE_TRANSFORM",
            "fusion": "ENABLE_SENTENCE_FUSION",
            "transition": "ENABLE_TRANSITION_INJECT",
            "reorder": "ENABLE_WORD_REORDER",
            "nominal": "ENABLE_NOMINALIZATION",
            "appositive": "ENABLE_APPOSITIVE",
            "discourse": "ENABLE_DISCOURSE_ROTATE",
        }
        for stage in args.disable_stages.split(","):
            stage_name = stage.strip().lower()
            if stage_name in stage_map:
                setattr(config, stage_map[stage_name], False)
                print(f"  [Disabled] {stage_name} transformation stage")

    # Handle --max-aggressiveness
    if args.max_aggressiveness:
        config.SYNONYM_ALIGNMENT = 0.95
        config.INTENSITY = 95.0
        config.VOICE_TRANSFORM_RATE = 0.90
        config.SENTENCE_FUSION_RATE = 0.80
        config.TRANSITION_INJECT_RATE = 0.80
        config.WORD_REORDER_RATE = 0.75
        config.NOMINALIZATION_RATE = 0.70
        config.APPOSITIVE_RATE = 0.85
        config.DISCOURSE_ROTATE_RATE = 0.95
        print("  [MAX AGGRESSIVENESS] All fire rates set to maximum (0.95)")

    modifier = DocumentModifier(config=config)
    processor = DocumentProcessor(modifier=modifier)

    print("\n⚡ [Turnitout Engine] Initializing Deterministic Pipeline...")

    # Load input
    if args.text:
        content = args.text
        ext = ".txt"
    else:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ Error: Input file '{args.file}' not found.")
            sys.exit(1)
        ext = file_path.suffix.lower()
        if ext == ".docx":
            content_bytes = file_path.read_bytes()
        else:
            content = file_path.read_text(encoding="utf-8")

    # Process
    enable_cites = args.citations > 0
    if ext == ".docx":
        res_bytes = processor.process_docx(
            content_bytes,
            enable_citations=enable_cites,
            citation_format=args.citation_format,
            max_citations=args.citations
        )
    elif ext == ".tex":
        res_text = processor.process_latex(
            content,
            enable_citations=enable_cites,
            citation_format=args.citation_format,
            max_citations=args.citations
        )
    elif ext == ".md":
        res_text = processor.process_markdown(
            content,
            enable_citations=enable_cites,
            citation_format=args.citation_format,
            max_citations=args.citations
        )
    else:
        res_text = processor.process_plain_text(
            content,
            enable_citations=enable_cites,
            citation_format=args.citation_format,
            max_citations=args.citations
        )

    # Print Verbose Changes Log
    if args.verbose:
        print("\n🔍 [Detailed Modification Trace]:")
        for log in modifier.changes_log[:50]:
            stage = log.get("stage", "edit")
            orig = log.get("from", "")
            repl = log.get("to", log.get("term", log.get("phrase", log.get("hedge", ""))))
            print(f"    [{stage}] {orig} → {repl}")

    # Output statistics breakdown required by GodGuide.md Section 6
    print("\n📊 [Transformation Statistics Summary]:")
    print(f"  Phrase rewrites:       {modifier.phrase_rewrite_count}")
    print(f"  Synonym substitutions: {modifier.synonym_count}")
    print(f"  Voice transforms:      {modifier.voice_transform_count}")
    print(f"  Sentence fusions:      {modifier.sentence_fusion_count}")
    print(f"  Transition injections: {modifier.transition_inject_count}")
    print(f"  Clause word reorders:  {modifier.clause_word_reorder_count}")
    print(f"  Nominalizations:       {modifier.nominalization_count}")
    print(f"  Appositive injections: {modifier.appositive_count}")
    print(f"  Discourse rotations:   {modifier.discourse_rotate_count}")
    print(f"  Determiner swaps:      {modifier.determiner_swap_count}")
    print(f"  Compound splits:       {modifier.compound_split_count}")
    print(f"  Hedge word injections: {modifier.hedge_word_count}")
    print(f"  Citations inserted:    {modifier.citation_count}")
    print(f"  --------------------------------------------------")
    print(f"  TOTAL MODIFICATIONS:   {modifier.total_transforms}")

    # Write output
    if args.dry_run:
        print("\n⚠️  [DRY RUN] Preview mode enabled — no output files were written.")
        if ext != ".docx":
            print("\nPreview Output:\n" + ("=" * 40))
            print(res_text[:600] + ("..." if len(res_text) > 600 else ""))
    else:
        if args.output:
            out_path = Path(args.output)
            if ext == ".docx":
                out_path.write_bytes(res_bytes)
            else:
                out_path.write_text(res_text, encoding="utf-8")
            print(f"\n✅ Successfully saved processed document to: {args.output}")
        elif args.text:
            print("\nHumanized Output:\n" + ("=" * 40))
            print(res_text)


if __name__ == "__main__":
    main()
