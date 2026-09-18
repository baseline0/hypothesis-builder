#!/usr/bin/env python3
"""
Import Causal Validations: Apply human review decisions to causal graph.

Reads machine-readable validation records and updates graph edge status,
binding review decisions to the specific graph version they validated.

Ensures:
  - Graph hash consistency (validation is version-specific)
  - Audit trail (who decided what, when, and why)
  - Deterministic workflow (no manual graph edits)
  - Validation rejection rules (invalid decisions, unknown edges, duplicates)

Usage:
    python scripts/import_causal_validations.py \\
        --validations manual/causal_validations.jsonl \\
        --graph automation/processed/causal_graph.json \\
        --output automation/processed/causal_graph_validated.json
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def canonical_json(obj: Any) -> bytes:
    """Canonicalize object to bytes for hashing."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_graph_hash(graph: Dict[str, Any]) -> str:
    """Compute canonical SHA256 hash of graph (without metadata)."""
    # Exclude compiler-added metadata from hash
    clean_graph = {
        k: v for k, v in graph.items()
        if k not in ["hash", "hash_metadata", "validated_at"]
    }
    return hashlib.sha256(canonical_json(clean_graph)).hexdigest()


class ValidationImporter:
    """Import and apply causal validations to graph."""

    VALID_DECISIONS = {"accepted", "rejected", "disputed", "requires_experiment"}

    def __init__(self, graph_path: Path, validations_path: Path):
        with open(graph_path) as f:
            self.graph = json.load(f)

        self.graph_hash = compute_graph_hash(self.graph)
        self.validations: List[Dict] = []
        self.validation_errors: List[str] = []

        # Load validation records
        with open(validations_path) as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    self.validations.append(record)
                except json.JSONDecodeError as e:
                    self.validation_errors.append(
                        f"Line {line_no}: Invalid JSON: {e}"
                    )

    def validate_records(self) -> bool:
        """Validate all review records before applying."""
        for i, record in enumerate(self.validations):
            errors = self._validate_record(record, i)
            self.validation_errors.extend(errors)

        return len(self.validation_errors) == 0

    def _validate_record(self, record: Dict, index: int) -> List[str]:
        """Validate a single review record."""
        errors = []
        prefix = f"Validation {index}:"

        # Required fields
        for field in ["edge_id", "decision", "reviewer", "reviewed_at", "graph_hash"]:
            if field not in record or not record[field]:
                errors.append(f"{prefix} missing {field}")

        # Graph hash binding
        if record.get("graph_hash") != self.graph_hash:
            errors.append(
                f"{prefix} graph_hash mismatch. "
                f"Record: {record.get('graph_hash')[:16]}..., "
                f"Graph: {self.graph_hash[:16]}..."
            )

        # Decision validity
        if record.get("decision") not in self.VALID_DECISIONS:
            errors.append(
                f"{prefix} invalid decision '{record.get('decision')}'. "
                f"Must be one of: {self.VALID_DECISIONS}"
            )

        # Edge existence
        edge_id = record.get("edge_id")
        edge_exists = any(e.get("edge_id") == edge_id for e in self.graph.get("edges", []))
        if not edge_exists:
            errors.append(f"{prefix} edge_id '{edge_id}' not found in graph")

        # Timestamp format
        try:
            datetime.fromisoformat(record.get("reviewed_at", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            errors.append(f"{prefix} malformed timestamp: {record.get('reviewed_at')}")

        # Check for duplicate validations of same edge
        same_edge = [
            r for r in self.validations[:index]
            if r.get("edge_id") == edge_id
        ]
        if same_edge:
            errors.append(
                f"{prefix} duplicate validation for edge_id '{edge_id}' "
                f"(previously at index {self.validations.index(same_edge[0])})"
            )

        return errors

    def apply_validations(self) -> bool:
        """Apply validated review decisions to graph edges."""
        if not self.validate_records():
            print("Validation errors:")
            for error in self.validation_errors:
                print(f"  ERROR: {error}")
            return False

        applied_count = 0
        for record in self.validations:
            edge_id = record["edge_id"]

            # Find edge and update
            for edge in self.graph.get("edges", []):
                if edge.get("edge_id") == edge_id:
                    edge["status"] = record["decision"]
                    edge["reviewer"] = record["reviewer"]
                    edge["reviewed_at"] = record["reviewed_at"]
                    edge["review_rationale"] = record.get("rationale", "")

                    # For disputed/requires_experiment, record relationships
                    if record.get("resolves_edge_ids"):
                        edge["resolves_edge_ids"] = record["resolves_edge_ids"]

                    applied_count += 1
                    break

        print(f"Applied {applied_count}/{len(self.validations)} validations")
        return True

    def export(self, output_path: Path) -> None:
        """Export updated graph with validation metadata."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add validation metadata (but not to hash)
        self.graph["validation_metadata"] = {
            "validations_applied": len(self.validations),
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "graph_hash_at_validation": self.graph_hash,
        }

        with open(output_path, "w") as f:
            json.dump(self.graph, f, indent=2)

        print(f"Validated graph exported: {output_path}")
        print(f"  Graph hash: {self.graph_hash[:16]}...")
        print(f"  Validations applied: {len(self.validations)}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Import human review decisions into causal graph",
        epilog="Binds decisions to graph version via hash; prevents manual edits.",
    )
    parser.add_argument(
        "--validations",
        type=Path,
        required=True,
        help="Path to causal_validations.jsonl (one decision per line)",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        required=True,
        help="Path to causal_graph.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("automation/processed/causal_graph_validated.json"),
        help="Output path for validated graph",
    )

    args = parser.parse_args()

    if not args.validations.exists():
        print(f"ERROR: Validations file not found: {args.validations}")
        sys.exit(1)

    if not args.graph.exists():
        print(f"ERROR: Graph file not found: {args.graph}")
        sys.exit(1)

    print("Importing causal validations...")
    importer = ValidationImporter(args.graph, args.validations)

    if not importer.apply_validations():
        sys.exit(1)

    importer.export(args.output)


if __name__ == "__main__":
    main()
