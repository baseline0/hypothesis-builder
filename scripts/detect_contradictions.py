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
from typing import Dict, List, Tuple, Set


def compute_claim_key(edge: Dict) -> Tuple:
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


def detect_contradictions(edges: List[Dict]) -> Dict[str, List[str]]:
    """
    Detect contradictory edges and return mapping.

    Returns: {edge_id: [contradicting_edge_ids]}
    """
    # Group edges by claim key
    by_key: Dict[Tuple, List[Dict]] = {}
    for edge in edges:
        key = compute_claim_key(edge)
        if key not in by_key:
            by_key[key] = []
        by_key[key].append(edge)

    contradictions: Dict[str, List[str]] = {}

    # Find contradictions: same key, opposite direction
    for key, group in by_key.items():
        if len(group) < 2:
            continue

        # Group by direction within this claim key
        by_direction: Dict[str, List[Dict]] = {}
        for edge in group:
            direction = edge.get("direction", "unknown")
            if direction not in by_direction:
                by_direction[direction] = []
            by_direction[direction].append(edge)

        # If we have multiple directions for same estimand, mark as contradictory
        if len(by_direction) > 1:
            all_edge_ids = [e["edge_id"] for e in group]
            for edge_id in all_edge_ids:
                contradictions[edge_id] = [
                    e["edge_id"] for e in group if e["edge_id"] != edge_id
                ]

    return contradictions


def apply_contradiction_status(graph: Dict, contradictions: Dict[str, List[str]]) -> None:
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
                edge["review_rationale"] = (
                    f"Contradicted by: {', '.join(contradictions[edge_id])}"
                )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect contradictory causal claims in graph"
    )
    parser.add_argument(
        "--graph",
        type=Path,
        required=True,
        help="Path to causal_graph.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("automation/processed/causal_graph_contradictions_marked.json"),
        help="Output path with contradiction flags",
    )

    args = parser.parse_args()

    with open(args.graph) as f:
        graph = json.load(f)

    edges = graph.get("edges", [])
    contradictions = detect_contradictions(edges)

    if contradictions:
        print(f"Found {len(contradictions)} contradictory edge(s):")
        for edge_id, contradicts in contradictions.items():
            print(f"  {edge_id} contradicts {contradicts}")

        apply_contradiction_status(graph, contradictions)
    else:
        print("No contradictions detected.")

    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(graph, f, indent=2)

    print(f"Graph with contradiction flags: {output_path}")


if __name__ == "__main__":
    main()
