#!/bin/bash
set -e

# Golden Path: End-to-end validation from clean checkout
# Runs the complete test suite for phases 1-4
# Usage: bash tests/fixtures/run_golden_path.sh

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Golden Path: End-to-End Validation"
echo "======================================"
echo "Repository: $REPO_DIR"
echo

cd "$REPO_DIR"

# Step 1: Run all test suite (phases 1-4)
echo "Step 1: Running test suite (Phases 1-4)..."
echo

python -m pytest tests/ -v --tb=short || {
    echo
    echo "❌ TESTS FAILED"
    exit 1
}

echo
echo "Step 2: Verifying test coverage..."
echo

# Count tests
TEST_COUNT=$(python -m pytest tests/ --collect-only -q 2>/dev/null | grep "test_" | wc -l)

if [ "$TEST_COUNT" -lt 23 ]; then
    echo "❌ INSUFFICIENT TESTS: Expected ≥23, found $TEST_COUNT"
    exit 1
fi

echo "✓ Test count: $TEST_COUNT tests"
echo

# Step 3: Verify consumer validator works
echo "Step 3: Testing consumer validator..."
echo

# Create a minimal valid spec for testing
python << 'PYEOF'
import json
from pathlib import Path

specs = {
    "schema_version": "1.0.0",
    "export_version": "1.0.0",
    "total_experiments": 1,
    "experiments": [{
        "schema_version": "1.0.0",
        "experiment_id": "exp_0000",
        "estimand": {
            "treatment": {"variable": "x", "levels": ["a", "b"]},
            "outcome": {"variable": "y", "metric": "m"},
            "population": "test"
        },
        "design": {"design_controls": {"x": "y"}},
        "analysis": {"summary": "mean"},
        "provenance": {
            "source_paper": "p",
            "source_page": 1,
            "source_quote": "q",
            "edge_id": "e1"
        }
    }]
}

Path("synthesis").mkdir(exist_ok=True)
with open("synthesis/golden_path_test.json", "w") as f:
    json.dump(specs, f)
PYEOF

python scripts/validate_experiment_specs.py synthesis/golden_path_test.json > /tmp/validator_output.txt 2>&1

if grep -q "VALID" /tmp/validator_output.txt; then
    echo "✓ Consumer validator passed"
else
    echo "❌ Consumer validator failed"
    cat /tmp/validator_output.txt
    exit 1
fi

echo
echo "======================================"
echo "✅ GOLDEN PATH COMPLETE"
echo
echo "Summary:"
echo "  ✓ All $TEST_COUNT tests passing (Phases 1-4)"
echo "  ✓ Contradiction detection working"
echo "  ✓ Compiler validation enforced"
echo "  ✓ Consumer validator functional"
echo
echo "Ready for corpus ingestion ✓"
echo "======================================"
exit 0
