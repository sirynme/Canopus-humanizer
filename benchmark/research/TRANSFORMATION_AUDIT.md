# Transformation Rule Audit & Risk Classification Report

**System**: Turnitout Transformation Engine  
**Version**: Core 2.6.0 Pipeline  
**Evaluation Standard**: Empirical Benchmark Failures & Published Literature  

---

## 1. Executive Summary

This audit inventories all 17 transformation stages in the Turnitout pipeline. Each rule is classified by its intended purpose, risk profile across four dimensions (Semantic, Mathematical, Citation, Grammatical), observed benchmark failures, required preconditions and postconditions, and whether it should be **disabled or constrained by default** for academic and technical text.

---

## 2. Comprehensive Transformation Inventory & Risk Matrix

| Stage | Name | Semantic Risk | Math Risk | Citation Risk | Grammatical Risk | Default for Academic | Research Support Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | LaTeX / Code Protection | LOW | HIGH (if regex fails) | LOW | LOW | **ENABLED (UPGRADE TO AST/STACK)** | Supported (Sojka & Líška 2011) |
| **2** | Phrase Rewriting | MED | LOW | LOW | MED | **CONSTRAINED (PURGE PURPLE PROSE)** | Supported (Daille 2017) |
| **3** | Synonym Substitution | MED | MED | LOW | HIGH | **CONSTRAINED (ALIGN POS/MWU)** | Supported (Zhang et al. 2020) |
| **4** | Clause Reordering | HIGH | HIGH | MED | HIGH | **DISABLED FOR FORMAL/ACADEMIC** | Engineering Hypothesis (Fails empirical test) |
| **5** | Determiner Swapping | MED | LOW | LOW | HIGH (Agreement) | **CONSTRAINED (ENFORCE AGREEMENT)** | Engineering Hypothesis |
| **6** | Compound Sentence Splitting | HIGH | MED | LOW | MED | **DISABLED FOR STRUCTURED TEXT** | Engineering Hypothesis |
| **7** | Hedge Word Injection | HIGH | HIGH | LOW | HIGH | **DISABLED BY DEFAULT** | Violates Gopen & Swan (1990) |
| **8** | N-Gram Winnowing Disruption | HIGH | HIGH | HIGH | HIGH | **DISABLED (CORRUPTS COMPOUND NOUNS)**| Misapplication of Schleimer et al. (2003) |
| **9** | Active <-> Passive Voice | HIGH | LOW | LOW | HIGH (Plural Agreement)| **DISABLED UNLESS POS VERIFIED** | Violates Gopen & Swan (1990) |
| **10**| Sentence Fusion | HIGH | HIGH | HIGH | HIGH | **DISABLED FOR HEADINGS & PROPOSALS**| Engineering Hypothesis (Fails empirical test) |
| **11**| Transition Phrase Injection | HIGH | LOW | LOW | HIGH (False Logic) | **DISABLED BY DEFAULT** | Violates Jiang et al. (2024) |
| **12**| Clause-Level Word Reordering | HIGH | HIGH | LOW | HIGH | **DISABLED FOR RESTRICTIVE CONDITIONS**| Engineering Hypothesis |
| **13**| Nominalization | MED | LOW | LOW | HIGH (Wordiness) | **DISABLED BY DEFAULT** | Violates Gopen & Swan (1990) |
| **14**| Appositive Injection | HIGH | HIGH | LOW | HIGH (Extrinsic Drift) | **DISABLED BY DEFAULT** | Violates Maynez et al. (2020) |
| **15**| Discourse Marker Rotation | LOW | LOW | LOW | LOW | **ENABLED (CLEAN REGISTRY ONLY)** | Supported (Non-destructive) |
| **16**| LaTeX / Formatting Restoration| LOW | HIGH | LOW | LOW | **ENABLED (VERIFY INTEGRITY)** | Supported |
| **17**| Contextual Citation Shielding | HIGH | LOW | HIGH | LOW | **DISABLED BY DEFAULT (NO FABRICATION)**| Mandatory Scholarly Integrity |

---

## 3. Detailed Stage-by-Stage Audit

### Stage 1: LaTeX & Formatting Protection (`_protect_latex`)
- **Purpose**: Shield equations, macros, citations, and markup from text replacement.
- **Eligible Text Types**: Any document with LaTeX or HTML.
- **Risks**:
  - *Mathematical Risk (HIGH)*: Flat regex `\\[a-zA-Z]+\*?(?:\[.*?\])?(?:\{.*?\})*` fails on nested commands (e.g. `\frac{\partial^2 f}{\partial x^2}`) or multiline matrix environments.
- **Observed Failures**: Unshielded math variables like `$x$` adjacent to text can be modified or currency `$4.5 million` mistaken for math.
- **Preconditions**: Text must be scanned before any word/character replacement.
- **Postconditions**: Byte-for-byte exact restoration of all protected tokens; fail-closed if token count mismatches.
- **Recommendation**: **Retain and upgrade** to a balanced-delimiter stack parser.

