"""The committed validator fixtures keep their outcomes: a valid spec file passes, and each invalid one fails.

These files are hand-written inputs, so a change to the validator that flips an outcome should fail here.
"""

import pytest
from validate_experiment_specs import ExperimentSpecValidator

from constants import REPO_ROOT

FIXTURES = REPO_ROOT / "tests" / "fixtures"


def test_valid_fixture_passes_validation() -> None:
    assert ExperimentSpecValidator(FIXTURES / "test_specs.json").validate() is True


@pytest.mark.parametrize("name", ["test_specs_invalid.json", "test_specs_invalid_rule.json"])
def test_invalid_fixture_fails_validation(name: str) -> None:
    assert ExperimentSpecValidator(FIXTURES / name).validate() is False
