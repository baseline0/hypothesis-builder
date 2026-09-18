# Literature Review Protocol: Quantum-Inspired P-Systems (QIPS)

**Customization of:** `REVIEW_PROTOCOL_TEMPLATE.md`
**Project:** Membrane (Quantum-Inspired P-Systems paper)
**Timeline:** Weeks 1-2 (10 curated papers)
**Author:** Started 2026-09-18

---

## 1. Research Context

**Project:** Quantum-Inspired P-Systems for Continuous Optimization
**Goal:** Propose QIPS (combining quantum-inspired computing with P-system formalism) and validate on CEC2017 10D subset against GA baseline.
**Timeline:** 10 papers, 2 weeks (Days 1-10: reading, Days 11-12: synthesis, Days 13-14: draft)
**Scope:** 10 curated papers covering quantum-inspired algorithms, P-systems theory, and CEC2017 benchmarks. Not comprehensive systematic review; focused landscape understanding + novelty positioning.

---

## 2. PICO Framework (QIPS-Specific)

**Population:**
Optimization algorithms in continuous spaces (real-valued, 10D-100D), particularly:
- Genetic Algorithms (GA)
- Particle Swarm Optimization (PSO)
- Quantum-Inspired Genetic Algorithms (QIGA)
- P-system based optimization approaches

**Intervention:**
Quantum-inspired concepts (superposition, interference, measurement/collapse) applied to P-system (membrane-based) optimization. Novel integration of:
- Quantum rotation gates encoding superposition in P-system particles
- Membrane rules implementing quantum interference
- Measurement operations as particle consolidation

**Comparison:**
- Classical GA baseline (50 individuals, 200 generations, standard crossover/mutation)
- Existing QIGA implementations (if benchmarked on same problems)
- Existing P-system optimization (if any exist)

**Outcomes:**
- Convergence speed (generations to acceptable solution)
- Solution quality (mean ± std deviation of best fitness)
- Performance on CEC2017 F1, F3-F8, F11, F14, F17, F21, F26 (10D)
- Behavioral differences across function categories (unimodal vs. multimodal vs. hybrid)
- Dimensionality scalability (degrades gracefully to 30D?)

---

## 3. Research Questions (RQ)

**RQ1: Novelty — Is quantum-inspired + P-systems genuinely new?**

*Why it matters:* If someone already combined these, we need to know what they did and how our approach differs.

*Operationalization:* Search all 10 papers for prior work combining quantum concepts + membrane systems.

*Success criteria:*
- [ ] Find 0 papers combining quantum + P-systems → **Our novelty claim is strong**
- [ ] Find 1-2 papers → **Understand their approach, differentiate ours**
- [ ] Find 3+ papers → **Novelty claim needs adjustment; focus on our specific innovation**

---

**RQ2: Gap — What causes dimensionality collapse in quantum-inspired algorithms?**

*Why it matters:* This is the problem we're trying to solve. Understanding the root cause informs algorithm design.

*Operationalization:* Extract any discussion of performance degradation at D>30, mechanisms behind diversity loss, and proposed solutions.

*Success criteria:*
- [ ] 3+ papers document collapse → **Well-known problem, our solution is timely**
- [ ] Root cause identified (diversity loss, exploration/exploitation imbalance) → **Can design targeted fix**
- [ ] Proposed solutions exist → **Learn from them; combine approaches in QIPS**

---

**RQ3: Methods — What adaptive strategies exist to maintain diversity?**

*Why it matters:* We'll combine multiple strategies (quantum superposition for exploration, P-system rules for adaptation, GA tournament for exploitation).

*Operationalization:* Extract adaptive mechanisms from papers: parameter tuning, rule updates, population management.

*Success criteria:*
- [ ] GA: tournament selection, adaptive mutation rates
- [ ] PSO: inertia weight adaptation, velocity clamping
- [ ] P-systems: rule rewriting, membrane division
- [ ] Which combinations are novel? Which work well together?

---

**RQ4: Baselines — What's the reference GA performance on CEC2017?**

*Why it matters:* We need concrete numbers to compare QIPS against. Provides reproducibility and comparison target.

