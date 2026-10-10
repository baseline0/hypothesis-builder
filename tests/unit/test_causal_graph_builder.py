"""Tests for CausalGraphBuilder: loading, merging claims into edges, and exports.

Happy paths: claims from several papers merge into one edge, mechanism status
and consensus follow the documented rules, and the exports write valid output.
Unhappy paths: missing or malformed inputs fail loudly, and a claim with an
empty cause or effect is skipped rather than becoming an edge.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pytest  # noqa: E402
from causal_graph_builder import CausalGraphBuilder  # noqa: E402


def claim(cause="rain", effect="wet_ground", mechanism="", direction="positive", confidence="high", design="rct"):
    return {
        "cause": cause,
        "effect": effect,
        "mechanism": mechanism,
        "direction": direction,
        "causal_confidence": confidence,
        "evidence_type": design,
    }


def write_paper(path, name, claims):
    path.write_text(json.dumps({"paper_name": name, "causal_claims": claims}))
    return path


@pytest.fixture
def builder():
    return CausalGraphBuilder()


# --- happy paths -------------------------------------------------------------------


def test_identical_claims_from_two_papers_merge_into_one_edge(builder, tmp_path):
    a = write_paper(tmp_path / "a.json", "paper_a", [claim()])
    b = write_paper(tmp_path / "b.json", "paper_b", [claim()])
    builder.load_evidence([a, b])

    builder.merge_edges()

    assert len(builder.edges) == 1
    edge = next(iter(builder.edges.values()))
    assert edge["supporting_papers"] == ["paper_a", "paper_b"]
    assert edge["supporting_claims"] == 2
    assert edge["status"] == "proposed"
    assert edge["review_status"] == "pending"


def test_claim_with_mechanism_is_hypothesized_and_without_is_unknown(builder, tmp_path):
    path = write_paper(
        tmp_path / "p.json",
        "paper",
        [claim(cause="a", effect="b", mechanism="osmosis"), claim(cause="c", effect="d", mechanism="")],
    )
    builder.load_evidence([path])

    builder.merge_edges()

    statuses = {e["cause"]: e["mechanism_status"] for e in builder.edges.values()}
    assert statuses == {"a": "hypothesized", "c": "unknown"}


def test_consensus_is_high_when_most_votes_are_high(builder):
    assert builder._consensus_confidence(["high", "high", "high", "low"]) == "high"


def test_consensus_is_medium_at_the_medium_threshold(builder):
    assert builder._consensus_confidence(["medium", "medium", "low", "low"]) == "medium"


def test_consensus_is_low_when_votes_are_split(builder):
    assert builder._consensus_confidence(["high", "low", "low", "low"]) == "low"


def test_export_graph_writes_proposed_edges_with_counts(builder, tmp_path):
    path = write_paper(tmp_path / "p.json", "paper", [claim()])
    builder.load_evidence([path])
    builder.merge_edges()
    out = tmp_path / "graph" / "graph.json"

    builder.export_graph(out)

    graph = json.loads(out.read_text())
    assert graph["total_papers"] == 1
    assert graph["total_edges"] == 1
    assert graph["status"].startswith("proposed")


def test_mermaid_export_shows_only_accepted_edges(builder, tmp_path):
    path = write_paper(tmp_path / "p.json", "paper", [claim()])
    builder.load_evidence([path])
    builder.merge_edges()
    out = tmp_path / "diagram.mmd"

    builder.export_mermaid(out)

    # Nothing is accepted until a human reviews it, so the diagram has no edges.
    assert out.read_text() == "graph LR"


# --- unhappy paths -----------------------------------------------------------------


def test_missing_evidence_file_fails_loudly(builder, tmp_path):
    with pytest.raises(FileNotFoundError):
        builder.load_evidence([tmp_path / "absent.json"])


def test_malformed_evidence_json_fails_loudly(builder, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")

    with pytest.raises(json.JSONDecodeError):
        builder.load_evidence([bad])


def test_evidence_without_paper_name_fails_loudly(builder, tmp_path):
    bad = tmp_path / "noname.json"
    bad.write_text(json.dumps({"causal_claims": [claim()]}))

    with pytest.raises(KeyError):
        builder.load_evidence([bad])


def test_claim_with_empty_cause_or_effect_is_skipped(builder, tmp_path):
    path = write_paper(
        tmp_path / "p.json",
        "paper",
        [claim(cause="", effect="b"), claim(cause="a", effect=""), claim(cause="a", effect="b")],
    )
    builder.load_evidence([path])

    builder.merge_edges()

    assert len(builder.edges) == 1
    assert next(iter(builder.edges.values()))["cause"] == "a"


def test_no_votes_means_low_consensus(builder):
    assert builder._consensus_confidence([]) == "low"
