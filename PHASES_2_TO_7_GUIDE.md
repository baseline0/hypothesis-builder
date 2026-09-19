# Implementation Guide: Phases 2-7

**Phase 1 (Contradiction Detection)** is committed. Continue with phases 2-7.

---

## Phase 2: Exit Code Testing

**File:** `tests/test_compiler_exit_codes.py` (NEW)

**Implementation:**

```python
import subprocess
import tempfile
import json
from pathlib import Path

def test_no_accepted_edges_exits_1():
    """No accepted edges → compiler exits 1."""
    graph = {
        "edges": [{
            "edge_id": "edge_0001",
            "status": "proposed",  # not accepted
            "cause": "X",
            "effect": "Y",
        }]
    }
    
    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"
        
        with open(graph_path, "w") as f:
            json.dump(graph, f)
        
        result = subprocess.run(
            [
                "python", "scripts/experiment_spec_compiler.py",
                "--graph", str(graph_path),
                "--output", str(output_path),
            ],
            cwd=".",
            capture_output=True,
        )
        
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert not output_path.exists(), "Output file should not exist on failure"

def test_valid_edge_exits_0():
    """Valid accepted edge → compiler exits 0."""
    # Create complete valid edge and verify exit 0
    # (Similar structure, but with status="accepted", reviewer, etc.)
    pass

def test_mixed_valid_invalid_exits_0():
    """Mixed valid/invalid → exit 0 with rejection report."""
    # Create graph with 1 valid + 2 invalid edges
    # Verify exit 0, output contains only valid edge
    pass
```

**Run:** `pytest tests/test_compiler_exit_codes.py -v`

---

## Phase 3: Enhanced Fixture

**File:** `tests/fixtures/golden_fixture_complete.py` (NEW)

**Implementation:**

```python
def create_complete_fixture():
    """Create 10-edge fixture for comprehensive testing."""
    return [
        # 1. Accepted, known mechanism, complete
        {
            "edge_id": "edge_1_accepted_known",
            "status": "accepted",
            "cause": "diversity_mechanism",
            "effect": "final_fitness",
            "mechanism": "entropy increases",
            "mechanism_status": "known",
            "direction": "increases",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00Z",
            "source": {"paper_id": "p1", "page": 42, "quote": "..."},
        },
        # 2. Accepted, unknown mechanism (exploratory)
        {
            "edge_id": "edge_2_accepted_unknown",
            "status": "accepted",
            "mechanism_status": "unknown",
            "purpose": "hypothesis_generating",
        },
        # 3. Low confidence, observational
        {
            "edge_id": "edge_3_low_confidence",
            "status": "accepted",
            "evidence_type": "observational",
            "causal_confidence": "low",
        },
        # 4-5. Contradictory pair (same estimand, opposite direction)
        {
            "edge_id": "edge_4_contradictory_a",
            "cause": "mechanism_X",
            "effect": "outcome_Y",
            "direction": "increases",
        },
        {
            "edge_id": "edge_5_contradictory_b",
            "cause": "mechanism_X",
            "effect": "outcome_Y",
            "direction": "decreases",
        },
        # 6-7. Independent outcomes (same cause, different effects)
        {
            "edge_id": "edge_6_independent_1",
            "cause": "mechanism_Z",
            "effect": "outcome_A",
        },
        {
            "edge_id": "edge_7_independent_2",
            "cause": "mechanism_Z",
            "effect": "outcome_B",
        },
        # 8. Multiple supporting papers
        {
            "edge_id": "edge_8_multi_source",
            "supporting_papers": ["p1", "p2", "p3", "p5"],
        },
        # 9. Proposed (should be rejected)
        {
            "edge_id": "edge_9_proposed",
            "status": "proposed",
        },
        # 10. Incomplete (missing reviewer)
        {
            "edge_id": "edge_10_incomplete",
            "status": "accepted",
            "reviewer": None,  # invalid
        },
    ]

def test_enhanced_fixture():
    """Test all 10 fixture types."""
    edges = create_complete_fixture()
    
    # Run through pipeline
    # Verify:
    # - Edges 1-8 compile (8 specs)
    # - Edge 4-5 marked disputed (or compile as discriminating)
    # - Edges 6-7 compile independently
    # - Edge 9 rejected (proposed)
    # - Edge 10 rejected (incomplete)
    
    assert len(compiled_specs) == 8  # or adjust based on contradiction policy
```

---

## Phase 4: Membrane Consumer Validator

**File:** `scripts/validate_experiment_specs.py` (NEW)

**Implementation:**

```python
def validate_experiment_specs(specs_path: Path) -> bool:
    """Validate specs against schema and business rules."""
    with open(specs_path) as f:
        specs = json.load(f)
    
    errors = []
    
    # Schema version
    if specs.get("schema_version") != "1.0.0":
        errors.append("Invalid schema_version")
    
    # Each experiment must have required fields
    for exp in specs.get("experiments", []):
        if not exp.get("estimand"):
            errors.append(f"{exp.get('id')}: missing estimand")
        if not exp.get("design", {}).get("design_controls"):
            errors.append(f"{exp.get('id')}: missing design_controls")
        if not exp.get("analysis"):
            errors.append(f"{exp.get('id')}: missing analysis")
        if not exp.get("provenance"):
            errors.append(f"{exp.get('id')}: missing provenance")
        
        # Estimand validation
        estimand = exp.get("estimand", {})
        if estimand.get("treatment") == estimand.get("outcome"):
            errors.append(f"{exp.get('id')}: treatment and outcome cannot be same")
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  {error}")
        return False
    
    print(f"✓ Spec validation passed: {len(specs.get('experiments', []))} experiments")
    return True
```

