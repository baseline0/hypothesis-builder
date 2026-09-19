#!/usr/bin/env python3
"""
Membrane Consumer Validator: Validate experiment specifications before ingestion.

Performs schema validation and business rule checks on compiled experiment specs.
Ensures that specs conform to the expected schema and meet all membrane requirements.

Exit codes:
  0: All specs valid, ready for membrane ingestion
  1: Schema or validation errors found
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


class ExperimentSpecValidator:
    """Validate experiment specifications against schema and business rules."""

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, specs_path: Path):
        """Load specs from JSON file."""
        with open(specs_path) as f:
            self.specs = json.load(f)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns True if all specs are valid, False if any errors found.
        """
        # Top-level validation
        self._validate_schema_version()
        self._validate_export_structure()

        # Per-experiment validation
        experiments = self.specs.get("experiments", [])
        if not experiments:
            self.errors.append("No experiments found in specs")
            return False

        for i, exp in enumerate(experiments):
            self._validate_experiment(exp, i)

        return len(self.errors) == 0

    def _validate_schema_version(self) -> None:
        """Check schema version matches expected version."""
        schema = self.specs.get("schema_version")
        if schema != self.SCHEMA_VERSION:
            self.errors.append(
                f"Invalid schema_version: '{schema}' (expected '{self.SCHEMA_VERSION}')"
            )

    def _validate_export_structure(self) -> None:
        """Check top-level export structure."""
        required_fields = ["schema_version", "experiments", "total_experiments"]

        for field in required_fields:
            if field not in self.specs:
                self.errors.append(f"Missing top-level field: {field}")

        total = self.specs.get("total_experiments", 0)
        actual = len(self.specs.get("experiments", []))
        if total != actual:
            self.errors.append(
                f"total_experiments mismatch: declared {total}, actual {actual}"
            )

    def _validate_experiment(self, exp: Dict[str, Any], index: int) -> None:
        """Validate a single experiment specification."""
        exp_id = exp.get("id") or exp.get("experiment_id") or f"exp_{index:04d}"

        # Schema version check
        if exp.get("schema_version") != self.SCHEMA_VERSION:
            self.errors.append(
                f"{exp_id}: schema_version mismatch (expected {self.SCHEMA_VERSION})"
            )

        # Status check
        if exp.get("status") not in ["validated", "accepted", "pending"]:
            self.warnings.append(f"{exp_id}: status '{exp.get('status')}' is non-standard")

        # Required sections
        self._validate_estimand(exp, exp_id)
        self._validate_design(exp, exp_id)
        self._validate_analysis(exp, exp_id)
        self._validate_provenance(exp, exp_id)
        self._validate_causal_claim(exp, exp_id)

    def _validate_estimand(self, exp: Dict[str, Any], exp_id: str) -> None:
        """Validate estimand section."""
        estimand = exp.get("estimand")
        if not estimand:
            self.errors.append(f"{exp_id}: missing estimand")
            return

        if not isinstance(estimand, dict):
            self.errors.append(f"{exp_id}: estimand must be a dict")
            return

        # Check treatment
        treatment = estimand.get("treatment")
        if not treatment:
            self.errors.append(f"{exp_id}: estimand.treatment missing")
        elif not isinstance(treatment, dict):
            self.errors.append(f"{exp_id}: estimand.treatment must be a dict")
        else:
            if not treatment.get("variable"):
                self.errors.append(f"{exp_id}: estimand.treatment.variable missing")
            if "levels" not in treatment:
                self.errors.append(f"{exp_id}: estimand.treatment.levels missing")

        # Check outcome
        outcome = estimand.get("outcome")
        if not outcome:
            self.errors.append(f"{exp_id}: estimand.outcome missing")
        elif not isinstance(outcome, dict):
            self.errors.append(f"{exp_id}: estimand.outcome must be a dict")
        else:
            if not outcome.get("variable"):
                self.errors.append(f"{exp_id}: estimand.outcome.variable missing")

        # Business rule: treatment != outcome
        if treatment and outcome:
            treatment_var = treatment.get("variable") if isinstance(treatment, dict) else None
            outcome_var = outcome.get("variable") if isinstance(outcome, dict) else None

            if treatment_var and outcome_var and treatment_var == outcome_var:
                self.errors.append(
                    f"{exp_id}: treatment and outcome cannot be the same variable"
                )

        # Other estimand fields
        if not estimand.get("population"):
            self.warnings.append(f"{exp_id}: estimand.population not specified")

    def _validate_design(self, exp: Dict[str, Any], exp_id: str) -> None:
        """Validate design section."""
        design = exp.get("design")
        if not design:
            self.errors.append(f"{exp_id}: missing design")
            return

        if not isinstance(design, dict):
            self.errors.append(f"{exp_id}: design must be a dict")
            return

        # Check design_controls
        controls = design.get("design_controls")
        if not controls:
            self.errors.append(f"{exp_id}: design.design_controls missing")
        elif not isinstance(controls, dict):
            self.errors.append(f"{exp_id}: design.design_controls must be a dict")
        elif len(controls) == 0:
            self.errors.append(f"{exp_id}: design.design_controls is empty")

    def _validate_analysis(self, exp: Dict[str, Any], exp_id: str) -> None:
        """Validate analysis section."""
        analysis = exp.get("analysis")
        if not analysis:
            self.errors.append(f"{exp_id}: missing analysis")
            return

        if not isinstance(analysis, dict):
            self.errors.append(f"{exp_id}: analysis must be a dict")
            return

        # Check required analysis fields
        if not analysis.get("primary_outcome"):
            self.warnings.append(f"{exp_id}: analysis.primary_outcome not specified")

        if "summary" not in analysis:
            self.warnings.append(f"{exp_id}: analysis.summary not specified")

    def _validate_provenance(self, exp: Dict[str, Any], exp_id: str) -> None:
        """Validate provenance section (source traceability)."""
        provenance = exp.get("provenance")
        if not provenance:
            self.errors.append(f"{exp_id}: missing provenance")
            return

        if not isinstance(provenance, dict):
            self.errors.append(f"{exp_id}: provenance must be a dict")
            return

        required = ["source_paper", "source_page", "source_quote", "edge_id"]
        for field in required:
            if not provenance.get(field):
                self.errors.append(f"{exp_id}: provenance.{field} missing")

    def _validate_causal_claim(self, exp: Dict[str, Any], exp_id: str) -> None:
        """Validate causal_claim section."""
        claim = exp.get("causal_claim")
        if not claim:
            self.warnings.append(f"{exp_id}: causal_claim section missing")
            return

        if not isinstance(claim, dict):
            self.errors.append(f"{exp_id}: causal_claim must be a dict")
            return

        # Check basic structure
        if not claim.get("cause"):
            self.errors.append(f"{exp_id}: causal_claim.cause missing")
        if not claim.get("effect"):
            self.errors.append(f"{exp_id}: causal_claim.effect missing")

        # Mechanism status should be one of known values
        mechanism_status = claim.get("mechanism_status")
        if mechanism_status:
            valid_status = ["known", "hypothesized", "unknown"]
            if mechanism_status not in valid_status:
                self.errors.append(
                    f"{exp_id}: causal_claim.mechanism_status '{mechanism_status}' invalid"
                )

    def report(self) -> None:
        """Print validation report to stdout."""
        total_specs = len(self.specs.get("experiments", []))

        print("\n" + "=" * 60)
        print("Experiment Specification Validation Report")
        print("=" * 60)

        if self.errors:
            print(f"\n❌ VALIDATION FAILED ({len(self.errors)} errors):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print(f"\n✓ All {total_specs} experiment specs passed validation")

        if self.warnings:
            print(f"\n⚠ {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")

        print(f"\nSchema version: {self.SCHEMA_VERSION}")
        print(f"Export version: {self.specs.get('export_version', 'unknown')}")
        print(f"Total experiments: {total_specs}")

        if self.errors:
            print("\n❌ Status: FAILED (fix errors before proceeding)")
        else:
            print("\n✓ Status: VALID (ready for membrane ingestion)")

        print("=" * 60)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate experiment specifications for membrane ingestion",
        epilog="Enforces schema compliance and business rule checks.",
    )
    parser.add_argument(
        "specs_path",
        type=Path,
        nargs="?",
        default=Path("synthesis/experiment_specs.json"),
        help="Path to experiment_specs.json (default: synthesis/experiment_specs.json)",
    )

    args = parser.parse_args()

    # Check file exists
    if not args.specs_path.exists():
        print(f"ERROR: Specs file not found: {args.specs_path}")
        print("First run: python scripts/experiment_spec_compiler.py --graph <graph.json>")
        sys.exit(1)

    # Validate
    validator = ExperimentSpecValidator(args.specs_path)
    valid = validator.validate()
    validator.report()

    # Exit with appropriate code
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
