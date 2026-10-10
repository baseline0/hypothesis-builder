"""Tests for contradiction detection over causal-graph edges.

Happy paths: opposite directions on the same claim are flagged in both
directions, and accepted, reviewed edges are left alone.
Unhappy paths: edges without an id fail loudly, and an edge with no direction
is treated as its own direction (documented, so a change is deliberate).
"""

import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pytest  # noqa: E402
from detect_contradictions import (  # noqa: E402
    apply_contradiction_status,
    compute_claim_key,
    detect_contradictions,
)


def edge(edge_id: str, direction: str | None = "positive", **extra) -> dict:
    base = {
        "edge_id": edge_id,
        "cause": "rain",
        "effect": "wet_ground",
        "conditions": {"season": "winter"},
        "time_horizon": "short",
    }
    if direction is not None:
        base["direction"] = direction
    base.update(extra)
    return base


# --- happy paths -------------------------------------------------------------------


def test_same_claim_with_opposite_directions_is_flagged_both_ways():
    edges = [edge("e1", "positive"), edge("e2", "negative")]

    result = detect_contradictions(edges)

    assert result == {"e1": ["e2"], "e2": ["e1"]}


def test_same_claim_with_same_direction_is_not_flagged():
    edges = [edge("e1", "positive"), edge("e2", "positive")]

    assert detect_contradictions(edges) == {}


def test_edges_with_different_claims_are_not_compared():
    edges = [edge("e1", "positive"), edge("e2", "negative", effect="dry_ground")]

    assert detect_contradictions(edges) == {}


def test_three_way_disagreement_lists_every_other_edge():
    edges = [edge("e1", "positive"), edge("e2", "negative"), edge("e3", "positive")]

    result = detect_contradictions(edges)

    assert sorted(result["e1"]) == ["e2", "e3"]
    assert result["e2"] == ["e1", "e3"]


def test_claim_key_ignores_condition_key_order():
    a = edge("e1", conditions={"a": 1, "b": 2})
    b = edge("e2", conditions={"b": 2, "a": 1})

    assert compute_claim_key(a) == compute_claim_key(b)


def test_apply_marks_proposed_edge_as_disputed_with_rationale():
    graph = {"edges": [edge("e1", status="proposed")]}

    apply_contradiction_status(graph, {"e1": ["e2"]})

    marked = graph["edges"][0]
    assert marked["contradiction_status"] == "contradictory"
    assert marked["status"] == "disputed"
    assert marked["review_rationale"] == "Contradicted by: e2"


def test_apply_leaves_accepted_and_reviewed_edges_alone():
    graph = {"edges": [edge("e1", status="accepted", reviewer="mark")]}

    apply_contradiction_status(graph, {"e1": ["e2"]})

    assert graph["edges"][0]["status"] == "accepted"
    assert "contradiction_status" not in graph["edges"][0]


# --- unhappy paths -----------------------------------------------------------------


def test_edge_without_id_in_a_contradiction_group_fails_loudly():
    # Same claim as a contradiction pair, but no edge_id: the group must not
    # be reported with a silently missing identifier.
    no_id = edge("placeholder", "positive")
    del no_id["edge_id"]

    with pytest.raises(KeyError):
        detect_contradictions([no_id, edge("e2", "negative")])


def test_missing_direction_is_its_own_direction_and_is_flagged():
    # Documented behaviour: an edge with no direction is treated as "unknown".
    # Against a "positive" edge on the same claim it is flagged, which is a
    # deliberate choice: an unstated direction should not pass silently.
    edges = [edge("e1", "positive"), edge("e2", direction=None)]

    assert detect_contradictions(edges) == {"e1": ["e2"], "e2": ["e1"]}


def test_empty_graph_has_no_contradictions():
    assert detect_contradictions([]) == {}
    graph = {"edges": []}
    apply_contradiction_status(graph, {})
    assert graph == {"edges": []}
