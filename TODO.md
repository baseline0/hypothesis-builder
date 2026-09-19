# hypothesis-builder: Implementation Checklist

**Last Updated:** 2026-09-18  
**Status:** Phases 1-3 complete. Phases 4-7 ready for implementation.

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

---

## ⏳ Remaining Phases

### Phase 4: Consumer Validator ⏳
- **File:** `scripts/validate_experiment_specs.py` (NEW)
- **Deliverable:** Schema validation + business rule checks
- **Implementation guide:** See `PHASES_2_TO_7_GUIDE.md` (Phase 4 section)
- **Effort:** ~1 hour
- **Next:** After Phase 4, proceed to Phase 5

### Phase 5: ADR Update ⏳
- **File:** `docs/ADR-001-CAUSAL-MODELING.md` (EDIT)
- **Changes:**
  - Add contradiction detection semantics
  - Document validation workflow (graph → importer → compiler)
  - Define exit codes policy
  - Detail fixture contract
- **Implementation guide:** See `PHASES_2_TO_7_GUIDE.md` (Phase 5 section)
- **Effort:** ~1 hour
- **Next:** After Phase 5, proceed to Phase 6

### Phase 6: Golden Path Script ⏳
- **File:** `tests/fixtures/run_golden_path.sh` (NEW)
- **Purpose:** End-to-end validation from clean checkout
- **Steps:**
  1. Create fixture extraction files (3-5 papers)
  2. Run graph builder
  3. Run contradiction detector
  4. Create validation records (JSONL)
  5. Run importer
  6. Run compiler
  7. Run consumer validator
- **Implementation guide:** See `PHASES_2_TO_7_GUIDE.md` (Phase 6 section)
- **Effort:** ~1 hour
- **Next:** After Phase 6, proceed to Phase 7

### Phase 7: Authorization Gate ⏳
- **File:** `AUTHORIZATION_GATE.md` (NEW)
- **Deliverable:** Final checklist before corpus ingestion
- **Checklist:**
  - [ ] Phase 1-6 all complete
  - [ ] run_golden_path.sh passes from clean checkout
  - [ ] Exit code tests pass
  - [ ] Enhanced fixture handles all 10 types
  - [ ] Consumer validator rejects invalid specs
  - [ ] ADR documents all policies
  - [ ] Hashes independently reproducible
- **Implementation guide:** See `PHASES_2_TO_7_GUIDE.md` (Phase 7 section)
- **Effort:** ~0.5 hour
- **Next:** After Phase 7, **AUTHORIZE CORPUS INGESTION**

---

## Test Status

| Test Suite | Status | Count |
|-----------|--------|-------|
| test_compiler_validation.py | ✅ Passing | 7 tests |
| test_compiler_exit_codes.py | ✅ Passing | 5 tests |
| test_golden_path_fixture | ✅ Ready | Not yet run |
| Run existing: | `python tests/test_compiler_validation.py` |
| Run exit codes: | `python tests/test_compiler_exit_codes.py` |
| Run fixture: | `python tests/fixtures/golden_fixture_10_types.py` |

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

**Before processing 10 papers, verify:**

- [ ] All 7 phases complete
- [ ] run_golden_path.sh passes
- [ ] All tests passing
- [ ] Hashes independently reproducible
- [ ] ADR documents all policies
- [ ] Manual review flow validated
- [ ] Consumer schema validates specs

**Authorization status:** PENDING (waiting for Phases 4-7)

---

## Notes

- All implementation guides in `PHASES_2_TO_7_GUIDE.md`
- Validation importer ready: `scripts/import_causal_validations.py`
- Contradiction detection ready: `scripts/detect_contradictions.py`
- Golden fixture ready: `tests/fixtures/golden_fixture_10_types.py`
- Next session: Begin Phase 4 (Consumer Validator)
