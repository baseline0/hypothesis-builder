"""Tests for importing causal validations: hash binding, record checks, input checks, and the CLI.

Happy paths: a record bound to the current graph hash is applied, and the CLI writes the validated graph.
Unhappy paths: a stale graph hash or an invalid decision is rejected (apply returns False, CLI exits 1),
a missing input file is reported with exit 1, and metadata keys do not change the graph hash.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pathlib import Path

from import_causal_validations import (
    ValidationImporter,
    app,
    compute_graph_hash,
    input_problem,
)
from typer.testing import CliRunner

GRAPH = {"edges": [{"edge_id": "e1", "status": "proposed"}]}


def _record(graph_hash: str, **overrides) -> dict:
    base = {
        "edge_id": "e1",
        "decision": "accepted",
        "reviewer": "reviewer",
        "reviewed_at": "2026-09-18T10:00:00Z",
        "graph_hash": graph_hash,
        "rationale": "checked the quote",
    }
    base.update(overrides)
    return base


def _write_inputs(tmp_path: Path, records: list[dict]) -> tuple[Path, Path]:
    graph_path = tmp_path / "graph.json"
    graph_path.write_text(json.dumps(GRAPH))
    validations_path = tmp_path / "validations.jsonl"
    validations_path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return graph_path, validations_path


def test_graph_hash_ignores_compiler_metadata():
    base = compute_graph_hash(GRAPH)

    assert compute_graph_hash({**GRAPH, "validated_at": "now", "hash": "x"}) == base


def test_valid_record_is_applied_to_the_edge(tmp_path):
    graph_hash = compute_graph_hash(GRAPH)
    graph_path, validations_path = _write_inputs(tmp_path, [_record(graph_hash)])

    importer = ValidationImporter(graph_path, validations_path)

    assert importer.apply_validations() is True
    assert importer.graph["edges"][0]["status"] == "accepted"
    assert importer.graph["edges"][0]["reviewer"] == "reviewer"


def test_stale_graph_hash_is_rejected(tmp_path):
    graph_path, validations_path = _write_inputs(tmp_path, [_record("0" * 64)])

    importer = ValidationImporter(graph_path, validations_path)

    assert importer.apply_validations() is False
    assert any("graph_hash mismatch" in e for e in importer.validation_errors)


def test_invalid_decision_is_rejected(tmp_path):
    graph_hash = compute_graph_hash(GRAPH)
    graph_path, validations_path = _write_inputs(tmp_path, [_record(graph_hash, decision="maybe")])

    importer = ValidationImporter(graph_path, validations_path)

    assert importer.apply_validations() is False
    assert importer.graph["edges"][0]["status"] == "proposed"


def test_input_problem_reports_validations_before_graph(tmp_path):
    missing = tmp_path / "absent.json"

    assert input_problem(missing, missing) == f"ERROR: Validations file not found: {missing}"


def test_input_problem_reports_missing_graph(tmp_path):
    validations = tmp_path / "validations.jsonl"
    validations.write_text("")
    missing = tmp_path / "absent.json"

    assert input_problem(validations, missing) == f"ERROR: Graph file not found: {missing}"


def test_input_problem_is_none_when_both_exist(tmp_path):
    graph_path, validations_path = _write_inputs(tmp_path, [])

    assert input_problem(validations_path, graph_path) is None


def test_cli_writes_validated_graph(tmp_path):
    graph_hash = compute_graph_hash(GRAPH)
    graph_path, validations_path = _write_inputs(tmp_path, [_record(graph_hash)])
    output = tmp_path / "out" / "validated.json"

    result = CliRunner().invoke(
        app,
        ["--validations", str(validations_path), "--graph", str(graph_path), "--output", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert "Validations applied: 1" in result.output
    assert json.loads(output.read_text())["edges"][0]["status"] == "accepted"


def test_cli_rejected_validation_exits_1_and_writes_nothing(tmp_path):
    graph_path, validations_path = _write_inputs(tmp_path, [_record("0" * 64)])
    output = tmp_path / "validated.json"

    result = CliRunner().invoke(
        app,
        ["--validations", str(validations_path), "--graph", str(graph_path), "--output", str(output)],
    )

    assert result.exit_code == 1
    assert not output.exists()


def test_cli_missing_validations_file_exits_1(tmp_path):
    graph_path, _ = _write_inputs(tmp_path, [])
    missing = tmp_path / "absent.jsonl"

    result = CliRunner().invoke(app, ["--validations", str(missing), "--graph", str(graph_path)])

    assert result.exit_code == 1
    assert f"ERROR: Validations file not found: {missing}" in result.output
