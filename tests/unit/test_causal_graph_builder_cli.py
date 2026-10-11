"""Tests for the causal graph builder CLI: pattern expansion, the no-match exit, and a full run.

Happy paths: a glob matches extraction files and the CLI writes the graph and the Mermaid diagram.
Unhappy paths: a pattern that matches nothing raises NoExtractionsError and the CLI exits 1 with
the pattern in its message; a missing --extractions option is a usage error (exit 2).
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pathlib import Path

import pytest
from causal_graph_builder import (
    NoExtractionsError,
    app,
    collect_extraction_files,
)
from typer.testing import CliRunner


def _write_extraction(path: Path, paper: str) -> None:
    claim = {
        "cause": "rain",
        "effect": "wet_ground",
        "mechanism": "",
        "direction": "positive",
        "causal_confidence": "high",
        "evidence_type": "rct",
    }
    path.write_text(json.dumps({"paper_name": paper, "causal_claims": [claim]}))


def test_collect_extraction_files_expands_the_glob(tmp_path):
    _write_extraction(tmp_path / "a.json", "paper_a")
    _write_extraction(tmp_path / "b.json", "paper_b")

    files = collect_extraction_files(str(tmp_path / "*.json"))

    assert sorted(p.name for p in files) == ["a.json", "b.json"]


def test_collect_extraction_files_raises_when_nothing_matches(tmp_path):
    with pytest.raises(NoExtractionsError, match="nothing-here"):
        collect_extraction_files(str(tmp_path / "nothing-here*.json"))


def test_cli_writes_graph_and_mermaid_from_matching_extractions(tmp_path):
    _write_extraction(tmp_path / "a.json", "paper_a")
    output = tmp_path / "graph.json"
    mermaid = tmp_path / "graph.mmd"

    result = CliRunner().invoke(
        app,
        ["--extractions", str(tmp_path / "*.json"), "--output", str(output), "--mermaid", str(mermaid)],
    )

    assert result.exit_code == 0, result.output
    assert "Loading 1 extraction files..." in result.output
    graph = json.loads(output.read_text())
    assert graph["total_papers"] == 1
    assert graph["total_edges"] == 1
    assert mermaid.exists()


def test_cli_no_match_exits_1_and_names_the_pattern(tmp_path):
    pattern = str(tmp_path / "missing*.json")

    result = CliRunner().invoke(app, ["--extractions", pattern])

    assert result.exit_code == 1
    assert f"❌ No extraction files found matching: {pattern}" in result.output


def test_cli_missing_extractions_option_is_a_usage_error():
    result = CliRunner().invoke(app, [])

    assert result.exit_code == 2
