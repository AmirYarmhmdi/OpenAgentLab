"""File guide.

- Use: Provides shared unit-test fixtures.
- Usage: Pytest loads this file automatically for tests under tests/unit.
- Duties: Keeps mutable runtime registries isolated between tests.
- Depends on: External packages: pytest. Project modules:
  openagentlab.tools.registry.
"""

import pytest

from openagentlab.tools.registry import _reset_runtime_registry_for_tests


@pytest.fixture(autouse=True)
def reset_runtime_registry() -> None:
    _reset_runtime_registry_for_tests()