*Operationalization:* Extract GA results from papers testing on CEC2017 (mean, std, best, worst).

*Success criteria:*
- [ ] Have mean ± std for F1, F3, F4 (unimodal baseline)
- [ ] Have mean ± std for F5, F6, F8 (multimodal baseline)
- [ ] Can compute "QIPS improvement %" as (GA_mean - QIPS_mean) / GA_mean × 100

---

**RQ5: Scalability — Does quantum-inspired + P-systems scale better to high-D?**

*Why it matters:* If our approach avoids dimensionality collapse, that's a major contribution.

*Operationalization:* Search papers for results at D=30, D=50, D=100. Compare convergence speed/quality.

*Success criteria:*
- [ ] Find high-D results → **Design QIPS to test at multiple D**
- [ ] See clear collapse pattern → **QIPS should show degradation curve, but less severe**

---

## 4. Inclusion/Exclusion Criteria

**Include papers if:**
- ✅ Published in peer-reviewed venue (journal or top conference)
- ✅ Addresses at least one RQ (novelty, gap, methods, baselines, scalability)
- ✅ Contains empirical results (algorithms tested on benchmarks)
- ✅ Available open-access or via UofM library

**Exclude papers if:**
- ❌ Pure theory (no experiments)
- ❌ Position papers or surveys without empirical validation
- ❌ Focuses on hardware implementation (NISQ, quantum circuits) — out of scope for paper 1
- ❌ Requires credentials we don't have (inaccessible)

**Note:** All 10 curated papers are already filtered to be relevant. Apply these criteria if adding papers.

---

## 5. Quality Assessment Rubric (QIPS-Customized)

Rate each paper 0-8 based on:

| Criterion | Strong (2) | Moderate (1) | Weak (0) |
|-----------|-----------|-------------|---------|
| **Algorithm clarity** | Pseudocode, clear state representation, initialization detailed | Algorithm described in prose, some details omitted | Vague "quantum-inspired" claims, no pseudocode |
| **Benchmark rigor** | Multiple CEC2017 functions, multiple dimensions (10D-100D), 30+ runs, statistical significance testing | Single dimension or few functions, 10-20 runs | One toy example, no error bars |
| **Relevance to RQs** | Directly addresses 2+ of our RQs | Addresses 1 RQ clearly | Tangential relevance |
| **Reproducibility** | Code available, parameters (pop, gen, mutation rates) clear | Enough detail to re-implement manually | Missing critical algorithmic details |

**Interpretation:**
- 7-8: High-quality, weight findings heavily
- 5-6: Moderate quality, use for context
- 3-4: Lower quality, note limitations
- 0-2: Weak, cite only for specific factual claims

---

## 6. Evidence Extraction Schema (QIPS-Specific)

**Template to fill for each paper:**

```yaml
### Paper #[N]: [Short Title]

Bibliographic:
  Title: [Full title]
  Authors: [First author et al.]
  Year: [2005 | 2010 | 2019 | 2020 | 2021 | 2022 | 2023]
  Venue: [Journal name, conference, or arXiv]
  DOI: [If available]
  Access: [open-access | library | manual]

Study Design:
  Algorithm: [QIGA | QiPSO | P-system | other]
  Problem domain: [continuous optimization | combinatorial | NP-hard | other]
  Benchmark suite: [CEC2017 | TSP | custom | other]
  Dimensions tested: [10D | 30D | 50D | 100D | other]
  Population size: [typical: 50-100]
  Generations: [typical: 200-300]

Main Contribution:
  Novel idea: [One sentence: what's the key idea?]
  Differs from prior: [How is this new?]
  Quantitative gain: [e.g., "15% faster convergence than GA" or N/A]
  Limitations: [What doesn't work? When does it fail?]

Evidence for RQs:
  RQ1 (novelty):
    - Combines quantum + P-systems? [Yes | No | Partial]
    - Evidence: [Quote or summary]

  RQ2 (collapse):
    - Discusses dimensionality degradation? [Yes | No]
    - Root cause identified? [If yes: what?]
    - Evidence: [Quote or benchmark table reference]

  RQ3 (methods):
    - What adaptive strategies used? [List: inertia weight, tournament, rule-based, etc.]
    - Which seem effective? [Quote or results]

  RQ4 (baselines):
    - GA results on CEC2017? [Yes | No]
    - Numbers: Mean ± Std for F1, F3-F8 [If available]

  RQ5 (scalability):
    - Tests at D>30? [Yes | No]
    - Performance trend: [Improves | degrades | stable] as D increases
    - Evidence: [Table or figure reference]

Key Quotes:
  - On superposition: "[Quote or page #]"
  - On P-system rules: "[Quote or page #]"
  - On dimensionality collapse: "[Quote or page #]"
  - Benchmark results: "[Table/figure reference]"

Quality Score: [0-2-4-6-8]
Quality rationale: [1-2 sentences explaining score]

Connection to QIPS:
  - We'll adopt: [Formula, method, parameter setting]
  - We'll adapt: [Take approach but modify for our use]
  - We'll avoid: [Limitation they hit; we'll handle differently]
```

