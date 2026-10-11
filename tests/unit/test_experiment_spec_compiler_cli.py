"""Tests for the experiment spec compiler CLI: skipped-edge reporting, the no-compilable-edges error, and the Typer wiring.

Happy paths: a complete accepted edge compiles and the CLI writes the spec file; invalid edges
next to a valid one are reported as skipped and do not stop the run.
Unhappy paths: no accepted edges, or only invalid accepted edges, raise NoCompilableEdgesError
(the CLI exits 1 with the report); a missing graph file exits 1 before anything is compiled.
"""

import copy
import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from experiment_spec_compiler import (  # noqa: E402
    ExperimentSpecCompiler,
    NoCompilableEdgesError,
    app,
    graph_missing_message,
)
from typer.testing import CliRunner  # noqa: E402

GOOD_EDGE = {
    "edge_id": "edge_0001",
    "cause": "algorithm_choice",
    "effect": "final_fitness",
    "mechanism": "",
    "mechanism_status": "unknown",
    "direction": "decreases",
    "consensus_confidence": "high",
    "supporting_papers": ["paper_a"],
    "status": "accepted",
    "reviewer": "reviewer",
    "reviewed_at": "2026-09-18T10:00:00Z",
    "source": {"paper_id": "paper_a", "page": 4, "quote": "quote text"},
}


def _graph_file(tmp_path: Path, edges: list[dict]) -> Path:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps({"edges": edges}))
    return path


def test_graph_missing_message_is_none_when_present(tmp_path):
    path = _graph_file(tmp_path, [])

    assert graph_missing_message(path) is None


def test_graph_missing_message_names_the_missing_path(tmp_path):
    path = tmp_path / "absent.json"

    assert graph_missing_message(path) == f"ERROR: Causal graph not found: {path}"


def test_complete_accepted_edge_compiles_with_no_skips(tmp_path):
    compiler = ExperimentSpecCompiler(_graph_file(tmp_path, [GOOD_EDGE]))

    skipped = compiler.build_experiment_specs()

    assert skipped == []
    assert list(compiler.experiments) == ["exp_0000"]


def test_invalid_accepted_edge_is_skipped_when_another_compiles(tmp_path):
    bad = copy.deepcopy(GOOD_EDGE) | {"edge_id": "edge_0002", "reviewer": None}
    compiler = ExperimentSpecCompiler(_graph_file(tmp_path, [GOOD_EDGE, bad]))

    skipped = compiler.build_experiment_specs()

    assert skipped == [("edge_0002", "reviewer is missing (no human accountability)")]
    assert len(compiler.experiments) == 1


def test_no_accepted_edges_raises_with_report_lines(tmp_path):
    compiler = ExperimentSpecCompiler(_graph_file(tmp_path, [GOOD_EDGE | {"status": "proposed"}]))

    with pytest.raises(NoCompilableEdgesError) as info:
        compiler.build_experiment_specs()

    assert info.value.lines == [
        "ERROR: No accepted edges found (total edges: 1)",
        "   Valid edges must have status='accepted'. Exiting.",
    ]


def test_all_accepted_edges_invalid_raises_with_each_reason(tmp_path):
    bad = GOOD_EDGE | {"reviewer": None}
    compiler = ExperimentSpecCompiler(_graph_file(tmp_path, [bad]))

    with pytest.raises(NoCompilableEdgesError) as info:
        compiler.build_experiment_specs()

    assert info.value.lines == [
        "ERROR: All 1 accepted edges failed validation:",
        "   edge_0001: reviewer is missing (no human accountability)",
    ]


def test_cli_writes_specs_and_warns_about_skipped_edges(tmp_path):
    bad = GOOD_EDGE | {"edge_id": "edge_0002", "reviewer": None}
    graph = _graph_file(tmp_path, [GOOD_EDGE, bad])
    output = tmp_path / "out" / "specs.json"

    result = CliRunner().invoke(app, ["--graph", str(graph), "--output", str(output)])

    assert result.exit_code == 0, result.output
    assert "WARNING: 1 edges failed validation (skipped):" in result.output
    assert json.loads(output.read_text())["total_experiments"] == 1


def test_cli_without_accepted_edges_exits_1_and_writes_nothing(tmp_path):
    graph = _graph_file(tmp_path, [GOOD_EDGE | {"status": "proposed"}])
    output = tmp_path / "specs.json"

    result = CliRunner().invoke(app, ["--graph", str(graph), "--output", str(output)])

    assert result.exit_code == 1
    assert "ERROR: No accepted edges found (total edges: 1)" in result.output
    assert not output.exists()


def test_cli_missing_graph_exits_1(tmp_path):
    missing = tmp_path / "absent.json"

    result = CliRunner().invoke(app, ["--graph", str(missing)])

    assert result.exit_code == 1
    assert f"ERROR: Causal graph not found: {missing}" in result.output
