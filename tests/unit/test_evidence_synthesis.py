"""Tests for evidence synthesis: the RQ rollups, the matrix shape, and the CLI wiring.

Happy paths: papers roll up into per-RQ findings with the documented confidence rules, and the
CLI writes the matrix for matching extraction files.
Unhappy paths: a pattern that matches nothing raises NoExtractionsError and the CLI exits 1.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))


import pytest
from evidence_synthesis import (
    EvidenceSynthesizer,
    NoExtractionsError,
    app,
    collect_extraction_files,
)
from typer.testing import CliRunner


def _paper(name: str, **overrides) -> dict:
    base = {
        "paper_name": name,
        "rq1_combines_quantum_psys": True,
        "quality_total": 6,
        "rq2_discusses_collapse": True,
        "rq2_root_cause": "diversity loss",
        "rq3_adaptive_mechanisms": ["tournament"],
        "rq4_cec2017_baseline": True,
        "rq4_ga_results": {"F1": {"mean": 10}},
        "rq5_high_d_tested": True,
        "rq5_scalability_trend": "degrades",
    }
    base.update(overrides)
    return base


def _synthesizer(*papers: dict) -> EvidenceSynthesizer:
    synthesizer = EvidenceSynthesizer()
    for paper in papers:
        synthesizer.papers[paper["paper_name"]] = paper
    return synthesizer


def test_rq1_is_high_confidence_when_no_paper_contradicts():
    result = _synthesizer(_paper("a"), _paper("b")).synthesize_rq1()

    assert result["supporting_papers"] == ["a", "b"]
    assert result["confidence"] == "high"
    assert result["quality_weighted_score"] == 12


def test_rq1_is_medium_confidence_when_a_paper_contradicts():
    result = _synthesizer(_paper("a"), _paper("b", rq1_combines_quantum_psys=False)).synthesize_rq1()

    assert result["contradicting_papers"] == ["b"]
    assert result["confidence"] == "medium"


def test_rq2_picks_the_most_common_root_cause_and_three_papers_is_high():
    synthesizer = _synthesizer(
        _paper("a", rq2_root_cause="x"),
        _paper("b", rq2_root_cause="x"),
        _paper("c", rq2_root_cause="y"),
    )

    result = synthesizer.synthesize_rq2()

    assert result["consensus_root_cause"] == "x"
    assert result["confidence"] == "high"


def test_rq3_marks_mechanisms_seen_three_times_as_high_confidence():
    synthesizer = _synthesizer(*(_paper(n) for n in ("a", "b", "c")))

    result = synthesizer.synthesize_rq3()

    assert result["mechanisms"]["tournament"]["count"] == 3
    assert result["confidence"] == "high"


def test_rq4_averages_baseline_means_across_papers():
    synthesizer = _synthesizer(
        _paper("a", rq4_ga_results={"F1": {"mean": 10}}),
        _paper("b", rq4_ga_results={"F1": {"mean": 30}}),
    )

    result = synthesizer.synthesize_rq4()

    assert result["averaged_results"] == {"F1": {"mean": 20.0}}
    assert result["confidence"] == "high"


def test_rq5_with_no_high_d_papers_is_low_confidence():
    result = _synthesizer(_paper("a", rq5_high_d_tested=False)).synthesize_rq5()

    assert result["confidence"] == "low"
    assert result["scalability_consensus"] == "Unknown"


def test_synthesize_all_has_metadata_and_all_five_rqs():
    result = _synthesizer(_paper("a")).synthesize_all()

    assert result["metadata"]["total_papers"] == 1
    assert set(result["evidence"]) == {
        "RQ1_novelty",
        "RQ2_collapse",
        "RQ3_adaptation",
        "RQ4_baseline",
        "RQ5_scalability",
    }


def test_collect_extraction_files_raises_when_nothing_matches(tmp_path):
    with pytest.raises(NoExtractionsError):
        collect_extraction_files(str(tmp_path / "none*.json"))


def test_cli_writes_matrix_for_matching_extractions(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps(_paper("a")))
    output = tmp_path / "out" / "matrix.json"

    result = CliRunner().invoke(app, ["--extractions", str(tmp_path / "*.json"), "--output", str(output)])

    assert result.exit_code == 0, result.output
    assert "Loading 1 extraction files..." in result.output
    assert json.loads(output.read_text())["metadata"]["total_papers"] == 1


def test_cli_no_match_exits_1(tmp_path):
    pattern = str(tmp_path / "none*.json")

    result = CliRunner().invoke(app, ["--extractions", pattern])

    assert result.exit_code == 1
    assert f"❌ No extraction files found matching: {pattern}" in result.output
