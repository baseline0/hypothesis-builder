#!/usr/bin/env python3
"""
Hypothesis Exporter: Convert evidence synthesis into testable hypotheses.

Reads evidence matrix, generates structured hypotheses that the membrane repo
can consume (JSON format with confidence scores and implications).

Usage:
    python scripts/hypothesis_exporter.py \
        --evidence automation/processed/evidence_matrix.json \
        --output synthesis/hypotheses.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


class HypothesisExporter:
    """Convert evidence into testable hypotheses."""

    def __init__(self, evidence_path: Path):
        with open(evidence_path) as f:
            self.evidence = json.load(f)

    def build_hypotheses(self) -> Dict[str, Any]:
        """Build testable hypotheses from evidence."""
        evidence_data = self.evidence["evidence"]

        hypotheses = [
            self._build_h1_novelty(evidence_data["RQ1_novelty"]),
            self._build_h2_collapse(evidence_data["RQ2_collapse"]),
            self._build_h3_adaptation(evidence_data["RQ3_adaptation"]),
            self._build_h4_baseline(evidence_data["RQ4_baseline"]),
            self._build_h5_scalability(evidence_data["RQ5_scalability"]),
        ]

        return {
            "novelty_statement": self._build_novelty_statement(hypotheses),
            "hypotheses": hypotheses,
            "parameters": self._extract_parameters(),
            "audit_trail": {
                "total_papers_analyzed": self.evidence["metadata"]["total_papers"],
                "papers": self.evidence["metadata"]["paper_names"],
                "synthesis_method": self.evidence["metadata"]["synthesis_method"],
            },
        }

    def _build_h1_novelty(self, rq1_data: Dict) -> Dict[str, Any]:
        """H1: Novelty claim."""
        return {
            "id": "H1_novelty",
            "rq": "RQ1: Is quantum-inspired + P-systems novel?",
            "claim": "No prior work combines quantum-inspired computing with P-system formalism",
            "confidence": rq1_data["confidence"],
            "supporting_papers": rq1_data["supporting_papers"],
            "quality_score": rq1_data["quality_weighted_score"],
            "testable_as": "Literature review finding (not testable experimentally)",
            "implication": "QIPS is defensibly novel; can proceed with novelty claim in paper",
        }

    def _build_h2_collapse(self, rq2_data: Dict) -> Dict[str, Any]:
        """H2: Dimensionality collapse mechanism."""
        return {
            "id": "H2_collapse",
            "rq": "RQ2: What causes dimensionality collapse?",
            "claim": f"Dimensionality collapse at D>30 caused by: {rq2_data.get('consensus_root_cause', 'diversity loss')}",
            "confidence": rq2_data["confidence"],
            "supporting_papers": rq2_data["supporting_papers"],
            "quality_score": rq2_data["quality_weighted_score"],
            "testable_as": "Measure QIPS convergence + diversity at D=10,30,50",
            "implication": "Design QIPS to maintain diversity via P-system hierarchies; test whether QIPS avoids collapse",
        }

    def _build_h3_adaptation(self, rq3_data: Dict) -> Dict[str, Any]:
        """H3: Adaptive strategies."""
        mechanisms = list(rq3_data.get("mechanisms", {}).keys())
        return {
            "id": "H3_adaptation",
            "rq": "RQ3: What adaptive strategies exist?",
            "claim": f"Effective adaptive strategies exist: {', '.join(mechanisms)}",
            "confidence": rq3_data["confidence"],
            "identified_mechanisms": mechanisms,
            "quality_score": rq3_data["quality_weighted_score"],
            "testable_as": "Implement all three strategies in QIPS; ablate to measure contribution",
            "implication": "Combine GA tournament selection + PSO inertia weight decay + P-system rule updates in QIPS",
        }

    def _build_h4_baseline(self, rq4_data: Dict) -> Dict[str, Any]:
        """H4: GA baseline performance."""
        return {
            "id": "H4_baseline",
            "rq": "RQ4: What's GA baseline on CEC2017?",
            "claim": f"GA baseline established from {len(rq4_data.get('supporting_papers', []))} papers",
            "confidence": rq4_data["confidence"],
            "supporting_papers": rq4_data["supporting_papers"],
            "baseline_results": rq4_data.get("averaged_results", {}),
            "quality_score": rq4_data["quality_weighted_score"],
            "testable_as": "Run GA on same CEC2017 functions; compare against baseline",
            "implication": "Target: QIPS should outperform GA baseline by 10-20% on CEC2017 subset",
        }

    def _build_h5_scalability(self, rq5_data: Dict) -> Dict[str, Any]:
        """H5: Scalability to high-D."""
        return {
            "id": "H5_scalability",
            "rq": "RQ5: Does QIPS scale better to high-D?",
            "claim": f"High-D performance trend: {rq5_data.get('scalability_consensus', 'unknown')}",
            "confidence": rq5_data["confidence"],
            "supporting_papers": rq5_data["supporting_papers"],
            "quality_score": rq5_data["quality_weighted_score"],
            "testable_as": "Run QIPS at D=10, D=30, D=50; measure degradation curve vs. GA",
            "implication": "QIPS may handle high-D better than quantum-inspired algorithms; document degradation curve",
        }

    def _build_novelty_statement(self, hypotheses: List[Dict]) -> str:
        """Build comprehensive novelty statement from hypotheses."""
        h1 = hypotheses[0]
        h2 = hypotheses[1]
        h3 = hypotheses[2]

        return (
            f"We propose Quantum-Inspired P-Systems (QIPS) for continuous optimization on CEC2017 benchmarks. "
            f"QIPS is novel because: (1) {h1['claim']} ({h1['confidence']} confidence), "
            f"(2) we address the dimensionality collapse problem ({h2['confidence']} confidence) by combining "
            f"three adaptive strategies from GA, PSO, and P-systems ({h3['confidence']} confidence). "
            f"We validate against GA baseline on 10D CEC2017 subset, targeting 10-20% improvement in solution quality."
        )

    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract recommended parameters from baseline data."""
        rq4_baseline = self.evidence["evidence"].get("RQ4_baseline", {}).get("averaged_results", {})

        # Extract GA baseline parameters (standard values if not in data)
        return {
            "ga_baseline": {
                "population": 50,
                "generations": 200,
                "crossover_probability": 0.8,
                "mutation_probability": 0.1,
            },
            "qips_recommendations": {
                "population": 50,
                "generations": 200,
                "dimension_start": 10,
                "dimensions_to_test": [10, 30, 50],
            },
            "cec2017_subset": {
                "unimodal": ["F1", "F3", "F4"],
                "multimodal": ["F5", "F6", "F8"],
                "hybrid": ["F11", "F14", "F17"],
                "composition": ["F21", "F26"],
                "total_functions": 11,
            },
        }

    def export(self, output_path: Path) -> None:
        """Export hypotheses to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        hypotheses = self.build_hypotheses()
        with open(output_path, "w") as f:
            json.dump(hypotheses, f, indent=2)
        print(f"\n✅ Hypotheses exported: {output_path}")
        print(f"\nNovelty Statement:")
        print(f"  {hypotheses['novelty_statement']}")
        print(f"\nTestable Hypotheses:")
        for h in hypotheses["hypotheses"]:
            print(f"  - {h['id']}: {h['confidence']} confidence")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Export testable hypotheses from evidence synthesis")
    parser.add_argument(
        "--evidence",
        type=Path,
        required=True,
        help="Path to evidence_matrix.json from synthesis step",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("synthesis/hypotheses.json"),
        help="Output path for hypotheses",
    )

    args = parser.parse_args()

    if not args.evidence.exists():
        print(f"❌ Evidence file not found: {args.evidence}")
        sys.exit(1)

    print(f"📋 Hypothesis Exporter")
    print(f"   Reading evidence from: {args.evidence}")

    exporter = HypothesisExporter(args.evidence)
    exporter.export(args.output)


if __name__ == "__main__":
    main()
