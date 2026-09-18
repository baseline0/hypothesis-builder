# Implementation Roadmap: Remaining Items

**Status:** Validation importer complete. Ready for following phases.

**Gate:** Complete all items below before ten-paper corpus ingestion.

---

## Phase 1: Contradiction Detection ⏳

**File:** `scripts/experiment_spec_compiler.py`

**Changes:**
1. Add `detect_contradictions()` method
   - Input: list of edges
   - Compute `claim_key = (cause, effect, conditions, time_horizon)`
   - Group edges by claim_key
   - For same claim_key + opposite direction → mark as contradictory pair
   - For different claim_key → independent (no contradiction)

2. Add contradiction handling to compiler
   - Input status: `disputed` (from validation importer)
   - Action: REJECT (do not compile)
   - Log: "Contradictory with edge_XXX; human adjudication required"

3. Optional: Add discriminating experiment semantics
   - If disputed pair is accepted: compile as `purpose: "discriminating"`
   - Output: experiment spec that distinguishes the claims

4. Test:
   - Same estimand, opposite direction → disputed (rejected)
   - Different estimands, same cause → independent (both compile)
   - Disputed edge explicitly rejected with reason

---

## Phase 2: Exit Code Testing ⏳

**File:** `tests/test_compiler_exit_codes.py` (NEW)

**Tests:**
```python
test_no_accepted_edges_exits_1()
test_proposed_only_exits_1()
test_rejected_edge_exits_1()
test_mixed_valid_invalid_exits_0_with_warnings()
test_invalid_edge_missing_reviewer_exits_1()
test_output_file_not_created_on_failure()
test_valid_edge_exits_0()
```

**Policy:**
- No eligible edges (proposed, rejected, incomplete) → exit 1
- Some valid, some invalid → exit 0 (with report of rejections)
- Compiler never emits executable specs from invalid edges

**Validation:**
```bash
python scripts/experiment_spec_compiler.py --graph invalid.json --output out.json
test $? -ne 0                    # exit code nonzero
test ! -f out.json || test ! -s out.json  # no/empty output file
```

---

## Phase 3: Enhanced Fixture ⏳

**File:** `tests/fixtures/golden_fixture_complete.py` (NEW)

**Fixture includes:**
1. Accepted edge (known mechanism, complete provenance)
2. Accepted edge (unknown mechanism, exploratory)
3. Accepted edge (low confidence, observational)
4. Contradictory pair (same estimand, opposite direction)
5. Independent pair (same cause, different outcomes)
6. Edge with 3+ supporting papers
7. Edge with alternative explanations
8. Proposed edge (should not compile)
9. Rejected edge (should not compile)
10. Incomplete edge (missing reviewer, should fail validation)

**Test assertions:**
```python
assert specs["total_experiments"] == 5  # edges 1-5 compile
assert specs["experiments"][0]["causal_claim"]["mechanism_status"] == "known"
assert specs["experiments"][1]["purpose"] == "hypothesis_generating"
assert specs["experiments"][1]["confidence_level"] == "exploratory"
assert "contradictory_with" in specs["experiments"][4] or specs["total_experiments"] == 4
assert disputed_edges not in output
assert incomplete_edges not in output
```

---

## Phase 4: Membrane Consumer Validator ⏳

**File:** `scripts/validate_experiment_specs.py` (NEW, for hypothesis-builder)

**Or:** `membrane/src/membrane/schemas/validator.py` (in membrane repo)

**Validates:**
- Schema version compatibility
- Required fields (estimand, design, analysis, provenance)
- Estimand structure (treatment, outcome, identification_status)
- Design controls valid (held_constant, stratified, blocked)
- Analysis plan valid (summary, uncertainty, seed policy)
- Provenance chain complete (edge_id → paper → quote)
- Graph hash matches
- No unknown fields

**Usage:**
```bash
python scripts/validate_experiment_specs.py synthesis/experiment_specs.json
# Exit 0: valid
# Exit 1: invalid (with specific errors)
```