---

### Stage 2: Multi-Word Phrase Rewrites (`_apply_phrase_rewrites`)
- **Purpose**: Replace formulaic AI clichés (*"delve into"*, *"comprehensive tapestry"*) with precise scholarly terms.
- **Eligible Text Types**: All prose containing formulaic phrases.
- **Risks**:
  - *Grammatical/Stylistic Risk (MED)*: Archaic substitutions (*"the current disquisition"*, *"was effectuated"*, *"accords harmoniously with"*) damage writing quality.
- **Observed Failures**: Replaces clean prose with purple prose.
- **Preconditions**: Exact multi-word pattern match on whole word boundaries.
- **Postconditions**: Replacement must preserve grammatical tense and voice.
- **Recommendation**: **Retain but purge archaic purple prose**. Restrict to clean, modern academic phrases (e.g. *"in order to"* $\to$ *"to"*).

---

### Stage 3: Synonym Substitution (`_apply_synonyms`)
- **Purpose**: Provide lexical variety to reduce n-gram predictability.
- **Eligible Text Types**: General and academic prose.
- **Risks**:
  - *Semantic/Grammatical Risk (HIGH)*: Single-word matching without part-of-speech awareness replaces words within multi-word technical units (*"learning rate"* $\to$ *"learning velocity"*).
- **Observed Failures**: Injects inappropriate synonyms (*"reckon"* for compute, *"sundry"* for several).
- **Preconditions**: Token must NOT be part of a multi-word technical term, named entity, or unit.
- **Postconditions**: The candidate synonym must match the target's exact part of speech and register.
- **Recommendation**: **Retain with strict multi-word unit shielding and pruned synonym lists**.

---

### Stage 4: Clause Reordering (`_reorder_clauses`)
- **Purpose**: Shift subordinate clauses to the sentence beginning.
- **Eligible Text Types**: Long compound-complex sentences with clean subordinate clauses.
- **Risks**:
  - *Semantic Risk (HIGH)*: Reorders conditional and restrictive clauses, flipping logical conditions (*"Unless X happens, Y will not occur"*).
  - *Mathematical Risk (HIGH)*: Separates mathematical assumptions (*"where $x > 0$"*) from governing equations.
- **Observed Failures**: Dropped numerical values and inverted conditions in benchmark Level 2 and Level 4 tests.
- **Recommendation**: **Disable by default for academic and technical text**.

---

### Stage 5: Determiner Rotation (`_swap_determiners`)
- **Purpose**: Vary ubiquitous articles and quantifiers.
- **Eligible Text Types**: General prose.
- **Risks**:
  - *Grammatical Risk (HIGH)*: Swapping *"all"* with *"every"* causes subject-verb agreement failure (*"All models were"* $\to$ *"Every models were"*).
- **Observed Failures**: Plurality agreement violations.
- **Preconditions**: Must check number agreement (singular vs plural).
- **Recommendation**: **Enforce strict number agreement constraints; remove destructive pairs**.

---

### Stage 6: Compound Sentence Splitting (`_split_compound_sentences`)
- **Purpose**: Break long sentences to vary sentence length distribution.
- **Eligible Text Types**: Compound sentences joined by coordinating conjunctions.
- **Risks**:
  - *Semantic Risk (HIGH)*: Splitting on commas severs qualifying percentages or causes run-on fragments.
- **Observed Failures**: Fragmented financial and statistical qualifications.
- **Recommendation**: **Disable for sentences containing numerical quantities, citations, or formulas**.

---

### Stage 7: Hedge Word Injection (`_insert_hedge_words`)
- **Purpose**: Inject probabilistic adverbs (*"arguably"*, *"assuredly"*, *"ostensibly"*) after commas.
- **Eligible Text Types**: None (Artificially inflates entropy).
- **Risks**:
  - *Semantic Risk (HIGH)*: Inverts epistemic certainty; inserts doubt or sarcasm into empirical statements (*"the patient was diagnosed, ostensibly, with diabetes"*).
- **Observed Failures**: Blatant distortion of factual claims and medical statements.
- **Recommendation**: **Permanently disable**. Supported by Gopen & Swan (1990) and Williams & Bizup (2017).

---

### Stage 8: N-Gram Winnowing Chain Breaker (`_break_ngram_chains`)
- **Purpose**: Break sequences of $>5$ identical words by inserting adverbs every 6th word.
- **Eligible Text Types**: None.
- **Risks**:
  - *Grammatical/Semantic Risk (CRITICAL)*: Injects adverbs blindly into fixed noun phrases (*"broadly learning rate"*, *"reliably gradient descent"*).
