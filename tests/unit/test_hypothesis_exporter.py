"""Tests for the hypothesis exporter: hypothesis building, the missing-file check, and the CLI wiring.

Happy paths: an evidence matrix becomes five hypotheses with the novelty statement, and the CLI
writes the hypotheses file.
Unhappy paths: a missing evidence file is reported with exit 1 and nothing is written.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))


from hypothesis_exporter import (  # noqa: E402
    HypothesisExporter,
    app,
    evidence_missing_message,
)
from typer.testing import CliRunner  # noqa: E402


def _matrix() -> dict:
    def rq(**extra) -> dict:
        return {"confidence": "high", "supporting_papers": ["a"], "quality_weighted_score": 5, **extra}

    return {
        "metadata": {"total_papers": 1, "paper_names": ["a"], "synthesis_method": "quality-weighted consensus"},
        "evidence": {
            "RQ1_novelty": rq(),
            "RQ2_collapse": rq(consensus_root_cause="diversity loss"),
            "RQ3_adaptation": {"confidence": "medium", "quality_weighted_score": 5, "mechanisms": {"tournament": {}}},
            "RQ4_baseline": rq(averaged_results={"F1": {"mean": 10}}),
            "RQ5_scalability": rq(scalability_consensus="degrades"),
        },
    }


def test_build_hypotheses_produces_five_hypotheses_and_novelty_statement(tmp_path):
    evidence_path = tmp_path / "matrix.json"
    evidence_path.write_text(json.dumps(_matrix()))

    result = HypothesisExporter(evidence_path).build_hypotheses()

    assert [h["id"] for h in result["hypotheses"]] == [
        "H1_novelty",
        "H2_collapse",
        "H3_adaptation",
        "H4_baseline",
        "H5_scalability",
    ]
    assert result["audit_trail"]["total_papers_analyzed"] == 1
    assert "QIPS is novel because" in result["novelty_statement"]
    assert result["hypotheses"][2]["identified_mechanisms"] == ["tournament"]


def test_evidence_missing_message_is_none_when_the_file_exists(tmp_path):
    path = tmp_path / "matrix.json"
    path.write_text("{}")

    assert evidence_missing_message(path) is None


def test_evidence_missing_message_names_the_missing_path(tmp_path):
    path = tmp_path / "absent.json"

    assert evidence_missing_message(path) == f"❌ Evidence file not found: {path}"


def test_cli_writes_hypotheses_from_an_existing_matrix(tmp_path):
    evidence_path = tmp_path / "matrix.json"
    evidence_path.write_text(json.dumps(_matrix()))
    output = tmp_path / "out" / "hypotheses.json"

    result = CliRunner().invoke(app, ["--evidence", str(evidence_path), "--output", str(output)])

    assert result.exit_code == 0, result.output
    assert "Hypotheses exported:" in result.output
    assert len(json.loads(output.read_text())["hypotheses"]) == 5


def test_cli_missing_evidence_exits_1_and_writes_nothing(tmp_path):
    output = tmp_path / "hypotheses.json"
    missing = tmp_path / "absent.json"

    result = CliRunner().invoke(app, ["--evidence", str(missing), "--output", str(output)])

    assert result.exit_code == 1
    assert f"❌ Evidence file not found: {missing}" in result.output
    assert not output.exists()