---

## Phase 5: Updated ADR

**File:** `docs/ADR-001-CAUSAL-MODELING.md`

**Add sections:**

```markdown
## Contradiction Detection

**Definition:** Same cause + same effect + opposite direction = contradictory

**Example:**
```
Edge A: diversity_mechanism → final_fitness, increases
Edge B: diversity_mechanism → final_fitness, decreases
```

**Policy:** Mark as disputed; excluded from normal specs
**Optional:** Compile as discriminating experiment (purpose: "discriminating")

## Validation Workflow (Updated)

1. causal_graph_builder.py → proposed graph
2. detect_contradictions.py → mark disputed edges
3. User creates manual/causal_validations.jsonl (JSONL records)
4. import_causal_validations.py → applies decisions (graph_hash binding)
5. experiment_spec_compiler.py → compiles validated edges only

**Graph hash binding ensures:** Validator reviewed exact version that compiles.

## Exit Codes

- No eligible edges → exit 1
- Valid + invalid mixed → exit 0 (with report)
- Compiler never emits specs from invalid edges
```

---

## Phase 6: Clean-Checkout Golden Path

**Script:** `run_golden_path.sh` (NEW)

```bash
#!/bin/bash
set -e

cd /tmp
rm -rf hypothesis-builder-test
git clone https://github.com/baseline0/hypothesis-builder.git hypothesis-builder-test
cd hypothesis-builder-test
git checkout 208a93c

# Create fixture
mkdir -p automation/extracted_evidence
cat > automation/extracted_evidence/fixture_a.json << 'EOF'
{...fixture paper A...}
EOF

# Build graph
python scripts/causal_graph_builder.py \
    --extractions "automation/extracted_evidence/fixture_a.json" \
    --output automation/processed/causal_graph.json

# Detect contradictions
python scripts/detect_contradictions.py \
    --graph automation/processed/causal_graph.json \
    --output automation/processed/causal_graph_marked.json

# Create validations
cat > manual/causal_validations.jsonl << 'EOF'
{"edge_id": "edge_0000", "decision": "accepted", "reviewer": "test", "reviewed_at": "2026-09-18T00:00Z", "graph_hash": "<computed>", "rationale": "test"}
EOF

# Import validations
python scripts/import_causal_validations.py \
    --validations manual/causal_validations.jsonl \
    --graph automation/processed/causal_graph_marked.json \
    --output automation/processed/causal_graph_validated.json

# Compile specs
python scripts/experiment_spec_compiler.py \
    --graph automation/processed/causal_graph_validated.json \
    --output synthesis/experiment_specs.json

# Validate specs
python scripts/validate_experiment_specs.py synthesis/experiment_specs.json

echo "✓ Golden path complete"
```

---

## Phase 7: Authorization Checklist

**File:** `AUTHORIZATION_GATE.md` (NEW)

```markdown
# Corpus Ingestion Authorization Gate

## Phase Completion Checklist

- [ ] Phase 1: detect_contradictions.py committed and tested
- [ ] Phase 2: test_compiler_exit_codes.py all tests pass
- [ ] Phase 3: golden_fixture_complete.py handles 10 types
- [ ] Phase 4: validate_experiment_specs.py rejects invalid specs
- [ ] Phase 5: ADR updated with all policies
- [ ] Phase 6: run_golden_path.sh passes from clean checkout
- [ ] Phase 7: All 6 checklist items above pass

## Execution Steps

1. `cd /tmp && bash run_golden_path.sh`
2. Verify exit code = 0
3. Verify synthesis/experiment_specs.json has 8+ valid specs
4. Verify rejected edges not in output
5. Verify hashes independently reproducible
6. **AUTHORIZE**: If all pass, proceed to ten-paper corpus

## Authorization Decision

Date: ___________
Authorized by: ___________
Notes: ___________
```

---

## Execution Order

```bash
# 1. Complete Phase 1 (already done: detect_contradictions.py)
git add scripts/detect_contradictions.py
git commit -m "phase-1: contradiction detection"

# 2. Implement Phase 2: exit codes
# (Write tests/test_compiler_exit_codes.py)
pytest tests/test_compiler_exit_codes.py -v

# 3. Implement Phase 3: enhanced fixture
# (Write tests/fixtures/golden_fixture_complete.py)
pytest tests/test_compiler_validation.py::test_golden_path_fixture -v

# 4. Implement Phase 4: consumer validator
# (Write scripts/validate_experiment_specs.py)
python scripts/validate_experiment_specs.py synthesis/experiment_specs.json

# 5. Update Phase 5: ADR
# (Edit docs/ADR-001-CAUSAL-MODELING.md)
git add docs/ADR-001-CAUSAL-MODELING.md

# 6. Run Phase 6: golden path
bash tests/fixtures/run_golden_path.sh

# 7. Final gate: checklist
# (Review AUTHORIZATION_GATE.md)
```

---

**Total estimate:** 6-8 hours for all phases.

**Result:** Production-ready corpus ingestion with full validation gates.