- **Observed Failures**: Primary cause of compound noun corruptions in Level 3, 4, and 5 tests.
- **Recommendation**: **Permanently disable**. Winnowing sequence disruption must be achieved via grammatical phrase variation, never blind token insertion.

---

### Stage 9: Active <-> Passive Voice Transformation (`_transform_voice`)
- **Purpose**: Invert active sentences into passive constructions.
- **Eligible Text Types**: Transitive active clauses with overt direct objects.
- **Risks**:
  - *Grammatical Risk (CRITICAL)*: Hardcodes singular *"was"*: transforms *"We analyzed the results"* into *"The results was analyzed"*, causing immediate grammatical agreement failure.
- **Observed Failures**: Plural subject-verb agreement violations across all levels.
- **Recommendation**: **Disable unless noun plurality is dynamically checked** (*"were"* for plural, *"was"* for singular). In academic writing, active voice is preferred anyway (Gopen & Swan 1990).

---

### Stage 10: Sentence Fusion (`fuse_adjacent_sentences`)
- **Purpose**: Merge short adjacent sentences with causal connectors (*", which consequently"*, *", thereby requiring"*).
- **Eligible Text Types**: Narrative paragraphs with short simple sentences.
- **Risks**:
  - *Semantic/Academic Risk (CRITICAL)*: Blurs distinct research objectives and merges numbered headers (*"1. Problem Statement ... , which consequently 2. Research Questions"*).
- **Observed Failures**: Complete rubric failure on Level 5 Research Proposals.
- **Recommendation**: **Disable for structured academic text, numbered items, and bullet points**.

---

### Stage 11: Transition Phrase Injection (`_inject_transitions`)
- **Purpose**: Inject sentence-initial discourse connectors.
- **Eligible Text Types**: None when chosen at random.
- **Risks**:
  - *Semantic Risk (CRITICAL)*: Picks a random category (e.g. contrast vs cause_effect), injecting *"Conversely,"* before agreeing claims or *"Therefore,"* before hypotheses.
- **Observed Failures**: Rhetorical coherence violations.
- **Recommendation**: **Permanently disable random injection**. Discourse markers must only be *rotated* when already present.

---

### Stage 12: Clause-Level Word Reordering (`_reorder_within_clause`)
- **Purpose**: Move initial prepositional phrases to the end.
- **Eligible Text Types**: Sentences with non-restrictive adjuncts.
- **Risks**:
  - *Semantic Risk (HIGH)*: Moves restrictive temporal/scope conditions (*"In 1971,"*, *"Under high concurrency,"*) to the end, altering topic-comment structure.
- **Recommendation**: **Disable for academic and technical text**.

---

### Stage 13: Nominalization (`_nominalize`)
- **Purpose**: Convert active verbs into abstract noun phrases (*"analyze"* $\to$ *"analysis was conducted"*).
- **Eligible Text Types**: None.
- **Risks**:
  - *Grammatical/Stylistic Risk (HIGH)*: Decreases readability, inflates sentence length, obscures agency.
- **Recommendation**: **Disable by default**. Explicitly contravened by Gopen & Swan (1990).

---

### Stage 14: Appositive Injection (`_inject_appositives`)
- **Purpose**: Insert explanatory parenthetical clauses (*", a discretization technique,"*).
- **Eligible Text Types**: Introductory educational text only.
- **Risks**:
  - *Semantic Risk (CRITICAL)*: Extrinsic hallucination (Maynez et al. 2020); injects elementary definitions into expert scientific manuscripts.
- **Recommendation**: **Permanently disable for academic presets**.

---

### Stage 15: Discourse Marker Rotation (`_rotate_discourse_markers`)
- **Purpose**: Substitute existing discourse markers with context-appropriate equivalents (*"However"* $\to$ *"Nevertheless"*).
- **Eligible Text Types**: All text containing explicit discourse markers.
- **Risks**:
  - *Stylistic Risk (LOW)*: If informal terms (*"On the flip side"*) are included.
- **Recommendation**: **Retain, but purge informal and colloquial entries**.

---

### Stage 16: LaTeX / Formatting Restoration (`_restore_latex`)
- **Purpose**: Reinsert protected placeholders.
- **Eligible Text Types**: Documents containing protected tokens.
- **Risks**:
  - *Mathematical Risk (CRITICAL)*: Fails if placeholders were damaged or dropped during processing.
- **Recommendation**: **Retain with strict integrity verification and fail-closed rollback**.

---

### Stage 17: Contextual Citation Shielding (`_maybe_add_citation`)
- **Purpose**: Injected synthetic bibliography keys.
- **Eligible Text Types**: None.
- **Risks**:
  - *Academic/Scholarly Risk (FATAL)*: Fabricating scholarly citations is scientific misconduct.
- **Recommendation**: **Permanently disable citation injection**. Real citations must be *protected*, never invented.
