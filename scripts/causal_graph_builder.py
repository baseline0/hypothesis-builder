#!/usr/bin/env python3
"""
Causal Graph Builder: Synthesize causal claims from all papers into a graph.

Reads extracted causal claims from papers, merges them into a consensus graph,
and identifies supporting/contradicting edges for human validation.

Output files:
  - automation/processed/causal_graph.json (canonical form)
  - automation/processed/causal_graph.mmd (Mermaid diagram for visualization)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class CausalGraphBuilder:
    """Build and manage causal evidence graph."""

    def __init__(self):
        self.papers: Dict[str, Dict] = {}
        self.edges: Dict[str, Dict] = {}  # edge_id → edge data
        self.edge_counter = 0

    def load_evidence(self, extraction_files: List[Path]) -> None:
        """Load causal claims from all papers."""
        for filepath in extraction_files:
            with open(filepath) as f:
                evidence = json.load(f)
            paper_id = evidence["paper_name"]
            self.papers[paper_id] = evidence
            print(f"✅ Loaded: {paper_id} ({len(evidence.get('causal_claims', []))} claims)")

    def merge_edges(self) -> None:
        """Merge causal claims from all papers into graph edges."""
        # Group claims by (cause, effect, mechanism)
        edge_groups: Dict[tuple, List[dict]] = defaultdict(list)

        for paper_id, evidence in self.papers.items():
            for claim in evidence.get("causal_claims", []):
                key = (claim["cause"], claim["effect"], claim.get("mechanism", ""))
                edge_groups[key].append((paper_id, claim))

        # For each unique (cause, effect) pair, create an edge
        for (cause, effect, mechanism), supporting_claims in edge_groups.items():
            if not cause or not effect:
                continue

            edge_id = f"edge_{self.edge_counter:04d}"
            self.edge_counter += 1

            # Aggregate evidence
            directions = [c["direction"] for _, c in supporting_claims]
            confidences = [c["causal_confidence"] for _, c in supporting_claims]
            evidence_designs = [c["evidence_type"] for _, c in supporting_claims]

            self.edges[edge_id] = {
                "edge_id": edge_id,
                "cause": cause,
                "effect": effect,
                "mechanism": mechanism,
                "direction": directions[0] if directions else "unknown",
                "supporting_papers": [p for p, _ in supporting_claims],
                "supporting_claims": len(supporting_claims),
                "evidence_designs": list(set(evidence_designs)),
                "causal_confidence_votes": dict(zip(
                    confidences,
                    [confidences.count(c) for c in confidences]
                )),
                "consensus_confidence": self._consensus_confidence(confidences),
                "status": "proposed",
                "review_status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "rationale": None,
            }

    def _consensus_confidence(self, confidences: List[str]) -> str:
        """Determine consensus confidence from votes."""
        if not confidences:
            return "low"
        high = confidences.count("high")
        medium = confidences.count("medium")
        low = confidences.count("low")

        if high >= len(confidences) * 0.7:
            return "high"
        elif medium >= len(confidences) * 0.5:
            return "medium"
        else:
            return "low"

    def export_graph(self, output_path: Path) -> None:
        """Export graph to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        graph = {
            "graph_version": "1.0.0",
            "generated_at": "2026-09-18",
            "total_papers": len(self.papers),
            "total_edges": len(self.edges),
            "edges": list(self.edges.values()),
            "status": "proposed - awaiting human validation",
        }

        with open(output_path, "w") as f:
            json.dump(graph, f, indent=2)

        print(f"\n✅ Causal graph exported: {output_path}")
        print(f"   Total edges: {len(self.edges)}")
        print(f"   Proposed → Pending review")

    def export_mermaid(self, output_path: Path) -> None:
        """Export graph as Mermaid diagram for visualization."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["graph LR"]

        for edge in self.edges.values():
            if edge["status"] != "accepted":
                continue  # Only show accepted edges in diagram

            source = edge["cause"].replace(" ", "_").replace("-", "_")
            target = edge["effect"].replace(" ", "_").replace("-", "_")
            mechanism = edge.get("mechanism", "")
            confidence = edge["consensus_confidence"]

            # Style by confidence
            style_map = {
                "high": "stroke:#2ecc71",
                "medium": "stroke:#f39c12",
                "low": "stroke:#e74c3c",
            }

            label = f"{mechanism} ({confidence})" if mechanism else f"({confidence})"
            lines.append(f"{source} -->|{label}| {target}")

        mermaid = "\n".join(lines)
        with open(output_path, "w") as f:
            f.write(mermaid)

        print(f"   Mermaid diagram: {output_path}")


def main():
    """Main entry point."""
    import argparse
    from glob import glob

    parser = argparse.ArgumentParser(description="Build causal graph from evidence")
    parser.add_argument(
        "--extractions",
        type=str,
        required=True,
        help="Pattern for extraction JSON files (e.g., automation/extracted_evidence/*.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("automation/processed/causal_graph.json"),
        help="Output path for causal graph",
    )
    parser.add_argument(
        "--mermaid",
        type=Path,
        default=Path("automation/processed/causal_graph.mmd"),
        help="Output path for Mermaid diagram",
    )

    args = parser.parse_args()

    # Expand glob pattern
    extraction_files = [Path(f) for f in glob(args.extractions)]

    if not extraction_files:
        print(f"❌ No extraction files found matching: {args.extractions}")
        sys.exit(1)

    print(f"📊 Causal Graph Builder")
    print(f"   Loading {len(extraction_files)} extraction files...")

    builder = CausalGraphBuilder()
    builder.load_evidence(extraction_files)
    builder.merge_edges()
    builder.export_graph(args.output)
    builder.export_mermaid(args.mermaid)


if __name__ == "__main__":
    main()
