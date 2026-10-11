"""Tests for the membrane consumer validator: schema and business-rule checks, the missing-file check, and the CLI.

Happy paths: a complete spec file validates with exit 0.
Unhappy paths: a wrong schema version or a missing provenance field fails validation (exit 1),
a missing specs file is reported with exit 1, and a treatment equal to the outcome is an error.
"""

import copy
import json
import sys

from constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from pathlib import Path  # noqa: E402

from typer.testing import CliRunner  # noqa: E402
from validate_experiment_specs import (  # noqa: E402
    ExperimentSpecValidator,
    app,
    specs_missing_message,
)

EXPERIMENT = {
    "schema_version": "1.0.0",
    "experiment_id": "exp_0000",
    "status": "validated",
    "estimand": {
        "name": "effect_of_a_on_b",
        "treatment": {"variable": "a", "levels": ["off", "on"]},
        "outcome": {"variable": "b"},
        "population": "CEC2017 benchmark functions",
    },
    "design": {"design_controls": {"random_seed": "blocked"}},
    "analysis": {"primary_outcome": "b", "summary": "median_and_iqr"},
    "provenance": {"source_paper": "paper", "source_page": 3, "source_quote": "quote", "edge_id": "edge_0000"},
    "causal_claim": {"cause": "a", "effect": "b", "mechanism_status": "known"},
}


def _specs(**overrides) -> dict:
    base = {
        "schema_version": "1.0.0",
        "export_version": "1.0.0",
        "total_experiments": 1,
        "experiments": [copy.deepcopy(EXPERIMENT)],
    }
    base.update(overrides)
    return base


def _write(path: Path, specs: dict) -> Path:
    path.write_text(json.dumps(specs))
    return path


def _validate(tmp_path: Path, specs: dict) -> ExperimentSpecValidator:
    validator = ExperimentSpecValidator(_write(tmp_path / "specs.json", specs))
    validator.validate()
    return validator


def test_complete_spec_file_has_no_errors(tmp_path):
    validator = _validate(tmp_path, _specs())

    assert validator.errors == []


def test_wrong_schema_version_is_an_error(tmp_path):
    validator = _validate(tmp_path, _specs(schema_version="0.9.0"))

    assert any("Invalid schema_version" in e for e in validator.errors)


def test_missing_provenance_field_is_an_error(tmp_path):
    specs = _specs()
    del specs["experiments"][0]["provenance"]["source_quote"]

    validator = _validate(tmp_path, specs)

    assert "exp_0000: provenance.source_quote missing" in validator.errors


def test_treatment_equal_to_outcome_is_an_error(tmp_path):
    specs = _specs()
    specs["experiments"][0]["estimand"]["outcome"]["variable"] = "a"

    validator = _validate(tmp_path, specs)

    assert "exp_0000: treatment and outcome cannot be the same variable" in validator.errors


def test_specs_missing_message_is_none_when_file_exists(tmp_path):
    path = _write(tmp_path / "specs.json", _specs())

    assert specs_missing_message(path) is None


def test_specs_missing_message_gives_the_compiler_hint(tmp_path):
    path = tmp_path / "absent.json"

    lines = specs_missing_message(path)

    assert lines == [
        f"ERROR: Specs file not found: {path}",
        "First run: python scripts/experiment_spec_compiler.py --graph <graph.json>",
    ]


def test_cli_valid_file_exits_0(tmp_path):
    path = _write(tmp_path / "specs.json", _specs())

    result = CliRunner().invoke(app, [str(path)])

    assert result.exit_code == 0, result.output
    assert "Status: VALID" in result.output


def test_cli_invalid_file_exits_1(tmp_path):
    path = _write(tmp_path / "specs.json", _specs(schema_version="0.9.0"))

    result = CliRunner().invoke(app, [str(path)])

    assert result.exit_code == 1
    assert "Status: FAILED" in result.output


def test_cli_missing_file_exits_1(tmp_path):
    path = tmp_path / "absent.json"

    result = CliRunner().invoke(app, [str(path)])

    assert result.exit_code == 1
    assert f"ERROR: Specs file not found: {path}" in result.output
