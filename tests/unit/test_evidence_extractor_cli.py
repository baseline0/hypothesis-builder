"""Tests for the evidence extractor CLI: the template renderers, the session banner, and the Typer wiring.

Happy paths: each template flag prints the matching JSON template, and no flag prints the
session banner with the export directory.
Unhappy paths: an unknown option is a usage error (exit 2).
"""

import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pathlib import Path

from evidence_extractor import (
    app,
    create_causal_claim_template,
    create_template_evidence,
    render_causal_template,
    render_template,
    session_banner,
)
from typer.testing import CliRunner


def test_render_template_is_the_evidence_template_as_json():
    assert json.loads(render_template()) == create_template_evidence()


def test_render_causal_template_is_the_claim_template_as_json():
    assert json.loads(render_causal_template()) == create_causal_claim_template()


def test_session_banner_names_the_export_directory():
    assert session_banner(Path("out/dir")) == [
        "📐 Evidence Extractor",
        "In this session, Claude reads PDFs directly and fills the template.",
        "Export to: out/dir/",
    ]


def test_cli_template_flag_prints_evidence_template():
    result = CliRunner().invoke(app, ["--template"])

    assert result.exit_code == 0
    assert json.loads(result.output) == create_template_evidence()


def test_cli_causal_template_flag_prints_claim_template():
    result = CliRunner().invoke(app, ["--causal-template"])

    assert result.exit_code == 0
    assert json.loads(result.output) == create_causal_claim_template()


def test_cli_without_flags_prints_banner_with_default_output():
    result = CliRunner().invoke(app, [])

    assert result.exit_code == 0
    assert result.output == (
        "📐 Evidence Extractor\n"
        "In this session, Claude reads PDFs directly and fills the template.\n"
        "Export to: automation/extracted_evidence/\n"
    )


def test_cli_unknown_option_is_a_usage_error():
    result = CliRunner().invoke(app, ["--bogus"])

    assert result.exit_code == 2
