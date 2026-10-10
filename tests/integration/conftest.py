"""Integration test configuration.

Every test under tests/integration/ gets the `integration` marker at collection
time, so `pytest -m integration` selects this folder. Integration tests may need
sibling repos, local services, or cross-package contracts.
"""

from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: test requiring sibling repos or local setup")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Mark every collected test that lives under tests/integration/."""
    integration_dir = Path(config.rootpath, "tests", "integration")
    for item in items:
        if Path(item.path).is_relative_to(integration_dir):
            item.add_marker(pytest.mark.integration)
