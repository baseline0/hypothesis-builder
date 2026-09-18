# hypothesis-builder

Automated literature review → testable hypotheses for the membrane repo.

## Overview

This repo generates structured **testable hypotheses** from automated literature review, producing a `hypotheses.json` contract that the [membrane](https://github.com/baseline0/membrane) repo consumes.

**Goal:** Transform 10 research papers into 5 evidence-backed hypotheses (RQ1-RQ5) with confidence scores, supporting papers, and algorithm parameters.

**Timeline:** 2 weeks (Days 1-10: extraction, Days 11-12: synthesis, Days 13-14: validation)

---

## Architecture

### Three-Track Pipeline

**Track A: Research Questions (RQs)**
```
Evidence extraction → Evidence matrix → Hypothesis export
(scripts/evidence_synthesis.py + hypothesis_exporter.py)
```

**Track B: Causal Modeling (NEW)**
```
Extracted causal claims → Causal graph → Human validation → Experiment specs
(scripts/causal_graph_builder.py + experiment_spec_compiler.py)
```

**Track C: Synthesis**
```
Both tracks converge → membrane repo
(hypotheses.json + experiment_specs.json)
```

Complete flow:

```
Papers (PDF)
    ↓
scripts/evidence_extractor.py
    ├─ Extracts RQ evidence (rq1_combines_quantum_psys, etc.)
    └─ Extracts causal claims (cause → effect with mechanism)
    ↓
automation/extracted_evidence/*.json
    ├─ Track A: scripts/evidence_synthesis.py → evidence_matrix.json
    │                                                          ↓
    │                                        hypothesis_exporter.py
    │                                                          ↓
    │                                        synthesis/hypotheses.json
    │
    └─ Track B: scripts/causal_graph_builder.py → causal_graph.json
                                                       ↓
                                        manual/CAUSAL_VALIDATION_TEMPLATE.md
                                                 (human review)
                                                       ↓
                                        experiment_spec_compiler.py
                                                       ↓
                                        synthesis/experiment_specs.json
    ↓
membrane repo
    ├─ paper/model.py (consumes hypotheses.json)
    └─ benchmarks/runners/cec2017_subset.py (consumes experiment_specs.json)
```

**Key innovation:** Causal track turns literature claims into testable experiments with explicit assumptions, not just prose hypotheses.


---

## Files & Directories

```
hypothesis-builder/
├── README.md                          # This file
├── docs/
│   ├── REVIEW_PROTOCOL_QIPS.md        # Protocol: 5 RQs, quality rubric, synthesis strategy
│   ├── REVIEW_PROTOCOL_TEMPLATE.md    # Reusable template for future reviews
│   └── LITERATURE_REVIEW_TEMPLATE.md  # Per-paper form (copy for each paper)
│
├── reference/lit_review/              # Papers (git-ignored, local only)
│   └── *.pdf
│
├── scripts/
│   ├── evidence_extractor.py          # Template + export (Claude reads PDFs)
│   ├── evidence_synthesis.py          # Build evidence matrix from extractions
│   └── hypothesis_exporter.py         # Convert synthesis to testable hypotheses
│
├── automation/
│   ├── extracted_evidence/            # Per-paper JSON (output from extractor)
│   │   ├── paper_1_zhang_2023.json
│   │   ├── paper_2_liu_2021.json
│   │   └── ... (×10 papers)
│   └── processed/
│       └── evidence_matrix.json       # Synthesis output (RQ × paper × finding)
│
├── manual/                            # User validations (spot-check phase)
│   └── validations.md                 # User review of extracted evidence
│
└── synthesis/
    └── hypotheses.json                # FINAL: testable hypotheses for membrane repo
```

---

## Causal Modeling (NEW: Track B)

The revised pipeline adds explicit **causal claims** extraction and validation:

### What is Causal Modeling?

Instead of just extracting findings (e.g., "dimensionality collapse occurs"), extract **causal relationships**:

```json
{
  "cause": "population_diversity",
  "effect": "premature_convergence",
  "mechanism": "Search space coverage decreases with low diversity",
  "direction": "increases",
  "causal_confidence": "medium",
  "evidence_type": "controlled_benchmark_experiment"
}
```

This enables:

1. **Causal graph synthesis** — Which variables affect which, through which mechanisms?
2. **Identified confounders** — What must be controlled to isolate the effect?
3. **Experiment generation** — What interventions can test the causal claim?
4. **Falsification criteria** — How would we know the hypothesis is wrong?

### Causal Workflow (Phases 1-3)

**Phase 1:** Claude extracts causal claims during evidence extraction
```bash
python scripts/evidence_extractor.py --causal-template
# Shows template for "cause → effect" relationships with provenance
```

**Phase 2:** Build and validate causal graph
```bash
python scripts/causal_graph_builder.py \
    --extractions "automation/extracted_evidence/*.json" \
    --output automation/processed/causal_graph.json
# Output: causal_graph.json (proposed edges) + causal_graph.mmd (diagram)
# Manual validation: manual/CAUSAL_VALIDATION_TEMPLATE.md
```

**Phase 3:** Generate experiment specifications
```bash
python scripts/experiment_spec_compiler.py \
    --graph automation/processed/causal_graph.json \
    --output synthesis/experiment_specs.json
# Output: testable experiment specs with interventions, outcomes, controls
```

## Workflow

### Phase 1: Extract Evidence (Days 1-10)

1. **Get papers**
   ```bash
   cd reference/lit_review/
   # Copy 10 PDFs here (git-ignored)
   ls *.pdf  # Should show 10 papers
   ```

2. **For each paper, Claude extracts evidence**
   ```bash
   python scripts/evidence_extractor.py --template
   # Shows empty JSON template
   ```
   
   In this Claude session:
   - User provides paper PDF
   - Claude reads it
   - Claude fills `automation/extracted_evidence/paper_N_<name>.json`
   - Repeat for all 10 papers

3. **Check extraction progress**
   ```bash
   ls automation/extracted_evidence/
   # Should show: paper_1, paper_2, ..., paper_10 (10 JSON files)
   ```

### Phase 2: Synthesize (Days 11-12)

1. **Build evidence matrix**
   ```bash
   python scripts/evidence_synthesis.py \
       --extractions "automation/extracted_evidence/*.json" \
       --output automation/processed/evidence_matrix.json
   ```
   
   Output: `automation/processed/evidence_matrix.json`
   - RQ1-RQ5 findings mapped across papers
   - Confidence scores (high/medium/low)
   - Quality-weighted evidence

2. **Export testable hypotheses**
   ```bash
   python scripts/hypothesis_exporter.py \
       --evidence automation/processed/evidence_matrix.json \
       --output synthesis/hypotheses.json
   ```
   
   Output: `synthesis/hypotheses.json`
   - 5 hypotheses (H1-H5), one per RQ
   - Novelty statement
   - Algorithm parameters
   - Audit trail (papers analyzed, synthesis method)

### Phase 3: Validate & Wire (Days 13-14)

1. **User spot-checks extraction**
   - Review `manual/validations.md`
   - Flag any conflicts or surprises in Claude's extraction
   - Record in `manual/validations.md`

2. **Wire into membrane repo**
   ```bash
   cd ../membrane
   cp ../hypothesis-builder/synthesis/hypotheses.json ./paper/hypotheses.json
   # Update paper/model.py to import hypotheses
   # Update benchmarks/runners/cec2017_subset.py to use parameters
   ```

---

## Running the Full Pipeline

```bash
# After all 10 papers extracted (Day 10):
python scripts/evidence_synthesis.py \
    --extractions "automation/extracted_evidence/*.json" \
    --output automation/processed/evidence_matrix.json

# Then export hypotheses:
python scripts/hypothesis_exporter.py \
    --evidence automation/processed/evidence_matrix.json \
    --output synthesis/hypotheses.json

# Result: synthesis/hypotheses.json ready for membrane repo
cat synthesis/hypotheses.json | jq '.novelty_statement'
```

---

## Evidence Template (For Each Paper)

Claude fills this template when reading each PDF:

```json
{
  "paper_name": "paper_1_zhang_2023",
  "title": "Survey of Quantum-Inspired Genetic Algorithms",
  "authors": "Zhang et al.",
  "year": 2023,
  "doi": "10.1234/...",
  "access_status": "open-access",
  
  "algorithm": "QIGA",
  "problem_domain": "continuous optimization",
  "benchmark_suite": "CEC2017",
  "dimensions_tested": "10D, 30D, 50D",
  "population_size": 50,
  "generations": 200,
  
  "novel_idea": "Applies quantum rotation gates to GA population",
  "differs_from_prior": "First to combine superposition with tournament selection",
  "quantitative_gain": "15% faster convergence vs standard GA",
  "limitations": "Collapses at D>30 due to diversity loss",
  
  "rq1_combines_quantum_psys": false,
  "rq1_evidence": "Paper covers QIGA but not P-systems",
  "rq1_quote": "Page 42: 'quantum rotation operates on binary chromosomes'",
  
  "rq2_discusses_collapse": true,
  "rq2_root_cause": "diversity loss in quantum rotation",
  "rq2_dimension_performance": {"10D": 45.2, "30D": 120.5, "50D": 450.0},
  "rq2_quote": "Section 4.3: 'Performance degrades rapidly beyond D=30'",
  
  "rq3_adaptive_mechanisms": ["inertia weight decay", "tournament selection"],
  "rq3_effectiveness": "Both proven effective; combined in proposed QIPS",
  "rq3_quote": "Figure 3 shows inertia decay maintains diversity",
  
  "rq4_cec2017_baseline": true,
  "rq4_ga_results": {
    "F1": {"mean": 50.2, "std": 15.3},
    "F3": {"mean": 120.5, "std": 42.0},
    "F4": {"mean": 89.3, "std": 28.1}
  },
  "rq4_quote": "Table 2: GA baseline on CEC2017 10D",
  
  "rq5_high_d_tested": true,
  "rq5_scalability_trend": "degrades",
  "rq5_d_performance": {"10D": 45.2, "30D": 120.5, "50D": 450.0},
  "rq5_quote": "Section 5: 'Scalability remains open problem for high-D'",
  
  "quality_algorithm_clarity": 2,
  "quality_benchmark_rigor": 2,
  "quality_relevance_rqs": 2,
  "quality_reproducibility": 1,
  "quality_total": 7,
  "quality_rationale": "Comprehensive survey with clear algorithms; CEC2017 benchmarks strong; limited discussion of P-systems",
  
  "will_adopt": ["quantum rotation formula", "tournament selection", "CEC2017 baseline"],
  "will_adapt": ["inertia decay → P-system rule update frequency"],
  "will_avoid": ["direct quantum simulation (classical only)"],
  
  "summary": "Comprehensive QIGA survey; establishes quantum rotation basics and GA baseline. Confirms dimensionality collapse problem at D>30."
}
```

---

## Evidence Synthesis Output

`automation/processed/evidence_matrix.json` structure:

```json
{
  "metadata": {
    "total_papers": 10,
    "paper_names": ["paper_1_zhang_2023", "paper_2_liu_2021", ...],
    "synthesis_method": "quality-weighted consensus"
  },
  "evidence": {
    "RQ1_novelty": {
      "rq": "RQ1: Is quantum-inspired + P-systems novel?",
      "finding": "No prior work combines quantum-inspired with P-systems",
      "supporting_papers": ["paper_1", "paper_4", "paper_6"],
      "confidence": "high",
      "quality_weighted_score": 18
    },
    "RQ2_collapse": {
      "rq": "RQ2: What causes dimensionality collapse?",
      "finding": "Dimensionality collapse at D>30 caused by: diversity loss",
      "consensus_root_cause": "diversity loss",
      "supporting_papers": ["paper_2", "paper_7"],
      "confidence": "high"
    },
    ...
  }
}
```

---

## Hypotheses Output

`synthesis/hypotheses.json` structure (consumed by membrane repo):

```json
{
  "novelty_statement": "We propose Quantum-Inspired P-Systems (QIPS) for continuous optimization on CEC2017 benchmarks. QIPS is novel because: (1) No prior work combines quantum-inspired computing with P-system formalism (high confidence), (2) we address the dimensionality collapse problem (high confidence) by combining three adaptive strategies from GA, PSO, and P-systems (high confidence). We validate against GA baseline on 10D CEC2017 subset, targeting 10-20% improvement in solution quality.",
  
  "hypotheses": [
    {
      "id": "H1_novelty",
      "rq": "RQ1: Is quantum-inspired + P-systems novel?",
      "claim": "No prior work combines quantum-inspired computing with P-system formalism",
      "confidence": "high",
      "supporting_papers": ["paper_1", "paper_4", "paper_6"],
      "implication": "QIPS is defensibly novel; can proceed with novelty claim in paper"
    },
    {
      "id": "H2_collapse",
      "rq": "RQ2: What causes dimensionality collapse?",
      "claim": "Dimensionality collapse at D>30 caused by: diversity loss",
      "confidence": "high",
      "testable_as": "Measure QIPS convergence + diversity at D=10,30,50",
      "implication": "Design QIPS to maintain diversity via P-system hierarchies; test whether QIPS avoids collapse"
    },
    ...
  ],
  
  "parameters": {
    "ga_baseline": {
      "population": 50,
      "generations": 200,
      "crossover_probability": 0.8,
      "mutation_probability": 0.1
    },
    "qips_recommendations": {
      "population": 50,
      "generations": 200,
      "dimension_start": 10,
      "dimensions_to_test": [10, 30, 50]
    },
    "cec2017_subset": {
      "unimodal": ["F1", "F3", "F4"],
      "multimodal": ["F5", "F6", "F8"],
      "hybrid": ["F11", "F14", "F17"],
      "composition": ["F21", "F26"],
      "total_functions": 11
    }
  },
  
  "audit_trail": {
    "total_papers_analyzed": 10,
    "papers": ["paper_1", "paper_2", ...],
    "synthesis_method": "quality-weighted consensus"
  }
}
```

---

## How Membrane Repo Uses This

In `membrane/paper/model.py`:

```python
import json
from pathlib import Path

# Load hypotheses from hypothesis-builder
with open("paper/hypotheses.json") as f:
    hypotheses = json.load(f)

# Extract novelty statement for paper
novelty_statement = hypotheses["novelty_statement"]

# Use parameter recommendations
ga_pop = hypotheses["parameters"]["ga_baseline"]["population"]
cec_functions = hypotheses["parameters"]["cec2017_subset"]["unimodal"]

# Reference supporting papers in bibliography
supporting_papers = [h["supporting_papers"] for h in hypotheses["hypotheses"]]
```

---

## Key Concepts

### 5 Research Questions (RQs)

| RQ | Question | Confidence Metric |
|----|----------|-------------------|
| RQ1 | Is quantum-inspired + P-systems novel? | Papers saying NO prior work |
| RQ2 | What causes dimensionality collapse? | Consensus on root cause |
| RQ3 | What adaptive strategies exist? | Mechanisms mentioned 3+ times |
| RQ4 | GA baseline on CEC2017? | 2+ papers with mean ± std |
| RQ5 | Does QIPS scale to high-D? | Papers testing D>30 |

### Confidence Levels

- **High:** Finding appears in 3+ papers or consensus is clear
- **Medium:** Finding appears in 1-2 papers or limited consensus
- **Low:** Finding mentioned but not well-supported

### Quality Scoring

Each paper rated 0-8 on:
- Algorithm clarity (0-2)
- Benchmark rigor (0-2)
- RQ relevance (0-2)
- Reproducibility (0-2)

High-quality papers (7-8) weight findings more heavily.

---

## Testing the Pipeline

```bash
# Create dummy evidence for testing
python -c "
import json
from pathlib import Path

evidence = {
    'paper_name': 'test_paper_1',
    'title': 'Test Paper',
    'authors': 'Test Author',
    'year': 2023,
    'doi': 'test/doi',
    'access_status': 'test',
    'algorithm': 'GA',
    'problem_domain': 'continuous',
    'benchmark_suite': 'CEC2017',
    'dimensions_tested': '10D',
    'population_size': 50,
    'generations': 200,
    'novel_idea': 'Test idea',
    'differs_from_prior': 'Test difference',
    'quantitative_gain': '10%',
    'limitations': 'None',
    'rq1_combines_quantum_psys': False,
    'rq1_evidence': 'No',
    'rq1_quote': 'N/A',
    'rq2_discusses_collapse': False,
    'rq2_root_cause': 'N/A',
    'rq2_dimension_performance': {},
    'rq2_quote': 'N/A',
    'rq3_adaptive_mechanisms': [],
    'rq3_effectiveness': 'N/A',
    'rq3_quote': 'N/A',
    'rq4_cec2017_baseline': False,
    'rq4_ga_results': {},
    'rq4_quote': 'N/A',
    'rq5_high_d_tested': False,
    'rq5_scalability_trend': 'N/A',
    'rq5_d_performance': {},
    'rq5_quote': 'N/A',
    'quality_algorithm_clarity': 1,
    'quality_benchmark_rigor': 1,
    'quality_relevance_rqs': 1,
    'quality_reproducibility': 1,
    'quality_total': 4,
    'quality_rationale': 'Test paper',
    'will_adopt': [],
    'will_adapt': [],
    'will_avoid': [],
    'summary': 'Test summary'
}

Path('automation/extracted_evidence').mkdir(parents=True, exist_ok=True)
with open('automation/extracted_evidence/test_paper_1.json', 'w') as f:
    json.dump(evidence, f, indent=2)
"

# Run synthesis
python scripts/evidence_synthesis.py \
    --extractions "automation/extracted_evidence/test_paper_1.json" \
    --output automation/processed/evidence_matrix.json

# Export hypotheses
python scripts/hypothesis_exporter.py \
    --evidence automation/processed/evidence_matrix.json \
    --output synthesis/hypotheses.json

# Check output
cat synthesis/hypotheses.json | jq '.novelty_statement'
```

---

## Integration with Membrane Repo

After synthesis is complete:

```bash
# Copy hypotheses to membrane repo
cp synthesis/hypotheses.json ../membrane/paper/hypotheses.json

# Update membrane model.py to import and use
cd ../membrane
git add paper/hypotheses.json
git commit -m "hypothesis-builder: Import testable hypotheses from lit review"
```

Membrane repo then:
1. Reads `hypotheses.json` in `paper/model.py`
2. Uses novelty statement in paper abstract
3. Uses parameters in `benchmarks/runners/cec2017_subset.py`
4. References supporting papers in bibliography

---

## Questions?

See `docs/REVIEW_PROTOCOL_QIPS.md` for detailed protocol.
See `docs/REVIEW_PROTOCOL_TEMPLATE.md` for reusable template for future projects.