---

## 7. Synthesis Strategy

**Steps (after reading all papers):**

1. **Fill evidence matrix:** Map each RQ to papers that address it
2. **Assess confidence:** Which findings appear in 3+ papers? (high confidence)
3. **Identify gaps:** Which RQs are weakly answered? (research opportunities)
4. **Note contradictions:** Where do papers disagree? (investigate further)
5. **Draft novelty:** Combine findings into coherent novelty statement
6. **Identify parameters:** Extract algorithm constants for QIPS implementation

---

## 8. Evidence Synthesis Table (QIPS-Specific)

**Fill this after reading all 10 papers:**

```markdown
| RQ | Finding | Papers Supporting | Confidence | Implication for QIPS |
|----|---------|-------------------|------------|----------------------|
| 1 (Novelty) | Quantum-inspired + P-systems NOT previously combined | #1, #4, #6, #8 | High | **NOVEL — novelty claim is strong** |
| 1 (Novelty) | Most prior work: quantum-inspired alone OR P-systems alone | #1, #2, #5, #7, #10 | High | **Gap we're filling** |
| 2 (Collapse) | Dimensionality collapse at D>30 documented | #2, #7, #9 | High | **Problem is real; worth solving** |
| 2 (Collapse) | Root cause: diversity loss in quantum rotation updates | #2, #7 | Medium | **Target: maintain diversity via P-system hierarchy** |
| 3 (Methods) | GA: tournament selection + adaptive mutation | #1, #2, #5 | High | **Adapt for QIPS population management** |
| 3 (Methods) | PSO: inertia weight decay maintains exploration | #1, #7 | Medium | **Apply to P-system rule update frequency** |
| 3 (Methods) | P-system: hierarchical membranes provide natural population structure | #3, #4, #6 | High | **CORE: use for multi-level adaptation** |
| 4 (Baselines) | GA performance on F1-F8 (10D): mean 50-150, σ 20-60 | #2, #7, #9 | High | **Target: beat these by 10-20%** |
| 5 (Scalability) | High-D results rare; few papers test D>50 | #7, #9 | Medium | **Opportunity: QIPS tested at 10D-30D** |
```

---

## 9. Novelty Statement (Iterative)

**Track versions as you read:**

```markdown
### Novelty Statement Evolution

**v1 (after papers #1-3, day 3):**
> "We propose Quantum-Inspired P-Systems (QIPS) for continuous optimization,
> combining quantum superposition concepts with membrane-based population structure."

**v2 (after papers #1-7, day 8):**
> "To our knowledge, QIPS is the first integration of quantum-inspired computing
> (superposition, interference, measurement) into P-system formalism.
> We address the dimensionality collapse problem (documented in papers #2, #7)
> by leveraging hierarchical P-system structure for adaptive exploration."

**v3 (after all papers + synthesis, day 12):**
> "We propose Quantum-Inspired P-Systems (QIPS) for continuous optimization on CEC2017
> benchmark functions. QIPS is novel in three ways:
> (1) First to combine quantum-inspired concepts with P-system formalism (RQ1),
> (2) Addresses dimensionality collapse via adaptive multi-level membrane rules (RQ2),
> (3) Integrates successful adaptive mechanisms from GA (tournament), PSO (inertia decay),
> and P-systems (rule rewriting). Preliminary 10D CEC2017 results show [X]% improvement
> over baseline GA, with maintained diversity in high-dimensional scaling (RQ5)."
```

