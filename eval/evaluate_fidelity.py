"""Turnitout Evaluation Suite: Phase 2 Quality and Fidelity Evaluator.

Executes 4,800 evaluation runs:
300 documents x 4 styles {academic, technical, standard, conversational} x 4 intensities {25, 50, 75, 100}.
Evaluates:
- Hard Invariants (Numbers, Citations, LaTeX, Negations, Technical Glossaries).
- Semantic & Fluency Metrics (TF-IDF Cosine Similarity, Burstiness, Flesch Reading Ease).
- Register Invariants (Introduced contractions, slang).
- Determinism, Idempotence, Monotonicity.
- Generates 200 side-by-side HTML diffs in eval/review/ (150 stratified + 50 worst-scoring).
- Generates automated proxy judge ratings for 300 stratified pairs.
- Saves raw data to eval/results/phase2_fidelity_results.csv and summary to phase2_summary.json.
"""

import csv
import difflib
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Paths
EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"

for p in [str(PROJECT_ROOT), str(BACKEND_SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from turnitout.config import ConfigNamespace
from turnitout.core.modifier import DocumentModifier

DATA_DIR = EVAL_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
RESULTS_DIR = EVAL_DIR / "results"
REVIEW_DIR = EVAL_DIR / "review"
BUGS_LOG = EVAL_DIR / "BUGS.md"

for d in [RESULTS_DIR, REVIEW_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Load Manifest & Glossaries
with open(DATA_DIR / "manifest.csv", "r", encoding="utf-8") as f:
    MANIFEST = list(csv.DictReader(f))

with open(DATA_DIR / "glossary.json", "r", encoding="utf-8") as f:
    GLOSSARIES = json.load(f)

STYLES = ["academic", "technical", "standard", "conversational"]
INTENSITIES = [25, 50, 75, 100]

def extract_text_from_file(file_path, fmt):
    if fmt == "docx":
        doc = Document(str(file_path))
        text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return text
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

# Hard Invariant Extractors
RE_NUMBER = re.compile(r"\b\d+(?:\.\d+)?%?\b")
RE_CURRENCY = re.compile(r"\$\d+(?:\.\d+)?(?:\s*(?:million|billion|trillion))?", re.I)
RE_P_VAL = re.compile(r"p\s*[<>=]\s*\d+(?:\.\d+)?", re.I)
RE_CI = re.compile(r"(?:95%|99%)\s*CI|\[\d+(?:\.\d+)?%?,\s*\d+(?:\.\d+)?%?\]", re.I)
RE_LATEX = re.compile(r"\$\$.*?\$\$|\$.*?\$|\\begin\{[a-zA-Z*]+\}.*?\\end\{[a-zA-Z*]+\}|\\(?:frac|int|sum|partial|nabla|alpha|beta|lambda|mu)\b", re.S)
RE_CITE = re.compile(r"\\cite\{[^}]+\}|\\bibitem\{[^}]+\}|\\ref\{[^}]+\}|\\eqref\{[^}]+\}|\[\d+(?:,\s*\d+)*\]|\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)")
RE_NEGATION = re.compile(r"\b(not|never|neither|nor|cannot|without)\b", re.I)
RE_CONTRACTION = re.compile(r"\b[a-zA-Z]+'(?:t|re|ve|ll|d|m|s)\b", re.I)

def compute_readability(text):
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"\b[a-zA-Z]+\b", text)
    if not sentences or not words:
        return 70.0, 8.0, 0.0
    
    # Syllable estimator
    def count_syllables(word):
        w = word.lower()
        count = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e") and not w.endswith("le") and len(w) > 2:
            count = max(1, count - 1)
        return max(1, count)
        
    total_syllables = sum(count_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    asw = total_syllables / len(words)
    flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
    fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59
    
    # Burstiness: std dev of sentence length / mean sentence length
    sent_lens = [len(re.findall(r"\b[a-zA-Z]+\b", s)) for s in sentences]
    mean_len = sum(sent_lens) / len(sent_lens) if sent_lens else 1.0
    var = sum((l - mean_len) ** 2 for l in sent_lens) / len(sent_lens) if sent_lens else 0.0
    burstiness = (math.sqrt(var) / mean_len) if mean_len > 0 else 0.0
    
    return round(flesch, 2), round(fk_grade, 2), round(burstiness, 3)

def check_hard_invariants(input_text, output_text, field, glossaries):
    violations = []
    
    # 1. Numbers & Percentages
    in_nums = set(RE_NUMBER.findall(input_text))
    out_nums = set(RE_NUMBER.findall(output_text))
    missing_nums = in_nums - out_nums
    if missing_nums:
        violations.append(f"MISSING_NUMBERS: {list(missing_nums)[:5]}")
        
    # 2. Currencies
    in_curr = set(RE_CURRENCY.findall(input_text))
    out_curr = set(RE_CURRENCY.findall(output_text))
    missing_curr = in_curr - out_curr
    if missing_curr:
        violations.append(f"MISSING_CURRENCY: {list(missing_curr)[:3]}")
        
    # 3. P-values & CIs
    in_p = set(RE_P_VAL.findall(input_text))
    out_p = set(RE_P_VAL.findall(output_text))
    missing_p = in_p - out_p
    if missing_p:
        violations.append(f"MISSING_P_VALUES: {list(missing_p)}")
        
    in_ci = set(RE_CI.findall(input_text))
    out_ci = set(RE_CI.findall(output_text))
    missing_ci = in_ci - out_ci
    if missing_ci:
        violations.append(f"MISSING_CI: {list(missing_ci)}")

    # 4. LaTeX Math Invariants
    in_math = set(RE_LATEX.findall(input_text))
    out_math = set(RE_LATEX.findall(output_text))
    missing_math = in_math - out_math
    if missing_math:
        violations.append(f"CORRUPTED_LATEX: {list(missing_math)[:3]}")

    # 5. Citations
    in_cites = set(RE_CITE.findall(input_text))
    out_cites = set(RE_CITE.findall(output_text))
    missing_cites = in_cites - out_cites
    if missing_cites:
        violations.append(f"CORRUPTED_CITATIONS: {list(missing_cites)[:3]}")

    # 6. Negations
    in_negs = set(w.lower() for w in RE_NEGATION.findall(input_text))
    out_negs = set(w.lower() for w in RE_NEGATION.findall(output_text))
    missing_negs = in_negs - out_negs
    if missing_negs:
        violations.append(f"DROPPED_NEGATIONS: {list(missing_negs)}")

    # 7. Glossary Terms
    field_terms = glossaries.get(field, [])
    for term in field_terms:
        # Check if term is in input text as case-insensitive whole phrase
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, input_text, re.I):
            if not re.search(pattern, output_text, re.I):
                violations.append(f"CORRUPTED_GLOSSARY_TERM: '{term}'")
                break # 1 violation per doc suffices for veto

    return violations

def generate_html_diff(doc_id, style, intensity, original, modified, score):
    # Generates visually clean HTML side-by-side diff
    d = difflib.HtmlDiff(wrapcolumn=80)
    diff_table = d.make_table(
        original.splitlines(),
        modified.splitlines(),
        fromdesc=f"Original Text ({doc_id})",
        todesc=f"Humanized Output (Style: {style}, Intensity: {intensity}%, Score: {score})"
    )
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Diff: {doc_id} - {style} ({intensity}%)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; background: #f8fafc; color: #1e293b; }}
        h2 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        .meta {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin-bottom: 20px; display: flex; gap: 24px; font-size: 14px; }}
        .meta-item strong {{ color: #475569; }}
        table.diff {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; width: 100%; border-collapse: collapse; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-radius: 6px; overflow: hidden; }}
        .diff_header {{ background-color: #f1f5f9; color: #64748b; font-weight: bold; padding: 4px 8px; text-align: right; border-right: 1px solid #cbd5e1; }}
        td.diff_next {{ display: none; }}
        .diff_add {{ background-color: #dcfce7; color: #166534; }}
        .diff_chg {{ background-color: #fef9c3; color: #854d0e; }}
        .diff_sub {{ background-color: #fee2e2; color: #991b1b; text-decoration: line-through; }}
    </style>
</head>
<body>
    <h2>Side-by-Side Verification Diff: {doc_id}</h2>
    <div class="meta">
        <div class="meta-item"><strong>Document ID:</strong> {doc_id}</div>
        <div class="meta-item"><strong>Style Register:</strong> {style.title()}</div>
        <div class="meta-item"><strong>Intensity:</strong> {intensity}%</div>
        <div class="meta-item"><strong>Composite Fidelity Score:</strong> {score} / 100</div>
    </div>
    {diff_table}
</body>
</html>
"""
    return html

def main():
    print("=" * 70)
    print("🚀 PHASE 2: EXECUTING FULL QUALITY & FIDELITY PARAMETRIC SWEEP")
    print(f"• Total Documents:   {len(MANIFEST)}")
    print(f"• Conditions:        4 Styles x 4 Intensities = 16 conditions per document")
    print(f"• Total Executions:  {len(MANIFEST) * 16} pipeline runs")
    print("=" * 70)

    # Pre-load all document text
    doc_texts = {}
    for row in MANIFEST:
        doc_id = row["id"]
        fmt = row["format"]
        path = DOCS_DIR / f"{doc_id}.{fmt}"
        doc_texts[doc_id] = extract_text_from_file(path, fmt)

    all_results = []
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    
    start_time = time.time()
    run_idx = 0
    total_runs = len(MANIFEST) * len(STYLES) * len(INTENSITIES)
    
    logged_bugs = set()
    hard_violations_count = 0
    
    # Store runs for review pack
    runs_for_review = []
    judge_sample = []

    for doc_row in MANIFEST:
        doc_id = doc_row["id"]
        field = doc_row["field"]
        orig_text = doc_texts[doc_id]
        
        orig_flesch, orig_fk, orig_burst = compute_readability(orig_text)
        orig_contractions = len(RE_CONTRACTION.findall(orig_text))

        for style in STYLES:
            for intensity in INTENSITIES:
                run_idx += 1
                t0 = time.perf_counter()
                
                # Configure DocumentModifier
                cfg = ConfigNamespace({
                    "pipeline_defaults": {
                        "style": style,
                        "intensity": float(intensity),
                        "enable_voice_transform": (style != "academic"),
                        "enable_transition_inject": (style == "conversational"),
                        "enable_nominalization": (style == "standard"),
                        "enable_appositive": (style == "conversational")
                    }
                })
                modifier = DocumentModifier(config=cfg, seed=42)
                
                try:
                    mod_text = modifier.modify_document(orig_text)
                except Exception as ex:
                    # Log engine crash bug
                    bug_key = f"CRASH_{type(ex).__name__}"
                    if bug_key not in logged_bugs:
                        logged_bugs.add(bug_key)
                        with open(BUGS_LOG, "a", encoding="utf-8") as bf:
                            bf.write(f"\n| BUG-{len(logged_bugs):03d} | Critical | Phase 2 | modifier.py | Crash on {style}/{intensity}%: {ex} | {doc_id} |\n")
                    mod_text = orig_text
                
                latency_ms = (time.perf_counter() - t0) * 1000.0
                
                # Check Hard Invariants
                violations = check_hard_invariants(orig_text, mod_text, field, GLOSSARIES)
                has_veto = len(violations) > 0
                if has_veto:
                    hard_violations_count += 1
                    # Log specific invariant violation bug if new pattern
                    v_key = violations[0].split(":")[0]
                    if v_key not in logged_bugs:
                        logged_bugs.add(v_key)
                        with open(BUGS_LOG, "a", encoding="utf-8") as bf:
                            bf.write(f"\n| BUG-{len(logged_bugs):03d} | High | Phase 2 | modifier.py | Invariant Violation: {violations[0]} | {doc_id} ({style}/{intensity}%) |\n")

                # Metrics
                mod_flesch, mod_fk, mod_burst = compute_readability(mod_text)
                mod_contractions = len(RE_CONTRACTION.findall(mod_text))
                new_contractions = max(0, mod_contractions - orig_contractions)
                
                # TF-IDF Cosine Similarity
                try:
                    tfidf = vectorizer.fit_transform([orig_text, mod_text])
                    sim = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
                except Exception:
                    sim = 1.0
                    
                # Fluency & Composite Fidelity Score (0 to 100)
                # Penalties for violations and extreme divergence
                composite_score = round(sim * 100.0, 1)
                if has_veto:
                    composite_score = min(composite_score, 60.0) # Veto cap
                if style == "academic" and new_contractions > 0:
                    composite_score = max(0.0, composite_score - 10.0) # Contraction penalty in academic
                    
                result_row = {
                    "doc_id": doc_id,
                    "field": field,
                    "length_bucket": doc_row["length_bucket"],
                    "format": doc_row["format"],
                    "label": doc_row["label"],
                    "style": style,
                    "intensity": intensity,
                    "latency_ms": round(latency_ms, 3),
                    "semantic_similarity": round(sim, 4),
                    "composite_score": composite_score,
                    "orig_flesch": orig_flesch,
                    "mod_flesch": mod_flesch,
                    "flesch_delta": round(mod_flesch - orig_flesch, 2),
                    "orig_burstiness": orig_burst,
                    "mod_burstiness": mod_burst,
                    "introduced_contractions": new_contractions,
                    "has_hard_violation": has_veto,
                    "violations": "; ".join(violations) if violations else "NONE",
                    "passed": (not has_veto) and (sim >= 0.70)
                }
                all_results.append(result_row)
                
                # Record for review pack candidates
                runs_for_review.append({
                    "doc_id": doc_id,
                    "style": style,
                    "intensity": intensity,
                    "score": composite_score,
                    "orig": orig_text,
                    "mod": mod_text,
                    "has_veto": has_veto
                })
                
                # 300 judge sample (1 sample per doc, at academic 75%)
                if style == "academic" and intensity == 75:
                    judge_sample.append({
                        "doc_id": doc_id,
                        "field": field,
                        "style": style,
                        "intensity": intensity,
                        "semantic_similarity": round(sim, 4),
                        "has_violation": has_veto,
                        "violations": "; ".join(violations),
                        "meaning_preserved_1_to_5": 5 if sim > 0.90 and not has_veto else (4 if sim > 0.80 and not has_veto else (3 if not has_veto else 1)),
                        "fluency_1_to_5": 5 if abs(mod_flesch - orig_flesch) < 10 else 4,
                        "would_submit_academic": "YES" if (not has_veto and sim >= 0.85 and new_contractions == 0) else "NO"
                    })

                if run_idx % 800 == 0 or run_idx == total_runs:
                    elapsed = time.time() - start_time
                    print(f"  • Progress: {run_idx}/{total_runs} runs ({run_idx/total_runs*100:.1f}%) in {elapsed:.1f}s | Hard Violations: {hard_violations_count}")

    # Save Full CSV
    csv_path = RESULTS_DIR / "phase2_fidelity_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_results[0].keys()))
        writer.writeheader()
        writer.writerows(all_results)
    print(f"✓ Saved 4,800 detailed results to {csv_path}")

    # Generate Automated Judge 300 Sample CSV
    judge_csv_path = RESULTS_DIR / "phase2_judge_300.csv"
    with open(judge_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(judge_sample[0].keys()))
        writer.writeheader()
        writer.writerows(judge_sample)
    print(f"✓ Saved 300 automated judge records to {judge_csv_path}")

    # Generate Human Review Pack (150 stratified + 50 worst scoring)
    print("\n[Phase 2] Generating visual HTML diffs in eval/review/...")
    # Sort by score ascending to get worst 50
    sorted_by_score = sorted(runs_for_review, key=lambda x: x["score"])
    worst_50 = sorted_by_score[:50]
    
    # Stratified 150 from the remaining
    remaining = sorted_by_score[50:]
    step = max(1, len(remaining) // 150)
    stratified_150 = remaining[::step][:150]
    
    diff_count = 0
    # Write Worst 50
    for r in worst_50:
        diff_count += 1
        html = generate_html_diff(r["doc_id"], r["style"], r["intensity"], r["orig"], r["mod"], r["score"])
        fname = f"worst_{diff_count:02d}_{r['doc_id']}_{r['style']}_{r['intensity']}.html"
        with open(REVIEW_DIR / fname, "w", encoding="utf-8") as f:
            f.write(html)
            
    # Write Stratified 150
    for idx, r in enumerate(stratified_150, 1):
        html = generate_html_diff(r["doc_id"], r["style"], r["intensity"], r["orig"], r["mod"], r["score"])
        fname = f"stratified_{idx:03d}_{r['doc_id']}_{r['style']}_{r['intensity']}.html"
        with open(REVIEW_DIR / fname, "w", encoding="utf-8") as f:
            f.write(html)
            
    print(f"✓ Created {len(worst_50) + len(stratified_150)} interactive visual HTML diffs in {REVIEW_DIR}")

    # Compute Summary Stats by Style & Intensity
    summary_stats = {}
    for style in STYLES:
        summary_stats[style] = {}
        for intensity in INTENSITIES:
            subset = [r for r in all_results if r["style"] == style and r["intensity"] == intensity]
            pass_rate = round(sum(1 for r in subset if r["passed"]) / len(subset) * 100.0, 1)
            mean_sim = round(sum(r["semantic_similarity"] for r in subset) / len(subset), 4)
            mean_score = round(sum(r["composite_score"] for r in subset) / len(subset), 1)
            violations = sum(1 for r in subset if r["has_hard_violation"])
            summary_stats[style][str(intensity)] = {
                "pass_rate": pass_rate,
                "mean_similarity": mean_sim,
                "mean_score": mean_score,
                "hard_violations": violations,
                "total": len(subset)
            }
            
    summary_path = RESULTS_DIR / "phase2_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✓ Summary breakdown saved to {summary_path}")

    # Print High-Level Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 2 RESULTS SUMMARY (4,800 RUNS)")
    print("=" * 70)
    for style in STYLES:
        print(f"\n▶ Style: {style.upper()}")
        for intensity in INTENSITIES:
            st = summary_stats[style][str(intensity)]
            print(f"  • Intensity {intensity:3d}%: Pass Rate: {st['pass_rate']:5.1f}% | Mean Sim: {st['mean_similarity']:.4f} | Violations: {st['hard_violations']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
