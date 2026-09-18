# Literature Review Extraction Template (Per-Paper)

**Copy this template for EACH paper you read.**

**How to use:**
1. Read paper
2. Copy this template
3. Fill in all sections (even if "N/A")
4. Commit to git with paper-specific message
5. Repeat for next paper

---

## Template: [PAPER NUMBER] — [SHORT TITLE]

```markdown
# Paper #[N]: [Title]

## Bibliographic

- **Title:** [Full title as published]
- **Authors:** [First author et al.]
- **Year:** [YYYY]
- **Venue:** [Journal/Conference/ArXiv]
- **DOI:** [If available, else "N/A"]
- **Access:** [open-access | library | manual]
- **Read date:** [YYYY-MM-DD]

---

## Study Design

- **Algorithm name:** [QIGA | QiPSO | P-system | hybrid | other]
- **Problem domain:** [continuous optimization | combinatorial | traveling salesman | NP-hard | other]
- **Benchmark suite:** [CEC2017 | CEC2015 | CEC2005 | custom | none]
- **Dimensions tested:** [10D | 30D | 50D | 100D | mixed | none]
- **Population size:** [if applicable, e.g., 50 individuals]
- **Generations/iterations:** [if applicable, e.g., 200]
- **Number of runs:** [e.g., 30 independent runs, or "1 run" / "not specified"]

---

## Main Contribution (1-2 sentences)

**What's the key novel idea in this paper?**

Example: "Proposes QiPSO, which encodes particles' positions as quantum superposition states and updates them via quantum rotation gates, showing 20% faster convergence on Sphere function than classical PSO."

[YOUR ANSWER HERE]

---

## How Does It Differ from Prior Work?

**What makes this different from what came before?**

Example: "Prior quantum-inspired GA used probability amplitudes; this work uses quantum phase angles for more fine-grained exploration."

[YOUR ANSWER HERE]

---

## Quantitative Results (if applicable)

**What are the concrete numbers reported?**

| Benchmark | Algorithm | Mean | Std Dev | Best | Worst |
|-----------|-----------|------|---------|------|-------|
| CEC2017 F1 (10D) | [Algo name] | [#] | [#] | [#] | [#] |
| CEC2017 F3 (10D) | [Algo name] | [#] | [#] | [#] | [#] |
| [Other] | [Algo name] | [#] | [#] | [#] | [#] |

Or if no benchmark results: "Not applicable — theoretical analysis only" or "Single toy example used"

[YOUR DATA HERE]

---

## Limitations Acknowledged by Authors

**What problems do the authors admit their approach has?**

Example: "Approach requires many function evaluations; computationally expensive for high-dimensional (D>50) problems. Convergence proof only for unimodal functions."

- Limitation 1: [...]
- Limitation 2: [...]
- Limitation 3: [...]

[YOUR ANSWER HERE]

---

## Evidence for Research Questions

### RQ1: Is quantum-inspired + P-systems genuinely novel?

- **Does this paper combine quantum-inspired with P-systems?** [Yes | No | Partial]
- **If yes, how?** [Quote or summary]
- **If no, what does it combine?** [e.g., "quantum-inspired GA + Sphere benchmark"]
- **Relevant quote:**
  > "[Paste quote or page reference]"

---

### RQ2: What causes dimensionality collapse in quantum-inspired algorithms?

- **Does the paper discuss performance degradation at D>30?** [Yes | No]
- **If yes, what's the root cause?** [e.g., "quantum rotation gates don't scale; particle diversity collapses"]
- **Specific finding:**
  - [D=10]: [Performance]
  - [D=30]: [Performance]
  - [D=50+]: [Performance or "not tested"]
- **Relevant quote:**
  > "[Paste quote explaining the collapse mechanism]"

---

### RQ3: What adaptive strategies exist to maintain diversity?

- **List all adaptive mechanisms used:**
  1. [Mechanism]: [Description] [GA | PSO | P-system | other]
  2. [Mechanism]: [Description] [GA | PSO | P-system | other]
  3. [...]

- **Which seem most effective?** [Opinion based on results / N/A]
- **Relevant quote:**
  > "[Paste quote about adaptive strategy]"

---

### RQ4: What's the reference GA performance on CEC2017?

- **Includes GA baseline on CEC2017?** [Yes | No]
- **If yes, provide table or summary:**
  - GA on CEC2017 F1 (10D): mean [#], σ [#]
  - GA on CEC2017 F3 (10D): mean [#], σ [#]
  - [...]
- **Relevant table reference:**
  - "[Table #, page #]"

---

### RQ5: Does quantum-inspired + P-systems scale better to high-D?

- **Tests at dimensions D>30?** [Yes | No]
- **If yes, what's the trend?** [Improves | Degrades | Stable] as D increases
- **Specific numbers:**
  - D=10: [performance]
  - D=30: [performance]
  - D=50+: [performance]
- **Relevant quote:**
  > "[Paste quote about scalability behavior]"

---

## Key Quotes (Verbatim from Paper)

**On quantum superposition / quantum concepts:**

> "[Quote with page #]"

**On P-system formalism (if mentioned):**

> "[Quote with page #]"

**On dimensionality collapse or diversity loss:**

> "[Quote with page #]"

**On adaptive mechanisms:**

> "[Quote with page #]"

**On benchmark performance:**

> "[Quote with page #]"

---

## Quality Assessment

**Rate this paper on the rubric from REVIEW_PROTOCOL_QIPS.md:**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Algorithm clarity | [0-2] | [Is pseudocode clear? Parameters specified?] |
| Benchmark rigor | [0-2] | [Multiple functions/dimensions? 30+ runs? Error bars?] |
| Relevance to RQs | [0-2] | [How many RQs does it address?] |
| Reproducibility | [0-2] | [Can someone re-implement this?] |
| **TOTAL** | **[0-8]** | **[Sum of above]** |

**Rationale for scores:**

- Algorithm clarity: [Why this score?]
- Benchmark rigor: [Why this score?]
- Relevance: [Why this score?]
- Reproducibility: [Why this score?]

---

## Connection to QIPS Algorithm

### What We'll Adopt from This Paper

**Formulas, methods, or parameter choices we'll take directly:**

- [Quantum rotation gate formula if mentioned]
- [Adaptive mechanism: inertia weight decay / tournament selection / rule update frequency]
- [Parameter: population size, mutation rate, etc.]
- [...]

### What We'll Adapt (Take Idea, Modify for Our Use)

**Approaches we like but need to customize:**

- [Paper uses inertia decay for PSO; we'll apply similar decay to P-system rule update frequency]
- [Paper uses hierarchical algorithm; we'll use hierarchical membranes]
- [...]

### What We'll Avoid (Limitation We Can Do Better)

**Problems this paper hits; we'll design around them:**

- Paper hits dimensionality collapse at D>50; we'll test whether QIPS handles it better
- Paper lacks theoretical convergence proof; we'll document QIPS empirically
- [...]

---

## Summary (1 paragraph)

**Concise summary for future reference:**

[Write 3-5 sentences capturing: novelty, methods, results, limitations, relevance to QIPS]

---

## Next Steps (Editor Notes)

**If you want to remember specific follow-ups:**

- [ ] Cite this paper in Methods section (quantum rotation gates)
- [ ] Compare benchmark results to Table #, Page #
- [ ] Investigate adaptive mechanism further (seems promising)
- [ ] Check if authors have code available (reproducibility)

---

**END TEMPLATE**

---

## Instructions for Git Commit

After filling this template:

```bash
# Save as: docs/LITERATURE_REVIEW_PAPER_#.md
# Then add and commit:
git add docs/LITERATURE_REVIEW.md docs/LITERATURE_REVIEW_PAPER_#.md
git commit -m "lit-review: Extract evidence from paper #N (Author Year)

- RQ1 finding: [1 sentence]
- RQ2 finding: [1 sentence]
- RQ3 finding: [1 sentence]
- RQ4 finding: [1 sentence]
- Quality score: [X/8]
- Connection: [1 sentence on what we'll adopt/avoid]
"
```

Each commit documents one paper's evidence, making the review traceable in git history.
