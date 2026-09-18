# Literature Review Protocol Template (Reusable)

**Purpose:** Define a structured narrative review protocol before reading papers. Use this template for any future research project.

**Benefits:**
- ✅ Reduces bias (define criteria before reading)
- ✅ Reproducible (anyone can follow same steps)
- ✅ Efficient (focus reading on relevant questions)
- ✅ Traceable (git commits show evolution)

---

## 1. Research Context

**Project:** [Name]
**Goal:** [1-2 sentence research objective]
**Timeline:** [e.g., Weeks 1-2 of project]
**Scope:** [e.g., 10 curated papers, narrow domain]

---

## 2. PICO Framework (Customized)

**Population:** [What domain/problem/system are you studying?]
Example: "Optimization algorithms (genetic, particle swarm, membrane-based)"

**Intervention:** [What technique/method are you investigating?]
Example: "Quantum-inspired concepts applied to membrane computing"

**Comparison:** [What's the baseline/alternative?]
Example: "Classical GA and PSO algorithms"

**Outcomes:** [What metrics/results matter?]
Example: "Convergence speed, solution quality, performance on CEC2017 benchmarks"

---

## 3. Research Questions (RQ)

List 3-5 specific questions your review will answer:

**RQ1:** [Critical question for novelty]
Example: "Has anyone combined quantum-inspired + P-systems before?"

**RQ2:** [Gap/problem to address]
Example: "What causes dimensionality collapse at D>30?"

**RQ3:** [Methods/techniques to learn from]
Example: "What adaptive strategies exist to prevent collapse?"

**RQ4:** [Baselines/benchmarks]
Example: "What's typical GA performance on CEC2017?"

**RQ5:** (Optional) [Practical constraint]
Example: "What are computational costs for high-D problems?"

---

## 4. Inclusion/Exclusion Criteria

**Include papers if:**
- [ ] Published in peer-reviewed venue (journal or top conference)
- [ ] Addresses at least one RQ
- [ ] Contains empirical results (algorithms tested, benchmarks run)
- [ ] Available via open-access or library access

**Exclude papers if:**
- [ ] Position papers / opinion pieces (no empirical work)
- [ ] Focuses on unrelated domain
- [ ] Too old / superseded by later work (unless foundational)

---

## 5. Quality Assessment Rubric

Rate each paper on these dimensions:

| Criterion | Strong (2) | Moderate (1) | Weak (0) |
|-----------|-----------|-------------|---------|
| **Methodological rigor** | Clear algorithm, reproducible, ablation studies | Algorithm described, some validation | Vague methods, hand-wavy results |
| **Experimental breadth** | Multiple benchmarks, multiple dimensions, statistical analysis | Single benchmark or limited variants | One toy example |
| **Relevance to RQs** | Directly addresses 2+ RQs | Addresses 1 RQ clearly | Marginal relevance |
| **Reproducibility** | Code available, parameters clear, datasets linked | Sufficient detail to re-implement | Missing critical details |

**Total:** 0-8 points. Use to weight findings (high-quality papers more influential).

---

## 6. Evidence Extraction Schema

**Standardized fields to extract from each paper:**

```yaml
Bibliographic:
  - Title
  - Authors
  - Year
  - Venue
  - DOI
  - Access status

Study Design:
  - Algorithm/method name
  - Problem domain
  - Benchmark suite (if applicable)
  - Dimensions tested
  - Comparison baseline

Main Contributions:
  - Novel idea (1 sentence)
  - How it differs from prior work
  - Quantitative improvements (if any)
  - Limitations acknowledged

Evidence for RQs:
  - RQ1: [Answer or N/A]
  - RQ2: [Answer or N/A]
  - RQ3: [Answer or N/A]
  - RQ4: [Answer or N/A]

Key Quotes:
  - [Passage on quantum concepts]
  - [Passage on P-system formalism]
  - [Passage on dimensionality issues]
  - [Performance numbers]

Quality Score: [0-8]
```

---

## 7. Synthesis Strategy

**After reading all papers, aggregate via:**

1. **Evidence matrix:** RQ × Paper findings (see Section 8)
2. **Consensus checks:** Which findings appear in 3+ papers? (high confidence)
3. **Gaps:** Which RQs are unanswered? (research opportunity)
4. **Contradictions:** Where do papers disagree? (investigate further)

---

## 8. Evidence Synthesis Table (Template)

```markdown
| RQ | Finding | Papers | Confidence | Implication |
|----|---------|--------|------------|-------------|
| 1  | [Summary of answer to RQ1] | #1, #4, #6 | High/Medium/Low | [What this means for your project] |
| 2  | [Summary of answer to RQ2] | #2, #7 | High/Medium/Low | [What this means for your project] |
| ... | ... | ... | ... | ... |
```

---

## 9. Novelty Statement (Iterative)

**Structure:**

```
## Novelty Statement (v1 → v2 → final)

**After papers 1-3:**
> "Preliminary: We propose combining [A] with [B] for [goal]..."

**After papers 1-7:**
> "Evidence suggests: [A + B] is novel because [RQ1 answer].
> It addresses [RQ2 gap]. Similar to [paper #X] but differs by [distinction]..."

**Final (after all papers + synthesis):**
> "We propose [Full name] combining [A, B, C] for [goal].
> Novel aspects: (1) [contribution], (2) [contribution].
> Gap addressed: [RQ2 finding].
> Validated on [benchmarks] showing [results]."
```

Track versions in git. Each commit shows how evidence refined your claim.

---

## 10. Review Schedule

**Template (adapt to your timeline):**

| Phase | Time | Task | Deliverable |
|-------|------|------|-------------|
| **Protocol** | Day 1 | Define PICO, RQs, criteria | This document (git commit) |
| **Reading** | Days 2-10 | Read papers, extract evidence | Per-paper evidence form + git commits |
| **Synthesis** | Days 11-12 | Fill evidence matrix, draft novelty | Synthesis table + novelty statement |
| **Integration** | Days 13-14 | Tie findings to implementation | Algorithm formulas, parameter choices |

---

## 11. Version Control Workflow

**Each paper gets a commit:**

```bash
git add docs/LITERATURE_REVIEW.md
git commit -m "lit-review: Extract evidence from paper #3 (Díaz-Pernil 2010)

- RQ1 finding: P-system tools exist but quantum-inspired not yet attempted
- RQ3 finding: Adaptive evolution strategies documented in P-lingua
- Quality: Moderate (2/8) — tools described but limited benchmarking
- Connection: QIPS will build on P-lingua framework
"
```

**Synthesis commit shows evolution:**

```bash
git commit -m "lit-review: Fill evidence synthesis matrix (papers 1-10 complete)

- RQ1: No prior quantum-inspired + P-system work (high confidence)
- RQ2: Dimensionality collapse documented in 3/10 papers
- RQ3: Three adaptive strategies identified (inertia, tournament, rules)
- Novelty statement: Now defensible based on evidence"
```

**Anyone can see your reasoning:**

```bash
git log --oneline docs/LITERATURE_REVIEW.md
# Shows step-by-step how you built the argument
```

---

## 12. Reuse for Future Projects

**To apply this protocol to a new review:**

1. Copy this file → `REVIEW_PROTOCOL_TEMPLATE.md` (no changes)
2. Create project-specific: `PROJECT_NAME/REVIEW_PROTOCOL.md`
3. Fill in sections 1-6 (customize PICO, RQs, criteria for new domain)
4. Follow sections 7-12 (same workflow, different research questions)

**Example:** Future review on "Quantum Optimization Algorithms" would:
- Keep PICO framework structure
- Change RQs to quantum-specific questions
- Adapt quality rubric to quantum computing standards
- Reuse evidence extraction schema
- Same synthesis approach

---

## Quick Reference

**Before reading:** Sections 1-6 (define your search)
**While reading:** Section 8 schema (extract evidence consistently)
**After reading:** Sections 7-9 (synthesize findings)
**Always:** Section 11 (track in git)
**Future:** Section 12 (reuse for new projects)
