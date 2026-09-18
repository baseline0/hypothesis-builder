# Phase 4: Integration with Membrane

**Status:** Not yet started  
**Triggered after:** Phase 3 (experiment specs compiled)  
**Prerequisite:** `synthesis/experiment_specs.json` exists and is reviewed

---

## Goal

Wire the causal track (`experiment_specs.json`) into the membrane repository so that:

1. Benchmark runner reads testable experiment specs
2. Factorial design (factors, levels, replicates) is extracted from specs
3. Mediator measurements are collected during algorithm execution
4. Predictions are checked post-execution
5. Falsification criteria determine experiment success/failure

---

## Files to Update in `membrane` Repo

### 1. `benchmarks/runners/cec2017_subset.py`

**Current state:** Hardcoded GA + QIPS parameters  
**Change:** Read from `hypotheses.json` and `experiment_specs.json`

```python
import json
from pathlib import Path

# Load both tracks
with open("paper/hypotheses.json") as f:
    hypotheses = json.load(f)

with open("benchmarks/experiment_specs.json") as f:
    experiment_specs = json.load(f)

# Extract factorial design
spec = experiment_specs["experiments"][0]  # or loop all
factors = {f["name"]: f["levels"] for f in spec["design"]["factors"]}
replicates = spec["design"]["replicates"]

# Run experiments
for factor_values in itertools.product(*factors.values()):
    for seed in range(replicates):
        result = run_algorithm(
            algorithm=factor_values[0],  # GA or QIPS
            dimension=factor_values[1],  # 10, 30, 50
            function=...,
            seed=seed,
        )
        
        # Collect mediator measurements
        mediator_trace = result.get("diversity_trajectory", [])
        
        # Check predictions
        predictions = spec["predictions"]
        for pred in predictions:
            verified = check_prediction(pred, result, mediator_trace)
            log_prediction_check(pred, verified)
        
        # Check falsification criteria
        falsified = False
        for criterion in spec["falsification_criteria"]:
            if criterion_triggered(criterion, result):
                falsified = True
                log_falsification(criterion)
```

### 2. `paper/model.py`

**Current state:** Placeholder formulas  
**Change:** Extract novelty statement and parameters from `hypotheses.json`

```python
import json

with open("paper/hypotheses.json") as f:
    hypotheses = json.load(f)

# Use novelty statement in abstract
NOVELTY_STATEMENT = hypotheses["novelty_statement"]

# Extract QIPS parameters
params = hypotheses["parameters"]
GA_POPULATION = params["ga_baseline"]["population"]  # 50
GA_GENERATIONS = params["ga_baseline"]["generations"]  # 200
CEC_FUNCTIONS = params["cec2017_subset"]["unimodal"]  # ["F1", "F3", "F4"]

# Build formulas referencing supporting papers
NOVELTY_CITATIONS = []
for h in hypotheses["hypotheses"]:
    for paper in h["supporting_papers"]:
        NOVELTY_CITATIONS.append(paper)
```

### 3. `docs/experiment_log.md` (NEW)

**Purpose:** Track prediction checks and falsification attempts

```markdown
# Experiment Execution Log

## Experiment exp_0042: Effect of Diversity Mechanism on Final Fitness

**Date:** 2026-10-15  
**Algorithm:** QIPS  
**Dimension:** 10D  
**Replicates:** 30  

### Predictions Checked

| Prediction | Status | Details |
|-----------|--------|---------|
| "Enabling diversity mechanism increases final fitness" | ✅ VERIFIED | QIPS mean=52.1, GA mean=48.3, p<0.05 |
| "Effect mediated by diversity" | ⚠️ PARTIAL | Diversity rose but mechanism less clear |
| "Effect larger on multimodal" | ✅ VERIFIED | Multimodal: +8.5%, Unimodal: +3.2% |

### Falsification Checks

| Criterion | Status | Action |
|-----------|--------|--------|
| "No improvement after controlling for eval count" | ❌ FALSIFIED | QIPS still 5% better with same budget |
| "Diversity increases" | ✅ SATISFIED | Entropy 0.78 vs 0.62 for GA |

### Conclusion

Hypothesis **H2b supported**. Proceed to next experiment.
```

---

## Data Contract: `experiment_specs.json` Format

Membrane imports specs with this structure:

```json
{
  "export_version": "1.0.0",
  "total_experiments": 5,
  "experiments": [
    {
      "experiment_id": "exp_0001",
      "hypothesis_id": "H2b",
      "causal_claim": {
        "cause": "diversity_mechanism",
        "effect": "final_fitness",
        "mechanism": "population entropy increases",
        "supporting_papers": ["paper_1", "paper_2"]
      },
      "design": {
        "factors": [
          {"name": "algorithm", "levels": ["GA", "QIPS"]},
          {"name": "dimension", "levels": ["10", "30", "50"]},
          {"name": "function_class", "levels": ["unimodal", "multimodal"]}
        ],
        "replicates": 30
      },
      "measurements": {
        "primary": [
          {"variable": "final_fitness", "metric": "best_fitness_of_run", "collection_point": "end_of_run"}
        ],
        "secondary": [
          {"variable": "diversity", "metric": "population_entropy", "collection_point": "every_10_generations"}
        ]
      },
      "predictions": [
        "Enabling diversity mechanism increases final fitness",
        "Effect mediated by population diversity",
        "Effect larger on multimodal functions"
      ],
      "falsification_criteria": [
        "If diversity increases but fitness doesn't, mechanism is wrong"
      ]
    }
  ]
}
```

---

## Integration Checklist

### Pre-Integration (hypothesis-builder)

- [x] Phase 0: Define causal vocabulary
- [x] Phase 1: Extract causal claims in evidence template
- [x] Phase 2: Build causal graph + human validation
- [x] Phase 3: Compile experiment specs
- [ ] Review causal edges (user validation in `manual/CAUSAL_VALIDATION_TEMPLATE.md`)
- [ ] Run `causal_graph_builder.py` after all 10 papers extracted
- [ ] Run `experiment_spec_compiler.py` after graph validation
- [ ] Commit validated `synthesis/experiment_specs.json`

### Integration (membrane)

- [ ] Copy `synthesis/experiment_specs.json` to `benchmarks/`
- [ ] Update `benchmarks/runners/cec2017_subset.py` to read specs
- [ ] Add mediator collection (diversity trajectory) during execution
- [ ] Add prediction verification logic
- [ ] Add falsification criterion checks
- [ ] Generate `docs/experiment_log.md` with results
- [ ] Link results back to `hypothesis-builder` via commit SHAs
- [ ] Update `paper/model.py` to consume hypotheses.json
- [ ] Test: Run single experiment spec, verify all fields populated
- [ ] Test: Verify predictions are checked and logged

### Validation

- [ ] All 5 experiment specs execute without errors
- [ ] Predictions are measured and reported
- [ ] Falsification checks work as expected
- [ ] Results are reproducible (same seed → same outcome)
- [ ] Audit trail includes links to `hypothesis-builder` evidence

---

## Example: First Experiment Execution

```bash
cd membrane

# Load experiment spec
python -c "
import json
with open('benchmarks/experiment_specs.json') as f:
    specs = json.load(f)
exp = specs['experiments'][0]
print(f'Running: {exp[\"hypothesis_id\"]}')
print(f'Factors: {[f[\"name\"] for f in exp[\"design\"][\"factors\"]]}')
"

# Run factorial design
python benchmarks/runners/cec2017_subset.py \
    --experiment-spec benchmarks/experiment_specs.json \
    --experiment-id exp_0001 \
    --output results/exp_0001.json

# Verify
python -c "
import json
with open('results/exp_0001.json') as f:
    result = json.load(f)
print(f'Predictions verified: {result[\"predictions_verified\"]}')
print(f'Falsification triggered: {result[\"falsification_triggered\"]}')
"
```

---

## Data Flow

```
hypothesis-builder/synthesis/experiment_specs.json
    ↓ (copy to)
membrane/benchmarks/experiment_specs.json
    ↓ (read by)
benchmarks/runners/cec2017_subset.py
    ↓ (during execution)
Collect mediator measurements
Check predictions
Verify falsification criteria
    ↓ (output)
results/exp_0001.json
    ↓ (summarize in)
docs/experiment_log.md
    ↓ (cite in)
paper/main.typ (Results section)
```

---

## Success Criteria

✅ Experiment specs load without errors  
✅ Factorial design is executed as specified  
✅ All predictions are measured and reported  
✅ Falsification criteria work  
✅ Results are reproducible  
✅ Audit trail links back to hypothesis-builder evidence  

---

## Timeline

- **Week 1:** User validates causal edges in `manual/CAUSAL_VALIDATION_TEMPLATE.md`
- **Week 2:** Run `causal_graph_builder.py` + `experiment_spec_compiler.py`
- **Week 3:** Integrate experiment_specs.json into membrane
- **Week 4:** Run first experiment suite, verify predictions
- **Week 5:** Refine based on results, write Results section in paper

---

## Notes

- Do not modify `experiment_specs.json` by hand; regenerate from validated graph
- Mediator measurements must match variable names in specs
- Falsification is not binary; track partial support, contradictions
- Link every result back to `hypothesis-builder` commit SHA for full audit trail

---

**Next:** After Phase 3 completes and causal graph is validated, proceed to Phase 4 integration.
