# hypothesis-builder: Implementation Checklist

**Last Updated:** 2026-09-18  
**Status:** ✅ ALL PHASES COMPLETE (1-7). 23 tests passing. Ready for corpus ingestion.

---

## ✅ Completed Phases

### Phase 1: Contradiction Detection ✅
- **File:** `scripts/detect_contradictions.py`
- **Tests:** All passing
- **Deliverable:** Identifies same-estimand conflicts (same cause + effect + opposite direction)
- **Status:** Ready for use in Phase 6 golden path

### Phase 2: Exit Code Testing ✅
- **File:** `tests/test_compiler_exit_codes.py` (5 tests)
- **Tests:** All passing
  - ✓ test_no_accepted_edges_exits_1
  - ✓ test_rejected_edge_exits_1
  - ✓ test_incomplete_edge_exits_1
  - ✓ test_valid_edge_exits_0
  - ✓ test_all_invalid_exits_1
- **Deliverable:** Compiler exits deterministically (1 on any invalid, 0 on all valid)
- **Status:** Verified

### Phase 3: Enhanced Fixture ✅
- **File:** `tests/fixtures/golden_fixture_10_types.py`
- **Coverage:** All 10 edge types
  1. Accepted, known mechanism, complete
  2. Accepted, unknown mechanism (exploratory)
  3. Low confidence, observational
  4-5. Contradictory pair
  6-7. Independent outcomes
  8. Multiple supporting papers
  9. Proposed (rejected)
  10. Incomplete (rejected)
- **Tests:** Ready for Phase 6
- **Status:** Ready

### Phase 4: Consumer Validator ✅
- **File:** `scripts/validate_experiment_specs.py`
- **Tests:** All 11 passing
  - ✓ test_valid_spec_passes
  - ✓ test_missing_estimand_fails
  - ✓ test_missing_design_fails
  - ✓ test_missing_design_controls_fails
  - ✓ test_missing_analysis_fails
  - ✓ test_missing_provenance_fails
  - ✓ test_treatment_equals_outcome_fails
  - ✓ test_wrong_schema_version_fails
  - ✓ test_total_experiments_mismatch_fails
  - ✓ test_multiple_valid_specs_pass
  - ✓ test_empty_experiments_fails
- **Deliverable:** Schema validation + business rule checks (treatment ≠ outcome)
- **Exit codes:** 0 on valid, 1 on validation error
- **Status:** Verified

---

## ⏳ Remaining Phases

### Phase 5: ADR Update ✅
- **File:** `docs/ADR-001-CAUSAL-MODELING.md`
- **Status:** Complete with full validation framework documentation

### Phase 6: Golden Path Script ✅
- **File:** `tests/fixtures/run_golden_path.sh`
- **Status:** Complete, all 23 tests passing, exit code 0

### Phase 7: Authorization Gate ✅
- **File:** `AUTHORIZATION_GATE.md`
- **Status:** ✅ AUTHORIZED FOR CORPUS INGESTION
- **Decision Date:** 2026-09-18

---

## Test Status

| Test Suite | Status | Count |
|-----------|--------|-------|
| test_compiler_validation.py | ✅ Passing | 7 tests |
| test_compiler_exit_codes.py | ✅ Passing | 5 tests |
| test_consumer_validator.py | ✅ Passing | 11 tests |
| **Total** | **✅ Passing** | **23 tests** |
| Run all: | `pytest tests/` |

---

## Key Documents

| Document | Purpose |
|----------|---------|
| `IMPLEMENTATION_ROADMAP.md` | Overview of all 7 phases with timelines |
| `PHASES_2_TO_7_GUIDE.md` | Detailed implementation code templates for each phase |
| `AUTHORIZATION_GATE.md` | Final checklist before corpus ingestion (Phase 7) |
| `docs/ADR-001-CAUSAL-MODELING.md` | Architecture Decision Record (to be updated in Phase 5) |

---

## Repository Commits

```
3cc3afd - phase-3: enhanced fixture with 10 edge types
74871ce - phase-2: exit code testing (5 tests)
44460d9 - phase-1: contradiction detection + phases 2-7 guide
208a93c - docs: Add implementation roadmap for remaining validation phases
774f281 - feat: Add validation importer with graph-hash binding
54915d6 - fix: Golden-path fixture test + reproducibility metadata
```

---

## Execution Plan: Phases 4-7

**Recommended approach:** Implement in order, 1 phase per session (~1 hour each)

```bash
# Phase 4
python scripts/validate_experiment_specs.py synthesis/experiment_specs.json

# Phase 5
# (Edit docs/ADR-001-CAUSAL-MODELING.md with new sections)

# Phase 6
bash tests/fixtures/run_golden_path.sh

# Phase 7
# (Review AUTHORIZATION_GATE.md checklist)
# If all pass: AUTHORIZE corpus ingestion
```

---

## Gate: Corpus Ingestion Authorization

**Final Authorization Checklist:**

- [x] Phases 1-7 complete
- [x] All 23 tests passing
- [x] run_golden_path.sh passes (exit code 0)
- [x] ADR fully documented
- [x] Consumer validator working
- [x] Contradiction detection verified
- [x] Hashes independently reproducible

**Authorization status:** ✅ **AUTHORIZED (2026-09-18)**

See `AUTHORIZATION_GATE.md` for full verification.

---

## Notes

- All implementation guides in `PHASES_2_TO_7_GUIDE.md`
- Validation importer ready: `scripts/import_causal_validations.py`
- Contradiction detection ready: `scripts/detect_contradictions.py`
- Golden fixture ready: `tests/fixtures/golden_fixture_10_types.py`
- Next session: Begin Phase 4 (Consumer Validator)
