"""Tests for the contradiction-detection CLI: the pure mark/report functions and the Typer wiring.

Happy paths: a contradictory graph is flagged and the report names every edge; a clean graph
is written unchanged with the 'no contradictions' line.
Unhappy paths: a missing --graph option is a usage error (exit 2) and writes nothing.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from detect_contradictions import (
    app,
    format_contradiction_report,
    mark_contradictions,
)
from typer.testing import CliRunner


def _edge(edge_id: str, direction: str, status: str = "proposed") -> dict:
    return {
        "edge_id": edge_id,
        "cause": "rain",
        "effect": "wet_ground",
        "conditions": {},
        "time_horizon": "short",
        "direction": direction,
        "status": status,
    }


def test_mark_contradictions_flags_opposite_edges_in_place():
    graph = {"edges": [_edge("e1", "positive"), _edge("e2", "negative")]}

    contradictions = mark_contradictions(graph)

    assert contradictions == {"e1": ["e2"], "e2": ["e1"]}
    assert graph["edges"][0]["status"] == "disputed"
    assert graph["edges"][1]["contradicts_edge_ids"] == ["e1"]


def test_mark_contradictions_leaves_clean_graph_unchanged():
    graph = {"edges": [_edge("e1", "positive")]}
    before = json.dumps(graph, sort_keys=True)

    assert mark_contradictions(graph) == {}
    assert json.dumps(graph, sort_keys=True) == before


def test_report_lists_each_contradictory_edge():
    lines = format_contradiction_report({"e1": ["e2"]})

    assert lines == ["Found 1 contradictory edge(s):", "  e1 contradicts ['e2']"]


def test_report_for_clean_graph_says_so():
    assert format_contradiction_report({}) == ["No contradictions detected."]


def test_cli_writes_marked_graph_and_reports(tmp_path):
    graph_path = tmp_path / "graph.json"
    output_path = tmp_path / "nested" / "marked.json"
    graph_path.write_text(json.dumps({"edges": [_edge("e1", "positive"), _edge("e2", "negative")]}))

    result = CliRunner().invoke(app, ["--graph", str(graph_path), "--output", str(output_path)])

    assert result.exit_code == 0, result.output
    assert "Found 2 contradictory edge(s):" in result.output
    assert f"Graph with contradiction flags: {output_path}" in result.output
    written = json.loads(output_path.read_text())
    assert written["edges"][0]["status"] == "disputed"


def test_cli_missing_graph_option_is_a_usage_error(tmp_path):
    result = CliRunner().invoke(app, ["--output", str(tmp_path / "out.json")])

    assert result.exit_code == 2
    assert not (tmp_path / "out.json").exists()
