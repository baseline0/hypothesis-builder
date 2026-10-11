#!/usr/bin/env python3
"""
Detect Contradictions: Identify conflicting causal claims in graph.

Detects when the same estimand has opposing direction claims.
Distinguishes contradictions from independent outcomes.

Contradiction = same cause + same effect + opposite direction
Independent = same cause + different effects

Disputed edges (from validation) are excluded from ordinary specs.
"""

import json
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Detect contradictory causal claims in graph", add_completion=False)

DEFAULT_OUTPUT = Path("automation/processed/causal_graph_contradictions_marked.json")


def compute_claim_key(edge: dict) -> tuple:
    """
    Compute normalized claim key for contradiction detection.

    Key = (cause, effect, conditions, time_horizon)
    Edges with same key but opposite direction = contradictory.
    """
    return (
        edge.get("cause", ""),
        edge.get("effect", ""),
        json.dumps(edge.get("conditions", {}), sort_keys=True),
        edge.get("time_horizon", "default"),
    )


def detect_contradictions(edges: list[dict]) -> dict[str, list[str]]:
    """
    Detect contradictory edges and return mapping.

    Returns: {edge_id: [contradicting_edge_ids]}
    """
    # Group edges by claim key
    by_key: dict[tuple, list[dict]] = {}
    for edge in edges:
        key = compute_claim_key(edge)
        if key not in by_key:
            by_key[key] = []
        by_key[key].append(edge)

    contradictions: dict[str, list[str]] = {}

    # Find contradictions: same key, opposite direction
    for key, group in by_key.items():
        if len(group) < 2:
            continue

        # Group by direction within this claim key
        by_direction: dict[str, list[dict]] = {}
        for edge in group:
            direction = edge.get("direction", "unknown")
            if direction not in by_direction:
                by_direction[direction] = []
            by_direction[direction].append(edge)

        # If we have multiple directions for same estimand, mark as contradictory
        if len(by_direction) > 1:
            all_edge_ids = [e["edge_id"] for e in group]
            for edge_id in all_edge_ids:
                contradictions[edge_id] = [e["edge_id"] for e in group if e["edge_id"] != edge_id]

    return contradictions


def apply_contradiction_status(graph: dict, contradictions: dict[str, list[str]]) -> None:
    """
    Mark edges as disputed if they have contradictions.
    Only mark if not already reviewed (status != "accepted").
    """
    for edge in graph.get("edges", []):
        edge_id = edge.get("edge_id")

        # Skip if already reviewed (human made the decision)
        if edge.get("status") == "accepted" and edge.get("reviewer"):
            continue

        # Mark as disputed if contradictory
        if edge_id in contradictions:
            edge["contradiction_status"] = "contradictory"
            edge["contradicts_edge_ids"] = contradictions[edge_id]
            if edge.get("status") == "proposed":
                edge["status"] = "disputed"
                edge["review_rationale"] = f"Contradicted by: {', '.join(contradictions[edge_id])}"


def mark_contradictions(graph: dict) -> dict[str, list[str]]:
    """
    Detect contradictions among the graph's edges and flag them in place.

    Returns the contradiction map ({edge_id: [contradicting_edge_ids]}). An empty map
    means nothing was flagged and the graph is unchanged.
    """
    contradictions = detect_contradictions(graph.get("edges", []))
    if contradictions:
        apply_contradiction_status(graph, contradictions)
    return contradictions


def format_contradiction_report(contradictions: dict[str, list[str]]) -> list[str]:
    """Human-readable report lines for a contradiction map."""
    if not contradictions:
        return ["No contradictions detected."]
    lines = [f"Found {len(contradictions)} contradictory edge(s):"]
    lines.extend(f"  {edge_id} contradicts {contradicts}" for edge_id, contradicts in contradictions.items())
    return lines


@app.command()
def main(
    graph: Annotated[Path, typer.Option("--graph", help="Path to causal_graph.json")],
    output: Annotated[Path, typer.Option("--output", help="Output path with contradiction flags")] = DEFAULT_OUTPUT,
) -> None:
    """Flag contradictory causal claims in a graph and write the marked graph."""
    with open(graph) as f:
        data = json.load(f)

    contradictions = mark_contradictions(data)
    for line in format_contradiction_report(contradictions):
        typer.echo(line)

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(data, f, indent=2)

    typer.echo(f"Graph with contradiction flags: {output}")


if __name__ == "__main__":
    app()