**Policy:**
- Stale graph hash → REJECT
- Missing provenance → REJECT
- Unsupported schema version → REJECT
- Treatment and outcome cannot be same variable → REJECT

---

## Phase 5: Updated ADR ⏳

**File:** `docs/ADR-001-CAUSAL-MODELING.md`

**Updates:**
1. Contradiction detection semantics
   - Define `claim_key = (cause, effect, conditions, time_horizon)`
   - Same key + opposite direction → contradictory
   - Different keys → independent
   - Policy: disputed edges rejected; optional discriminating experiment

2. Validation workflow
   - Graph → proposed graph → validation records → importer → validated graph
   - Graph hash binding (version-specific decisions)
   - No manual graph edits
   - Audit trail: reviewer, timestamp, rationale

3. Exit codes
   - No eligible edges → exit 1
   - Valid + invalid mixed → exit 0, report rejections
   - Output contract: only accepted/validated edges compile

4. Fixture contract
   - Known mechanism
   - Unknown mechanism (explicit uncertainty)
   - Low confidence (exploratory)
   - Contradictions (disputed)
   - Independent outcomes
   - Multi-source claims
   - Invalid edges (rejected)

---

## Phase 6: Clean-Checkout Golden Path ⏳

**Steps:**
1. `git clone` from fresh checkout
2. Create `automation/extracted_evidence/fixture_*.json` (3-5 papers)
3. Run `causal_graph_builder.py`
4. Create `manual/causal_validations.jsonl`
5. Run `import_causal_validations.py`
6. Run `experiment_spec_compiler.py`
7. Run `validate_experiment_specs.py`
8. Verify:
   - Exit codes correct
   - Hashes reproducible
   - All specs have required fields
   - Contradictions handled correctly
   - Rejected edges not in output

---

## Phase 7: Ten-Paper Corpus Authorization Gate

**Checklist:**
- [ ] Clean checkout reproduces tests (Phase 2)
- [ ] Golden path end-to-end (Phase 6)
- [ ] Contradiction semantics explicit and tested (Phase 1)
- [ ] Exit codes deterministic (Phase 2)
- [ ] Enhanced fixture passes all assertions (Phase 3)
- [ ] Membrane validator rejects invalid specs (Phase 4)
- [ ] ADR documents all policies (Phase 5)
- [ ] Provenance hashes independently reproducible
- [ ] Manual review flow validated (importer → validated graph → compiler)
- [ ] Exit code tests pass at process boundary

**Only after all checks pass:** Ingest ten-paper corpus

---

## Implementation Dependencies

```
Phase 1 (contradiction detection)
    ↓
Phase 2 (exit code tests)
    ↓
Phase 3 (enhanced fixture)
    ↓
Phase 4 (membrane validator)
    ↓
Phase 5 (updated ADR)
    ↓
Phase 6 (golden path verification)
    ↓
Phase 7 (corpus authorization)
```

Each phase enables the next. Phases can be partially parallelized if needed.

---

## Success Criteria Per Phase

| Phase | Criterion |
|-------|-----------|
| 1 | Contradictions detected; disputed edges rejected |
| 2 | Exit 1 on invalid input; exit 0 on valid with report |
| 3 | All 10 fixture types handled correctly |
| 4 | Stale specs rejected; invalid schema rejected |
| 5 | Policies documented; semantics explicit |
| 6 | Clean checkout golden path reproducible |
| 7 | All gates pass; corpus authorization granted |

---

## Timeline Estimate

- Phase 1-2: 2 hours (contradiction + exit codes)
- Phase 3: 1.5 hours (enhanced fixture + assertions)
- Phase 4: 1 hour (membrane validator)
- Phase 5: 1 hour (ADR update)
- Phase 6: 1 hour (golden path execution)
- Phase 7: 30 min (checklist verification)

**Total:** ~7 hours, non-blocking

---

**Next:** Implement Phase 1 (contradiction detection).
