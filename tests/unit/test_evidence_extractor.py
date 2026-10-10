"""Tests for the evidence extractor's templates and export.

Happy paths: the claim template carries every field the graph builder reads,
and exports round-trip through JSON and create their output directory.
Unhappy path: data that cannot be serialized fails loudly rather than writing
a partial file.
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

import pytest  # noqa: E402
from evidence_extractor import (  # noqa: E402
    create_causal_claim_template,
    create_template_evidence,
    export_evidence,
)

# Fields CausalGraphBuilder reads from every claim. The extractor template must
# provide them, or the two scripts drift apart without any test noticing.
BUILDER_REQUIRED_CLAIM_FIELDS = {"cause", "effect", "direction", "causal_confidence", "evidence_type"}


def test_claim_template_provides_every_field_the_graph_builder_reads():
    template = create_causal_claim_template()

    assert BUILDER_REQUIRED_CLAIM_FIELDS <= set(template)


def test_template_evidence_has_paper_level_fields():
    template = create_template_evidence()

    assert "paper_name" in template
    assert template["causal_claims"] == []


def test_export_round_trips_through_json(tmp_path):
    data = {"paper_name": "paper_x", "causal_claims": [{"cause": "a", "effect": "b"}]}
    out = tmp_path / "nested" / "evidence.json"

    export_evidence(data, out)

    assert json.loads(out.read_text()) == data


def test_export_creates_missing_parent_directories(tmp_path):
    out = tmp_path / "deep" / "er" / "evidence.json"

    export_evidence({"paper_name": "p"}, out)

    assert out.exists()


def test_export_of_unserializable_data_fails_loudly(tmp_path):
    with pytest.raises(TypeError):
        export_evidence({"paper_name": object()}, tmp_path / "bad.json")