Each version tagged by day in git. Evolution shows rigorous synthesis process.

---

## 10. Review Schedule (QIPS Timeline)

| Phase | Days | Task | Deliverable | Git Commit |
|-------|------|------|-------------|-----------|
| **Setup** | 1 | Finalize protocol (this doc), organize papers | `REVIEW_PROTOCOL_QIPS.md` | "lit-review: Define PICO, RQs, quality rubric" |
| **Reading** | 2-10 | Read papers #1-10, extract evidence | Per-paper evidence form | "lit-review: Paper #[N] findings" (×10) |
| **Synthesis** | 11-12 | Fill evidence matrix, draft novelty v1-v3 | Synthesis table + novelty statement | "lit-review: Synthesis complete, novelty statement drafted" |
| **Integration** | 13-14 | Map findings to model.py, benchmark config | Algorithm formulas, parameters | "model: Populate QIPS formulas from lit review findings" |

---

## 11. Version Control Workflow (QIPS-Specific)

**Each paper → one commit:**

```bash
# After reading paper #1 (Zhang survey)
git add docs/LITERATURE_REVIEW.md
git commit -m "lit-review: Extract evidence from paper #1 (Zhang et al. 2023 survey)

- RQ1: Survey covers QIGA, QiPSO, P-systems separately — no prior quantum+P-system fusion
- RQ2: Identifies dimensionality collapse as open problem
- RQ3: Catalogs adaptive strategies from GA and PSO
- RQ4: No CEC2017 baseline in this survey paper
- Quality: High (8/8) — comprehensive reference work
- Connection: Sets landscape context for our novelty claim
"
```

**After synthesis:**

```bash
git commit -m "lit-review: Synthesis complete — novelty statement defensible

Evidence synthesis:
- RQ1 (novelty): 0 prior quantum+P-system work (high confidence, papers #1,4,6,8)
- RQ2 (collapse): Root cause = diversity loss (papers #2,7)
- RQ3 (methods): 3-way strategy = tournament (GA) + inertia (PSO) + hierarchies (P-sys)
- RQ4 (baselines): GA mean=50-150, σ=20-60 on F1-F8
- Novelty statement v3: Ready for implementation

Next: Fill model.py with QIPS formulas based on findings
"
```

**Check evolution:**

```bash
git log --oneline docs/LITERATURE_REVIEW.md | head -15
# Shows: setup → paper #1 → paper #2 → ... → synthesis → ready
```

---

## 12. Reuse for Future Projects

**This protocol is customizable:**

### For a new paper/project:
1. Copy `REVIEW_PROTOCOL_TEMPLATE.md` (unchanged reference)
2. Create `REVIEW_PROTOCOL_[PROJECT].md` (this file, customized)
3. Sections 1-6: Customize PICO, RQs, quality rubric
4. Sections 7-12: Same workflow, different domain

### Example: Future project "Quantum Error Correction"
- RQs would be: "What codes exist? What's the error threshold? How do we compare codes?"
- Quality rubric would emphasize: "Theoretical analysis? Experimental validation? Scalability?"
- Evidence matrix would track: "Which codes scale? Which have threshold proven?"
- Reuse structure, adapt content

---

## Start Here

**Day 1 checklist:**
- [ ] Read this protocol (sections 1-6)
- [ ] Skim the 10 papers (note which address which RQ)
- [ ] Commit protocol to git: `git add && git commit -m "lit-review: Protocol ready"`
- [ ] Ready to start reading papers

**Per-paper (Days 2-10):**
- [ ] Read paper thoroughly
- [ ] Fill evidence extraction schema (section 6)
- [ ] Commit findings
- [ ] Move to next paper

**Synthesis (Days 11-12):**
- [ ] Fill evidence matrix (section 8)
- [ ] Draft novelty statement v3 (section 9)
- [ ] Commit synthesis
- [ ] Ready for algorithm implementation

---

**Questions during review?** Refer back to this protocol. The structure keeps you on track.
