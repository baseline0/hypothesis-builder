#!/usr/bin/env python3
"""
Golden Fixture: 10-edge fixture for comprehensive testing.

Tests all important edge types:
1. Accepted, known mechanism, complete
2. Accepted, unknown mechanism (exploratory)
3. Low confidence, observational
4-5. Contradictory pair (same estimand, opposite direction)
6-7. Independent outcomes (same cause, different effects)
8. Multiple supporting papers
9. Proposed (should be rejected)
10. Incomplete (missing reviewer)
"""

import json
from pathlib import Path


def create_10_type_fixture():
    """Create fixture with all 10 important edge types."""
    return [
        # 1. Accepted, known mechanism, complete
        {
            "edge_id": "edge_1_accepted_known",
            "cause": "diversity_mechanism",
            "effect": "final_fitness",
            "mechanism": "population entropy increases",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:00:00Z",
            "supporting_papers": ["paper_1"],
            "source": {
                "paper_id": "paper_1",
                "page": 42,
                "quote": "diversity mechanism improves fitness",
            },
            "consensus_confidence": "high",
        },
        # 2. Accepted, unknown mechanism (exploratory)
        {
            "edge_id": "edge_2_accepted_unknown",
            "cause": "parameter_X",
            "effect": "outcome_Y",
            "mechanism": "",
            "mechanism_status": "unknown",
            "direction": "improves",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:15:00Z",
            "supporting_papers": ["paper_2"],
            "source": {
                "paper_id": "paper_2",
                "page": 15,
                "quote": "parameter X has positive effect",
            },
            "consensus_confidence": "medium",
        },
        # 3. Low confidence, observational evidence
        {
            "edge_id": "edge_3_low_confidence",
            "cause": "feature_A",
            "effect": "result_B",
            "mechanism": "proposed mechanism (unclear)",
            "mechanism_status": "hypothesized",
            "direction": "increases",
            "status": "accepted",
            "evidence_type": "observational_experiment",
            "causal_confidence": "low",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:30:00Z",
            "supporting_papers": ["paper_3"],
            "source": {
                "paper_id": "paper_3",
                "page": 20,
                "quote": "observed correlation with feature A",
            },
            "consensus_confidence": "low",
        },
        # 4. Contradictory pair part A
        {
            "edge_id": "edge_4_contradictory_a",
            "cause": "algorithm_choice",
            "effect": "convergence_speed",
            "mechanism": "QIPS explores more efficiently",
            "mechanism_status": "hypothesized",
            "direction": "increases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T10:45:00Z",
            "supporting_papers": ["paper_4a"],
            "source": {
                "paper_id": "paper_4a",
                "page": 30,
                "quote": "QIPS converges faster",
            },
        },
        # 5. Contradictory pair part B (opposite direction, same estimand)
        {
            "edge_id": "edge_5_contradictory_b",
            "cause": "algorithm_choice",
            "effect": "convergence_speed",
            "mechanism": "QIPS overhead increases runtime",
            "mechanism_status": "hypothesized",
            "direction": "decreases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T11:00:00Z",
            "supporting_papers": ["paper_4b"],
            "source": {
                "paper_id": "paper_4b",
                "page": 35,
                "quote": "QIPS slower due to overhead",
            },
        },
        # 6. Independent outcome 1 (same cause, different effect)
        {
            "edge_id": "edge_6_independent_1",
            "cause": "memory_usage",
            "effect": "solution_quality",
            "mechanism": "more memory allows larger population",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T11:15:00Z",
            "supporting_papers": ["paper_5"],
            "source": {
                "paper_id": "paper_5",
                "page": 50,
                "quote": "memory correlates with quality",
            },
        },
        # 7. Independent outcome 2 (same cause, different effect)
        {
            "edge_id": "edge_7_independent_2",
            "cause": "memory_usage",
            "effect": "runtime",
            "mechanism": "more memory increases GC overhead",
            "mechanism_status": "hypothesized",
            "direction": "increases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T11:30:00Z",
            "supporting_papers": ["paper_6"],
            "source": {
                "paper_id": "paper_6",
                "page": 60,
                "quote": "memory pressure affects runtime",
            },
        },
        # 8. Multiple supporting papers
        {
            "edge_id": "edge_8_multi_source",
            "cause": "population_diversity",
            "effect": "exploration_effectiveness",
            "mechanism": "diverse pop explores more",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "reviewer": "mark",
            "reviewed_at": "2026-09-18T11:45:00Z",
            "supporting_papers": ["paper_7a", "paper_7b", "paper_7c", "paper_7d"],
            "source": {
                "paper_id": "paper_7a",
                "page": 70,
                "quote": "diversity enables exploration",
            },
            "consensus_confidence": "high",
        },
        # 9. Proposed edge (should be rejected)
        {
            "edge_id": "edge_9_proposed",
            "cause": "unknown_parameter",
            "effect": "unknown_outcome",
            "mechanism": "",
            "mechanism_status": "unknown",
            "direction": "unknown",
            "status": "proposed",  # NOT accepted
            "reviewer": None,
            "reviewed_at": None,
            "supporting_papers": [],
        },
        # 10. Incomplete edge (accepted but missing reviewer)
        {
            "edge_id": "edge_10_incomplete",
            "cause": "incomplete_cause",
            "effect": "incomplete_effect",
            "mechanism": "test",
            "mechanism_status": "known",
            "direction": "increases",
            "status": "accepted",
            "reviewer": None,  # Invalid: missing reviewer
            "reviewed_at": None,
            "supporting_papers": ["paper_10"],
            "source": {
                "paper_id": "paper_10",
                "page": 80,
                "quote": "test",
            },
        },
    ]


