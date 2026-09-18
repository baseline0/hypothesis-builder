#!/usr/bin/env python3
"""
Experiment Specification Compiler: Turn reviewed causal graph into testable experiments.

Reads validated causal edges and generates experiment specifications that define:
  - Intervention (what to change)
  - Outcome (what to measure)
  - Mediator (mechanism)
  - Controls (what to hold constant)
  - Effect modifiers (when effect varies)
  - Falsification criterion (how the hypothesis could be proven wrong)

Output: synthesis/experiment_specs.json (machine-readable contracts for membrane)
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class ExperimentSpecCompiler:
    """Compile causal graph into experiment specifications."""

    def __init__(self, causal_graph_path: Path):
        with open(causal_graph_path) as f:
            self.graph = json.load(f)
        self.experiments: Dict[str, Dict] = {}
        self.experiment_counter = 0

    def build_experiment_specs(self) -> None:
        """Generate experiment specs from accepted causal edges."""
        accepted_edges = [e for e in self.graph["edges"] if e.get("status") == "accepted"]

        if not accepted_edges:
            print("⚠️  No accepted causal edges found; generating specs from proposed edges")
            accepted_edges = [e for e in self.graph["edges"] if e.get("status") == "proposed"]

        # Group edges by (cause, effect) to build chains
        for edge in accepted_edges:
            self._build_spec_from_edge(edge)

    def _build_spec_from_edge(self, edge: Dict[str, Any]) -> None:
        """Build experiment spec from single causal edge."""
        exp_id = f"exp_{self.experiment_counter:04d}"
        self.experiment_counter += 1

        spec = {
            "experiment_id": exp_id,
            "hypothesis_id": f"H_causal_{exp_id}",
            "source_edge_id": edge["edge_id"],
            "status": "proposed",

            "causal_claim": {
                "cause": edge["cause"],
                "effect": edge["effect"],
                "mechanism": edge.get("mechanism", ""),
                "direction": edge.get("direction", "unknown"),
                "consensus_confidence": edge.get("consensus_confidence", "low"),
                "supporting_papers": edge.get("supporting_papers", []),
            },

            "estimand": {
                "name": f"effect_of_{edge['cause']}_on_{edge['effect']}",
                "treatment": {
                    "variable": edge["cause"],
                    "levels": self._infer_treatment_levels(edge["cause"]),
                    "manipulable": self._is_manipulable(edge["cause"]),
                },
                "outcome": {
                    "variable": edge["effect"],
                    "metric": self._infer_outcome_metric(edge["effect"]),
                    "direction": edge.get("direction", "unknown"),
                },
                "population": "CEC2017 multimodal functions, 10D",
                "time_horizon": "200 generations",
                "comparator": f"same algorithm without {edge['cause']}",
                "confounding_set": self._infer_confounders(edge),
                "mediators": [edge.get("mechanism", "")],
                "effect_modifiers": ["problem_dimension", "function_modality"],
                "identification_assumptions": [
                    "Consistency: Treatment has well-defined outcome",
                    "No unmeasured confounding: All confounders are recorded",
                    "Positivity: Both treatment levels are achievable",
                    "No interference: Algorithm choice doesn't affect others",
                ],
            },

            "design": {
                "design_type": "controlled_benchmark_experiment",
                "factors": self._build_factorial_design(edge),
                "replicates": 30,
                "random_seed_strategy": "blocked by dimension and function",
            },

            "measurements": {
                "primary": [
                    {
                        "variable": edge["effect"],
                        "metric": self._infer_outcome_metric(edge["effect"]),
                        "collection_point": "end_of_run",
                    }
                ],
                "secondary": [
                    {
                        "variable": edge.get("mechanism", "diversity"),
                        "metric": "population_entropy",
                        "collection_point": "every_10_generations",
                    }
                ],
                "diagnostic": [
                    {
                        "variable": "convergence_speed",
                        "metric": "generations_to_threshold",
                    }
                ],
            },

            "predictions": self._build_predictions(edge),

            "falsification_criteria": [
                f"If {edge['cause']} does not change {edge['effect']} direction, hypothesis is falsified",
                "If mechanism measurement shows no change despite outcome change, mechanism incorrect",
                "If effect exists only on unimodal functions, generalizability limited",
            ],

            "dependencies": {
                "papers_to_cite": edge.get("supporting_papers", []),
                "prerequisite_experiments": [],
            },
        }

        self.experiments[exp_id] = spec

    def _infer_treatment_levels(self, cause: str) -> List[str]:
        """Infer treatment levels for a causal variable."""
        level_map = {
            "diversity_mechanism": ["disabled", "enabled"],
            "adaptive_update_frequency": ["static", "dynamic"],
            "algorithm_choice": ["GA", "QIPS"],
            "population_size": ["50", "100"],
            "initialization_strategy": ["random", "informed"],
        }
        return level_map.get(cause, ["off", "on"])

    def _is_manipulable(self, cause: str) -> bool:
        """Check if a causal variable can be experimentally manipulated."""
        manipulable = [
            "diversity_mechanism",
            "adaptive_update_frequency",
            "algorithm_choice",
            "population_size",
            "initialization_strategy",
        ]
        not_manipulable = [
            "problem_dimension",
            "function_class",
            "evaluation_budget",
        ]

        if cause in manipulable:
            return True
        elif cause in not_manipulable:
            return False
        else:
            return True  # Assume manipulable unless marked otherwise

    def _infer_outcome_metric(self, outcome: str) -> str:
        """Suggest measurement for an outcome variable."""
        metric_map = {
            "final_fitness": "best_fitness_of_run",
            "convergence_speed": "generations_to_threshold",
            "solution_diversity": "population_entropy",
            "runtime": "wall_clock_time",
            "premature_convergence": "diversity_at_generation_200",
        }
        return metric_map.get(outcome, f"measure_{outcome}")

    def _infer_confounders(self, edge: Dict) -> List[str]:
        """Suggest confounders to control."""
        default_confounders = [
            "problem_dimension",
            "function_class",
            "evaluation_budget",
            "random_seed",
        ]
        return default_confounders

    def _build_factorial_design(self, edge: Dict) -> List[Dict]:
        """Build factorial design factors."""
        factors = [
            {
                "name": edge["cause"],
                "levels": self._infer_treatment_levels(edge["cause"]),
            },
            {
                "name": "dimension",
                "levels": ["10", "30", "50"],
            },
            {
                "name": "function_class",
                "levels": ["unimodal", "multimodal", "hybrid", "composition"],
            },
        ]
        return factors

    def _build_predictions(self, edge: Dict) -> List[str]:
        """Build testable predictions from causal edge."""
        cause = edge["cause"]
        effect = edge["effect"]
        direction = edge.get("direction", "unknown")

        predictions = [
            f"Enabling {cause} will {direction} {effect}",
            f"The mechanism operates through {edge.get('mechanism', 'unknown pathway')}",
            f"Effect is stronger on multimodal functions than unimodal",
            f"Effect persists as dimension increases (D=10,30,50)",
        ]
        return predictions

    def export(self, output_path: Path) -> None:
        """Export experiment specifications."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        specs = {
            "export_version": "1.0.0",
            "generated_at": "2026-09-18",
            "source_graph": str(self.graph.get("generated_at", "")),
            "total_experiments": len(self.experiments),
            "experiments": list(self.experiments.values()),
        }

        with open(output_path, "w") as f:
            json.dump(specs, f, indent=2)

        print(f"\n✅ Experiment specs exported: {output_path}")
        print(f"   Total experiments: {len(self.experiments)}")
        print(f"   Status: Ready for membrane integration")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Compile experiment specs from causal graph")
    parser.add_argument(
        "--graph",
        type=Path,
        required=True,
        help="Path to validated causal_graph.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("synthesis/experiment_specs.json"),
        help="Output path for experiment specifications",
    )

    args = parser.parse_args()

    if not args.graph.exists():
        print(f"❌ Causal graph not found: {args.graph}")
        sys.exit(1)

    print(f"🧪 Experiment Specification Compiler")
    print(f"   Reading causal graph: {args.graph}")

    compiler = ExperimentSpecCompiler(args.graph)
    compiler.build_experiment_specs()
    compiler.export(args.output)


if __name__ == "__main__":
    main()
