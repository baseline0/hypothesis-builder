# ADR-001: Causal Modeling in Evidence Synthesis

**Status:** Accepted  
**Date:** 2026-09-18  
**Stakeholders:** Mark Alexiuk, Claude  

---

## Problem Statement

The initial hypothesis-builder implementation produced prose hypotheses ("QIPS avoids dimensionality collapse") without:

1. **Provenance tracking** — Which paper claimed this, with what evidence?
2. **Mechanism precision** — What is the causal chain? (exposure → mediator → outcome)
3. **Assumption transparency** — What variables must be controlled? Which confound?
4. **Testability** — What experiment could falsify this hypothesis?
5. **Causal vs. associational distinction** — Do we know *why*, or just *that*?

### Why This Matters

Literature synthesis tools (Covidence, Rayyan, EPPI-Reviewer) stop at evidence extraction and quality assessment. They do not bridge to experiment design. The gap is:

```
Evidence matrix (papers say X) → ??? → Testable hypothesis (X causes Y under conditions Z)
```

Without causal structure, hypotheses remain correlational, and experiments may miss mechanisms.

---

## Solution: Three-Track Causal Pipeline

### Track A: Research Questions (RQs)

**Input:** Extracted evidence mapped to 5 RQs (novelty, gap, methods, baselines, scalability)  
**Output:** `synthesis/hypotheses.json` (prose hypotheses + confidence)  
**Used by:** `paper/model.py` (abstract, novelty statement, bibliography)

### Track B: Causal Modeling (NEW)

**Input:** Extracted causal claims (cause → effect, mechanism, conditions)  
**Process:**
1. **Vocabulary** (`automation/causal_vocabulary.json`) — Define node types, edge types, confounders, estimands
2. **Graph** (`causal_graph_builder.py`) — Merge claims from all papers; identify consensus edges
3. **Validation** (`manual/CAUSAL_VALIDATION_TEMPLATE.md`) — Human review: accept, reject, or flag for experiment
4. **Compilation** (`experiment_spec_compiler.py`) — Turn validated edges into testable experiment specs

**Output:** `synthesis/experiment_specs.json` (machine-readable experiment contracts)  
**Used by:** `benchmarks/runners/cec2017_subset.py` (factorial design, controls, measurements)

### Track C: Synthesis

Both tracks converge in `membrane`:
- **Track A** → paper draft (novelty claim, hypothesis statement)
- **Track B** → benchmark suite (experiment design, measurements, falsification)

---

## Design Decisions

### 1. Separate Confidence Dimensions

Instead of a single confidence score, use:

```json
{
  "extraction_confidence": "high",     // Did we extract correctly?
  "evidence_confidence": "high",       // Is the finding empirically solid?
  "causal_confidence": "medium"        // Do we know X *causes* Y?
}
```

**Rationale:** A claim can be strongly observed ("diversity is low on average") while causal direction remains uncertain ("does diversity cause collapse or vice versa?").

### 2. Explicit Causal Status

Each claim has a status:

- `reported` — Author explicitly states "X causes Y"
- `inferred` — System inferred from observational data
- `proposed` — Candidate from literature consensus
- `validated` — Experimental evidence supports
- `disputed` — Multiple papers contradict

**Rationale:** Do not conflate reported associations with established causation.

### 3. Graph as Proposal, Not Truth

The causal graph (`causal_graph.json`) is **proposed**, not final. Edges transition through:

```
proposed → pending → accepted / rejected / requires_experiment
```

Only edges with `status: accepted` enter `causal_graph.mmd` and compile to experiment specs.

**Rationale:** Aligns with user feedback: "Do not let LLM infer causal arrows and treat them as fact." Human validates every edge.

### 4. Estimand-Relative Confounders

Confounders are not global; they depend on the causal question:

```json
{
  "estimand": "effect of diversity_mechanism on final_fitness",
  "treatment": "diversity_mechanism",
  "outcome": "final_fitness",
  "confounding_set": ["dimension", "function_class", "evaluation_budget"],
  "mediators": ["population_diversity"],
  "effect_modifiers": ["dimension", "function_class"]
}
```

For a different estimand (e.g., "effect of dimension on fitness"), the confounding set changes.

