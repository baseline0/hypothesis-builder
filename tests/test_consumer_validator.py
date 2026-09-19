#!/usr/bin/env python3
"""
Phase 4: Consumer Validator Tests

Tests for the experiment specs consumer validator. Validates that:
1. Schema version is correct
2. All required fields present
3. Business rules enforced (treatment != outcome)
4. Exit codes correct (0 for valid, 1 for invalid)
"""

import json
import subprocess
import tempfile
from pathlib import Path


def create_valid_spec():
    """Create a minimal valid experiment spec."""
    return {
        "schema_version": "1.0.0",
        "experiment_id": "exp_0000",
        "hypothesis_id": "H_causal_exp_0000",
        "source_edge_id": "edge_0001",
        "status": "validated",
        "causal_claim": {
            "cause": "diversity_mechanism",
            "effect": "final_fitness",
            "mechanism": "entropy increases",
            "mechanism_status": "known",
            "direction": "increases",
            "consensus_confidence": "high",
            "supporting_papers": ["paper_1"],
            "reviewer": "test_user",
            "reviewed_at": "2026-09-18T10:00:00Z",
        },
        "estimand": {
            "name": "effect_of_diversity_mechanism_on_final_fitness",
            "treatment": {
                "variable": "diversity_mechanism",
                "levels": ["disabled", "enabled"],
                "manipulable": True,
            },
            "outcome": {
                "variable": "final_fitness",
                "metric": "best_fitness_of_run",
                "direction": "increases",
            },
            "population": "CEC2017 benchmark",
            "time_horizon": "200 generations",
        },
        "design": {
            "design_type": "controlled_benchmark_experiment",
            "factors": [],
            "replicates": 30,
            "design_controls": {"evaluation_budget": "held_constant", "dimension": "stratified"},
        },
        "analysis": {
            "primary_outcome": "final_fitness",
            "unit": "run",
            "summary": "median_and_iqr",
            "uncertainty": "bootstrap_ci",
        },
        "provenance": {
            "source_paper": "paper_1",
            "source_page": 42,
            "source_quote": "A diversity mechanism increases fitness",
            "edge_id": "edge_0001",
            "reviewer": "test_user",
            "reviewed_at": "2026-09-18T10:00:00Z",
        },
    }


def create_specs_json(experiments):
    """Create complete specs JSON with given experiments."""
    return {
        "schema_version": "1.0.0",
        "export_version": "1.0.0",
        "protocol_version": "qips-2026-09-18",
        "total_experiments": len(experiments),
        "experiments": experiments,
        "compiler_validation_enforced": True,
    }


def test_valid_spec_passes():
    """Valid spec should pass validation."""
    specs = create_specs_json([create_valid_spec()])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}\n{result.stdout}"
        assert "VALID" in result.stdout or "passed validation" in result.stdout


def test_missing_estimand_fails():
    """Spec without estimand should fail."""
    exp = create_valid_spec()
    del exp["estimand"]

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "missing estimand" in result.stdout


def test_missing_design_fails():
    """Spec without design section should fail."""
    exp = create_valid_spec()
    del exp["design"]

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "missing design" in result.stdout


def test_missing_design_controls_fails():
    """Spec with design but no design_controls should fail."""
    exp = create_valid_spec()
    del exp["design"]["design_controls"]

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "design_controls" in result.stdout


def test_missing_analysis_fails():
    """Spec without analysis should fail."""
    exp = create_valid_spec()
    del exp["analysis"]

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "missing analysis" in result.stdout


def test_missing_provenance_fails():
    """Spec without provenance should fail."""
    exp = create_valid_spec()
    del exp["provenance"]

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "missing provenance" in result.stdout


def test_treatment_equals_outcome_fails():
    """Business rule: treatment and outcome must be different."""
    exp = create_valid_spec()
    exp["estimand"]["treatment"]["variable"] = "fitness"
    exp["estimand"]["outcome"]["variable"] = "fitness"

    specs = create_specs_json([exp])

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "cannot be the same" in result.stdout


def test_wrong_schema_version_fails():
    """Wrong schema version should fail."""
    specs = create_specs_json([create_valid_spec()])
    specs["schema_version"] = "2.0.0"

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "schema_version" in result.stdout


def test_total_experiments_mismatch_fails():
    """total_experiments mismatch should fail."""
    specs = create_specs_json([create_valid_spec()])
    specs["total_experiments"] = 99  # Mismatch!

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "mismatch" in result.stdout


def test_multiple_valid_specs_pass():
    """Multiple valid specs should all pass."""
    specs_list = []
    for i in range(3):
        exp = create_valid_spec()
        exp["experiment_id"] = f"exp_{i:04d}"
        exp["estimand"]["outcome"]["variable"] = f"outcome_{i}"  # Make unique
        specs_list.append(exp)

    specs = create_specs_json(specs_list)

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "3" in result.stdout and "passed validation" in result.stdout


def test_empty_experiments_fails():
    """Empty experiments list should fail."""
    specs = create_specs_json([])
    specs["total_experiments"] = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        specs_path = Path(tmpdir) / "specs.json"
        with open(specs_path, "w") as f:
            json.dump(specs, f)

        result = subprocess.run(
            ["python", "scripts/validate_experiment_specs.py", str(specs_path)],
            cwd=".",
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "No experiments" in result.stdout
