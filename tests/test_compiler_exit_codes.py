#!/usr/bin/env python3
"""
Exit Code Tests: Verify compiler deterministic failure behavior.

Tests that compiler exits with correct codes at process boundary.
- No accepted edges → exit 1
- Valid edges → exit 0
- Mixed valid/invalid → exit 0 with warnings
"""

import subprocess
import json
import tempfile
from pathlib import Path


def run_compiler(graph_path: Path, output_path: Path) -> tuple:
    """Run compiler and return (exit_code, stderr, stdout)."""
    result = subprocess.run(
        [
            "python",
            "scripts/experiment_spec_compiler.py",
            "--graph",
            str(graph_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr, result.stdout


def test_no_accepted_edges_exits_1():
    """No accepted edges → exit 1."""
    graph = {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "edges": [
            {
                "edge_id": "edge_proposed",
                "status": "proposed",
                "cause": "X",
                "effect": "Y",
            }
        ],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        exit_code, stderr, stdout = run_compiler(graph_path, output_path)

        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        assert not output_path.exists(), "Output file should not exist on failure"
        print("✓ test_no_accepted_edges_exits_1")


def test_rejected_edge_exits_1():
    """Rejected edges only → exit 1."""
    graph = {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "edges": [
            {
                "edge_id": "edge_rejected",
                "status": "rejected",
                "cause": "X",
                "effect": "Y",
            }
        ],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        exit_code, _, _ = run_compiler(graph_path, output_path)

        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        print("✓ test_rejected_edge_exits_1")


def test_incomplete_edge_exits_1():
    """Accepted edge without reviewer → exit 1 (validation fails)."""
    graph = {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "edges": [
            {
                "edge_id": "edge_incomplete",
                "status": "accepted",
                "reviewer": None,  # Missing reviewer
                "cause": "X",
                "effect": "Y",
            }
        ],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        exit_code, _, _ = run_compiler(graph_path, output_path)

        assert exit_code == 1, f"Expected exit 1, got {exit_code}"
        print("✓ test_incomplete_edge_exits_1")


def test_valid_edge_exits_0():
    """Valid complete accepted edge → exit 0."""
    graph = {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "edges": [
            {
                "edge_id": "edge_valid",
                "status": "accepted",
                "cause": "diversity_mechanism",
                "effect": "final_fitness",
                "mechanism": "entropy increases",
                "mechanism_status": "known",
                "direction": "increases",
                "reviewer": "test_user",
                "reviewed_at": "2026-09-18T10:00:00Z",
                "supporting_papers": ["paper_1"],
                "source": {
                    "paper_id": "paper_1",
                    "page": 42,
                    "quote": "test quote",
                },
            }
        ],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        exit_code, _, _ = run_compiler(graph_path, output_path)

        assert exit_code == 0, f"Expected exit 0, got {exit_code}"
        assert output_path.exists(), "Output file should exist on success"

        with open(output_path) as f:
            specs = json.load(f)

        assert specs["total_experiments"] == 1
        print("✓ test_valid_edge_exits_0")


def test_all_invalid_exits_1():
    """All invalid edges → exit 1."""
    graph = {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "edges": [
            {
                "edge_id": "edge_proposed",
                "status": "proposed",  # Invalid: not accepted
                "cause": "A",
                "effect": "B",
            },
            {
                "edge_id": "edge_incomplete",
                "status": "accepted",  # Invalid: no reviewer
                "reviewer": None,
                "cause": "C",
                "effect": "D",
            },
        ],
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        exit_code, stderr, stdout = run_compiler(graph_path, output_path)

        # Should exit 1 because no valid edges exist
        assert exit_code == 1, f"Expected exit 1 (all invalid), got {exit_code}"
        print("✓ test_all_invalid_exits_1")


def run_all_tests():
    """Run all exit code tests."""
    print("Running exit code tests...\n")

    tests = [
        test_no_accepted_edges_exits_1,
        test_rejected_edge_exits_1,
        test_incomplete_edge_exits_1,
        test_valid_edge_exits_0,
        test_all_invalid_exits_1,
    ]

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            return False

    print(f"\n✓ All {len(tests)} exit code tests passed")
    return True


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
