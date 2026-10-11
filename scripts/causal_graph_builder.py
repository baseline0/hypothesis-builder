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
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Build causal graph from evidence", add_completion=False, pretty_exceptions_enable=False)

DEFAULT_OUTPUT = Path("automation/processed/causal_graph.json")
DEFAULT_MERMAID = Path("automation/processed/causal_graph.mmd")


class CausalGraphBuilder:
    """Build and manage causal evidence graph."""

    def __init__(self):
        self.papers: dict[str, dict] = {}
        self.edges: dict[str, dict] = {}  # edge_id → edge data
        self.edge_counter = 0

    def load_evidence(self, extraction_files: list[Path]) -> None:
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
        edge_groups: dict[tuple, list[dict]] = defaultdict(list)

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

            # Determine mechanism status (explicit uncertainty handling)
            mechanism_status = "unknown"
            if mechanism and len(mechanism.strip()) > 0:
                # If mechanism string is present, mark as 'hypothesized'
                # Only change to 'known' after human validation
                mechanism_status = "hypothesized"

            self.edges[edge_id] = {
                "edge_id": edge_id,
                "cause": cause,
                "effect": effect,
                "mechanism": mechanism,
                "mechanism_status": mechanism_status,  # known | hypothesized | unknown
                "direction": directions[0] if directions else "unknown",
                "supporting_papers": [p for p, _ in supporting_claims],
                "supporting_claims": len(supporting_claims),
                "evidence_designs": list(set(evidence_designs)),
                "causal_confidence_votes": dict(zip(confidences, [confidences.count(c) for c in confidences])),
                "consensus_confidence": self._consensus_confidence(confidences),
                "status": "proposed",
                "review_status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "source": None,
                "rationale": None,
            }

    def _consensus_confidence(self, confidences: list[str]) -> str:
        """Determine consensus confidence from votes."""
        if not confidences:
            return "low"
        high = confidences.count("high")
        medium = confidences.count("medium")

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
        print("   Proposed → Pending review")

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

            label = f"{mechanism} ({confidence})" if mechanism else f"({confidence})"
            lines.append(f"{source} -->|{label}| {target}")

        mermaid = "\n".join(lines)
        with open(output_path, "w") as f:
            f.write(mermaid)

        print(f"   Mermaid diagram: {output_path}")


class NoExtractionsError(ValueError):
    """The extraction pattern matched no files."""


def collect_extraction_files(pattern: str) -> list[Path]:
    """Expand a glob pattern into extraction files. Raises NoExtractionsError when nothing matches."""
    files = [Path(f) for f in glob(pattern)]
    if not files:
        raise NoExtractionsError(pattern)
    return files


@app.command()
def main(
    extractions: Annotated[
        str,
        typer.Option(
            "--extractions",
            help="Pattern for extraction JSON files (e.g., automation/extracted_evidence/*.json)",
        ),
    ],
    output: Annotated[Path, typer.Option("--output", help="Output path for causal graph")] = DEFAULT_OUTPUT,
    mermaid: Annotated[Path, typer.Option("--mermaid", help="Output path for Mermaid diagram")] = DEFAULT_MERMAID,
) -> None:
    """Build a causal graph from extracted evidence."""
    try:
        extraction_files = collect_extraction_files(extractions)
    except NoExtractionsError as exc:
        typer.echo(f"❌ No extraction files found matching: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo("📊 Causal Graph Builder")
    typer.echo(f"   Loading {len(extraction_files)} extraction files...")

    builder = CausalGraphBuilder()
    builder.load_evidence(extraction_files)
    builder.merge_edges()
    builder.export_graph(output)
    builder.export_mermaid(mermaid)


if __name__ == "__main__":
    app()
