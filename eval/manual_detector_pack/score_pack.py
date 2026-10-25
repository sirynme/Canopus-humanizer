"""Ingests filled CSV and computes AUROC and TPR reductions for commercial detectors."""
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
