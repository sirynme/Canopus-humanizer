"""Turnitout Evaluation Suite: Phase 3 Detector Evaluation & Forensic Fingerprint.

Evaluates AI detection efficacy, false positive rates, and forensic signatures:
1. ZipPy Perplexity & Shannon Entropy Detector (repo's proxy).
2. Karp-Rabin Winnowing Local Similarity Index.
3. Forensic Fingerprint Classifier (TF-IDF + Logistic Regression on held-out split):
   - Measures if humanizer leaves an identifiable signature.
   - Extracts top 20 predictive features exposing Turnitout output.
4. Evaluates:
   - AUROC {human vs AI}.
   - TPR @ 1% and 5% FPR for original AI vs humanized AI.
   - FPR on genuine human text and non-native English text.
   - Degradation test: does humanizing human text increase AI false positive scores?
   - Length sensitivity (sentence vs paragraph vs section vs long vs full paper).
5. Commercial Detectors (GPTZero, Copyleaks, Originality.ai, Sapling):
   - Marked "NOT RUN (no public API key provided)" in accordance with ground rules.
"""

import csv
import json
import math
import os
import random
import sys
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from docx import Document

# Paths
EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"

for p in [str(PROJECT_ROOT), str(BACKEND_SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from turnitout.core.checker import ZipPyChecker
from turnitout.core.winnowing import WinnowingEngine
from turnitout.config import ConfigNamespace
from turnitout.core.modifier import DocumentModifier

DATA_DIR = EVAL_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
RESULTS_DIR = EVAL_DIR / "results"

with open(DATA_DIR / "manifest.csv", "r", encoding="utf-8") as f:
    MANIFEST = list(csv.DictReader(f))

def extract_text(doc_id, fmt):
    path = DOCS_DIR / f"{doc_id}.{fmt}"
    if fmt == "docx":
        doc = Document(str(path))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def compute_tpr_at_fixed_fpr(y_true, y_scores, target_fpr):
    # Computes TPR at specific FPR (e.g. 0.01 or 0.05)
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    # Find closest FPR <= target_fpr
    valid_indices = [i for i, f in enumerate(fpr) if f <= target_fpr]
    if not valid_indices:
        return 0.0
    best_idx = valid_indices[-1]
    return float(tpr[best_idx])

def main():
    print("=" * 70)
    print("🔍 PHASE 3: DETECTOR EVALUATION & FORENSIC FINGERPRINT AUDIT")
    print("=" * 70)

    # 1. Prepare Evaluated Datasets
    # Load texts
    records = []
    print("[Phase 3.1] Loading and humanizing test partitions...")
    
    # We evaluate Academic 75% as primary benchmark, plus sample across styles
    cfg_academic = ConfigNamespace({"pipeline_defaults": {"style": "academic", "intensity": 75.0}})
    mod_academic = DocumentModifier(config=cfg_academic, seed=42)

    cfg_conversational = ConfigNamespace({
        "pipeline_defaults": {
            "style": "conversational",
            "intensity": 75.0,
            "enable_transition_inject": True,
            "enable_appositive": True
        }
    })
    mod_conversational = DocumentModifier(config=cfg_conversational, seed=42)
    winnow_engine = WinnowingEngine()

    for row in MANIFEST:
        doc_id = row["id"]
        fmt = row["format"]
        label = row["label"]
        field = row["field"]
        source = row["source"]
        length = row["length_bucket"]
        
        orig_text = extract_text(doc_id, fmt)
        if not orig_text or len(orig_text.strip()) < 10:
            continue
            
        # Evaluate ZipPy on original
        res_orig = ZipPyChecker.evaluate(orig_text)
        
        # Humanize text
        hum_text_acad = mod_academic.modify_document(orig_text)
        res_hum_acad = ZipPyChecker.evaluate(hum_text_acad)

        hum_text_conv = mod_conversational.modify_document(orig_text)
        res_hum_conv = ZipPyChecker.evaluate(hum_text_conv)

        # Winnowing overlap
        winnow_orig_vs_acad, _, _ = winnow_engine.calculate_similarity(orig_text, hum_text_acad)
        winnow_orig_vs_conv, _, _ = winnow_engine.calculate_similarity(orig_text, hum_text_conv)

        records.append({
            "doc_id": doc_id,
            "field": field,
            "label": label, # human or ai
            "source": source,
            "length_bucket": length,
            "orig_ai_prob": res_orig["ai_probability"],
            "orig_entropy": res_orig["shannon_entropy"],
            "orig_compression": res_orig["zlib_compression_ratio"],
            "acad_ai_prob": res_hum_acad["ai_probability"],
            "acad_entropy": res_hum_acad["shannon_entropy"],
            "acad_compression": res_hum_acad["zlib_compression_ratio"],
            "acad_winnowing_overlap": winnow_orig_vs_acad,
            "conv_ai_prob": res_hum_conv["ai_probability"],
            "conv_entropy": res_hum_conv["shannon_entropy"],
            "conv_winnowing_overlap": winnow_orig_vs_conv,
            "orig_text": orig_text,
            "acad_text": hum_text_acad,
            "conv_text": hum_text_conv
        })

    print(f"✓ Processed {len(records)} documents through detection & information theory evaluation.")

    # 2. Benchmark Statistical AUROC & TPR/FPR
    # Ground truth: 1 for AI, 0 for Human
    y_true_orig = [1 if r["label"] == "ai" else 0 for r in records]
    scores_orig = [r["orig_ai_prob"] / 100.0 for r in records]

    # Scores of humanized AI text evaluated against human text
    human_scores = [r["orig_ai_prob"] / 100.0 for r in records if r["label"] == "human"]
    human_scores_after_hum = [r["acad_ai_prob"] / 100.0 for r in records if r["label"] == "human"]
    ai_scores_orig = [r["orig_ai_prob"] / 100.0 for r in records if r["label"] == "ai"]
    ai_scores_acad = [r["acad_ai_prob"] / 100.0 for r in records if r["label"] == "ai"]
    ai_scores_conv = [r["conv_ai_prob"] / 100.0 for r in records if r["label"] == "ai"]

    # Non-native English false positives
    non_native_records = [r for r in records if "non_native" in r["source"]]
    non_native_fp_orig = sum(1 for r in non_native_records if r["orig_ai_prob"] > 50.0) / len(non_native_records) if non_native_records else 0.0
    non_native_fp_acad = sum(1 for r in non_native_records if r["acad_ai_prob"] > 50.0) / len(non_native_records) if non_native_records else 0.0

    # AUROC {Human vs Original AI}
    auroc_orig = roc_auc_score(y_true_orig, scores_orig)

    # AUROC {Human vs Academic Humanized AI}
    y_eval_acad = [0] * len(human_scores) + [1] * len(ai_scores_acad)
    scores_eval_acad = human_scores + ai_scores_acad
    auroc_acad = roc_auc_score(y_eval_acad, scores_eval_acad)

    # AUROC {Human vs Conversational Humanized AI}
    y_eval_conv = [0] * len(human_scores) + [1] * len(ai_scores_conv)
    scores_eval_conv = human_scores + ai_scores_conv
    auroc_conv = roc_auc_score(y_eval_conv, scores_eval_conv)

    # TPR @ 1% and 5% FPR
    tpr_1pct_orig = compute_tpr_at_fixed_fpr(y_true_orig, scores_orig, 0.01)
    tpr_5pct_orig = compute_tpr_at_fixed_fpr(y_true_orig, scores_orig, 0.05)
    tpr_1pct_acad = compute_tpr_at_fixed_fpr(y_eval_acad, scores_eval_acad, 0.01)
    tpr_5pct_acad = compute_tpr_at_fixed_fpr(y_eval_acad, scores_eval_acad, 0.05)

    # FPR on Human text (threshold = 0.50)
    fpr_human_baseline = sum(1 for s in human_scores if s > 0.50) / len(human_scores) if human_scores else 0.0
    fpr_human_after_tool = sum(1 for s in human_scores_after_hum if s > 0.50) / len(human_scores_after_hum) if human_scores_after_hum else 0.0

    # Average AI Probability Reduction
    mean_ai_prob_orig = float(np.mean(ai_scores_orig)) * 100.0
    mean_ai_prob_acad = float(np.mean(ai_scores_acad)) * 100.0
    mean_ai_prob_conv = float(np.mean(ai_scores_conv)) * 100.0
    ai_prob_reduction_acad = round(mean_ai_prob_orig - mean_ai_prob_acad, 1)
    ai_prob_reduction_conv = round(mean_ai_prob_orig - mean_ai_prob_conv, 1)

    print("\n" + "-" * 70)
    print("DETECTOR PERFORMANCE METRICS")
    print("-" * 70)
    print(f"• Baseline AUROC (Human vs Original AI):      {auroc_orig:.4f}")
    print(f"• Academic AUROC (Human vs Humanized AI):    {auroc_acad:.4f} (Delta: {auroc_acad - auroc_orig:+.4f})")
    print(f"• Conversational AUROC:                      {auroc_conv:.4f} (Delta: {auroc_conv - auroc_orig:+.4f})")
    print(f"• TPR @ 1% FPR:  Original: {tpr_1pct_orig*100:.1f}%  ->  Academic Humanized: {tpr_1pct_acad*100:.1f}%")
    print(f"• TPR @ 5% FPR:  Original: {tpr_5pct_orig*100:.1f}%  ->  Academic Humanized: {tpr_5pct_acad*100:.1f}%")
    print(f"• Mean AI Probability on AI Drafts:           {mean_ai_prob_orig:.1f}% -> {mean_ai_prob_acad:.1f}% (Drop: {ai_prob_reduction_acad}%)")
    print(f"• False Positive Rate on Genuine Human Text:  {fpr_human_baseline*100:.1f}% (Baseline) -> {fpr_human_after_tool*100:.1f}% (Post-Humanized)")
    print(f"• False Positive Rate on Non-Native English:  {non_native_fp_orig*100:.1f}% (Baseline) -> {non_native_fp_acad*100:.1f}% (Post-Humanized)")
    print("-" * 70)

    # 3. Forensic Fingerprint Test (TF-IDF + Logistic Regression Classifier)
    print("\n[Phase 3.2] Training Forensic Fingerprint Classifier (Human vs Humanizer Output)...")
    
    # Dataset: Genuine human texts (label 0) vs Turnitout humanized texts (label 1)
    fingerprint_texts = []
    fingerprint_labels = []
    
    for r in records:
        if r["label"] == "human":
            fingerprint_texts.append(r["orig_text"])
            fingerprint_labels.append(0) # Genuine Human
        fingerprint_texts.append(r["acad_text"])
        fingerprint_labels.append(1) # Humanizer Output

    X_train, X_test, y_train, y_test = train_test_split(
        fingerprint_texts, fingerprint_labels, test_size=0.25, random_state=42, stratify=fingerprint_labels
    )

    tfidf_clf = TfidfVectorizer(max_features=2500, ngram_range=(1, 3))
    X_train_vec = tfidf_clf.fit_transform(X_train)
    X_test_vec = tfidf_clf.transform(X_test)

    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_vec, y_train)

    train_acc = clf.score(X_train_vec, y_train)
    test_acc = clf.score(X_test_vec, y_test)
    y_test_probs = clf.predict_proba(X_test_vec)[:, 1]
    fp_roc_auc = roc_auc_score(y_test, y_test_probs)

    print(f"✓ Forensic Classifier Test Accuracy: {test_acc*100:.1f}% | ROC-AUC: {fp_roc_auc:.4f}")

    # Top Features
    feature_names = tfidf_clf.get_feature_names_out()
    coefs = clf.coef_[0]
    top_humanizer_indices = np.argsort(coefs)[-20:][::-1]
    top_human_indices = np.argsort(coefs)[:20]

    top_features = []
    for idx in top_humanizer_indices:
        top_features.append({
            "feature": feature_names[idx],
            "coefficient": round(float(coefs[idx]), 4),
            "indicates": "Humanizer Signature"
        })
    for idx in top_human_indices:
        top_features.append({
            "feature": feature_names[idx],
            "coefficient": round(float(coefs[idx]), 4),
            "indicates": "Genuine Human Anchor"
        })

    # Save Top Features CSV
    feat_csv_path = RESULTS_DIR / "phase3_top_fingerprint_features.csv"
    with open(feat_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["feature", "coefficient", "indicates"])
        writer.writeheader()
        writer.writerows(top_features)
    print(f"✓ Saved top 40 fingerprint features to {feat_csv_path}")

    # 4. Save Detector Results CSV
    csv_rows = []
    for r in records:
        csv_rows.append({
            "doc_id": r["doc_id"],
            "field": r["field"],
            "label": r["label"],
            "source": r["source"],
            "length_bucket": r["length_bucket"],
            "orig_ai_prob": r["orig_ai_prob"],
            "acad_ai_prob": r["acad_ai_prob"],
            "conv_ai_prob": r["conv_ai_prob"],
            "acad_ai_reduction": round(r["orig_ai_prob"] - r["acad_ai_prob"], 1),
            "acad_winnowing_overlap": round(r["acad_winnowing_overlap"], 4),
            "conv_winnowing_overlap": round(r["conv_winnowing_overlap"], 4),
            "orig_entropy": r["orig_entropy"],
            "acad_entropy": r["acad_entropy"],
            "orig_compression": r["orig_compression"],
            "acad_compression": r["acad_compression"]
        })
    
    det_csv_path = RESULTS_DIR / "phase3_detector_results.csv"
    with open(det_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"✓ Saved detailed detector evaluations to {det_csv_path}")

    # 5. Save Summary JSON
    summary = {
        "commercial_detectors": {
            "GPTZero": "NOT RUN (no public API key provided)",
            "Originality.ai": "NOT RUN (no public API key provided)",
            "Copyleaks": "NOT RUN (no public API key provided)",
            "Sapling": "NOT RUN (no public API key provided)"
        },
        "zippy_metrics": {
            "baseline_auroc": round(auroc_orig, 4),
            "academic_auroc": round(auroc_acad, 4),
            "conversational_auroc": round(auroc_conv, 4),
            "tpr_at_1pct_fpr_original": round(tpr_1pct_orig, 4),
            "tpr_at_1pct_fpr_academic": round(tpr_1pct_acad, 4),
            "tpr_at_5pct_fpr_original": round(tpr_5pct_orig, 4),
            "tpr_at_5pct_fpr_academic": round(tpr_5pct_acad, 4),
            "mean_ai_prob_original": round(mean_ai_prob_orig, 1),
            "mean_ai_prob_academic": round(mean_ai_prob_acad, 1),
            "mean_ai_prob_conversational": round(mean_ai_prob_conv, 1),
            "mean_ai_reduction_academic": ai_prob_reduction_acad,
            "mean_ai_reduction_conversational": ai_prob_reduction_conv,
            "human_false_positive_baseline": round(fpr_human_baseline * 100.0, 1),
            "human_false_positive_post_tool": round(fpr_human_after_tool * 100.0, 1),
            "non_native_false_positive_baseline": round(non_native_fp_orig * 100.0, 1),
            "non_native_false_positive_post_tool": round(non_native_fp_acad * 100.0, 1)
        },
        "forensic_fingerprint_test": {
            "test_accuracy": round(test_acc * 100.0, 1),
            "roc_auc": round(fp_roc_auc, 4),
            "is_vulnerable_to_fingerprinting": bool(test_acc > 75.0),
            "top_humanizer_signatures": [f["feature"] for f in top_features if f["indicates"] == "Humanizer Signature"][:10]
        }
    }

    sum_path = RESULTS_DIR / "phase3_summary.json"
    with open(sum_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved Phase 3 summary to {sum_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
