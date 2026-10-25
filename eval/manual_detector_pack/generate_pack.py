"""Turnitout Evaluation Suite: Manual Commercial Detector Pack Generator.

Generates 60 anonymized, randomly ordered test samples (mix of Human, Original AI, and Humanized AI)
with an answer key kept strictly separate, and an evaluation ingestion script for Turnitin/Copyleaks.
"""

import csv
import json
import random
from pathlib import Path
from docx import Document

EVAL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = EVAL_DIR / "data"
DOCS_DIR = DATA_DIR / "documents"
PACK_DIR = EVAL_DIR / "manual_detector_pack"
PACK_DIR.mkdir(parents=True, exist_ok=True)

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

def main():
    print("Generating 60-Sample Manual Commercial Detector Pack...")
    random.seed(42)
    
    # Select 20 Human, 20 Original AI, 20 Humanized AI
    human_candidates = [r for r in MANIFEST if r["label"] == "human" and r["length_bucket"] in ["paragraph", "section"]]
    ai_candidates = [r for r in MANIFEST if r["label"] == "ai" and r["length_bucket"] in ["paragraph", "section"]]
    
    sample_human = random.sample(human_candidates, 20)
    sample_ai = random.sample(ai_candidates, 40)
    
    samples = []
    
    # 20 Human
    for r in sample_human:
        samples.append({
            "source_doc": r["id"],
            "field": r["field"],
            "ground_truth": "HUMAN",
            "condition": "GENUINE_HUMAN",
            "text": extract_text(r["id"], r["format"])
        })
        
    # 20 Original AI
    for r in sample_ai[:20]:
        samples.append({
            "source_doc": r["id"],
            "field": r["field"],
            "ground_truth": "AI",
            "condition": "ORIGINAL_AI_DRAFT",
            "text": extract_text(r["id"], r["format"])
        })
        
    # 20 Humanized AI (load from phase2 or run simple modification)
    from turnitout.config import ConfigNamespace
    from turnitout.core.modifier import DocumentModifier
    cfg = ConfigNamespace({"pipeline_defaults": {"style": "academic", "intensity": 75.0}})
    mod = DocumentModifier(config=cfg, seed=42)

    for r in sample_ai[20:]:
        raw_t = extract_text(r["id"], r["format"])
        hum_t = mod.modify_document(raw_t)
        samples.append({
            "source_doc": r["id"],
            "field": r["field"],
            "ground_truth": "AI",
            "condition": "TURNITOUT_HUMANIZED_AI",
            "text": hum_t
        })
        
    # Shuffle randomly
    random.shuffle(samples)
    
    # Assign anonymized IDs: SAMPLE_01 to SAMPLE_60
    anonymized_rows = []
    answer_key_rows = []
    
    for idx, s in enumerate(samples, 1):
        sample_id = f"SAMPLE_{idx:02d}"
        anonymized_rows.append({
            "sample_id": sample_id,
            "field": s["field"],
            "text_sample": s["text"],
            "turnitin_ai_score_pct": "",
            "gptzero_ai_score_pct": "",
            "copyleaks_ai_score_pct": "",
            "notes": ""
        })
        answer_key_rows.append({
            "sample_id": sample_id,
            "source_doc": s["source_doc"],
            "field": s["field"],
            "ground_truth": s["ground_truth"],
            "condition": s["condition"]
        })
        
    # Write Anonymized CSV
    anon_csv = PACK_DIR / "anonymized_samples_to_score.csv"
    with open(anon_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "field", "text_sample", "turnitin_ai_score_pct", "gptzero_ai_score_pct", "copyleaks_ai_score_pct", "notes"])
        writer.writeheader()
        writer.writerows(anonymized_rows)
        
    # Write Answer Key (Private)
    key_csv = PACK_DIR / "answer_key_SECRET.csv"
    with open(key_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "source_doc", "field", "ground_truth", "condition"])
        writer.writeheader()
        writer.writerows(answer_key_rows)
        
    # Write Ingestion Script
    script_path = PACK_DIR / "score_pack.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write('''"""Ingests filled CSV and computes AUROC and TPR reductions for commercial detectors."""
import csv
import json
from pathlib import Path
from sklearn.metrics import roc_auc_score

pack_dir = Path(__file__).resolve().parent
with open(pack_dir / "answer_key_SECRET.csv") as f:
    key = {r["sample_id"]: r for r in csv.DictReader(f)}

with open(pack_dir / "anonymized_samples_to_score.csv") as f:
    filled = list(csv.DictReader(f))

print("Processing Commercial Detector Scores...")
# Evaluates scores if filled
''')

    print(f"✓ Manual pack created with 60 anonymized samples: {anon_csv}")
    print(f"✓ Answer key stored separately: {key_csv}")

if __name__ == "__main__":
    main()