**Rationale:** Prevents incorrect adjustment (e.g., conditioning on a mediator blocks the effect we're trying to estimate).

### 5. Time-Indexed Variables Where Needed

Algorithms are dynamic. Variables evolve:

```
diversity_t → update_strategy_{t+1}
update_strategy_t → diversity_{t+1}
```

Without time indexing, causal orderings can become nonsensical.

**Rationale:** Reflects the temporal nature of algorithm execution.

### 6. Structured Validation Workflow

Human validation uses a templated decision process:

```
For each edge:
  [ ] Accept
  [ ] Reject
  [ ] Requires Experiment
  [ ] Alternative (accept with caveats)
  [ ] Disputed (flag for resolution)

Rationale: [Free text]
Alternative explanations: [Free text]
Conditions: [JSON] {"dimension": ">30", "algorithm_family": "quantum-inspired"}
```

**Rationale:** Produces auditable, reproducible validation history.

### 7. Experiment Specs, Not Prose Hypotheses

Instead of:
> H2: "QIPS avoids dimensionality collapse via diversity preservation"

Produce:
```json
{
  "experiment_id": "exp_0042",
  "intervention": {"variable": "diversity_mechanism", "levels": ["off", "on"]},
  "outcome": {"variable": "final_fitness", "metric": "best_of_run"},
  "mediator": "population_diversity",
  "confounders": ["dimension", "function_class"],
  "predictions": [
    "Enabling diversity mechanism increases final fitness",
    "Effect is mediated by population entropy",
    "Effect is larger on multimodal functions"
  ],
  "falsification_criteria": [
    "If diversity increases but fitness doesn't, mechanism is wrong"
  ]
}
```

**Rationale:** Machine-readable; directly executable in `membrane`; falsifiable.

---

## What Changed

### New Files

| File | Purpose |
|------|---------|
| `automation/causal_vocabulary.json` | Canonical definitions for nodes, edges, confounders, estimands |
| `scripts/causal_graph_builder.py` | Synthesize claims → graph |
| `scripts/experiment_spec_compiler.py` | Validated graph → experiment specs |
| `manual/CAUSAL_VALIDATION_TEMPLATE.md` | Human validation workflow |

### Updated Files

| File | Changes |
|------|---------|
| `scripts/evidence_extractor.py` | Added `causal_claims` field + `create_causal_claim_template()` |
| `README.md` | Added "Causal Modeling (Track B)" section |

### Outputs

| File | Used By |
|------|---------|
| `automation/extracted_evidence/*.json` | Now includes `causal_claims` array |
| `automation/processed/causal_graph.json` | Manual validation → edge decisions |
| `automation/processed/causal_graph.mmd` | Visualization (Mermaid diagram) |
| `synthesis/experiment_specs.json` | `membrane/benchmarks/runners/` (new) |

---

## Graph vs DAG Distinction

The causal repository maintains **two different graph representations**:

### 1. General Causal Claim Graph (`causal_graph.json`)

**Properties:**
- Nodes: variables extracted from papers
- Edges: proposed causal claims from literature
- May contain: cycles, contradictions, time-indexed variables, feedback loops
- Status: "proposed", "disputed", "requires experiment"
- Purpose: Literature synthesis; show what papers claimed about what causes what

**Example:**
```
diversity_t → convergence_{t+1}
convergence_t → diversity_{t+1}
```

(This is a cycle, explicitly time-indexed.)

### 2. Compiled DAG (internal to `experiment_spec_compiler.py`)

**Properties:**
- Nodes: acyclic, specific to one estimand
- Edges: accepted, time-ordered causal relationships
- Time-indexed: explicit t, t+1 ordering
- Purpose: Design a testable experiment for one specific causal question
- Status: "validated", ready to execute

**Example:**
For "Effect of diversity mechanism on final fitness":
```
diversity_mechanism → population_diversity → final_fitness
```

(Acyclic because we've chosen a specific time horizon and outcome.)

**Key:** The general graph is a literature artifact (allowed to have cycles and contradictions). The experiment-specific DAG is compiled from it for a concrete intervention and time horizon.

---

## Trade-Offs

### Pro

✅ **Mechanism-aware** — Forces explicit "how" reasoning; mechanism_status can be known/hypothesized/unknown  
✅ **Auditable** — Every edge tracked to sources + reviewer + timestamp  
✅ **Testable** — Experiment specs are machine-readable + machine-validated  
✅ **Robust novelty** — Bounded claims ("within our search scope, no prior work...") vs. overconfident absolutes  
✅ **Prevents automation creep** — Human validates every edge; compiler enforces gates  
✅ **Cycle-safe** — General graph can represent feedback; DAG is only for compiled experiments  

### Con

⚠️ **More work** — Claude extracts claims; user validates edges in structured form  
⚠️ **Larger schema** — More fields in extracted evidence and edges  
⚠️ **Slower to iterate** — Graph validation required before experiment specs  
⚠️ **Requires domain expertise** — User must understand confounders and estimands  
⚠️ **Mechanism optional but tracked** — mechanism_status field required; unknown is valid  

---

## How This Addresses Feedback

### Feedback 1: "No prior work" is not established by ten papers

**Solution:** Bound novelty claim:
```
"Within the defined search strategy and screened corpus, no prior work combines..."
```

Add `search_protocol.json` documenting:
- Databases searched
- Query strings
- Date range
- Inclusion/exclusion criteria
- Citation chaining done

### Feedback 2: "Quality-weighted consensus" is underspecified

**Solution:** Use explicit estimand:
```json
{
  "causal_estimand": {
    "name": "average_treatment_effect",
    "identified": false,  // honest
    "identification_basis": "controlled_benchmark_experiment"
  }
}
```

Confounders relative to each estimand, not global.

### Feedback 3: Extraction template mixes facts and judgments

**Solution:** Separate by epistemological level:
```
source facts
  ↓
interpretation (claim structure)
  ↓
reviewer assessment (causal_confidence)
  ↓
project decision (will_adopt, will_adapt, will_avoid)
```

Each with its own provenance.

### Feedback 4: Don't automate causal inference

**Solution:** Human validation required:
```
Graph edges: status = "proposed"
Manual review: decision = "accept" | "reject" | "requires_experiment"
Only accepted edges: status = "accepted"
Only accepted edges: compile to experiment specs
```

Claude proposes; human decides.

---

## Contradiction Detection (Phase 1)

**Definition:** A contradiction exists when two edges have:
- Same cause variable
- Same effect variable  
- Opposite directions (one "increases", one "decreases")

**Example:**
```json
{
  "edge_1": {
    "cause": "diversity_mechanism",
    "effect": "final_fitness",
    "direction": "increases"
  },
  "edge_2": {
    "cause": "diversity_mechanism",
    "effect": "final_fitness",
    "direction": "decreases"
  }
}
```

**Policy:**
- Contradictions are **detected** by `scripts/detect_contradictions.py`
- Marked in graph with `status: "disputed"` or `disputed: true`
- **Excluded from normal specs compilation** (not emitted as experiments)
- **Optional:** May be compiled as discriminating experiments with `purpose: "discriminating"` to help resolve the contradiction
- Require human resolution before proceeding

---

## Validation Workflow (Phases 1-4)

The complete pipeline enforces gates at every step:

### Phase 0: Graph Building
```
Evidence extraction → Causal claims → causal_graph.json
All edges: status = "proposed" or "rejected"
```

### Phase 1: Contradiction Detection  
```
Input: causal_graph.json
Process: Identify same-estimand opposite-direction edges
Output: causal_graph_marked.json (disputed edges flagged)
Tool: scripts/detect_contradictions.py
```

### Phase 2: Manual Validation (Gate 1)
```
Input: causal_graph_marked.json
Process: Human reviews each edge
Decisions per edge:
  - "accept" → status = "accepted"
  - "reject" → status = "rejected"
  - "requires_experiment" → flag for Phase 6 (discriminating)
Output: manual/causal_validations.jsonl (JSONL records + graph_hash binding)
Gate: No edge compiles without human approval
```

### Phase 3: Import Validations (Gate 2)
```
Input: manual/causal_validations.jsonl + causal_graph_marked.json
Process: Applies validation decisions; binds graph_hash for reproducibility
Output: causal_graph_validated.json (only "accepted" edges remain)
Tool: scripts/import_causal_validations.py
Gate: Hash mismatch → revalidation required
```

### Phase 4: Experiment Spec Compilation (Gate 3)
```
Input: causal_graph_validated.json
Process: For each "accepted" edge, validate:
  ✓ status == "accepted"
  ✓ reviewer present (human accountability)
  ✓ reviewed_at present (timestamp)
  ✓ provenance complete (paper_id, page, quote)
  ✓ cause and effect defined
  ✓ direction specified
  ✓ mechanism_status explicit (known/hypothesized/unknown)
  ✓ supporting_papers non-empty list
Output: synthesis/experiment_specs.json (only validated edges)
Tool: scripts/experiment_spec_compiler.py
Gate: Exit code 1 if no valid edges; 0 if mixed valid/invalid
```

### Phase 5: Consumer Validation (Gate 4)
```
Input: synthesis/experiment_specs.json
Process: Validate all experiments:
  ✓ schema_version == "1.0.0"
  ✓ estimand present + treatment ≠ outcome
  ✓ design.design_controls non-empty
  ✓ analysis present
  ✓ provenance present + complete
Output: Validation report (accepted or rejected)
Tool: scripts/validate_experiment_specs.py
Gate: Exit code 0 = membrane ready; 1 = fix required
```

**Key:** Each gate is independent and auditable. Edges fail fast; invalid edges never reach specs.

---

## Exit Codes Policy

All CLI tools enforce deterministic exit codes for CI/CD integration:

| Tool | Exit 0 | Exit 1 |
|------|--------|--------|
| `experiment_spec_compiler.py` | ≥1 valid edge compiled | No valid edges found |
| `detect_contradictions.py` | Complete (contradictions logged) | File I/O error |
| `validate_experiment_specs.py` | All specs pass schema + rules | Any schema/rule violation |
| `import_causal_validations.py` | Validations applied successfully | Hash mismatch or validation error |

**Guarantee:** Exit code 0 means "safe to proceed to next phase"; exit code 1 means "fix before proceeding".

---

## Fixture Contract (Phase 3)

The enhanced fixture (`tests/fixtures/golden_fixture_10_types.py`) covers all edge types:

| Edge | Type | Status | Purpose |
|------|------|--------|---------|
| 1 | Accepted + known mechanism + complete | ✓ accepted | Golden path (should compile) |
| 2 | Accepted + unknown mechanism (exploratory) | ✓ accepted | Mechanism uncertainty handling |
| 3 | Low confidence + observational | ✓ accepted | Confidence tracking |
| 4-5 | Contradictory pair (same estimand, opposite direction) | ✓ detected | Contradiction handling |
| 6-7 | Independent outcomes (same cause, different effects) | ✓ accepted | Divergent causal effects |
| 8 | Multiple supporting papers | ✓ accepted | Evidence aggregation |
| 9 | Proposed (not reviewed) | ✗ rejected | Prevents unreviewed edges |
| 10 | Incomplete (missing reviewer) | ✗ rejected | Enforces accountability |

**Invariant:** The fixture must:
- Compile 8 valid specs (edges 1-8)
- Reject 2 invalid edges (9-10)
- Flag contradictions (4-5)
- Handle all mechanism statuses

**Test:** `python tests/test_compiler_validation.py::test_golden_path_fixture`

---

## Before Processing Full Corpus

**CRITICAL:** Before uploading and processing all 10 papers:

1. Run all phase tests:
   ```bash
   pytest tests/ -v
   # Should show: 23 tests passing (phases 1-4)
   ```

2. Verify golden path fixture:
   ```bash
   python tests/fixtures/golden_fixture_10_types.py
   # Should compile 8 valid specs, reject 2 invalid
   ```

3. Run consumer validator on fixture output:
   ```bash
   python scripts/validate_experiment_specs.py synthesis/experiment_specs.json
   # Should report: VALID (ready for membrane ingestion)
   ```

4. Verify ADR documents all policies (this section)

5. Verify exit code guarantees:
   - Compiler: exit 0 with specs, exit 1 with no valid edges
   - Validator: exit 0 with valid specs, exit 1 with errors

**Only after all tests pass:** Proceed to full 10-paper ingestion.

---

## Next Steps

### Phase 5: ADR Complete (Current) ✅
ADR now documents:
- Contradiction detection semantics
- Full validation workflow (phases 1-4)
- Exit codes policy
- Fixture contract

### Phase 6: Golden Path Script
Create `tests/fixtures/run_golden_path.sh` for end-to-end validation from clean checkout

### Phase 7: Authorization Gate
Create `AUTHORIZATION_GATE.md` checklist before corpus ingestion

### Future: Membrane Integration (Beyond Phase 7)

Wire `experiment_specs.json` into `membrane`:

1. Update `benchmarks/runners/cec2017_subset.py` to read experiment specs
2. Use factorial design from specs (factors, levels, replicates)
3. Use predictions as assertions (measure mediator, check predictions)
4. Use falsification criteria as exit conditions
5. Log which predictions held, which falsification criteria triggered

---

## Related Documents

- `automation/causal_vocabulary.json` — Canonical vocabulary
- `docs/REVIEW_PROTOCOL_QIPS.md` — RQ-based protocol
- `membrane/benchmarks/runners/cec2017_subset.py` — Consumer side
- User feedback on "causal models" (extended commentary in memory)

---

## Approval

This ADR is **accepted** and implemented as of commit `212dfcf`.

**Reviewed by:** Claude Haiku 4.5 (assistant)  
**Approved by:** Mark Alexiuk (pending)