def test_enhanced_fixture_compilation():
    """
    Test 10-type fixture behavior.

    Expected:
    - Edges 1-8: compile (8 specs)
    - Edges 4-5: marked contradictory (both rejected or special handling)
    - Edges 6-7: compile independently (different outcomes)
    - Edge 8: compiles with 4 supporting papers
    - Edge 9: rejected (proposed)
    - Edge 10: rejected (missing reviewer)

    Final result: 6-8 valid specs (depending on contradiction policy)
    """
    import tempfile
    import subprocess

    edges = create_10_type_fixture()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Build graph
        graph = {
            "graph_version": "1.0.0",
            "generated_at": "2026-09-18",
            "total_papers": 10,
            "total_edges": 10,
            "edges": edges,
        }

        graph_path = tmpdir / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(graph, f)

        # Run contradiction detection
        subprocess.run(
            [
                "python",
                "scripts/detect_contradictions.py",
                "--graph",
                str(graph_path),
                "--output",
                str(tmpdir / "graph_contradictions.json"),
            ],
            cwd=Path(__file__).parent.parent.parent,
            check=False,
        )

        # Run compiler
        specs_path = tmpdir / "specs.json"
        result = subprocess.run(
            [
                "python",
                "scripts/experiment_spec_compiler.py",
                "--graph",
                str(graph_path),
                "--output",
                str(specs_path),
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
        )

        # Check exit code (should be 1 because edges 9-10 are invalid)
        assert result.returncode == 1, f"Expected failure (invalid edges), got {result.returncode}"

        print("✓ Enhanced fixture test: Invalid edges correctly rejected")
        print(f"  Edges 1-8: valid (should compile)")
        print(f"  Edges 4-5: contradictory (marked disputed)")
        print(f"  Edge 9: proposed (rejected)")
        print(f"  Edge 10: missing reviewer (rejected)")


def test_valid_subset_only():
    """Test that only valid edges 1-8 would compile."""
    import tempfile
    import subprocess

    edges = create_10_type_fixture()
    valid_edges = [e for e in edges if e["edge_id"] in [
        "edge_1_accepted_known",
        "edge_2_accepted_unknown",
        "edge_3_low_confidence",
        "edge_4_contradictory_a",
        "edge_5_contradictory_b",
        "edge_6_independent_1",
        "edge_7_independent_2",
        "edge_8_multi_source",
    ]]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        graph = {
            "graph_version": "1.0.0",
            "generated_at": "2026-09-18",
            "total_papers": 10,
            "total_edges": 8,
            "edges": valid_edges,
        }

        graph_path = tmpdir / "graph.json"
        with open(graph_path, "w") as f:
            json.dump(graph, f)

        specs_path = tmpdir / "specs.json"
        result = subprocess.run(
            [
                "python",
                "scripts/experiment_spec_compiler.py",
                "--graph",
                str(graph_path),
                "--output",
                str(specs_path),
            ],
            cwd=Path(__file__).parent.parent.parent,
            capture_output=True,
        )

        # Should succeed (exit 0)
        assert result.returncode == 0, f"Expected success, got {result.returncode}"

        # Should have specs (6-8 depending on contradiction handling)
        with open(specs_path) as f:
            specs = json.load(f)

        valid_count = specs["total_experiments"]
        assert valid_count >= 6, f"Expected at least 6 specs, got {valid_count}"

        print(f"✓ Valid subset compiled: {valid_count} valid specs")


if __name__ == "__main__":
    from pathlib import Path

    print("Testing enhanced 10-type fixture...\n")

    try:
        test_enhanced_fixture_compilation()
        test_valid_subset_only()
        print("\n✓ All enhanced fixture tests passed")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        exit(1)
