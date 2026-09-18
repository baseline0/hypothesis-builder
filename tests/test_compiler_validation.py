#!/usr/bin/env python3
"""
Contract Tests: Experiment Spec Compiler Validation.

These tests prove that the compiler enforces strict validation gates:
  - proposed edges are rejected
  - rejected edges are rejected
  - incomplete edges are rejected (missing reviewer, provenance, etc)
  - complete, accepted edges are emitted

Tests use synthetic fixtures (2-3 edges) to avoid processing real papers.
This is the minimal test suite before ingesting the full corpus.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from experiment_spec_compiler import ExperimentSpecCompiler


def create_fixture_graph(edges_list):
    """Create a minimal causal graph fixture."""
    return {
        "graph_version": "1.0.0",
        "generated_at": "2026-09-18",
        "total_papers": 1,
        "total_edges": len(edges_list),
        "edges": edges_list,
        "status": "fixture",
    }


def test_proposed_edge_rejected():
    """Test: proposed edge is rejected by compiler."""
    edges = [
        {
            "edge_id": "edge_0001",
            "cause": "diversity_mechanism",
            "effect": "final_fitness",
            "mechanism": "entropy preservation",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "proposed",  # NOT accepted
            "supporting_papers": ["paper_1"],
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_1",
                "page": 42,
                "quote": "diversity improves fitness",
            },
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)

        # Should exit with error (proposed edge rejected)
        try:
            compiler.build_experiment_specs()
            assert False, "Expected SystemExit but compiled succeeded"
        except SystemExit as e:
            assert e.code == 1, f"Expected exit code 1, got {e.code}"

    print("PASS: test_proposed_edge_rejected")


def test_rejected_edge_rejected():
    """Test: edge marked as 'rejected' is rejected."""
    edges = [
        {
            "edge_id": "edge_0002",
            "cause": "population_size",
            "effect": "convergence_speed",
            "mechanism": "larger population = more evals",
            "mechanism_status": "hypothesized",
            "direction": "decreases",
            "status": "rejected",  # Explicitly rejected
            "supporting_papers": ["paper_1"],
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_1",
                "page": 50,
                "quote": "...",
            },
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)

        try:
            compiler.build_experiment_specs()
            assert False, "Expected SystemExit"
        except SystemExit as e:
            assert e.code == 1

    print("PASS: test_rejected_edge_rejected")


def test_accepted_without_reviewer_rejected():
    """Test: accepted edge missing reviewer is rejected."""
    edges = [
        {
            "edge_id": "edge_0003",
            "cause": "adaptive_update_frequency",
            "effect": "solution_diversity",
            "mechanism": "frequent updates = responsive",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "supporting_papers": ["paper_1"],
            "reviewer": None,  # MISSING
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_1",
                "page": 30,
                "quote": "...",
            },
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)

        try:
            compiler.build_experiment_specs()
            assert False, "Expected SystemExit"
        except SystemExit as e:
            assert e.code == 1

    print("PASS: test_accepted_without_reviewer_rejected")


def test_accepted_without_provenance_rejected():
    """Test: accepted edge missing provenance is rejected."""
    edges = [
        {
            "edge_id": "edge_0004",
            "cause": "algorithm_choice",
            "effect": "final_fitness",
            "mechanism": "QIPS more expressive",
            "mechanism_status": "hypothesized",
            "direction": "increases",
            "status": "accepted",
            "supporting_papers": ["paper_1"],
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_1",
                "page": None,  # MISSING page
                "quote": "...",
            },
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)

        try:
            compiler.build_experiment_specs()
            assert False, "Expected SystemExit"
        except SystemExit as e:
            assert e.code == 1

    print("PASS: test_accepted_without_provenance_rejected")


def test_complete_accepted_edge_compiles():
    """Test: complete, accepted edge compiles to experiment spec."""
    edges = [
        {
            "edge_id": "edge_0005",
            "cause": "diversity_mechanism",
            "effect": "final_fitness",
            "mechanism": "population entropy increases",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "supporting_papers": ["paper_1", "paper_2"],
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_1",
                "page": 42,
                "quote": "diversity mechanism increases fitness on 11/11 functions",
            },
            "consensus_confidence": "high",
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)
        compiler.build_experiment_specs()
        compiler.export(output_path)

        # Verify output
        with open(output_path) as f:
            specs = json.load(f)

        assert specs["total_experiments"] == 1
        assert specs["compiler_validation_enforced"] is True

        exp = specs["experiments"][0]
        assert exp["experiment_id"] == "exp_0000"
        assert exp["status"] == "validated"
        assert exp["causal_claim"]["cause"] == "diversity_mechanism"
        assert exp["causal_claim"]["effect"] == "final_fitness"
        assert exp["causal_claim"]["reviewer"] == "mark"
        assert exp["provenance"]["source_paper"] == "paper_1"

        # Verify estimand is present
        assert "estimand" in exp
        assert exp["estimand"]["identification_status"] == "planned_experiment"

        # Verify design controls are explicit
        assert "design_controls" in exp["design"]
        assert exp["design"]["design_controls"]["dimension"] == "stratified"

        # Verify analysis plan is present
        assert "analysis" in exp
        assert exp["analysis"]["summary"] == "median_and_iqr"

    print("PASS: test_complete_accepted_edge_compiles")


def test_unknown_mechanism_status_accepted():
    """Test: edge with mechanism_status='unknown' compiles (mechanism optional)."""
    edges = [
        {
            "edge_id": "edge_0006",
            "cause": "evaluation_budget",
            "effect": "convergence_speed",
            "mechanism": "",  # Unknown/not specified
            "mechanism_status": "unknown",  # EXPLICIT unknown
            "direction": "improves",
            "status": "accepted",
            "supporting_papers": ["paper_3"],
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "source": {
                "paper_id": "paper_3",
                "page": 15,
                "quote": "larger budget improves convergence",
            },
            "consensus_confidence": "medium",
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        with open(graph_path, "w") as f:
            json.dump(create_fixture_graph(edges), f)

        compiler = ExperimentSpecCompiler(graph_path)
        compiler.build_experiment_specs()
        compiler.export(output_path)

        # Verify output
        with open(output_path) as f:
            specs = json.load(f)

        assert specs["total_experiments"] == 1
        exp = specs["experiments"][0]
        assert exp["causal_claim"]["mechanism_status"] == "unknown"
        # Mediator measurements should be empty when mechanism unknown
        assert exp["measurements"]["mediator"] == []

    print("PASS: test_unknown_mechanism_status_accepted")


def run_all_tests():
    """Run all validation tests."""
    print("Running contract tests: Experiment Spec Compiler\n")

    tests = [
        test_proposed_edge_rejected,
        test_rejected_edge_rejected,
        test_accepted_without_reviewer_rejected,
        test_accepted_without_provenance_rejected,
        test_complete_accepted_edge_compiles,
        test_unknown_mechanism_status_accepted,
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}")
            print(f"  Error: {e}")
            sys.exit(1)

    print(f"\n✓ All {len(tests)} tests passed")
    print("Compiler validation gates are working correctly.")


if __name__ == "__main__":
    run_all_tests()
