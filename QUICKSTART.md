# Quick Start: Evidence Extraction & Synthesis

## 1️⃣ Extract Evidence (Days 1-10)

For each of the 10 papers in `reference/lit_review/`:

**In this Claude session:**

1. Upload paper PDF
2. Claude reads it and asks you to spot-check findings
3. Claude exports evidence to `automation/extracted_evidence/paper_N_<name>.json`

**Repeat for all 10 papers**

```bash
# Check progress
ls -1 automation/extracted_evidence/*.json | wc -l
# Should show: 10 (when all papers extracted)
```

---

## 2️⃣ Synthesize Evidence (Day 11-12)

Once all 10 papers are extracted:

```bash
# Build evidence matrix
python scripts/evidence_synthesis.py \
    --extractions "automation/extracted_evidence/*.json" \
    --output automation/processed/evidence_matrix.json

# Export testable hypotheses
python scripts/hypothesis_exporter.py \
    --evidence automation/processed/evidence_matrix.json \
    --output synthesis/hypotheses.json
```

**Check the output:**

```bash
cat synthesis/hypotheses.json | jq '.novelty_statement'
# Shows: "We propose Quantum-Inspired P-Systems (QIPS)..."

cat synthesis/hypotheses.json | jq '.hypotheses[].id'
# Shows: H1_novelty, H2_collapse, H3_adaptation, H4_baseline, H5_scalability
```

---

## 3️⃣ Validate & Wire (Days 13-14)

**User spot-check:**

1. Review extracted evidence in `automation/extracted_evidence/`
2. Compare with your notes from reading papers
3. Record findings in `manual/validations.md`
4. Fix any extraction errors

**Wire into membrane repo:**

```bash
cp synthesis/hypotheses.json ../membrane/paper/hypotheses.json
cd ../membrane
git add paper/hypotheses.json
git commit -m "hypothesis-builder: Import testable hypotheses from lit review"
```

---

## 📊 Understanding the Evidence Flow

```
Your 10 Papers (PDFs)
    ↓
Claude extracts structured evidence
    ↓
automation/extracted_evidence/*.json (per-paper JSON files)
    ↓
evidence_synthesis.py (builds evidence matrix, calculates confidence)
    ↓
automation/processed/evidence_matrix.json
    ↓
hypothesis_exporter.py (converts to testable hypotheses)
    ↓
synthesis/hypotheses.json ← Consumed by membrane repo
```

---

## 🔍 Evidence Template (What Claude Fills)

When Claude reads each paper, it extracts:

- **Metadata:** title, authors, year, DOI
- **Study design:** algorithm, benchmark, dimensions, population size
- **Main contribution:** novel idea, differs from prior, quantitative gain
- **RQ Evidence:** Findings for each of 5 research questions
- **Quality score:** 0-8 based on algorithm clarity, benchmark rigor, etc.
- **Connection to QIPS:** What we'll adopt/adapt/avoid

Example:
```json
{
  "paper_name": "paper_1_zhang_2023",
  "title": "Survey of Quantum-Inspired Genetic Algorithms",
  "rq1_combines_quantum_psys": false,
  "rq2_discusses_collapse": true,
  "rq2_root_cause": "diversity loss",
  "rq4_ga_results": {
    "F1": {"mean": 50.2, "std": 15.3}
  },
  "quality_total": 7,
  ...
}
```

---

## 📋 The 5 Research Questions (RQs)

| RQ | Question | Success Criteria |
|----|----------|------------------|
| **RQ1** | Is quantum-inspired + P-systems novel? | 0 papers mention prior work = HIGH confidence |
| **RQ2** | What causes dimensionality collapse? | 3+ papers identify root cause = HIGH confidence |
| **RQ3** | What adaptive strategies exist? | Mechanisms from GA/PSO/P-systems = evidence-based design |
| **RQ4** | GA baseline on CEC2017? | Mean ± std for 11 functions = comparison target |
| **RQ5** | Does QIPS scale to high-D? | Tests at D=10,30,50 = degradation curve |

---

## ✨ Hypothesis Output (synthesis/hypotheses.json)

The final JSON contains:

```json
{
  "novelty_statement": "We propose Quantum-Inspired P-Systems...",
  
  "hypotheses": [
    {
      "id": "H1_novelty",
      "rq": "RQ1: Is quantum-inspired + P-systems novel?",
      "claim": "No prior work combines quantum-inspired computing with P-system formalism",
      "confidence": "high",
      "supporting_papers": ["paper_1", "paper_4", "paper_6"],
      "implication": "QIPS is defensibly novel"
    },
    ...
  ],
  
  "parameters": {
    "ga_baseline": {"population": 50, "generations": 200, ...},
    "qips_recommendations": {...},
    "cec2017_subset": {
      "unimodal": ["F1", "F3", "F4"],
      "multimodal": ["F5", "F6", "F8"],
      "hybrid": ["F11", "F14", "F17"],
      "composition": ["F21", "F26"]
    }
  },
  
  "audit_trail": {
    "total_papers_analyzed": 10,
    "papers": ["paper_1", ...],
    "synthesis_method": "quality-weighted consensus"
  }
}
```

This is what the membrane repo consumes in `paper/model.py` and `benchmarks/runners/cec2017_subset.py`.

---

## 🚀 Next Steps

1. **Day 1:** Skim 10 papers, note which RQ each addresses
2. **Days 2-10:** Upload each PDF to Claude, get extraction
3. **Day 11:** Run `evidence_synthesis.py`
4. **Day 12:** Run `hypothesis_exporter.py`
5. **Days 13-14:** Validate and wire to membrane repo

See `README.md` for full documentation and `docs/REVIEW_PROTOCOL_QIPS.md` for detailed protocol.
