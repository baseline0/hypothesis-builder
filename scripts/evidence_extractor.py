#!/usr/bin/env python3
"""
Evidence Extractor: Claude reads PDFs and fills evidence template.

Reads papers (PDF or text), extracts structured evidence for each RQ,
and outputs JSON files ready for synthesis.

Usage:
    python scripts/evidence_extractor.py --pdf path/to/paper.pdf --output automation/

    (In practice, Claude reads PDFs in this session and exports results)
"""

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class PaperEvidence:
    """Structured evidence extracted from a single paper."""

    paper_name: str
    title: str
    authors: str
    year: int
    doi: Optional[str]
    access_status: str

    # Study design
    algorithm: str
    problem_domain: str
    benchmark_suite: str
    dimensions_tested: str
    population_size: Optional[int]
    generations: Optional[int]
    num_runs: Optional[int]

    # Main contribution
    novel_idea: str
    differs_from_prior: str
    quantitative_gain: str
    limitations: str

    # Evidence for RQs (QIPS-specific, adapt as needed)
    rq1_combines_quantum_psys: bool
    rq1_evidence: str
    rq1_quote: str

    rq2_discusses_collapse: bool
    rq2_root_cause: str
    rq2_dimension_performance: dict  # {D: performance}
    rq2_quote: str

    rq3_adaptive_mechanisms: list  # ["tournament", "inertia decay", ...]
    rq3_effectiveness: str
    rq3_quote: str

    rq4_cec2017_baseline: bool
    rq4_ga_results: dict  # {"F1": {"mean": 50, "std": 20}, ...}
    rq4_quote: str

    rq5_high_d_tested: bool
    rq5_scalability_trend: str  # "improves" | "degrades" | "stable"
    rq5_d_performance: dict  # {D: performance}
    rq5_quote: str

    # Quality assessment
    quality_algorithm_clarity: int  # 0-2
    quality_benchmark_rigor: int  # 0-2
    quality_relevance_rqs: int  # 0-2
    quality_reproducibility: int  # 0-2
    quality_total: int  # 0-8 (sum of above)
    quality_rationale: str

    # Causal claims (NEW)
    causal_claims: list  # See causal_claim_template() for structure

    # Connection to QIPS
    will_adopt: list  # Formulas/methods we'll take
    will_adapt: list  # Ideas we'll modify
    will_avoid: list  # Limitations we'll work around

    # Summary
    summary: str  # 1-2 sentences

    def to_dict(self):
        """Convert to JSON-serializable dict."""
        return asdict(self)


def create_causal_claim_template() -> dict:
    """Template for a single causal claim extracted from a paper."""
    return {
        "claim_id": "claim_0001",
        "cause": "",  # Variable name
        "effect": "",  # Variable name
        "mechanism": "",  # How cause leads to effect
        "direction": "",  # "increases" | "decreases" | "enables" | "prevents"
        "conditions": {},  # Under what conditions (e.g., {"dimension": ">30"})
        "evidence_type": "",  # observational_benchmark | controlled_experiment | etc
        "source": {
            "paper_id": "",
            "section": "",
            "page": None,
            "quote": "",
        },
        "causal_status": "reported",  # reported | inferred | proposed | disputed
        "extraction_method": "claude_with_human_verification",
        "review_status": "pending",  # pending | accepted | rejected | requires_experiment
        "extraction_confidence": "medium",  # high | medium | low
        "evidence_confidence": "medium",
        "causal_confidence": "medium",  # Separate from evidence confidence
        "mechanism_confidence": "medium",
        "alternative_explanations": [],  # Other possible causes
    }


def create_template_evidence() -> dict:
    """Create an empty evidence template for filling in."""
    return {
        "paper_name": "",
        "title": "",
        "authors": "",
        "year": None,
        "doi": None,
        "access_status": "open-access|library|manual",
        "algorithm": "",
        "problem_domain": "",
        "benchmark_suite": "",
        "dimensions_tested": "",
        "population_size": None,
        "generations": None,
        "num_runs": None,
        "novel_idea": "",
        "differs_from_prior": "",
        "quantitative_gain": "",
        "limitations": "",
        "rq1_combines_quantum_psys": False,
        "rq1_evidence": "",
        "rq1_quote": "",
        "rq2_discusses_collapse": False,
        "rq2_root_cause": "",
        "rq2_dimension_performance": {},
        "rq2_quote": "",
        "rq3_adaptive_mechanisms": [],
        "rq3_effectiveness": "",
        "rq3_quote": "",
        "rq4_cec2017_baseline": False,
        "rq4_ga_results": {},
        "rq4_quote": "",
        "rq5_high_d_tested": False,
        "rq5_scalability_trend": "",
        "rq5_d_performance": {},
        "rq5_quote": "",
        "causal_claims": [],  # List of causal_claim_template() objects filled by Claude
        "quality_algorithm_clarity": 0,
        "quality_benchmark_rigor": 0,
        "quality_relevance_rqs": 0,
        "quality_reproducibility": 0,
        "quality_total": 0,
        "quality_rationale": "",
        "will_adopt": [],
        "will_adapt": [],
        "will_avoid": [],
        "summary": "",
    }


def export_evidence(evidence: dict, output_path: Path) -> None:
    """Export evidence to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(evidence, f, indent=2)
    print(f"✅ Exported: {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract evidence from paper (Claude reads PDF in session)"
    )
    parser.add_argument("--template", action="store_true", help="Show empty evidence template")
    parser.add_argument("--causal-template", action="store_true", help="Show causal claim template")
    parser.add_argument("--output", type=Path, default=Path("automation/extracted_evidence"))

    args = parser.parse_args()

    if args.template:
        print(json.dumps(create_template_evidence(), indent=2))
        return

    if args.causal_template:
        print(json.dumps(create_causal_claim_template(), indent=2))
        return

    print("📐 Evidence Extractor")
    print("In this session, Claude reads PDFs directly and fills the template.")
    print(f"Export to: {args.output}/")


if __name__ == "__main__":
    main()
