"""Turnitout Evaluation Suite: Master Orchestrator.

One command that reproduces everything end-to-end with --resume support:
Usage: python3 eval/run_all.py [--resume]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_DIR.parent
PYTHON_EXE = EVAL_DIR / ".venv" / "bin" / "python"
CHECKPOINT_FILE = EVAL_DIR / "results" / "checkpoint.json"

PHASES = [
    ("Phase 1: Corpus Construction", "build_corpus.py"),
    ("Phase 2: Quality & Fidelity Parametric Sweep", "evaluate_fidelity.py"),
    ("Phase 3: Detector Evaluation & Forensic Signature", "evaluate_detectors.py"),
    ("Phase 4: Scale, Robustness, Concurrency & Security", "evaluate_scale_robustness.py"),
    ("Phase 5: Real Full-Paper Integrity Tests", "evaluate_full_papers.py"),
    ("Phase 6: Final Verdict & Master Deliverables", "generate_final_report.py")
]

def load_checkpoints():
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_checkpoint(phase_name):
    cp = load_checkpoints()
    cp[phase_name] = {"completed_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Turnitout Master Evaluation Runner")
    parser.add_argument("--resume", action="store_true", help="Resume from last completed checkpoint")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🛡️  TURNITOUT INDEPENDENT LARGE-SCALE EVALUATION SUITE")
    print("=" * 70)
    print(f"• Mode:          {'Resume from Checkpoint' if args.resume else 'Full Sequential Execution'}")
    print(f"• Interpreter:   {PYTHON_EXE}")
    print(f"• Base Directory: {EVAL_DIR}")
    print("=" * 70 + "\n")

    completed = load_checkpoints() if args.resume else {}

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'backend' / 'src'}:{PROJECT_ROOT}"

    start_total = time.time()

    for phase_title, script_name in PHASES:
        if args.resume and phase_title in completed:
            print(f"⏩ Skipping {phase_title} (Already completed at {completed[phase_title].get('completed_at')})")
            continue

        print(f"\n▶ Starting {phase_title} ({script_name})...")
        script_path = EVAL_DIR / script_name
        
        t0 = time.time()
        ret = subprocess.run([str(PYTHON_EXE), str(script_path)], env=env)
        elapsed = time.time() - t0

        if ret.returncode != 0:
            print(f"\n❌ Error in {phase_title}. Exited with code {ret.returncode}.")
            sys.exit(ret.returncode)

        save_checkpoint(phase_title)
        print(f"✅ {phase_title} completed in {elapsed:.1f}s. Checkpoint recorded.")

    total_elapsed = time.time() - start_total
    print("\n" + "=" * 70)
    print(f"🎉 ALL EVALUATION PHASES COMPLETED SUCCESSFULLY IN {total_elapsed:.1f}s")
    print(f"• Master Report:    {EVAL_DIR / 'REPORT.md'}")
    print(f"• HTML Dashboard:   {EVAL_DIR / 'report.html'}")
    print(f"• Raw Metric Data:  {EVAL_DIR / 'results'}")
    print(f"• Bug Ledger:       {EVAL_DIR / 'BUGS.md'}")
    print(f"• Decisions Ledger: {EVAL_DIR / 'DECISIONS.md'}")
    print(f"• Blockers Ledger:  {EVAL_DIR / 'BLOCKERS.md'}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
