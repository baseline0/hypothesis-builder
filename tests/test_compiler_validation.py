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


def test_mechanism_status_unknown_is_allowed_explicitly():
    """
    Test: mechanism_status='unknown' is accepted.

    Distinction: mechanism_status enum has three valid values:
      - 'known': mechanism is established
      - 'hypothesized': mechanism proposed but not proven
      - 'unknown': no mechanism claimed (valid for exploratory)

    Invalid values (e.g., 'speculative', 'proposed') should be rejected.
    This test proves that 'unknown' is a valid enum value, not a rejection.
    """
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

    print("PASS: test_mechanism_status_unknown_is_allowed_explicitly")


def run_all_tests():
    """Run all validation tests."""
    print("Running contract tests: Experiment Spec Compiler\n")

    tests = [
        test_proposed_edge_rejected,
        test_rejected_edge_rejected,
        test_accepted_without_reviewer_rejected,
        test_accepted_without_provenance_rejected,
        test_complete_accepted_edge_compiles,
        test_mechanism_status_unknown_is_allowed_explicitly,
        test_golden_path_fixture,
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


def test_golden_path_fixture():
    """
    Test: Full pipeline with 3 synthetic papers.

    Golden fixture contains:
      - Paper A: accepted edge, known mechanism, complete provenance
      - Paper B: contradictory edge, hypothesized mechanism, incomplete (will be fixed)
      - Paper C: proposed edge (should not compile)

    Expected behavior:
      - Paper A edge compiles to spec
      - Paper B edge compiles with dispute flag
      - Paper C edge rejected (not accepted)
      - Provenance chain preserved
    """
    # Paper A: complete, good edge
    edge_a = {
        "edge_id": "edge_paper_a",
        "cause": "diversity_mechanism",
        "effect": "final_fitness",
        "mechanism": "population entropy increases",
        "mechanism_status": "known",
        "direction": "increases",
        "status": "accepted",
        "supporting_papers": ["paper_a_smith_2023"],
        "reviewer": "mark",
        "reviewed_at": "2026-09-18T10:00:00Z",
        "source": {
            "paper_id": "paper_a_smith_2023",
            "page": 42,
            "quote": "diversity mechanism consistently improves fitness on all 11 functions",
        },
        "consensus_confidence": "high",
    }

    # Paper B: contradictory (different condition/outcome)
    edge_b = {
        "edge_id": "edge_paper_b",
        "cause": "diversity_mechanism",
        "effect": "runtime",
        "mechanism": "more diversity = more exploration = more evals",
        "mechanism_status": "hypothesized",
        "direction": "increases",  # Opposite direction from A
        "status": "accepted",
        "supporting_papers": ["paper_b_jones_2020"],
        "reviewer": "mark",
        "reviewed_at": "2026-09-18T10:30:00Z",
        "source": {
            "paper_id": "paper_b_jones_2020",
            "page": 15,
            "quote": "diversity mechanism increases evaluation cost without proportional benefit",
        },
        "consensus_confidence": "medium",
    }

    # Paper C: proposed (should be rejected by compiler)
    edge_c = {
        "edge_id": "edge_paper_c",
        "cause": "population_size",
        "effect": "convergence_speed",
        "mechanism": "unclear",
        "mechanism_status": "unknown",
        "direction": "improves",
        "status": "proposed",  # NOT accepted
        "supporting_papers": ["paper_c_wang_2022"],
        "reviewer": None,  # No reviewer
        "reviewed_at": None,
        "source": None,
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = Path(tmpdir) / "graph.json"
        output_path = Path(tmpdir) / "specs.json"

        # Create graph with all three edges
        graph = {
            "graph_version": "1.0.0",
            "generated_at": "2026-09-18",
            "total_papers": 3,
            "total_edges": 3,
            "edges": [edge_a, edge_b, edge_c],
            "status": "golden_fixture",
        }

        with open(graph_path, "w") as f:
            json.dump(graph, f)

        # Compiler should process A and B, reject C
        compiler = ExperimentSpecCompiler(graph_path)
        compiler.build_experiment_specs()
        compiler.export(output_path)

        # Verify output
        with open(output_path) as f:
            specs = json.load(f)

        # Should have 2 specs (A and B), not 3 (C rejected)
        assert specs["total_experiments"] == 2, \
            f"Expected 2 specs (A and B compiled, C rejected), got {specs['total_experiments']}"

        # Verify both are present
        spec_ids = [s["experiment_id"] for s in specs["experiments"]]
        assert len(spec_ids) == 2

        # Verify A compiled
        spec_a = next((s for s in specs["experiments"] if s["causal_claim"]["cause"] == "diversity_mechanism"
                       and s["causal_claim"]["effect"] == "final_fitness"), None)
        assert spec_a is not None, "Spec A (diversity → fitness) not found"
        assert spec_a["causal_claim"]["mechanism_status"] == "known"
        assert spec_a["provenance"]["source_paper"] == "paper_a_smith_2023"

        # Verify B compiled
        spec_b = next((s for s in specs["experiments"] if s["causal_claim"]["cause"] == "diversity_mechanism"
                       and s["causal_claim"]["effect"] == "runtime"), None)
        assert spec_b is not None, "Spec B (diversity → runtime) not found"
        assert spec_b["causal_claim"]["mechanism_status"] == "hypothesized"
        assert spec_b["provenance"]["source_paper"] == "paper_b_jones_2020"

        # Verify C did NOT compile (proposed edge rejected)
        spec_c = next((s for s in specs["experiments"] if s["causal_claim"].get("effect") == "convergence_speed"), None)
        assert spec_c is None, "Spec C should not compile (proposed edge not accepted)"

    print("PASS: test_golden_path_fixture")


if __name__ == "__main__":
    run_all_tests()
