# Turnitout Evaluation: Bug Log & Defect Tracking

This document logs all bugs, unexpected crashes, invariant violations, and behavioral defects discovered during the independent evaluation of Turnitout-Humanizer.

Per the evaluation ground rules:
* Engine source code is **NEVER** modified.
* All bugs are recorded here with a minimal, reproducible test case.
* Failures are tracked against specific writing registers (`academic`, `technical`, `standard`, `conversational`) and intensities ($25\% - 100\%$).

---

## Bug Index

| Bug ID | Severity | Phase Discovered | Module / Stage | Summary | Reproduction Artifact |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **BUG-001** | High | Phase 2 Audit | `modifier.py` (Stage 6) | Double preposition `"is essential to in"` introduced during phrase rewrite | See reproduction below |

---

## Detailed Bug Reports

### BUG-001: Ungrammatical Double Preposition Introduced by Stage 6 Phrase Rewriter
* **Severity**: High (Grammar & Syntactic Integrity Failure)
* **Component**: `backend/src/turnitout/core/modifier.py` (`_apply_phrase_rewrites`) / `backend/rules/phrases.json`
* **Discovered On**: `DOC_0200_LAW`, `DOC_0210_LAW`, `DOC_0220_LAW`, `DOC_0230_LAW`
* **Description**:
  When processing text containing the common academic phrase `"plays a crucial role in"`, the rewriter substitutes `"plays a crucial role"` with `"is essential to"`. However, the regex pattern fails to consume the trailing preposition `"in"`. As a result, the output contains an ungrammatical double preposition: `"is essential to in"`.
* **Minimal Reproducible Example**:
  ```python
  from turnitout.config import ConfigNamespace
  from turnitout.core.modifier import DocumentModifier

  text = "Furthermore, constitutional jurisprudence plays a crucial role in safeguarding individual liberties."

  cfg = ConfigNamespace({"pipeline_defaults": {"style": "academic", "intensity": 75.0}})
  modifier = DocumentModifier(config=cfg, seed=42)
  output = modifier.modify_document(text)

  print("INPUT: ", text)
  print("OUTPUT:", output)
  # OUTPUT: "Additionally, constitutional jurisprudence is essential to in safeguarding individual liberties."
  assert "to in" not in output, "BUG-001: Ungrammatical double preposition detected!"
  ```
* **Status**: Open (Engine source left untouched per evaluation ground rules).
